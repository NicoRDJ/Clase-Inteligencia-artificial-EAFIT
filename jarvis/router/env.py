"""El problema del router como un MDP (semana 4) sobre datos reales del benchmark.

Un episodio es "un día de JARVIS": llegan N peticiones y hay un presupuesto
diario en dólares. En cada paso el agente elige qué cerebro atiende la
petición actual.

    Estado   s = (categoría, dificultad, privada, nivel_de_presupuesto)
    Acción   a ∈ cerebros disponibles (local, claude, gpt, grok)
    Recompensa
        r = calidad − λ · costo / costo_ref − μ · latencia / latencia_ref
        r = −PENAL_FUGA        si la petición es privada y a no es local
        r = −PENAL_PRESUP      si a cuesta más que el presupuesto que queda
    Transición: el presupuesto baja con el costo real; llega la siguiente petición.

El presupuesto es lo que vuelve el problema *secuencial* (γ > 0): gastar en
peticiones fáciles temprano deja sin cerebros caros a las difíciles del final.
Calidad, costo y latencia NO se inventan: salen de data/results.jsonl, es
decir, de haber corrido de verdad cada tarea en cada cerebro.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PENAL_FUGA = 2.0
PENAL_PRESUP = 1.0
NIVELES = ("agotado", "bajo", "medio", "alto")


@dataclass
class Outcome:
    score: float
    cost: float
    latency: float


def load_results(path: Path, brains: list[str]) -> tuple[dict, dict]:
    """→ (outcomes[(task_id, brain)] = Outcome, tasks[task_id] = fila de metadatos)."""
    outcomes, tasks = {}, {}
    for r in map(json.loads, Path(path).read_text().splitlines()):
        if r["brain"] in brains and not r.get("error"):
            outcomes[(r["task_id"], r["brain"])] = Outcome(r["score"], r["cost_usd"], r["latency_s"])
            tasks[r["task_id"]] = {k: r[k] for k in ("category", "difficulty", "private")}
    # solo tareas que tienen resultado en TODOS los cerebros
    completas = {t for t in tasks if all((t, b) in outcomes for b in brains)}
    return ({k: v for k, v in outcomes.items() if k[0] in completas},
            {t: m for t, m in tasks.items() if t in completas})


class RouterEnv:
    def __init__(self, outcomes: dict, tasks: dict, brains: list[str], task_ids: list[str], *,
                 episode_len: int = 20, daily_budget: float = 0.05, lam: float = 0.5, mu: float = 0.2,
                 local: str = "local", seed: int = 0, observed: dict | None = None):
        """`observed[task_id] = (categoría, dificultad, privada)` según la percepción (Naive Bayes +
        detector). Si se da, el agente decide con lo que *ve*, pero las fugas se cuentan con la
        etiqueta real: un dato privado que el detector deja pasar es una fuga aunque el escudo exista."""
        self.o, self.meta, self.brains, self.ids = outcomes, tasks, brains, list(task_ids)
        self.observed = observed
        self.n, self.budget0, self.lam, self.mu, self.local = episode_len, daily_budget, lam, mu, local
        self.rng = random.Random(seed)
        costs = [v.cost for v in outcomes.values() if v.cost > 0]
        lats = [v.latency for v in outcomes.values()]
        self.cost_ref = (sum(costs) / len(costs)) if costs else 1.0
        self.lat_ref = sorted(lats)[len(lats) // 2] if lats else 1.0

    # ── estado ──────────────────────────────────────────────────────────────
    def _nivel(self) -> str:
        f = self.budget / self.budget0
        return "agotado" if f <= 1e-9 else "bajo" if f < 0.25 else "medio" if f < 0.6 else "alto"

    def _state(self):
        tid = self.queue[self.t]
        if self.observed is not None:
            return (*self.observed[tid], self._nivel())
        m = self.meta[tid]
        return (m["category"], m["difficulty"], m["private"], self._nivel())

    def reset(self, task_sequence: list[str] | None = None):
        self.queue = task_sequence or [self.rng.choice(self.ids) for _ in range(self.n)]
        self.t, self.budget = 0, self.budget0
        self.stats = defaultdict(float)
        return self._state()

    # ── dinámica ────────────────────────────────────────────────────────────
    def step(self, action: str):
        tid = self.queue[self.t]
        m, out = self.meta[tid], self.o[(tid, action)]
        fuga = m["private"] and action != self.local
        sin_plata = out.cost > self.budget + 1e-12

        if fuga:
            r = -PENAL_FUGA
        elif sin_plata:
            r = -PENAL_PRESUP
        else:
            r = out.score - self.lam * out.cost / self.cost_ref - self.mu * out.latency / self.lat_ref

        # la petición se atiende de todas formas; si no alcanza la plata, la atiende el local
        real = out if not sin_plata else self.o[(tid, self.local)]
        self.budget = max(0.0, self.budget - (out.cost if not sin_plata else 0.0))
        self.stats["calidad"] += real.score
        self.stats["costo"] += out.cost if not sin_plata else 0.0
        self.stats["latencia"] += real.latency
        self.stats["fugas"] += fuga
        self.stats["nube"] += (action != self.local) and not sin_plata
        self.stats["sin_presupuesto"] += sin_plata
        self.t += 1
        done = self.t >= len(self.queue)
        return (None if done else self._state()), r, done
