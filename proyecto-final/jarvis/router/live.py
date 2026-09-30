"""Router en producción: decide qué cerebro atiende cada mensaje real.

Orden de decisión:
1. Privacidad (regla dura): si el mensaje tiene datos sensibles → solo el cerebro local.
2. Política aprendida: si existe data/q_router.json (Q-learning del Checkpoint 1), se usa.
3. Política por reglas mientras no hay entrenamiento: el mejor cerebro disponible
   para la categoría detectada.
4. Salud: un cerebro que falla (sin saldo, sin cuota, caído) queda en "enfriamiento"
   unos minutos y la petición pasa al siguiente.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from jarvis.brains import registry
from jarvis.router.features import Perception

ROOT = Path(__file__).resolve().parents[2]
PREFERENCIA = {  # mientras no hay política aprendida: del más capaz al más barato
    "matematicas": ["claude", "gpt", "gemini", "grok", "local"],
    "codigo":      ["claude", "gpt", "gemini", "grok", "local"],
    "default":     ["gemini", "claude", "gpt", "grok", "local"],
}
ENFRIAMIENTO_S = 600
PRESUPUESTO_DIA = float(os.getenv("JARVIS_DAILY_BUDGET_USD", "1.0"))   # gasto diario tolerado en cerebros de pago


def nivel_presupuesto(gastado: float, total: float = PRESUPUESTO_DIA) -> str:
    """Mismos niveles que el MDP del Checkpoint 1."""
    f = max(0.0, total - gastado) / total if total > 0 else 0.0
    return "agotado" if f <= 1e-9 else "bajo" if f < 0.25 else "medio" if f < 0.6 else "alto"


@dataclass
class Decision:
    order: list[str]
    category: str
    private: bool
    reason: str
    difficulty: str = "easy"


class LiveRouter:
    def __init__(self):
        tasks = [json.loads(l) for l in (ROOT / "bench" / "tasks.jsonl").read_text().splitlines()]
        self.perceive = Perception(tasks)     # la misma percepción que se evalúa en el Checkpoint 1
        self.down_until: dict[str, float] = {}
        self.status: dict[str, str] = {}
        q = ROOT / "data" / "q_router.json"
        self.q = json.loads(q.read_text())["Q"] if q.exists() else None

    def probe(self) -> dict[str, str]:
        """Prueba real (1 token) de cada cerebro de pago: detecta saldo agotado,
        llaves inválidas o cuotas, y los deja fuera hasta la próxima prueba."""
        estado = {}
        for name in registry.available():
            sp = registry.SPECS[name]
            if sp.local or (sp.price_in + sp.price_out) == 0:   # local o gratis con cuota: no gastar cuota en pruebas
                estado[name] = "ok"
                continue
            r = registry.load(name).ask("ok", max_tokens=5)
            if r.ok:
                self.down_until.pop(name, None)
                estado[name] = "ok"
            else:
                self.down_until[name] = time.time() + ENFRIAMIENTO_S
                e = (r.error or "").lower()
                estado[name] = ("sin saldo" if "credit" in e or "balance" in e or "billing" in e
                                else "sin permiso" if "403" in e or "permission" in e
                                else "cuota" if "429" in e or "quota" in e else "error")
        self.status = estado
        return estado

    def healthy(self) -> list[str]:
        now = time.time()
        return [b for b in registry.available() if self.down_until.get(b, 0) < now]

    def mark_down(self, brain: str):
        self.down_until[brain] = time.time() + ENFRIAMIENTO_S

    def q_values(self, category: str, difficulty: str, nivel: str) -> dict | None:
        """Q(s, ·) con el mismo respaldo que el agente: si el estado no se visitó,
        promedio de los estados de la misma categoría y dificultad, luego de la categoría."""
        if not self.q:
            return None
        exacto = self.q.get(f"{category}|{difficulty}|False|{nivel}")
        if exacto:
            return exacto
        for prefijo in (f"{category}|{difficulty}|False|", f"{category}|"):
            vecinos = [v for k, v in self.q.items() if k.startswith(prefijo)]
            if vecinos:
                return {a: sum(v[a] for v in vecinos) / len(vecinos) for a in vecinos[0]}
        return None

    def decide(self, text: str, fast: bool = False, spent_today: float = 0.0) -> Decision:
        category, difficulty, private = self.perceive(text)
        vivos = self.healthy()
        if private:
            return Decision(["local"], category, True, "datos privados → nunca salen del Mac", difficulty)
        if fast:  # conversación por voz: prima la latencia (la nube responde en ~1 s, el local en ~10 s)
            nube = [b for b in PREFERENCIA.get(category, PREFERENCIA["default"]) if b in vivos and b != "local"]
            if nube:
                return Decision(nube + ["local"], category, False, "modo voz → el cerebro más rápido disponible", difficulty)
        q = self.q_values(category, difficulty, nivel_presupuesto(spent_today))
        if q:
            orden = sorted([b for b in q if b in vivos], key=q.get, reverse=True)
            return Decision(orden + [b for b in vivos if b not in orden], category, False,
                            "política aprendida (Q-learning)", difficulty)
        pref = PREFERENCIA.get(category, PREFERENCIA["default"])
        return Decision([b for b in pref if b in vivos], category, False, f"reglas para '{category}'", difficulty)
