# Clase 8 — CNN: transfer learning, fine-tuning y YOLO (resueltos)

| Notebook | Tema | Estado |
|---|---|---|
| `taller_transfer_learning_resuelto.ipynb` | Taller de transfer learning con dataset propio (31 `TODO`) | ✅ **ejecutado de verdad**: dataset descargado (DuckDuckGo), limpiado a mano y clasificado con EfficientNetB0 |
| `yolo/Lecture_08_Yolo_Intro_resuelto.ipynb` | Ejercicio de inferencia con YOLO sobre una imagen propia | ✅ **ejecutado**: detecta 2 personas + 1 corbata en `zidane.jpg` |

## Taller de transfer learning

Problema elegido: clasificar **espresso / cappuccino / latte** — el ejemplo que
sugiere el propio enunciado y, a propósito, el más difícil de los sugeridos
(un primer intento con pizza/hamburguesa/sushi dio 100% de accuracy sin un
solo error, porque son clases demasiado distintas para EfficientNet y no
dejaban nada que analizar en el TODO 6).

- **Dataset:** 201 imágenes descargadas → 169 tras limpieza técnica (0
  inválidas) y semántica manual (32 quitadas: clipart, infografías,
  empaques, tazas/vasos vacíos — sobre todo en "cappuccino", que quedó con
  menos imágenes que las otras dos clases).
- **Split:** 70/15/15 → train 118, val 24, test 27.
- **Resultado (test):** 81.5% antes del fine-tuning → **74.1% después**
  (bajó 7.4 puntos). El TODO 6 analiza por qué el fine-tuning no ayudó en
  esta corrida (dataset pequeño + 20 capas descongeladas = sobreajuste),
  siguiendo la advertencia del propio enunciado: "si el resultado empeora,
  no significa que el experimento salió mal".
- **Confusión principal:** `cappuccino` ↔ `latte` (ambas llevan espuma de
  leche); `espresso` es la clase mejor distinguida.

`data_raw/` (imágenes descargadas) y `dataset/` (split train/val/test) están
en `.gitignore` — no se versionan porque son contenido scrapeado de la web
(revisión de licencias pendiente si se quisiera redistribuir) y se
regeneran solos al volver a ejecutar el notebook con `Restart & Run All`.

## YOLO — ejercicio de imagen propia

`Lecture_08_Yolo_Intro_resuelto.ipynb` prueba el modelo sobre `zidane.jpg`
(otra imagen de ejemplo de Ultralytics, distinta de `bus.jpg` que ya usa el
resto del notebook), con `conf=0.35`.

Los notebooks guiados sin `TODO` (`CNN_Transfer_Keras3.ipynb`,
`Lecture_08_Yolo_training[.ipynb / _own_data.ipynb]`,
`yolo/deployment/test.ipynb`) no se tocaron: son demos de referencia que
además requieren API keys externas (Roboflow) y datasets que no están en
este repo.
