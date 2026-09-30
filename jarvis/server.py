"""Servidor de JARVIS (FastAPI): una sola puerta para cualquier cliente
(terminal, Telegram, atajos de iOS, otras apps locales).

    uvicorn jarvis.server:app --host 127.0.0.1 --port 8765

Endpoints:
    GET  /health            → cerebros disponibles y gasto del día
    POST /ask  {"text", "session"} → respuesta + qué cerebro respondió y por qué
    GET  /                  → mini chat web
"""
from __future__ import annotations

from fastapi import FastAPI
from pathlib import Path

from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json as _json
from pydantic import BaseModel

from jarvis.assistant import Jarvis

import threading
import time as _time

app = FastAPI(title="JARVIS")
jarvis = Jarvis()


def _vigilante():
    while True:
        jarvis.router.probe()
        _time.sleep(600)


threading.Thread(target=_vigilante, daemon=True).start()


class Ask(BaseModel):
    text: str
    session: str = "web"
    fast: bool = False
    lang: str = "es"


class VoiceEvent(BaseModel):
    state: str
    text: str | None = None
    lang: str | None = None


_bus: list[dict] = []          # bus de eventos para el HUD (voz + consejo)


def publish(kind: str, **data):
    ev = {"kind": kind, "seq": (_bus[-1]["seq"] + 1) if _bus else 1, "ts": _time.time(), **data}
    _bus.append(ev)
    del _bus[:-200]


@app.post("/voice/event")
def voice_event(ev: VoiceEvent):
    """El oído (jarvis.voice.ears) publica aquí su estado: listening, thinking, heard, speaking, idle."""
    publish("voice", **ev.model_dump())
    return {"ok": True}


@app.get("/events")
async def events():
    """Server-Sent Events: el HUD recibe en vivo lo que hace la voz."""
    async def gen():
        last = _bus[-1]["seq"] if _bus else 0
        while True:
            for ev in [e for e in _bus if e["seq"] > last]:
                last = ev["seq"]
                yield f"data: {_json.dumps(ev, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.08)
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/health")
def health():
    return {"status": "online", "brains": jarvis.router.healthy(),
            "spent_today_usd": round(jarvis.memory.spent_today(), 4), "facts": len(jarvis.memory.facts())}


@app.get("/state")
def state():
    """Datos para los paneles del HUD."""
    from jarvis.brains import registry
    vivos = set(jarvis.router.healthy())
    brains = [{"name": n, "model": s.model, "local": s.local, "online": n in vivos,
               "status": jarvis.router.status.get(n, "verificando"),
               "paid": (s.price_in + s.price_out) > 0} for n, s in registry.SPECS.items()
              if n in registry.available()]
    rows = jarvis.memory.db.execute(
        "SELECT brain, COUNT(*), AVG(latency) FROM messages WHERE role='assistant' GROUP BY brain").fetchall()
    return {"brains": brains, "facts": jarvis.memory.facts()[-6:],
            "spent_today_usd": round(jarvis.memory.spent_today(), 4),
            "usage": [{"brain": b, "n": n, "avg_latency": round(l or 0, 1)} for b, n, l in rows],
            "learned_policy": jarvis.router.q is not None}


@app.post("/ask")
def ask(q: Ask):
    r = jarvis.ask(q.text, session=q.session, fast=q.fast, lang=q.lang, emit=publish)
    return {"text": r.text, "brain": r.brain, "category": r.category, "private": r.private,
            "reason": r.reason, "cost_usd": r.cost, "latency_s": round(r.latency, 2), "tried": r.tried,
            "members": r.members, "lang": r.lang}


WEB = Path(__file__).parent / "web"


@app.get("/", response_class=HTMLResponse)
def home():
    return (WEB / "index.html").read_text(encoding="utf-8")
