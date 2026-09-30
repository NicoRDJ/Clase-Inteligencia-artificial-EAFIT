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

from fastapi.responses import HTMLResponse
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
    r = jarvis.ask(q.text, session=q.session)
    return {"text": r.text, "brain": r.brain, "category": r.category, "private": r.private,
            "reason": r.reason, "cost_usd": r.cost, "latency_s": round(r.latency, 2), "tried": r.tried}


WEB = Path(__file__).parent / "web"


@app.get("/", response_class=HTMLResponse)
def home():
    return (WEB / "index.html").read_text(encoding="utf-8")
