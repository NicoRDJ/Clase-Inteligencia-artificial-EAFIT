"""Corre el banco de tareas contra los cerebros y guarda los resultados.

Uso:  python -m bench.run_bench [cerebro ...]      (por defecto, todos los disponibles)
      python -m bench.run_bench --oculto local gemini   (banco oculto → data/hidden_results.jsonl)
      python -m bench.run_bench --tareas mis_tareas.jsonl --salida data/mis_resultados.jsonl local gemini

Con JARVIS_GEMINI_STRICT=1, Gemini usa solo el modelo configurado (sin caer al
Flash-Lite): así los resultados son comparables con los del banco público.

Cada fila de data/results.jsonl = (tarea, cerebro, nota, costo, latencia, respuesta).
Es reanudable: si una combinación tarea×cerebro ya existe, se salta.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from bench.grader import grade
from jarvis.brains import registry

ROOT = Path(__file__).resolve().parents[1]
def _arg(flag: str, default: Path) -> Path:
    return Path(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


OCULTO = "--oculto" in sys.argv
TASKS = [json.loads(l) for l in _arg("--tareas", ROOT / "bench" / ("hidden_tasks.jsonl" if OCULTO else "tasks.jsonl"))
         .read_text().splitlines()]
OUT = _arg("--salida", ROOT / "data" / ("hidden_results.jsonl" if OCULTO else "results.jsonl"))
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
        if name == "gemini" and os.getenv("JARVIS_GEMINI_STRICT"):
            brain.FALLBACK = [brain.spec.model]
        pendientes = [t for t in TASKS if (t["id"], name) not in hechos]
        print(f"== {name}: {len(pendientes)} tareas pendientes", flush=True)
        for i, t in enumerate(pendientes, 1):
            max_tokens = 900 if t["category"] == "codigo" else 400
            r = brain.ask(t["prompt"], system=SYSTEM, max_tokens=max_tokens, temperature=0.0)
            if r.ok is False and "cuota" in (r.error or ""):
                print(f"  sin cuota: se detiene (reanudable) — {r.error[:80]}", flush=True)
                break
            score = grade(t, r.text) if r.ok else 0.0
            row = {"task_id": t["id"], "category": t["category"], "difficulty": t["difficulty"],
                   "private": t["private"], "brain": name, "model": getattr(brain, "last_model", brain.spec.model), "score": score, "cost_usd": r.cost_usd,
                   "latency_s": round(r.latency_s, 2), "in_tok": r.input_tokens, "out_tok": r.output_tokens,
                   "error": r.error, "response": r.text}
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"  [{i}/{len(pendientes)}] {t['id']:15s} nota={score:.2f} {r.latency_s:5.1f}s {r.error or ''}", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    for flag in ("--tareas", "--salida"):
        if flag in args:
            i = args.index(flag); del args[i:i + 2]
    main([a for a in args if not a.startswith("--")])
