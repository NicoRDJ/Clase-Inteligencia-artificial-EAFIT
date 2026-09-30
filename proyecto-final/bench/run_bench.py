"""Corre el banco de tareas contra los cerebros y guarda los resultados.

Uso:  python -m bench.run_bench [cerebro ...]      (por defecto, todos los disponibles)

Cada fila de data/results.jsonl = (tarea, cerebro, nota, costo, latencia, respuesta).
Es reanudable: si una combinación tarea×cerebro ya existe, se salta.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from bench.grader import grade
from jarvis.brains import registry

ROOT = Path(__file__).resolve().parents[1]
TASKS = [json.loads(l) for l in (ROOT / "bench" / "tasks.jsonl").read_text().splitlines()]
OUT = ROOT / "data" / "results.jsonl"
SYSTEM = "Eres JARVIS, un asistente preciso. Responde en español y sigue exactamente el formato que te piden."


def done_pairs() -> set[tuple[str, str]]:
    if not OUT.exists():
        return set()
    return {(r["task_id"], r["brain"]) for r in map(json.loads, OUT.read_text().splitlines()) if not r.get("error")}


def main(names: list[str]) -> None:
    names = names or registry.available()
    hechos = done_pairs()
    for name in names:
        brain = registry.load(name)
        pendientes = [t for t in TASKS if (t["id"], name) not in hechos]
        print(f"== {name}: {len(pendientes)} tareas pendientes", flush=True)
        for i, t in enumerate(pendientes, 1):
            max_tokens = 900 if t["category"] == "codigo" else 400
            r = brain.ask(t["prompt"], system=SYSTEM, max_tokens=max_tokens, temperature=0.0)
            score = grade(t, r.text) if r.ok else 0.0
            row = {"task_id": t["id"], "category": t["category"], "difficulty": t["difficulty"],
                   "private": t["private"], "brain": name, "score": score, "cost_usd": r.cost_usd,
                   "latency_s": round(r.latency_s, 2), "in_tok": r.input_tokens, "out_tok": r.output_tokens,
                   "error": r.error, "response": r.text}
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"  [{i}/{len(pendientes)}] {t['id']:15s} nota={score:.2f} {r.latency_s:5.1f}s {r.error or ''}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
