"""Valida el banco oculto: referencias de código y respuestas correctas deben sacar 1.0,
y respuestas equivocadas típicas deben sacar 0 (un calificador laxo inflaría la nota)."""
import json
from pathlib import Path

import pytest

from bench import grader

HIDDEN = {t["id"]: t for t in map(json.loads, (Path(__file__).parents[1] / "bench" / "hidden_tasks.jsonl")
                                  .read_text().splitlines())}
CODE = {t["answer"]["function"]: t for t in HIDDEN.values() if t["grader"] == "code"}

REFERENCIAS = {
    "suma_digitos": "def suma_digitos(n):\n    return sum(int(c) for c in str(n))",
    "count_words": "def count_words(s):\n    d = {}\n    for w in s.lower().split():\n        d[w] = d.get(w, 0) + 1\n    return d",
    "es_primo": "def es_primo(n):\n    return n > 1 and all(n % k for k in range(2, int(n ** .5) + 1))",
    "rotar_matriz": "def rotar_matriz(m):\n    return [list(r) for r in zip(*m[::-1])]",
    "longest_common_prefix": ("def longest_common_prefix(xs):\n    if not xs:\n        return ''\n    p = xs[0]\n"
                              "    for x in xs[1:]:\n        while not x.startswith(p):\n            p = p[:-1]\n    return p"),
    "k_mas_frecuentes": ("from collections import Counter\ndef k_mas_frecuentes(xs, k):\n"
                         "    return [x for x, _ in Counter(xs).most_common(k)]"),
}


def test_banco_oculto_balanceado():
    cats = {t["category"] for t in HIDDEN.values()}
    assert cats == {"matematicas", "codigo", "extraccion", "hechos", "formato", "privado"}
    assert len(HIDDEN) == 42
    assert all(t["private"] == (t["category"] == "privado") for t in HIDDEN.values())


def test_no_se_solapa_con_el_publico():
    publico = {json.loads(l)["prompt"] for l in (Path(__file__).parents[1] / "bench" / "tasks.jsonl").read_text().splitlines()}
    assert not publico & {t["prompt"] for t in HIDDEN.values()}


@pytest.mark.parametrize("fn", sorted(REFERENCIAS))
def test_referencia_oculta_saca_1(fn):
    assert grader.grade(CODE[fn], f"```python\n{REFERENCIAS[fn]}\n```") == 1.0


@pytest.mark.parametrize("tid,buena,mala", [
    ("oculta-matematicas-07", "5", "100"),                      # máquinas: la intuición dice 100
    ("oculta-matematicas-08", "47", "24"),                      # nenúfares: la intuición dice 24
    ("oculta-matematicas-11", "8", "10"),                       # caracol
    ("oculta-privado-01", "3", "2"),
    ("oculta-privado-04", "61,5", "60"),
    ("oculta-privado-06", "5", "4"),
    ("oculta-hechos-05", "Tungsten.", "Wolverine"),
    ("oculta-privado-03", "No, reusing it is a bad idea.", "Sure, go ahead and use it everywhere."),
    ("oculta-formato-02", "YES", "NO"),
])
def test_respuestas_ocultas(tid, buena, mala):
    assert grader.grade(HIDDEN[tid], buena) == 1.0
    assert grader.grade(HIDDEN[tid], mala) == 0.0


def test_json_oculto():
    t = HIDDEN["oculta-privado-05"]
    ok = '{"paciente": "Nicolás R.", "glucosa": 126, "medicamento": "metformina"}'
    assert grader.grade(t, ok) == 1.0
