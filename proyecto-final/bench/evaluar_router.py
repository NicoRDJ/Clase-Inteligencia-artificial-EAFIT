"""Evalúa el router congelado de JARVIS (data/q_router.json) sobre cualquier banco.

Pensado para casos ocultos: el profesor escribe sus propias tareas con el formato de
bench/tasks.jsonl, corre los cerebros y evalúa, sin reentrenar nada:

    python -m bench.run_bench --tareas sus_tareas.jsonl --salida data/sus_resultados.jsonl local gemini
    python -m bench.evaluar_router sus_tareas.jsonl data/sus_resultados.jsonl

Por defecto evalúa el banco oculto (bench/hidden_tasks.jsonl + data/hidden_results.jsonl).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jarvis.router.env import RouterEnv
from jarvis.router.evaluation import compare, check, dias, load_priced
from jarvis.router.features import Perception
from jarvis.router.qlearning import QRouter

ROOT = Path(__file__).resolve().parents[1]
BRAINS = ["local", "gemini"]


def main(tareas: Path, resultados: Path) -> bool:
    agent, cfg = QRouter.load(ROOT / "data" / "q_router.json")
    publico = [json.loads(l) for l in (ROOT / "bench" / "tasks.jsonl").read_text().splitlines()]
    ver = Perception(publico)                       # la percepción se entrena SOLO con el banco público
    nuevas = {t["id"]: t for t in map(json.loads, Path(tareas).read_text().splitlines())}
    outcomes, meta = load_priced(resultados, BRAINS)
    ids = [i for i in meta if i in nuevas]
    if not ids:
        print("No hay tareas con resultados de todos los cerebros todavía.")
        return False
    obs = {i: ver(nuevas[i]["prompt"]) for i in ids}
    env = RouterEnv(outcomes, meta, BRAINS, ids, episode_len=20, daily_budget=cfg["budget"],
                    lam=cfg["lam"], mu=cfg["mu"], seed=99, observed=obs)
    res = compare(agent, env, dias(ids, seed=2027))
    print(f"{len(ids)} tareas evaluadas de {len(nuevas)}\n")
    print(f"{'política':24s} {'calidad':>8s} {'vs segura':>9s} {'% nube':>7s} {'fugas':>6s}")
    for k, r in res.items():
        print(f"{k:24s} {r['calidad media']:8.3f} {r['calidad vs. nube segura']:9.1%} {r['% nube']:7.0%} {r['fugas privadas']:6d}")
    print()
    ok = check(res["Q-learning (JARVIS)"])
    for c, v in ok.items():
        print("✅" if v else "❌", c)
    return all(ok.values())


if __name__ == "__main__":
    a = sys.argv[1:]
    main(Path(a[0]) if a else ROOT / "bench" / "hidden_tasks.jsonl",
         Path(a[1]) if len(a) > 1 else ROOT / "data" / "hidden_results.jsonl")
