# Clase 7 — Redes neuronales (challenges de Keras 3, resueltos)

MLP fully-connected (`Flatten → Dense(h, relu) → Dense(clases)`), pérdida
`SparseCategoricalCrossentropy(from_logits=True)`, optimizador `Adam`.

| Notebook | Dataset | Estado |
|---|---|---|
| `Challenge_Keras3_OlivettiFaces_resuelto.ipynb` | Olivetti Faces (400 caras, 40 personas) | ✅ **ejecutado** (backend TensorFlow) — test accuracy ≈ **0.96** |
| `Challenge_Keras3_CIFAR10_Grayscale_resuelto.ipynb` | CIFAR-10 en escala de grises (10 clases) | ✅ código + respuestas completos · ⚠️ **no ejecutado aquí** (descarga de CIFAR-10 throttled). `Restart & Run All` local: ~2 min de entrenamiento en CPU |

Ambos incluyen las 10 preguntas respondidas.

> **Nota técnica.** A los dos notebooks se les añadió un **centrado de los píxeles
> a media 0** (con la estadística de train). El notebook de Olivetti no lo traía y,
> con una entrada 100 % positiva, un MLP de una capa oculta se queda atascado en una
> región plana de la pérdida y no aprende (accuracy = 1/nº de clases). Restar la media
> lo soluciona; para CIFAR se dejó también por robustez.

El notebook guiado `YourFirstDeepNN_FashionMNIST_Keras3.ipynb` del repo del curso
**no tiene `TODO`** (es la receta base ya resuelta) — mismo patrón que estos dos.

Requiere: `keras` (3.x) + un backend (`tensorflow`, `jax` o `torch`), `scikit-learn`
(Olivetti), `numpy`, `matplotlib`.
