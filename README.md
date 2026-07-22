# Clase Inteligencia Artificial — EAFIT

Repositorio de trabajos, talleres y actividades del curso de Inteligencia Artificial en EAFIT.

## Contenido

| # | Trabajo | Tema | Archivo |
|---|---|---|---|
| 1 | Analizando Agentes de IA con Hugging Face Spaces | Componentes PEAS, clasificación del entorno y tipos de programa de agente, aplicados al Space [Omni Image Editor 2.0](https://huggingface.co/spaces/selfit-camera/Omni-Image-Editor) | [trabajos/Trabajo1-Agentes-IA-HuggingFace.md](trabajos/Trabajo1-Agentes-IA-HuggingFace.md) |

## Estructura

```
.
├── trabajos/       # Una carpeta o archivo Markdown autocontenido por trabajo (TrabajoN-tema-corto.md)
└── streamlit/       # Dashboard de análisis SEO en Streamlit
    ├── app.py
    └── requirements.txt
```

### App de Streamlit: Dashboard de análisis SEO

Dashboard que recibe el link de cualquier página web (propia o de terceros) y estima
un puntaje básico de SEO (0-100), mostrando el detalle por criterio: HTTPS, código de
respuesta, tiempo de carga, título, meta description, etiquetas H1, imágenes con `alt`,
cantidad de contenido, mobile-friendly, y enlaces internos/externos.

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

## Estado

Repositorio activo — se actualiza a medida que se desarrollan nuevos talleres y actividades del curso.
