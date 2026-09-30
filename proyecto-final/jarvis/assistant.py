"""JARVIS: une memoria + router + cerebros en una sola conversación."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass

from jarvis.brains import registry
from jarvis.council import deliberate
from jarvis.memory import Memory
from jarvis.router.live import LiveRouter

PERSONA = """Eres J.A.R.V.I.S., el asistente personal de Nicolás Rodríguez (Nico): estudiante de ingeniería
de software en EAFIT (Medellín), emprendedor y trader. Personalidad: el JARVIS de las películas —
mayordomo británico impecable, calmado, preciso, con ingenio seco y leal; lo llamas "señor".
Reglas:
- Responde en el idioma en que te hablen (español por defecto).
- Sé breve: 1–3 frases salvo que pidan detalle. Nada de listas ni markdown en respuestas habladas.
- Usa los datos del CONTEXTO EN VIVO para hora, fecha y clima; nunca inventes datos en tiempo real.
  Si no tienes un dato, dilo con elegancia.
- Usa lo que Nico te pidió recordar solo cuando sea relevante para la pregunta; no lo menciones por iniciativa."""

_WX = {"t": 0, "txt": "no disponible"}


def contexto_en_vivo() -> str:
    import datetime
    import requests
    if time.time() - _WX["t"] > 900:
        try:
            j = requests.get("https://api.open-meteo.com/v1/forecast?latitude=6.2442&longitude=-75.5812"
                             "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m", timeout=4).json()["current"]
            _WX.update(t=time.time(), txt=f"{j['temperature_2m']:.0f} °C, humedad {j['relative_humidity_2m']} %, "
                                          f"viento {j['wind_speed_10m']:.0f} km/h (código WMO {j['weather_code']})")
        except Exception:
            pass
    ahora = datetime.datetime.now()
    return f"CONTEXTO EN VIVO: {ahora:%A %d de %B de %Y, %H:%M} (Medellín). Clima en Medellín: {_WX['txt']}."


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
    members: list[dict] | None = None
    lang: str = "es"
    difficulty: str = "easy"


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
        partes = [contexto_en_vivo()]
        hechos = self.memory.facts()
        if hechos:
            partes.append("Cosas que Nico te pidió recordar:\n" + "\n".join(f"- {h}" for h in hechos))
        hist = self.memory.history(session)
        if hist:
            partes.append("Conversación reciente:\n" + "\n".join(f"{'Nico' if r == 'user' else 'JARVIS'}: {t}" for r, t in hist))
        partes.append(f"Nico: {text}")
        return "\n\n".join(partes)

    def ask(self, text: str, session: str = "default", fast: bool = False, lang: str = "es",
            emit=lambda *a, **k: None) -> Reply:
        m = re.match(r"^\s*(recuerda|recuérdalo|anota|remember)\s+(que\s+|that\s+)?(.+)", text, re.IGNORECASE)
        if m:
            self.memory.remember(m.group(3).strip())
        d = self.router.decide(text, fast=fast, spent_today=self.memory.spent_today())
        members = d.order
        if fast and not d.private and any(b != "local" for b in members):
            members = [b for b in members if b != "local"]     # en voz, el local (lento) no entra al consejo
        idioma = "English" if lang == "en" else "español"
        prompt = self._prompt(session, text) + f"\n\n(Responde en {idioma}.)"
        emit("route", category=d.category, difficulty=d.difficulty, private=d.private, reason=d.reason, members=members)
        res = deliberate(prompt, text, members, self._brain, system=PERSONA,
                         deadline_s=9.0 if fast else 30.0, emit=emit)
        for info in res.members:
            if info["status"] != "ok":
                self.router.mark_down(info["brain"]) if info["status"] == "fallo" else None
        self.memory.add(session, "user", text, category=d.category, private=d.private)
        self.memory.add(session, "assistant", res.text, brain=res.synthesizer or "-", category=d.category,
                        private=d.private, cost=res.cost, latency=res.latency)
        return Reply(res.text, "consejo" if len([i for i in res.members if i["status"] == "ok"]) > 1 else (res.synthesizer or "-"),
                     d.category, d.private, d.reason, res.cost, res.latency, [i["brain"] for i in res.members],
                     res.members, lang, d.difficulty)
