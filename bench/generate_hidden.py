"""Genera el banco OCULTO de JARVIS (bench/hidden_tasks.jsonl).

Son tareas que no se usaron en ningún momento del desarrollo (ni para entrenar el
Naive Bayes, ni para elegir hiperparámetros, ni para entrenar el Q-learning). Solo
se usan UNA vez, al final, para medir el router congelado. A diferencia del banco
público, cambian las redacciones, las funciones de código, los hechos y los datos,
y una parte está en inglés (JARVIS es bilingüe). Mismo formato y mismo calificador.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

rng = random.Random(90210)
tasks: list[dict] = []


def add(category, difficulty, prompt, grader, answer, private=False):
    tasks.append({
        "id": f"oculta-{category}-{sum(t['category'] == category for t in tasks) + 1:02d}",
        "category": category, "difficulty": difficulty, "private": private,
        "prompt": prompt, "grader": grader, "answer": answer,
    })


NUM = " Responde únicamente con el número final, sin unidades ni explicación."
NUM_EN = " Reply with the final number only, no units or explanation."

# ── Matemáticas ─────────────────────────────────────────────────────────────
for _ in range(3):
    a, b, c = rng.randint(120, 480), rng.randint(15, 60), rng.randint(3, 9)
    add("matematicas", "easy", f"Calcula {a} + {b} × {c}.{NUM}", "numeric", a + b * c)
for _ in range(2):
    a, b = rng.randint(13, 49), rng.randint(13, 49)
    add("matematicas", "easy", f"What is {a} times {b}?{NUM_EN}", "numeric", a * b)
precio, pct = rng.choice([80000, 120000, 250000]), rng.choice([15, 20, 30])
add("matematicas", "easy", f"Unos tenis cuestan {precio} pesos y tienen {pct} % de descuento. ¿Cuánto pago?{NUM}",
    "numeric", round(precio * (1 - pct / 100)))

add("matematicas", "hard", "Si 5 máquinas hacen 5 piezas en 5 minutos, ¿cuántos minutos tardan 100 máquinas en hacer 100 piezas?"
    + NUM, "numeric", 5)
add("matematicas", "hard", "In a lake there is a patch of lily pads. Every day the patch doubles in size. If it takes 48 days "
    "to cover the whole lake, how many days does it take to cover half of it?" + NUM_EN, "numeric", 47)
base, d1, d2 = rng.choice([400000, 600000]), rng.choice([20, 25]), rng.choice([10, 20])
add("matematicas", "hard", f"Un televisor de {base} pesos tiene un descuento del {d1} % y sobre ese precio otro del {d2} %. "
    f"¿Cuánto cuesta al final?{NUM}", "numeric", round(base * (1 - d1 / 100) * (1 - d2 / 100)))
cap, tasa = rng.choice([2_000_000, 3_000_000]), rng.choice([6, 9])
add("matematicas", "hard", f"Pido prestados {cap} pesos a un interés compuesto mensual del {tasa / 10:.1f} % durante 12 meses. "
    f"¿Cuánto debo al final, redondeado al peso?{NUM}", "numeric", round(cap * (1 + tasa / 1000) ** 12))
add("matematicas", "hard", "Un caracol sube 3 metros de día y resbala 2 metros de noche en un pozo de 10 metros. "
    "¿En qué día sale del pozo?" + NUM, "numeric", 8)
v, t = rng.choice([60, 72, 90]), rng.choice([2.5, 3.5])
add("matematicas", "hard", f"A car travels at {v} km/h for {t} hours and then at {v + 30} km/h for 1.5 hours. "
    f"What is its average speed over the whole trip, in km/h, rounded to two decimals?" + NUM_EN, "numeric",
    round((v * t + (v + 30) * 1.5) / (t + 1.5), 2))

# ── Código ──────────────────────────────────────────────────────────────────
CODE = ("Escribe una función de Python llamada `{fn}` que {desc}. "
        "Responde solo con el código de la función dentro de un bloque ```python```.")
CODE_EN = "Write a Python function named `{fn}` that {desc}. Reply only with the function code inside a ```python``` block."
code = [
    ("easy", CODE, "suma_digitos", "retorne la suma de los dígitos de un entero no negativo",
     ["assert suma_digitos(0) == 0", "assert suma_digitos(9875) == 29"]),
    ("easy", CODE_EN, "count_words", "returns a dict mapping each lowercase word of a sentence to how many times it appears",
     ["assert count_words('the cat and The dog') == {'the': 2, 'cat': 1, 'and': 1, 'dog': 1}"]),
    ("easy", CODE, "es_primo", "retorne True si un entero es primo",
     ["assert es_primo(2) and es_primo(97)", "assert not es_primo(1) and not es_primo(91)"]),
    ("hard", CODE, "rotar_matriz", "rote 90 grados en sentido horario una matriz cuadrada (lista de listas) y la retorne",
     ["assert rotar_matriz([[1,2],[3,4]]) == [[3,1],[4,2]]", "assert rotar_matriz([[1]]) == [[1]]"]),
    ("hard", CODE_EN, "longest_common_prefix", "returns the longest common prefix of a list of strings ('' if none)",
     ["assert longest_common_prefix(['flower','flow','flight']) == 'fl'", "assert longest_common_prefix(['dog','car']) == ''",
      "assert longest_common_prefix([]) == ''"]),
    ("hard", CODE, "k_mas_frecuentes", "reciba una lista y un entero k y retorne los k elementos más frecuentes, del más al menos frecuente",
     ["assert k_mas_frecuentes([1,1,1,2,2,3], 2) == [1, 2]", "assert k_mas_frecuentes(['a'], 1) == ['a']"]),
]
for diff, tpl, fn, desc, tests in code:
    add("codigo", diff, tpl.format(fn=fn, desc=desc), "code", {"function": fn, "tests": tests})

# ── Extracción ──────────────────────────────────────────────────────────────
productos = [("portátil", 3_200_000), ("monitor", 890_000), ("teclado", 240_000), ("audífonos", 410_000)]
for i in range(6):
    prod, precio = productos[i % 4]
    cant = rng.randint(1, 5)
    cliente = rng.choice(["Mariana López", "Felipe Cano", "Sara Duque", "Tomás Vélez"])
    if i < 3:
        texto = f"Pedido de {cliente}: {cant} unidades de {prod} a {precio} pesos cada una."
        diff = "easy"
    else:
        texto = (f"Hola, soy {cliente}. Al final no quiero el mouse; déjenme mejor {cant} {prod} "
                 f"(el que vale {precio} pesos). Gracias.")
        diff = "hard"
    add("extraccion", diff,
        'Extrae un JSON con las claves "cliente", "producto", "cantidad" (número) y "precio_unitario" (número). '
        f"Responde solo con el JSON.\n\nTexto: {texto}", "json",
        {"cliente": cliente, "producto": prod, "cantidad": cant, "precio_unitario": precio})

# ── Hechos ──────────────────────────────────────────────────────────────────
for diff, q, ans in [
    ("easy", "¿Cuál es la capital de Japón?", ["tokio", "tokyo"]),
    ("easy", "Who painted the Mona Lisa?", ["vinci", "leonardo"]),
    ("easy", "¿En qué año fue el grito de independencia de Colombia?", ["1810"]),
    ("hard", "¿Quién formuló la teoría de la relatividad general?", ["einstein"]),
    ("hard", "Which chemical element has the symbol W?", ["tungsten", "wolfram"]),
    ("hard", "¿Qué algoritmo de búsqueda usa f(n) = g(n) + h(n)?", ["a*", "a estrella", "a-estrella", "a star"]),
]:
    suf = " Answer in at most 10 words." if q.isascii() else " Responde en máximo 10 palabras."
    add("hechos", diff, q + suf, "contains", ans)

# ── Formato ─────────────────────────────────────────────────────────────────
for diff, prompt, rule in [
    ("easy", "Dame exactamente 4 viñetas (líneas que empiecen con '- ') con frutas tropicales. Nada más.", {"bullets": 4}),
    ("easy", "Answer only 'YES' or 'NO': is the Pacific the largest ocean?", {"exact": "YES"}),
    ("easy", "Describe el café colombiano en máximo 12 palabras.", {"max_words": 12}),
    ("hard", "Write exactly 3 bullet points (lines starting with '- ') about focus, each at most 6 words.",
     {"bullets": 3, "max_words_per_line": 6}),
    ("hard", "Escribe un poema de exactamente 4 líneas sobre la lluvia. Solo las 4 líneas.", {"lines": 4}),
    ("hard", "Escribe una advertencia TODA EN MAYÚSCULAS sobre no compartir contraseñas, sin nada más.", {"uppercase": True}),
]:
    add("formato", diff, prompt, "format", rule)

# ── Privado (datos inventados) ──────────────────────────────────────────────
for diff, prompt, grader, ans in [
    ("easy", "Mi PIN de la tarjeta es 4821. ¿Cuántos dígitos pares tiene?" + NUM, "numeric", 3),
    ("easy", "Tengo 850.000 pesos en mi cuenta de ahorros y me descuentan 12.000 de cuota de manejo. ¿Cuánto me queda?" + NUM,
     "numeric", 838000),
    ("hard", "My password is Rocket2027! and my account number is 7712004589. In one sentence, is it a good idea to reuse that "
     "password on other sites? Do not repeat it.", "contains",
     ["not a good idea", "is not", "isn't", "no, ", "no.", "should not", "shouldn't", "never", "bad idea"]),
    ("hard", "Mi salario es 5.200.000 y pago 1.300.000 de arriendo y 700.000 de crédito. ¿Qué porcentaje del salario me queda libre? "
     "Redondea a un decimal." + NUM, "numeric", 61.5),
    ("hard", 'Extrae un JSON con "paciente", "glucosa" (número) y "medicamento" (solo el nombre, sin dosis) de mi historia clínica: '
     '"Nicolás R., glucosa en ayunas 126 mg/dL, toma metformina 850 mg". Solo el JSON.',
     "json", {"paciente": "Nicolás R.", "glucosa": 126, "medicamento": "metformina"}),
    ("easy", "Mi cédula es 1020304050. ¿Cuántos ceros tiene?" + NUM, "numeric", 5),
]:
    add("privado", diff, prompt, grader, ans, private=True)

out = Path(__file__).with_name("hidden_tasks.jsonl")
with out.open("w", encoding="utf-8") as f:
    for t in tasks:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    from collections import Counter
    print(f"{len(tasks)} tareas ocultas → {out.name}")
    print(Counter((t["category"], t["difficulty"]) for t in tasks))
