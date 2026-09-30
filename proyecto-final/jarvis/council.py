"""Consejo de cerebros: JARVIS es UNA sola IA hecha de varias.

Para cada petición:
1. El router decide QUIÉNES deliberan (privacidad → solo el local; presupuesto, salud).
2. Todos los participantes piensan EN PARALELO con el mismo prompt.
3. Se espera hasta un plazo (corto en voz, más largo en texto); los que no llegan
   a tiempo no retrasan la respuesta.
4. Un sintetizador (el cerebro más capaz disponible) fusiona las respuestas en una
   sola voz: toma lo correcto de cada una, resuelve contradicciones y descarta errores.
   Si solo llegó una respuesta, se usa directamente (sin costo extra).

Cada paso se publica como evento para que el HUD muestre al consejo pensando.
"""
from __future__ import annotations

import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from typing import Callable

from jarvis.brains.base import BrainResponse

SINTESIS = """Eres el núcleo de síntesis de J.A.R.V.I.S. Varios cerebros respondieron la misma petición.
Fusiónalas en UNA sola respuesta final, en la voz de JARVIS (mayordomo británico, preciso, ingenio seco,
llama "señor" a Nico). Reglas:
- Si discrepan en un hecho o cálculo, verifica el razonamiento y quédate con lo correcto.
- Conserva lo mejor de cada una; no menciones que hubo varios cerebros ni los compares.
- Mismo idioma que la petición. Breve (1–3 frases) salvo que pidan detalle. Sin markdown.

PETICIÓN DE NICO:
{pregunta}

RESPUESTAS DE LOS CEREBROS:
{respuestas}

RESPUESTA FINAL DE JARVIS:"""

# del más capaz al menos capaz: el primero disponible sintetiza
SINTETIZADORES = ["claude", "gpt", "gemini", "grok", "local"]


@dataclass
class CouncilResult:
    text: str
    members: list[dict] = field(default_factory=list)   # {brain, status, latency, cost, preview}
    synthesizer: str | None = None
    latency: float = 0.0
    cost: float = 0.0


def deliberate(prompt: str, question: str, members: list[str], load: Callable, *, system: str,
               deadline_s: float, grace_s: float = 6.0, emit: Callable = lambda *a, **k: None,
               max_tokens: int = 700) -> CouncilResult:
    t0 = time.perf_counter()
    emit("council_start", members=members)
    pool = ThreadPoolExecutor(max_workers=len(members))
    futs = {pool.submit(load(m).ask, prompt, system=system, max_tokens=max_tokens, temperature=0.4): m for m in members}
    # plazo de gracia: cuando llega la primera respuesta útil, los demás tienen grace_s más
    pendientes, primera = set(futs), None
    while pendientes:
        restante = deadline_s - (time.perf_counter() - t0)
        if primera is not None:
            restante = min(restante, grace_s - (time.perf_counter() - primera))
        if restante <= 0:
            break
        listos, pendientes = wait(pendientes, timeout=restante, return_when=FIRST_COMPLETED)
        if primera is None and any(f.result().ok for f in listos):
            primera = time.perf_counter()
    done = set(futs) - pendientes
    pool.shutdown(wait=False, cancel_futures=True)

    oks: list[BrainResponse] = []
    info = []
    for f, m in futs.items():
        if f in done and f.result().ok and f.result().text.strip():
            r = f.result()
            oks.append(r)
            info.append({"brain": m, "status": "ok", "latency": round(r.latency_s, 2), "cost": r.cost_usd,
                         "preview": r.text.strip()[:140]})
        else:
            err = f.result().error if f in done else "fuera de tiempo"
            info.append({"brain": m, "status": "fallo" if f in done else "tarde", "latency": None, "cost": 0,
                         "preview": (err or "")[:80]})
        emit("council_member", **info[-1])

    cost = sum(r.cost_usd for r in oks)
    if not oks:
        return CouncilResult("Ninguno de mis cerebros respondió a tiempo, señor.", info, None,
                             time.perf_counter() - t0, 0.0)
    if len(oks) == 1:
        return CouncilResult(oks[0].text.strip(), info, oks[0].brain, time.perf_counter() - t0, cost)

    vivos = {r.brain for r in oks}
    synth = next((b for b in SINTETIZADORES if b in vivos), oks[0].brain)
    emit("council_synth", brain=synth)
    bloque = "\n\n".join(f"[Cerebro {i + 1}]\n{r.text.strip()}" for i, r in enumerate(oks))
    s = load(synth).ask(SINTESIS.format(pregunta=question, respuestas=bloque), system=system,
                        max_tokens=max_tokens, temperature=0.2)
    if s.ok and s.text.strip():
        return CouncilResult(s.text.strip(), info, synth, time.perf_counter() - t0, cost + s.cost_usd)
    mejor = next(r for r in oks if r.brain == synth)
    return CouncilResult(mejor.text.strip(), info, synth, time.perf_counter() - t0, cost)
