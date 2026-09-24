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
| `challenge/` (01 data, 02 training, 03 evaluation & deployment) | Challenge | ✅ `notebooks/clase6-ml/challenge/` — pipeline completo, campeón LogisticRegression, test acc ≈ 0.97 |
| `classification/` (pipeline de 6 notebooks: profiling, EDA, feature engineering, training, evaluation, inference) | Notebooks | ⬜ |
| P5: motor de inferencia bayesiana · P6: integrador Parte 1 | Proyectos | ⬜ |

## Semana 7 — Modelos lineales y redes neuronales  (`slides/clase7.md`, `notebooks/lecture7`)  · *no entra en el Examen 01*

| Actividad | Tipo | Estado |
|---|---|---|
| `YourFirstDeepNN_FashionMNIST_Keras3.ipynb` | Notebook guiado (sin TODO) | — (receta base ya resuelta) |
| `Challenge_Keras3_OlivettiFaces.ipynb` | Challenge | ✅ `notebooks/clase7-redes-neuronales/` — ejecutado, test acc ≈ 0.96 |
| `Challenge_Keras3_CIFAR10_Grayscale.ipynb` | Challenge | ✅ código + respuestas; no ejecutado aquí (descarga de CIFAR-10 throttled) |
| Ejemplo/ejercicio de clase (slide "Ejemplo y ejercicio de clase") | Actividad en clase | ⬜ |

## Semana 8 — CNN (transfer learning, fine-tuning, YOLO)  (`slides/clase8.md`, `notebooks/lecture8`)  · *no entra en el Examen 01*

| Actividad | Tipo | Estado |
|---|---|---|
| `CNN_Transfer_Keras3.ipynb` | Notebook guiado (sin TODO) | — (receta base ya resuelta) |
| `taller_transfer_learning_datos_propios_keras3.ipynb` (31 `TODO`, dataset propio) | **Taller** | ✅ `notebooks/clase8-cnn/taller_transfer_learning_resuelto.ipynb` — ejecutado de verdad de principio a fin: descarga real de imágenes (DuckDuckGo), limpieza técnica + semántica manual, split 70/15/15, EfficientNetB0 congelada → cabeza entrenada → fine-tuning. Ver detalle abajo. |
| `Lecture_08_Yolo_Intro.ipynb` (1 ejercicio) | Notebook de clase | ✅ `notebooks/clase8-cnn/yolo/Lecture_08_Yolo_Intro_resuelto.ipynb` — ejecutado con YOLO real sobre una imagen nueva (zidane.jpg): detecta 2 personas + 1 corbata |
| `Lecture_08_Yolo_training[.ipynb / _own_data.ipynb]`, `yolo/deployment/test.ipynb` | Notebooks demo (sin TODO, requieren API key de Roboflow y datasets externos) | — |

**Detalle del taller de transfer learning (dataset: espresso / cappuccino / latte, elegido porque es el ejemplo que sugiere el enunciado y es difícil de verdad — un primer intento con pizza/hamburguesa/sushi dio 100% sin errores y no servía para el TODO 6):**

- 201 imágenes descargadas → 169 tras limpieza técnica (0 inválidas) y semántica manual (32 quitadas: clipart, íconos, empaques, tazas/vasos vacíos, infografías — sobre todo en "cappuccino").
- Split 70/15/15 → train 118, val 24, test 27.
- Cabeza (EfficientNetB0 congelada): **val_accuracy 33% → 71%** en 10 épocas.
- Test **antes** del fine-tuning: **70.4%** accuracy (19/27).
- Fine-tuning (20 capas descongeladas, BatchNorm congelado, lr=1e-5, 6 épocas): test **74.1%** accuracy (20/27), **+3.7 pp**.
- Confusión principal (antes y después): **latte confundido con cappuccino** (3 de 10 latte) — las dos llevan espuma de leche y son visualmente parecidas; el fine-tuning corrigió 1 caso de espresso→cappuccino pero no tocó esa confusión latte/cappuccino.
- 7 errores analizados en el TODO 6 (mínimo pedido: 5).

## Semana 9 — Transformers y NLP (LLMs, chatbots, RAG)  (`slides/clase9.md`, `notebooks/Lecture9`)  · *no entra en el Examen 01*

| Actividad | Tipo | Estado |
|---|---|---|
| `01_local_chatbot_lab`, `02_local_remote_hf_chatbot_lab`, `03_nvidia_chatbot_lab`, `04_nvidia_gradio_lab` | Notebooks guiados (sin blancos de código) | — (ya están completos, solo requieren Ollama / HuggingFace / API key de NVIDIA propia para correr) |
| `05_ejercicio_nvidia_documentos.ipynb` (4 celdas "Escribe tu código aquí") | **Ejercicio** (asistente de documentos con NVIDIA NIM + Gradio sobre el paper *Attention Is All You Need*) | ✅ `notebooks/clase9-transformers-nlp/05_ejercicio_nvidia_documentos_resuelto.ipynb` — Paso 1 (extracción del PDF) ejecutado de verdad: 15 páginas, 39,510 caracteres. Pasos 2–4 (cliente NVIDIA NIM + app Gradio) tienen el código completo pero **no se ejecutaron** porque requieren una `NVIDIA_API_KEY` personal (gratuita en build.nvidia.com) que no está disponible en este entorno. |

---

## Estado global de actividades/talleres con `TODO`

| Semana | Notebooks/actividades con TODO | Hechos |
|---|---:|---:|
| 1–2 | actividad de entornos + búsqueda | ✅ (actividad) · notebooks ya estaban |
| 3 — Optimización | 8 | **8 / 8** ✅ |
| 4 — MDP | 1 lab + 1 actividad | **2 / 2** ✅ |
| 5 — RL | 3 talleres código + taller a mano + taxi | **5 / 5** ✅ |
| 6 — ML | 3 (challenge) | **3 / 3** ✅ (Olivetti/CIFAR ver nota) |
| 7 — Redes neuronales | 2 challenges (+ 1 guiado sin TODO) | **2 / 2** ✅ (CIFAR: código+respuestas, sin ejecutar) |
| 8 — CNN | taller (31 TODO) + ejercicio YOLO | **2 / 2** ✅ (ejecutados de verdad, con dataset e inferencia reales) |
| 9 — Transformers/NLP | 1 ejercicio (4 celdas en blanco) | **1 / 1** ✅ (Paso 1 ejecutado; Pasos 2-4 completos pero sin ejecutar por falta de API key) |

**Todas** las actividades/talleres con `TODO` (o celdas en blanco) del repo del curso están resueltas.
Las Semanas 1–5 (Parte 1 → Examen 01) además están **ejecutadas y verificadas**
(corren de principio a fin, los `assert` pasan).

## Notas y lo que queda por fuera

- `notebooks/clase7-redes-neuronales/Challenge_Keras3_CIFAR10_Grayscale_resuelto.ipynb`:
  todo el código y las 10 respuestas están; **no se ejecutó aquí** porque la descarga
  de CIFAR-10 (~170 MB) estaba throttled. `Restart & Run All` local lo termina en ~2 min.
- `notebooks/lecture6/classification/` (6 notebooks) — **no tienen `TODO`**: pipeline de
  referencia ya completo, solo hay que leerlo/ejecutarlo.
- `YourFirstDeepNN_FashionMNIST_Keras3.ipynb` — **sin `TODO`**, notebook guiado.
- `notebooks/clase9-transformers-nlp/05_ejercicio_nvidia_documentos_resuelto.ipynb`: para
  ver el chat funcionando de verdad hace falta una `NVIDIA_API_KEY` propia (gratis en
  https://build.nvidia.com/settings/api-keys) en un archivo `.env` junto al notebook.
- Proyectos P0–P11 y P1 "estilo Pac-Man" — entregas por tema, con criterios de corrección
  propios (ver pacto); no son actividades de notebook con `TODO`.
