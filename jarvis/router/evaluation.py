"""Evaluación del router, compartida por el notebook del Checkpoint 1 y por
`bench/evaluar_router.py` (el mismo código mide el banco público, el oculto y
cualquier banco nuevo que traiga el profesor).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from jarvis.router.env import Outcome, RouterEnv, load_results
from jarvis.router.qlearning import evaluate, fixed, random_policy, rule_based

# USD por millón de tokens (entrada, salida), precio de lista. Gemini se usa en plan
# gratuito pero con cuota diaria: se le asigna su precio para que la nube sea escasa.
PRECIO = {"gemini": (0.30, 2.50), "local": (0.0, 0.0)}
EPISODIO = 20

CRITERIOS = {
    "calidad": ("Calidad ≥ 95 % de 'nube salvo privado'", lambda r: r["calidad vs. nube segura"] >= 0.95),
    "nube": ("Uso de nube ≤ 60 % (ahorro ≥ 40 %)", lambda r: r["% nube"] <= 0.60),
    "fugas": ("0 fugas de datos privados", lambda r: r["fugas privadas"] == 0),
}


def load_priced(path: Path, brains: list[str]) -> tuple[dict, dict]:
    """Resultados reales con el costo recalculado a precio de lista a partir de los tokens."""
    outcomes, meta = load_results(path, brains)
    filas = {(r["task_id"], r["brain"]): r for r in map(json.loads, Path(path).read_text().splitlines())
             if not r.get("error")}
    for k, o in outcomes.items():
        pin, pout = PRECIO[k[1]]
        f = filas[k]
        outcomes[k] = Outcome(o.score, (f["in_tok"] * pin + f["out_tok"] * pout) / 1e6, o.latency)
    return outcomes, meta


def nube_segura(state, env):
    """La mejor política *permitida*: nube siempre, salvo lo que el detector marca privado."""
    return env.local if state[2] else "gemini"


def baselines() -> dict:
    return {"Nube salvo privado": nube_segura, "Siempre nube (gemini)": fixed("gemini"),
            "Siempre local": fixed("local"), "Aleatoria": random_policy(3), "Regla manual": rule_based("gemini")}


def dias(ids: list[str], n: int = 200, seed: int = 123) -> list[list[str]]:
    rng = random.Random(seed)
    return [[rng.choice(ids) for _ in range(EPISODIO)] for _ in range(n)]


def compare(agent, env: RouterEnv, seqs: list[list[str]], extra: dict | None = None) -> dict[str, dict]:
    """Evalúa el agente y las líneas base sobre los MISMOS días; agrega la calidad relativa."""
    pols = {"Q-learning (JARVIS)": agent, **baselines(), **(extra or {})}
    res = {k: evaluate(p, env, seqs) for k, p in pols.items()}
    ref = res["Nube salvo privado"]["calidad media"]
    for r in res.values():
        r["calidad vs. nube segura"] = r["calidad media"] / ref
    return res


def check(r: dict) -> dict[str, bool]:
    return {nombre: f(r) for nombre, f in CRITERIOS.values()}
