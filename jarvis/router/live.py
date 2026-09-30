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
import time
from dataclasses import dataclass
from pathlib import Path

from jarvis.brains import registry
from jarvis.router.features import NaiveBayes, PrivacyDetector

ROOT = Path(__file__).resolve().parents[2]
PREFERENCIA = {  # mientras no hay política aprendida: del más capaz al más barato
    "matematicas": ["claude", "gpt", "gemini", "grok", "local"],
    "codigo":      ["claude", "gpt", "gemini", "grok", "local"],
    "default":     ["gemini", "claude", "gpt", "grok", "local"],
}
ENFRIAMIENTO_S = 600


@dataclass
class Decision:
    order: list[str]
    category: str
    private: bool
    reason: str


class LiveRouter:
    def __init__(self):
        tasks = [json.loads(l) for l in (ROOT / "bench" / "tasks.jsonl").read_text().splitlines()]
        self.intent = NaiveBayes().fit([t["prompt"] for t in tasks], [t["category"] for t in tasks])
        self.privacy = PrivacyDetector(self.intent)
        self.down_until: dict[str, float] = {}
        q = ROOT / "data" / "q_router.json"
        self.q = json.loads(q.read_text())["Q"] if q.exists() else None

    def healthy(self) -> list[str]:
        now = time.time()
        return [b for b in registry.available() if self.down_until.get(b, 0) < now]

    def mark_down(self, brain: str):
        self.down_until[brain] = time.time() + ENFRIAMIENTO_S

    def decide(self, text: str) -> Decision:
        category = self.intent.predict(text)
        private = self.privacy.is_private(text)
        vivos = self.healthy()
        if private:
            return Decision(["local"], category, True, "datos privados → nunca salen del Mac")
        if self.q:
            dificultad = "hard" if len(text) > 160 else "easy"
            q = self.q.get(f"{category}|{dificultad}|False|alto")
            if q:
                orden = sorted([b for b in q if b in vivos], key=q.get, reverse=True)
                return Decision(orden + [b for b in vivos if b not in orden], category, False, "política aprendida (Q-learning)")
        pref = PREFERENCIA.get(category, PREFERENCIA["default"])
        return Decision([b for b in pref if b in vivos], category, False, f"reglas para '{category}'")
