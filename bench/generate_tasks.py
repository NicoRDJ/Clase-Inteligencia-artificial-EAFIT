"""Genera el banco de tareas de JARVIS (bench/tasks.jsonl).

Cada tarea es verificable automáticamente: las respuestas de matemáticas se
calculan aquí mismo (no se escriben a mano), el código se califica ejecutando
tests y la extracción se compara campo a campo. Semilla fija → banco
reproducible.

Campos de cada tarea:
    id, category, difficulty (easy|hard), private (bool), prompt, grader, answer
"""
from __future__ import annotations

import json
import random
from pathlib import Path

rng = random.Random(2026)
tasks: list[dict] = []


def add(category, difficulty, prompt, grader, answer, private=False):
    tasks.append({
        "id": f"{category}-{sum(t['category'] == category for t in tasks) + 1:02d}",
        "category": category, "difficulty": difficulty, "private": private,
        "prompt": prompt, "grader": grader, "answer": answer,
    })


NUM = " Responde únicamente con el número final, sin unidades ni explicación."

# ── Matemáticas fáciles (aritmética directa) ────────────────────────────────
for _ in range(12):
    a, b = rng.randint(12, 99), rng.randint(12, 99)
    add("matematicas", "easy", f"¿Cuánto es {a} × {b}?{NUM}", "numeric", a * b)
for _ in range(6):
    precio, n, pago = rng.choice([1500, 2500, 3200, 4800]), rng.randint(2, 6), 50000
    add("matematicas", "easy",
        f"Compro {n} empanadas a {precio} pesos cada una y pago con un billete de {pago}. ¿Cuánto me devuelven?{NUM}",
        "numeric", pago - n * precio)

# ── Matemáticas difíciles (varios pasos / trampas intuitivas) ───────────────
for total, diff in [(1.10, 1.00), (2.20, 2.00), (1.30, 1.20), (5.50, 5.00)]:
    ball = round((total - diff) / 2, 2)
    add("matematicas", "hard",
        f"Un bate y una pelota cuestan {total:.2f} dólares en total. El bate cuesta {diff:.2f} dólares más que la pelota. "
        f"¿Cuánto cuesta la pelota, en dólares?{NUM}", "numeric", ball)
for _ in range(5):
    cap, tasa, anos = rng.choice([1_000_000, 2_500_000, 5_000_000]), rng.choice([5, 8, 10, 12]), rng.randint(2, 4)
    final = round(cap * (1 + tasa / 100) ** anos)
    add("matematicas", "hard",
        f"Invierto {cap} pesos a un interés compuesto anual del {tasa} % durante {anos} años. "
        f"¿Cuánto tendré al final, redondeado al peso más cercano?{NUM}", "numeric", final)
for _ in range(4):
    base, sube, baja = rng.choice([200, 180, 150]), rng.choice([10, 20, 25]), rng.choice([10, 20, 25])
    final = round(base * (1 + sube / 100) * (1 - baja / 100), 2)
    add("matematicas", "hard",
        f"Una cuenta de trading de {base} mil dólares sube un {sube} % y luego baja un {baja} %. "
        f"¿Cuántos miles de dólares quedan?{NUM}", "numeric", final)
for _ in range(3):
    v1, v2, d = rng.choice([40, 60, 80]), rng.choice([50, 70, 90]), rng.choice([300, 420, 600])
    t = round(d / (v1 + v2), 2)
    add("matematicas", "hard",
        f"Dos trenes salen al mismo tiempo de ciudades separadas {d} km, uno hacia el otro, a {v1} km/h y {v2} km/h. "
        f"¿En cuántas horas se cruzan? Redondea a dos decimales.{NUM}", "numeric", t)

# ── Código (se califica ejecutando tests) ───────────────────────────────────
CODE = ("Escribe una función de Python llamada `{fn}` que {desc}. "
        "Responde solo con el código de la función dentro de un bloque ```python```.")
code_tasks = [
    ("easy", "es_palindromo", "reciba un texto y retorne True si es palíndromo ignorando mayúsculas, espacios y tildes",
     ["assert es_palindromo('Anita lava la tina')", "assert es_palindromo('Yo hago yoga hoy')", "assert not es_palindromo('Python')"]),
    ("easy", "contar_vocales", "retorne cuántas vocales (a, e, i, o, u, con o sin tilde) tiene un texto",
     ["assert contar_vocales('Murciélago') == 5", "assert contar_vocales('xyz') == 0"]),
    ("easy", "mcd", "retorne el máximo común divisor de dos enteros positivos sin usar math.gcd",
     ["assert mcd(48, 18) == 6", "assert mcd(17, 5) == 1", "assert mcd(100, 25) == 25"]),
    ("easy", "invertir_palabras", "reciba una frase y retorne las palabras en orden inverso separadas por un espacio",
     ["assert invertir_palabras('hola mundo feliz') == 'feliz mundo hola'", "assert invertir_palabras('uno') == 'uno'"]),
    ("easy", "segundo_mayor", "reciba una lista de enteros y retorne el segundo valor distinto más grande (o None si no existe)",
     ["assert segundo_mayor([4, 1, 9, 9, 7]) == 7", "assert segundo_mayor([3, 3]) is None", "assert segundo_mayor([2, 5]) == 2"]),
    ("easy", "fizzbuzz", "reciba n y retorne una lista de strings de 1 a n donde múltiplos de 3 son 'Fizz', de 5 'Buzz' y de ambos 'FizzBuzz'",
     ["assert fizzbuzz(5) == ['1', '2', 'Fizz', '4', 'Buzz']", "assert fizzbuzz(15)[-1] == 'FizzBuzz'"]),
    ("easy", "aplanar", "reciba una lista que puede contener listas anidadas a cualquier profundidad y la retorne aplanada",
     ["assert aplanar([1, [2, [3, [4]]], 5]) == [1, 2, 3, 4, 5]", "assert aplanar([]) == []"]),
    ("hard", "a_romano", "convierta un entero entre 1 y 3999 a número romano",
     ["assert a_romano(1994) == 'MCMXCIV'", "assert a_romano(3999) == 'MMMCMXCIX'", "assert a_romano(4) == 'IV'"]),
    ("hard", "es_parentesis_valido", "reciba un string con (), [] y {} y retorne True si están correctamente balanceados y anidados",
     ["assert es_parentesis_valido('{[()()]}')", "assert not es_parentesis_valido('([)]')", "assert not es_parentesis_valido('((')"]),
    ("hard", "mas_largo_sin_repetir", "retorne la longitud de la subcadena más larga sin caracteres repetidos",
     ["assert mas_largo_sin_repetir('abcabcbb') == 3", "assert mas_largo_sin_repetir('bbbbb') == 1", "assert mas_largo_sin_repetir('pwwkew') == 3"]),
    ("hard", "drawdown_maximo", "reciba una lista de valores de equity y retorne el drawdown máximo como fracción (0.2 = 20 %) medido desde el pico previo",
     ["assert abs(drawdown_maximo([100, 120, 90, 130, 104]) - 0.25) < 1e-9", "assert drawdown_maximo([1, 2, 3]) == 0"]),
    ("hard", "merge_intervalos", "reciba una lista de intervalos [inicio, fin] y retorne la lista de intervalos fusionados ordenada",
     ["assert merge_intervalos([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]", "assert merge_intervalos([[1,4],[4,5]]) == [[1,5]]"]),
    ("hard", "bfs_camino", "reciba un grafo como dict de listas de adyacencia, un origen y un destino, y retorne el camino más corto (lista de nodos) con BFS o None si no existe",
     ["g={'A':['B','C'],'B':['D'],'C':['D','E'],'D':['F'],'E':['F'],'F':[]}", "assert bfs_camino(g,'A','F') in (['A','B','D','F'],['A','C','D','F'],['A','C','E','F'])", "assert bfs_camino(g,'F','A') is None"]),
    ("hard", "lru_cache_manual", "implemente una clase-función: una función que reciba una capacidad y retorne un objeto con métodos get(k) y put(k, v) con política LRU (get retorna -1 si no existe). La función se llama `lru_cache_manual`",
     ["c = lru_cache_manual(2)", "c.put(1, 1); c.put(2, 2)", "assert c.get(1) == 1", "c.put(3, 3)", "assert c.get(2) == -1", "assert c.get(3) == 3"]),
]
for diff, fn, desc, tests in code_tasks:
    add("codigo", diff, CODE.format(fn=fn, desc=desc), "code", {"function": fn, "tests": tests})

# ── Extracción estructurada (JSON campo a campo) ────────────────────────────
nombres = ["Laura Gómez", "Andrés Restrepo", "Camila Ortiz", "Julián Mejía", "Valentina Ruiz", "Santiago Arango"]
ciudades = ["Medellín", "Bogotá", "Cali", "Barranquilla", "Cartagena", "Pereira"]
cargos = ["ingeniera de datos", "gerente comercial", "analista financiera", "desarrollador backend", "diseñadora UX", "consultor de IA"]
for i in range(10):
    n, c, g = nombres[i % 6], ciudades[(i * 5) % 6], cargos[(i * 7) % 6]
    edad = rng.randint(23, 48)
    empresa = rng.choice(["Bancolombia", "Rappi", "EPM", "Globant", "Nequi"])
    texto = rng.choice([
        f"{n}, de {edad} años, trabaja como {g} en {empresa} y vive en {c}.",
        f"Desde {c}, {n} ({edad}) lidera su equipo como {g} en {empresa}.",
        f"En {empresa} contrataron a {n} como {g}; tiene {edad} años y es de {c}.",
    ])
    add("extraccion", "easy" if i < 5 else "hard",
        f'Extrae del texto un JSON con las claves "nombre", "edad" (número), "cargo", "empresa" y "ciudad". '
        f"Responde solo con el JSON.\n\nTexto: {texto}", "json",
        {"nombre": n, "edad": edad, "cargo": g, "empresa": empresa, "ciudad": c})

# ── Hechos (respuesta corta, se acepta cualquier variante válida) ───────────
hechos = [
    ("easy", "¿Cuál es la capital de Australia?", ["canberra"]),
    ("easy", "¿Quién escribió 'Cien años de soledad'?", ["garcía márquez", "garcia marquez"]),
    ("easy", "¿En qué año llegó el Apolo 11 a la Luna?", ["1969"]),
    ("easy", "¿Cuál es el símbolo químico del oro?", ["au"]),
    ("easy", "¿Cuál es el planeta más grande del sistema solar?", ["júpiter", "jupiter"]),
    ("easy", "¿Qué idioma es el oficial de Brasil?", ["portugués", "portugues"]),
    ("easy", "¿Cuál es la capital de Canadá?", ["ottawa"]),
    ("hard", "¿En qué año cayó el Muro de Berlín?", ["1989"]),
    ("hard", "¿Qué elemento químico tiene número atómico 26?", ["hierro", "fe"]),
    ("hard", "¿Quién propuso la arquitectura Transformer en el paper 'Attention Is All You Need'? Nombra al primer autor.", ["vaswani"]),
    ("hard", "¿Cuántos huesos tiene el cuerpo humano adulto?", ["206"]),
    ("hard", "¿Qué matemático formuló la ecuación que da nombre a la programación dinámica en MDP (ecuación de ...)?", ["bellman"]),
]
for diff, q, ans in hechos:
    add("hechos", diff, q + " Responde en máximo 10 palabras.", "contains", ans)

# ── Formato (instrucciones verificables) ────────────────────────────────────
formatos = [
    ("easy", "Dame exactamente 3 viñetas (líneas que empiecen con '- ') con consejos para dormir mejor. Nada más.",
     {"bullets": 3}),
    ("easy", "Escribe una frase motivacional TODA EN MAYÚSCULAS, sin nada más.", {"uppercase": True}),
    ("easy", "Describe Medellín en máximo 15 palabras.", {"max_words": 15}),
    ("easy", "Responde solo 'SI' o 'NO': ¿el agua hierve a 100 °C a nivel del mar?", {"exact": "SI"}),
    ("hard", "Dame exactamente 5 viñetas (líneas que empiecen con '- ') con ideas de negocio, cada una de máximo 8 palabras.",
     {"bullets": 5, "max_words_per_line": 8}),
    ("hard", "Escribe un haiku (3 líneas) sobre la inteligencia artificial. Solo las 3 líneas.", {"lines": 3}),
    ("hard", "Lista 4 lenguajes de programación en una sola línea separados por punto y coma, sin espacios extra ni texto adicional.",
     {"separator_count": (";", 4)}),
    ("hard", "Responde con un número entero entre 1 y 10 y NADA más: ¿qué tan importante es dormir bien para programar?",
     {"int_range": (1, 10)}),
]
for diff, prompt, rule in formatos:
    add("formato", diff, prompt, "format", rule)

# ── Privado (datos sensibles: la regla dura es que NUNCA salgan del Mac) ────
privados = [
    ("easy", "Mi cédula es 1034987654 y mi clave del banco es Nico#2026. Recuérdame en una frase qué dos datos te acabo de dar (sin repetirlos).",
     "contains", ["cédula", "cedula", "clave", "contraseña"]),
    ("easy", "Tengo 3.200.000 pesos en Nequi y 1.450.000 en Bancolombia. ¿Cuánto tengo en total?" + NUM, "numeric", 4650000),
    ("easy", "Mi saldo en la cuenta de fondeo es 192000 dólares y el piso es 184000. ¿Cuánto margen me queda antes de perderla?" + NUM,
     "numeric", 8000),
    ("hard", "Mis gastos del mes: arriendo 1.800.000, comida 950.000, gasolina 420.000, gimnasio 150.000. Si gano 4.500.000, ¿cuánto ahorro?" + NUM,
     "numeric", 1180000),
    ("hard", 'Extrae un JSON con "banco", "cuenta" y "titular" de este mensaje privado: '
     '"Consígname a la cuenta de ahorros Bancolombia 042-783912-55 a nombre de Nicolás Rodríguez". Solo el JSON.',
     "json", {"banco": "Bancolombia", "cuenta": "042-783912-55", "titular": "Nicolás Rodríguez"}),
    ("hard", "Historia clínica: paciente de 22 años, presión 140/90, fuma 10 cigarrillos al día. ¿La presión está por encima de 120/80? Responde solo SI o NO.",
     "format", {"exact": "SI"}),
    ("easy", "Mi usuario de Atmos es nrodri y la contraseña es Tr4d3r!. ¿Cuántos caracteres tiene la contraseña?" + NUM, "numeric", 7),
    ("hard", "El EIN de mi LLC es 88-1234567 y la dirección del registered agent es 123 Main St. Dime en una frase para qué sirve un EIN, sin repetir el número.",
     "contains", ["impuesto", "tax", "identificación", "identificacion", "fiscal"]),
]
for diff, prompt, grader, ans in privados:
    add("privado", diff, prompt, grader, ans, private=True)

out = Path(__file__).with_name("tasks.jsonl")
with out.open("w", encoding="utf-8") as f:
    for t in tasks:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")

from collections import Counter
print(f"{len(tasks)} tareas → {out.name}")
print(Counter((t["category"], t["difficulty"]) for t in tasks))
