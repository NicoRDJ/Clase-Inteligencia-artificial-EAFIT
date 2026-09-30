"""JARVIS: une memoria + router + cerebros en una sola conversación."""
from __future__ import annotations

import re
from dataclasses import dataclass

from jarvis.brains import registry
from jarvis.memory import Memory
from jarvis.router.live import LiveRouter

PERSONA = """Eres JARVIS, el asistente personal de Nicolás Rodríguez (Nico): estudiante de ingeniería
de software en EAFIT (Medellín), emprendedor y trader. Respondes en español, con precisión,
directo y con un toque de ingenio, como el JARVIS de Tony Stark. Si no sabes algo, lo dices.
Formato: respuestas cortas salvo que te pidan detalle."""


@dataclass
class Reply:
    text: str
    brain: str
    category: str
    private: bool
    reason: str
    cost: float
    latency: float
    tried: list[str]


class Jarvis:
    def __init__(self):
        self.memory = Memory()
        self.router = LiveRouter()
        self._brains: dict = {}

    def _brain(self, name):
        if name not in self._brains:
            self._brains[name] = registry.load(name)
        return self._brains[name]

    def _prompt(self, session: str, text: str) -> str:
        partes = []
        hechos = self.memory.facts()
        if hechos:
            partes.append("Cosas que Nico te pidió recordar:\n" + "\n".join(f"- {h}" for h in hechos))
        hist = self.memory.history(session)
        if hist:
            partes.append("Conversación reciente:\n" + "\n".join(f"{'Nico' if r == 'user' else 'JARVIS'}: {t}" for r, t in hist))
        partes.append(f"Nico: {text}")
        return "\n\n".join(partes)

    def ask(self, text: str, session: str = "default") -> Reply:
        m = re.match(r"^\s*(recuerda|recuérdalo|anota)\s+(que\s+)?(.+)", text, re.IGNORECASE)
        if m:
            self.memory.remember(m.group(3).strip())
        d = self.router.decide(text)
        prompt = self._prompt(session, text)
        tried = []
        for name in d.order:
            tried.append(name)
            r = self._brain(name).ask(prompt, system=PERSONA, max_tokens=800, temperature=0.4)
            if r.ok and r.text.strip():
                self.memory.add(session, "user", text, category=d.category, private=d.private)
                self.memory.add(session, "assistant", r.text, brain=name, category=d.category,
                                private=d.private, cost=r.cost_usd, latency=r.latency_s)
                return Reply(r.text.strip(), name, d.category, d.private, d.reason, r.cost_usd, r.latency_s, tried)
            self.router.mark_down(name)
        return Reply("Ningún cerebro está disponible en este momento.", "-", d.category, d.private, d.reason, 0, 0, tried)
