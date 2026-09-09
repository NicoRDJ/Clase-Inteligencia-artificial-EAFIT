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
| `01_hill_climbing.ipynb` (2 TODO) | Notebook de clase | ✅ `notebooks/clase3-optimizacion/01_hill_climbing_resuelto.ipynb` |
| `02_simulated_annealing.ipynb` (1) · `02_simulated_annealing_hospitales.ipynb` (3) | Notebooks | ✅ `notebooks/clase3-optimizacion/02_simulated_annealing[_hospitales]_resuelto.ipynb` |
| `03_algoritmos_geneticos.ipynb` (2) · `..._hospitales.ipynb` (3) | Notebooks | ✅ `notebooks/clase3-optimizacion/03_algoritmos_geneticos[_hospitales]_resuelto.ipynb` |
| `04_programacion_lineal.ipynb` (1 TODO) | Notebook | ✅ `notebooks/clase3-optimizacion/04_programacion_lineal_resuelto.ipynb` |
| `05_csp.ipynb` (3 TODO) · `05_csp_ac3.ipynb` (sin TODO) | Notebooks | ✅ `notebooks/clase3-optimizacion/05_csp_resuelto.ipynb` |
| `06_workshop_reinas_optimizacion_local.ipynb` (8 actividades) | **Workshop** | ✅ `notebooks/clase3-optimizacion/06_workshop_reinas_resuelto.ipynb` — las 8 actividades + comparación (100 corridas) |
| Actividad slide: selección proporcional al fitness (ruleta) y cruce uniforme en GA | Actividad en clase | ✅ resuelta dentro de `03_algoritmos_geneticos_resuelto.ipynb` |

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
| `03_qlearning_taxi.ipynb` (7 TODO + 7 preguntas) | Notebook de clase | ✅ `notebooks/clase5-rl/03_qlearning_taxi_resuelto.ipynb` — entrena en Taxi-v4, recompensa −200 → +10, 7 preguntas respondidas |
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

## Estado global de actividades/talleres con `TODO`

| Semana | Notebooks/actividades con TODO | Hechos |
|---|---:|---:|
| 1–2 | actividad de entornos + búsqueda | ✅ (actividad) · notebooks ya estaban |
| 3 — Optimización | 8 | **8 / 8** ✅ |
| 4 — MDP | 1 lab + 1 actividad | **2 / 2** ✅ |
| 5 — RL | 3 talleres código + taller a mano + taxi | **5 / 5** ✅ |
| 6 — ML | 3 (challenge) | ver abajo |
| 7 — Redes neuronales | 2 (challenges) + 1 guiado | ver abajo |

Todas las actividades/talleres con `TODO` de las **Semanas 1–5 (Parte 1 → Examen 01)**
están resueltas y verificadas (ejecutan de principio a fin, los `assert` pasan).

## Pendiente: Semanas 6–7 (Parte 2 · Evaluación 2, no el Examen 01)

- `notebooks/lecture6/challenge/` (3 notebooks, dataset `wine.csv`) — requiere `scikit-learn`.
- `notebooks/lecture6/classification/` (6 notebooks) — **no tienen `TODO`**: son un pipeline
  de referencia ya completo, solo hay que leerlos/ejecutarlos.
- `notebooks/lecture7/` (CIFAR-10 grayscale, Olivetti Faces) — requiere `keras`/`tensorflow`
  y entrenamiento de redes (varios minutos por notebook en CPU).
- `YourFirstDeepNN_FashionMNIST_Keras3.ipynb` — **sin `TODO`**, notebook guiado.
- Proyectos P0–P11 — entregas por tema, con criterios de corrección propios (ver pacto).
