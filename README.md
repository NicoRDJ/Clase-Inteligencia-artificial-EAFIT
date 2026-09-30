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
| MDP | estado = (categoría, dificultad, privada, nivel de presupuesto); recompensa = calidad − λ·costo − μ·latencia |
| Q-learning tabular ε-greedy | aprende a qué cerebro enviar cada tipo de petición, con escudo de privacidad |

Resultados en tareas no vistas (86 tareas reales, 6 categorías, calificadas automáticamente):

- Calidad **101.5 %** de la mejor política permitida ("nube salvo lo privado").
- La nube se usa en el **57 %** de las peticiones, con un costo diario del 58 % del de la línea base.
- **0 fugas** de datos privados.
- λ, μ y el decaimiento de ε se eligen con una partición de validación, sin tocar el test.

## Estructura

```
jarvis/        núcleo: cerebros, router, consejo, memoria, servidor FastAPI, HUD web y voz
bench/         banco de 86 tareas y su calificador
data/          resultados del banco (results.jsonl) y política aprendida (q_router.json)
notebooks/     checkpoint 1
tests/         pruebas (pytest)
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
