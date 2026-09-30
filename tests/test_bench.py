"""Valida el banco y el calificador: un benchmark con tests mal escritos
castigaría injustamente a todos los cerebros."""
import json
from pathlib import Path

import pytest

from bench import grader

TASKS = [json.loads(l) for l in (Path(__file__).parents[1] / "bench" / "tasks.jsonl").read_text().splitlines()]
BY_FN = {t["answer"]["function"]: t for t in TASKS if t["grader"] == "code"}

# Soluciones de referencia escritas a mano: todas deben sacar 1.0
REFERENCIAS = {
    "es_palindromo": '''
import unicodedata
def es_palindromo(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = "".join(c for c in t if c.isalnum())
    return t == t[::-1]''',
    "contar_vocales": '''
def contar_vocales(t):
    return sum(c in "aeiouáéíóúAEIOUÁÉÍÓÚ" for c in t)''',
    "mcd": '''
def mcd(a, b):
    while b:
        a, b = b, a % b
    return a''',
    "invertir_palabras": '''
def invertir_palabras(f):
    return " ".join(f.split()[::-1])''',
    "segundo_mayor": '''
def segundo_mayor(xs):
    u = sorted(set(xs), reverse=True)
    return u[1] if len(u) > 1 else None''',
    "fizzbuzz": '''
def fizzbuzz(n):
    return ["FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i) for i in range(1, n + 1)]''',
    "aplanar": '''
def aplanar(xs):
    out = []
    for x in xs:
        out.extend(aplanar(x) if isinstance(x, list) else [x])
    return out''',
    "a_romano": '''
def a_romano(n):
    vals = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    s = ""
    for v, r in vals:
        while n >= v:
            s += r; n -= v
    return s''',
    "es_parentesis_valido": '''
def es_parentesis_valido(s):
    pares, pila = {")": "(", "]": "[", "}": "{"}, []
    for c in s:
        if c in "([{": pila.append(c)
        elif c in pares:
            if not pila or pila.pop() != pares[c]: return False
    return not pila''',
    "mas_largo_sin_repetir": '''
def mas_largo_sin_repetir(s):
    ult, ini, best = {}, 0, 0
    for i, c in enumerate(s):
        if c in ult and ult[c] >= ini: ini = ult[c] + 1
        ult[c] = i; best = max(best, i - ini + 1)
    return best''',
    "drawdown_maximo": '''
def drawdown_maximo(eq):
    pico, dd = float("-inf"), 0.0
    for v in eq:
        pico = max(pico, v); dd = max(dd, (pico - v) / pico)
    return dd''',
    "merge_intervalos": '''
def merge_intervalos(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out''',
    "bfs_camino": '''
from collections import deque
def bfs_camino(g, s, t):
    prev, q = {s: None}, deque([s])
    while q:
        u = q.popleft()
        if u == t:
            path = []
            while u is not None: path.append(u); u = prev[u]
            return path[::-1]
        for v in g.get(u, []):
            if v not in prev: prev[v] = u; q.append(v)
    return None''',
    "lru_cache_manual": '''
from collections import OrderedDict
def lru_cache_manual(cap):
    class C:
        def __init__(self): self.d = OrderedDict()
        def get(self, k):
            if k not in self.d: return -1
            self.d.move_to_end(k); return self.d[k]
        def put(self, k, v):
            self.d[k] = v; self.d.move_to_end(k)
            if len(self.d) > cap: self.d.popitem(last=False)
    return C()''',
}


def test_banco_tiene_todas_las_categorias():
    cats = {t["category"] for t in TASKS}
    assert cats == {"matematicas", "codigo", "extraccion", "hechos", "formato", "privado"}
    assert len({t["id"] for t in TASKS}) == len(TASKS)


@pytest.mark.parametrize("fn", sorted(BY_FN))
def test_referencia_de_codigo_saca_1(fn):
    respuesta = f"```python\n{REFERENCIAS[fn]}\n```"
    assert grader.grade(BY_FN[fn], respuesta) == 1.0


def test_codigo_incorrecto_no_pasa():
    assert grader.grade(BY_FN["mcd"], "```python\ndef mcd(a, b):\n    return 1\n```") < 1.0


@pytest.mark.parametrize("texto,esperado", [("391", 391), ("El total es 4.650.000", 4650000),
                                             ("0.05", 0.05), ("La pelota cuesta $0,05", 0.05), ("1,180,000", 1180000)])
def test_numerico_acepta_formatos(texto, esperado):
    assert grader.grade_numeric(texto, esperado) == 1.0


def test_numerico_rechaza_error():
    assert grader.grade_numeric("401", 391) == 0.0


def test_json_parcial():
    ans = {"nombre": "Laura Gómez", "edad": 30, "ciudad": "Cali"}
    assert grader.grade_json('{"nombre": "Laura Gomez", "edad": 30, "ciudad": "Cali"}', ans) == 1.0
    assert abs(grader.grade_json('```json\n{"nombre": "Laura", "edad": "30", "ciudad": "Cali"}\n```', ans) - 2 / 3) < 1e-9


def test_formatos():
    assert grader.grade_format("- a\n- b\n- c", {"bullets": 3}) == 1.0
    assert grader.grade_format("- a\n- b", {"bullets": 3}) == 0.0
    assert grader.grade_format("¡VAMOS CON TODO!", {"uppercase": True}) == 1.0
    assert grader.grade_format("Sí.", {"exact": "SI"}) == 1.0
    assert grader.grade_format("Python;Rust;Go;C", {"separator_count": (";", 4)}) == 1.0
    assert grader.grade_format("8", {"int_range": (1, 10)}) == 1.0
