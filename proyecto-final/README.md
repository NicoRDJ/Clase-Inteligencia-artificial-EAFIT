# J.A.R.V.I.S. — proyecto final SI3003

Asistente personal de voz, siempre encendido, hecho de **varios cerebros que piensan como uno solo**.
Proyecto individual de Nicolás Rodríguez para *SI3003 — Inteligencia Artificial* (EAFIT, 2026-2).

## Idea

JARVIS no es un selector de chatbots. Cada petición pasa por un **router aprendido** que decide
quién entra al **consejo** (el modelo local, Gemini, Claude, GPT o Grok, según salud, presupuesto y privacidad).
Los cerebros elegidos responden en paralelo y uno sintetiza **una sola respuesta** con la voz de JARVIS.

```
voz / HUD ─► router (Naive Bayes + MDP + Q-learning) ─► consejo en paralelo ─► síntesis ─► voz / HUD
                 │ privado → solo el cerebro local (0 fugas)
```

## Checkpoint 1 — Router de cerebros (Parte 1 del curso)

Notebook: [`notebooks/checkpoint1_router.ipynb`](notebooks/checkpoint1_router.ipynb) (lo genera `notebooks/build_checkpoint1.py`).

| Técnica | Uso |
|---|---|
| Naive Bayes multinomial (desde cero) | intención de la petición y detección de datos privados |
| Árbol de decisión de un nivel | dificultad (umbral de longitud por categoría) |
| MDP | estado = (categoría, dificultad, privada, nivel de presupuesto); recompensa = calidad − λ·costo − μ·latencia |
| Q-learning tabular ε-greedy | a qué cerebro enviar cada tipo de petición, con escudo de privacidad y paso α = n(s,a)^-0.7 |

Evaluación **de punta a punta** (el router decide con lo que predice la percepción; las fugas se cuentan con la etiqueta real), hiperparámetros elegidos en validación, criterio exigido en el **peor de 10 entrenamientos**:

| Criterio | Meta | Resultado en test |
|---|---|---|
| Calidad vs. "nube salvo lo privado" | ≥ 95 % | ✅ 102.0 % |
| Peticiones enviadas a la nube | ≤ 60 % | ✅ 42 % (costo diario: 25 % del de la línea base) |
| Fugas de datos privados | 0 | ✅ 0 |

**Casos ocultos.** `bench/hidden_tasks.jsonl` tiene 42 tareas nuevas (un tercio en inglés) que no se usaron para entrenar ni para elegir nada. El router congelado (`data/q_router.json`) se evalúa sobre ellas, o sobre cualquier banco nuevo, sin reentrenar:

```bash
python -m bench.run_bench --tareas tareas.jsonl --salida data/resultados.jsonl local gemini
python -m bench.evaluar_router tareas.jsonl data/resultados.jsonl
```

## Estructura

```
jarvis/        núcleo: cerebros, router, consejo, memoria, servidor FastAPI, HUD web y voz
bench/         banco público (86 tareas), banco oculto (42), calificador y evaluador del router
data/          resultados del banco (results.jsonl) y política aprendida (q_router.json)
notebooks/     checkpoint 1
tests/         pruebas (pytest): calificador, banco oculto y router
deploy/        agente launchd (24/7 en macOS) y lanzador de manos libres
docs/          investigación: referencias del JARVIS de las películas y proyectos reales
```

## Ejecutar

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # llaves de API (no se versiona)
python -m pytest -q               # pruebas
uvicorn jarvis.server:app --port 8765   # HUD en http://localhost:8765
python -m jarvis.voice.ears       # manos libres: diga «Hey JARVIS»
```

El modelo local corre en Ollama (`qwen3:4b-instruct-2507`). Idiomas habilitados: inglés y español (`JARVIS_LANGS`).
