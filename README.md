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

### App de Streamlit: Dashboard de SEO & Marketing Digital

Dashboard para llevar seguimiento de la salud SEO y de marketing de varias páginas o
negocios propios (o de terceros). Recibe el link de una página y una palabra clave
objetivo opcional, y entrega:

- **Score general (0-100)** y desglose por categoría (Técnico, Contenido, Social).
- **Técnico y rastreo:** HTTPS, status code, tiempo de respuesta, `robots.txt` y
  `sitemap.xml` accesibles, meta robots, canonical, contenido mixto, URL limpia.
- **Contenido y keywords:** título y meta description (con largo ideal), jerarquía de
  encabezados, extensión del contenido, `alt` en imágenes, mobile-friendly, idioma,
  favicon, enlaces internos, **contador de palabras clave más frecuentes** y análisis
  de densidad/ubicación de una keyword objetivo.
- **Social y confianza:** Open Graph, Twitter Card, datos estructurados (JSON-LD) y
  señales de confianza (contacto, acerca de, privacidad, términos).
- **Plan de acción priorizado** con recomendaciones concretas ordenadas por impacto.
- **Historial de sesión** para comparar varias páginas/negocios y exportarlo a CSV.

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

## Estado

Repositorio activo — se actualiza a medida que se desarrollan nuevos talleres y actividades del curso.
