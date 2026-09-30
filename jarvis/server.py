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
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from jarvis.assistant import Jarvis

app = FastAPI(title="JARVIS")
jarvis = Jarvis()


class Ask(BaseModel):
    text: str
    session: str = "web"


@app.get("/health")
def health():
    return {"status": "online", "brains": jarvis.router.healthy(),
            "spent_today_usd": round(jarvis.memory.spent_today(), 4), "facts": len(jarvis.memory.facts())}


@app.post("/ask")
def ask(q: Ask):
    r = jarvis.ask(q.text, session=q.session)
    return {"text": r.text, "brain": r.brain, "category": r.category, "private": r.private,
            "reason": r.reason, "cost_usd": r.cost, "latency_s": round(r.latency, 2), "tried": r.tried}


PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JARVIS</title><style>
body{margin:0;font-family:-apple-system,system-ui,sans-serif;background:#0b0f14;color:#e6edf3}
header{padding:14px 18px;border-bottom:1px solid #1f2a36;font-weight:600;letter-spacing:.5px}
header span{color:#39c5ff}#log{padding:18px;max-width:820px;margin:auto;padding-bottom:110px}
.m{margin:10px 0;padding:10px 14px;border-radius:12px;line-height:1.45;white-space:pre-wrap}
.u{background:#1b2633;margin-left:18%}.j{background:#111a23;border:1px solid #1f2a36;margin-right:18%}
.meta{font-size:12px;color:#7d8b99;margin-top:6px}form{position:fixed;bottom:0;left:0;right:0;background:#0b0f14;
border-top:1px solid #1f2a36;padding:12px}.row{display:flex;gap:8px;max-width:820px;margin:auto}
input{flex:1;padding:12px;border-radius:10px;border:1px solid #2b3a4a;background:#111a23;color:#e6edf3;font-size:15px}
button{padding:0 18px;border-radius:10px;border:0;background:#39c5ff;color:#001018;font-weight:600}
</style></head><body><header><span>●</span> JARVIS</header><div id="log"></div>
<form id="f"><div class="row"><input id="t" placeholder="Habla con JARVIS…" autofocus><button>Enviar</button></div></form>
<script>
const log=document.getElementById('log');
function add(c,t,m){const d=document.createElement('div');d.className='m '+c;d.textContent=t;
if(m){const s=document.createElement('div');s.className='meta';s.textContent=m;d.appendChild(s)}log.appendChild(d);scrollTo(0,1e9)}
document.getElementById('f').onsubmit=async e=>{e.preventDefault();const i=document.getElementById('t');const t=i.value.trim();if(!t)return;
i.value='';add('u',t);const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});
const j=await r.json();add('j',j.text,`${j.brain} · ${j.latency_s}s · $${j.cost_usd.toFixed(4)} · ${j.reason}`)}
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE
