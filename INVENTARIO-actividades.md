# Inventario de actividades, talleres y tareas — SI3003

Revisión completa del repo del curso `github.com/EAFIT-IA/si3003-artificial-intelligence`
(slides + notebooks + workshops). Marca qué está hecho en este repo y qué falta.

**Leyenda:** ✅ hecho aquí · 🟡 parcial / pendiente · ⬜ no empezado · ⭐ entra en el Examen 01

---

## Semana 1 — Agentes racionales  (`slides/clase1.md`, `notebooks/lecture1` no existe)

| Actividad | Tipo | Estado |
|---|---|---|
| Clasificar entornos de tarea (crucigrama, ajedrez, póker, taxi, …) por observable/determinista/… | Actividad en clase | ✅ `actividades-clase/actividades-resueltas.md` |
| P0 (no calificado): agente reflejo simple, mundo de la aspiradora | Proyecto | ⬜ |
| `trabajos/Trabajo1-Agentes-IA-HuggingFace.md` | Trabajo | ✅ (ya estaba en el repo) |

## Semana 2 — Búsqueda  (`slides/clase2.md`, `notebooks/lecture2`)

| Actividad | Tipo | Estado |
|---|---|---|
| `02_algoritmos_busqueda_grafo`, `02_busqueda_en_laberintos`, `02_degrees_bfs` | Notebooks de clase | ✅ `notebooks/clase2-busqueda/` (ya estaban) |
| `trabajos/Trabajo2-Algoritmos-Busqueda.md` (grafos, laberintos, red de actores IMDb) | Trabajo | ✅ (ya estaba) |
| P1: agente de búsqueda estilo Pac-Man | Proyecto | 🟡 revisar contra criterios del proyecto |

## Semana 3 — Optimización  (`slides/clase3.md`, `notebooks/lecture3`)

| Actividad | Tipo | Estado |
|---|---|---|
| `01_hill_climbing.ipynb` (2 TODO) | Notebook de clase | ⬜ |
| `02_simulated_annealing.ipynb` (1 TODO) · `02_simulated_annealing_hospitales.ipynb` (3) | Notebooks | ⬜ |
| `03_algoritmos_geneticos.ipynb` (2 TODO) · `..._hospitales.ipynb` (3) | Notebooks | ⬜ |
| `04_programacion_lineal.ipynb` (1 TODO) | Notebook | ⬜ |
| `05_csp.ipynb` (3 TODO) · `05_csp_ac3.ipynb` | Notebooks | ⬜ |
| `06_workshop_reinas_optimizacion_local.ipynb` (8 actividades) | **Workshop** | 🟡 mismo contenido que `talleres/modulo1/02_optimizacion_resuelto.ipynb` (conflicts, vecinos, hill climbing, SA, comparación) — falta random restart y las preguntas de discusión propias de este notebook |
| Actividad slide: selección proporcional al fitness en GA; extender GA a una frase objetivo | Actividad en clase | ⬜ |

## Semana 4 — MDP  (`slides/clase4.md`, `notebooks/lecture4`)

| Actividad | Tipo | Estado |
|---|---|---|
| Actividad slide "calculen a mano en parejas": `V³(2,1)` del Gridworld 4×3 | Actividad en clase | ✅ ⭐ `actividades-clase/actividades-resueltas.md` |
| `03_lab_warehouse_mdp_estudiantes.ipynb` (modelar MDP + Value Iteration + Policy Iteration) | **Laboratorio** | ✅ ⭐ `notebooks/clase4-mdp/03_lab_warehouse_mdp_resuelto.ipynb` — VI y PI dan la misma política, `assert` final pasa |
| `01_value_iteration_gridworld`, `02_policy_iteration_gridworld` | Notebooks demo (sin TODO) | — |
| P3: Gridworld configurable con Value Iteration y Policy Iteration | Proyecto | 🟡 el lab cubre la base; falta el "configurable" |

## Semana 5 — Aprendizaje por refuerzo  (`slides/clase5.md`, `notebooks/lecture5`)  ⭐

| Actividad | Tipo | Estado |
|---|---|---|
| Taller a mano Módulo 1 (búsqueda + optimización + Q-learning) | **Taller de preparación** | ✅ ⭐ `talleres/modulo1/taller_a_mano_resuelto.md` |
| `workshops/module1/01_search_code_challenge.ipynb` | Taller de código | ✅ ⭐ `talleres/modulo1/01_busqueda_resuelto.ipynb` |
| `workshops/module1/02_optimization_code_challenge.ipynb` | Taller de código | ✅ ⭐ `talleres/modulo1/02_optimizacion_resuelto.ipynb` |
| `workshops/module1/03_q_learning_code_challenge.ipynb` | Taller de código | ✅ ⭐ `talleres/modulo1/03_q_learning_resuelto.ipynb` |
| `01_cheeseworld_q_learning`, `02_qlearning_frozenlake` | Notebooks demo (sin TODO) | — (el contenido está explicado en la guía de estudio del examen) |
| `03_qlearning_taxi.ipynb` (7 TODO) | Notebook de clase | ⬜ |
| `workshops/module1/Midterm Exam/` (Q-learning tabular con Pac-Man) | Práctica examen práctico | 🟡 hay una plantilla comentada en `~/Desktop/universidad/materia IA/Examen 01/4 - Plantilla codigo Q-learning (practico).py` |
| P4 (proyecto puente): comparación de 3 formas de obtener una política | Proyecto | ⬜ |

## Semana 6 — Machine Learning  (`slides/clase6.md`, `notebooks/lecture6`)  · *no entra en el Examen 01*

| Actividad | Tipo | Estado |
|---|---|---|
| `challenge/` (01 data, 02 training, 03 evaluation & deployment) | Challenge | ⬜ |
| `classification/` (pipeline de 6 notebooks: profiling, EDA, feature engineering, training, evaluation, inference) | Notebooks | ⬜ |
| P5: motor de inferencia bayesiana · P6: integrador Parte 1 | Proyectos | ⬜ |

## Semana 7 — Modelos lineales y redes neuronales  (`slides/clase7.md`, `notebooks/lecture7`)  · *no entra en el Examen 01*

| Actividad | Tipo | Estado |
|---|---|---|
| `YourFirstDeepNN_FashionMNIST_Keras3.ipynb` | Notebook guiado | ⬜ |
| `Challenge_Keras3_CIFAR10_Grayscale.ipynb` · `Challenge_Keras3_OlivettiFaces.ipynb` | Challenges | ⬜ |
| Ejemplo/ejercicio de clase (slide "Ejemplo y ejercicio de clase") | Actividad en clase | ⬜ |

---

## Qué falta para dejar el Examen 01 (⭐) al 100 %

Todo lo marcado ⭐ ya está hecho y verificado. Opcionales que refuerzan:

1. `notebooks/lecture5/03_qlearning_taxi.ipynb` — Q-learning tabular en el entorno Taxi de Gym (7 TODO). Mismo patrón que `talleres/modulo1/03_q_learning_resuelto.ipynb`.
2. `workshops/module1/Midterm Exam/` — resolver la versión Pac-Man para llegar afinado al componente práctico.
3. Semana 3 completa (optimización) y P3 configurable de la Semana 4, si el parcial termina cubriendo más de RL.

## Siguiente lote sugerido (fuera del Examen 01)

Semana 3 notebooks · Semana 6 (ML pipeline + challenge) · Semana 7 (Keras). Son más largos
y corresponden a la segunda evaluación / proyectos, no al Examen 01.
