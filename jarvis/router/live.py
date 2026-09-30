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

    def decide(self, text: str, fast: bool = False) -> Decision:
        category = self.intent.predict(text)
        private = self.privacy.is_private(text)
        vivos = self.healthy()
        if private:
            return Decision(["local"], category, True, "datos privados → nunca salen del Mac")
        if fast:  # conversación por voz: prima la latencia (la nube responde en ~1 s, el local en ~10 s)
            nube = [b for b in PREFERENCIA.get(category, PREFERENCIA["default"]) if b in vivos and b != "local"]
            if nube:
                return Decision(nube + ["local"], category, False, "modo voz → el cerebro más rápido disponible")
        if self.q:
            dificultad = "hard" if len(text) > 160 else "easy"
            q = self.q.get(f"{category}|{dificultad}|False|alto")
            if q:
                orden = sorted([b for b in q if b in vivos], key=q.get, reverse=True)
                return Decision(orden + [b for b in vivos if b not in orden], category, False, "política aprendida (Q-learning)")
        pref = PREFERENCIA.get(category, PREFERENCIA["default"])
        return Decision([b for b in pref if b in vivos], category, False, f"reglas para '{category}'")
