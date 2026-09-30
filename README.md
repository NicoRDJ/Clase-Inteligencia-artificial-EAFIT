# Clase Inteligencia Artificial — EAFIT (SI3003)

Repositorio de **Nicolás Rodríguez** con los trabajos clase a clase del curso *SI3003 — Inteligencia Artificial* de la Universidad EAFIT. Material del curso: [EAFIT-IA/si3003-artificial-intelligence](https://github.com/EAFIT-IA/si3003-artificial-intelligence).

Cada clase tiene su entrega (los proyectos por tema P1–P11 del pacto pedagógico). Todos los notebooks están **resueltos y ejecutados**, con las salidas guardadas.

## Entregas por clase

| Clase | Tema | Entrega | Resultado destacado |
|---|---|---|---|
| 1 | Agentes racionales (PEAS, tipos de entorno) | [Trabajo 1 — análisis PEAS de un agente real](trabajos/Trabajo1-Agentes-IA-HuggingFace.md) · [actividad de entornos](actividades-clase/actividades-resueltas.md) | Omni Image Editor 2.0 (Hugging Face Spaces) |
| 2 | Búsqueda | [Trabajo 2 — BFS, Greedy y A*](trabajos/Trabajo2-Algoritmos-Busqueda.md) · [`notebooks/clase2-busqueda/`](notebooks/clase2-busqueda/) | Grafo, laberintos y *Six Degrees of Kevin Bacon* (IMDb) |
| 3 | Optimización | [`notebooks/clase3-optimizacion/`](notebooks/clase3-optimizacion/) (8 notebooks) | Hill climbing, simulated annealing, algoritmos genéticos, PL, CSP y workshop de N-reinas |
| 4 | MDP | [`notebooks/clase4-mdp/`](notebooks/clase4-mdp/) | Lab Warehouse: Value Iteration y Policy Iteration llegan a la misma política |
| 5 | Aprendizaje por refuerzo | [`notebooks/clase5-rl/`](notebooks/clase5-rl/) · [`talleres/modulo1/`](talleres/modulo1/) | Q-learning en Taxi (recompensa −200 → +10) y taller del Módulo 1 |
| 6 | Machine Learning | [`notebooks/clase6-ml/challenge/`](notebooks/clase6-ml/challenge/) | Pipeline completo, campeón LogisticRegression, test acc ≈ 0.97 |
| 7 | Redes neuronales (Keras 3) | [`notebooks/clase7-redes-neuronales/`](notebooks/clase7-redes-neuronales/) | Olivetti ≈ 0.96 · CIFAR-10 en grises 43.0 % (con análisis por clase) |
| 8 | CNN: transfer learning y YOLO | [`notebooks/clase8-cnn/`](notebooks/clase8-cnn/) | EfficientNetB0 sobre dataset propio (espresso/cappuccino/latte): 70.4 % → 74.1 % con fine-tuning · YOLO sobre imagen nueva |
| 9 | Transformers y NLP | [`notebooks/clase9-transformers-nlp/`](notebooks/clase9-transformers-nlp/) | Word2Vec: analogías y PCA 3D del *jaguar* · asistente de documentos con NVIDIA NIM + Gradio |
| 10 | Prompt engineering y RAG | [`notebooks/clase10-rag/`](notebooks/clase10-rag/) | RAG con LangChain + Qdrant + Gemini sobre *Attention* y *RAG*: quiz 4/5 + bonus parcial, 0 alucinaciones |

Seguimiento detallado de cada actividad: [`INVENTARIO-actividades.md`](INVENTARIO-actividades.md).

## Estructura

```
.
├── actividades-clase/   # Actividades hechas en clase (a mano)
├── trabajos/            # Trabajos escritos (Markdown autocontenido por trabajo)
├── talleres/            # Talleres de preparación (Módulo 1)
├── notebooks/           # Un directorio por clase: claseN-tema/ con los notebooks resueltos
└── streamlit/           # Dashboard de análisis SEO en Streamlit (proyecto adicional)
```

## Cómo ejecutar

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r notebooks/<claseN-tema>/requirements.txt jupyter
jupyter notebook
```

Las clases 9 y 10 usan APIs externas (NVIDIA NIM y Google Gemini). Las llaves van en un archivo `.env` en la raíz del repo, que **no se versiona**:

```
GOOGLE_API_KEY=...
NVIDIA_API_KEY=...
```

## App de Streamlit — Dashboard de SEO & Marketing Digital

Dashboard para seguir la salud SEO de varias páginas: score general 0–100, auditoría técnica, análisis de contenido y keywords, señales sociales y de confianza, plan de acción priorizado e historial exportable a CSV.

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```
