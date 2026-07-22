import time
from urllib.parse import urlparse

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="Dashboard SEO", page_icon="🔎", layout="wide")

st.title("🔎 Dashboard de análisis SEO")
st.write(
    "Ingresa el link de cualquier página (tuya o de un tercero) para estimar, "
    "de forma básica, qué tan bien está optimizada para SEO."
)

url = st.text_input("URL a analizar", placeholder="https://ejemplo.com")
analizar = st.button("Analizar", type="primary")


def normalizar_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def analizar_pagina(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SEO-Dashboard-EAFIT/1.0)"}
    inicio = time.time()
    resp = requests.get(url, headers=headers, timeout=10)
    tiempo_respuesta = time.time() - inicio

    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else ""

    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

    h1_tags = soup.find_all("h1")

    imgs = soup.find_all("img")
    imgs_sin_alt = [img for img in imgs if not img.get("alt")]

    viewport_tag = soup.find("meta", attrs={"name": "viewport"})

    texto = soup.get_text(separator=" ", strip=True)
    n_palabras = len(texto.split())

    dominio = urlparse(url).netloc
    links = soup.find_all("a", href=True)
    internos = [a for a in links if a["href"].startswith("/") or dominio in a["href"]]
    externos = [a for a in links if a not in internos]

    return {
        "status_code": resp.status_code,
        "https": url.startswith("https://"),
        "tiempo_respuesta": tiempo_respuesta,
        "title": title,
        "meta_desc": meta_desc,
        "n_h1": len(h1_tags),
        "n_imgs": len(imgs),
        "n_imgs_sin_alt": len(imgs_sin_alt),
        "viewport": viewport_tag is not None,
        "n_palabras": n_palabras,
        "n_links_internos": len(internos),
        "n_links_externos": len(externos),
    }


def calcular_score(m: dict):
    checks = []

    puntos = 10 if m["https"] else 0
    checks.append({"Criterio": "Usa HTTPS", "Estado": "✅" if puntos else "❌", "Puntos": puntos, "Máximo": 10})

    ok_status = m["status_code"] == 200
    puntos = 10 if ok_status else 0
    checks.append({"Criterio": "Responde 200 OK", "Estado": "✅" if ok_status else "❌", "Puntos": puntos, "Máximo": 10})

    if m["tiempo_respuesta"] < 1:
        puntos, estado = 10, "✅"
    elif m["tiempo_respuesta"] < 3:
        puntos, estado = 6, "⚠️"
    else:
        puntos, estado = 2, "❌"
    checks.append({"Criterio": f"Tiempo de respuesta ({m['tiempo_respuesta']:.2f}s)", "Estado": estado, "Puntos": puntos, "Máximo": 10})

    largo_title = len(m["title"])
    if 10 <= largo_title <= 60:
        puntos, estado = 15, "✅"
    elif largo_title > 0:
        puntos, estado = 8, "⚠️"
    else:
        puntos, estado = 0, "❌"
    checks.append({"Criterio": f"Título ({largo_title} caracteres)", "Estado": estado, "Puntos": puntos, "Máximo": 15})

    largo_desc = len(m["meta_desc"])
    if 50 <= largo_desc <= 160:
        puntos, estado = 15, "✅"
    elif largo_desc > 0:
        puntos, estado = 8, "⚠️"
    else:
        puntos, estado = 0, "❌"
    checks.append({"Criterio": f"Meta description ({largo_desc} caracteres)", "Estado": estado, "Puntos": puntos, "Máximo": 15})

    if m["n_h1"] == 1:
        puntos, estado = 10, "✅"
    elif m["n_h1"] > 1:
        puntos, estado = 5, "⚠️"
    else:
        puntos, estado = 0, "❌"
    checks.append({"Criterio": f"Etiquetas H1 ({m['n_h1']})", "Estado": estado, "Puntos": puntos, "Máximo": 10})

    if m["n_imgs"] == 0:
        puntos, estado = 10, "✅"
    else:
        ratio = 1 - (m["n_imgs_sin_alt"] / m["n_imgs"])
        puntos = round(ratio * 10)
        estado = "✅" if ratio == 1 else ("⚠️" if ratio > 0.5 else "❌")
    checks.append({
        "Criterio": f"Imágenes con alt ({m['n_imgs'] - m['n_imgs_sin_alt']}/{m['n_imgs']})",
        "Estado": estado, "Puntos": puntos, "Máximo": 10,
    })

    if m["n_palabras"] >= 300:
        puntos, estado = 10, "✅"
    elif m["n_palabras"] >= 100:
        puntos, estado = 5, "⚠️"
    else:
        puntos, estado = 0, "❌"
    checks.append({"Criterio": f"Contenido ({m['n_palabras']} palabras)", "Estado": estado, "Puntos": puntos, "Máximo": 10})

    puntos = 10 if m["viewport"] else 0
    checks.append({"Criterio": "Meta viewport (mobile-friendly)", "Estado": "✅" if puntos else "❌", "Puntos": puntos, "Máximo": 10})

    score_total = sum(c["Puntos"] for c in checks)
    return score_total, checks


if analizar and url:
    url_normalizada = normalizar_url(url.strip())
    try:
        with st.spinner(f"Analizando {url_normalizada}..."):
            metricas = analizar_pagina(url_normalizada)
            score, checks = calcular_score(metricas)
    except requests.exceptions.RequestException as e:
        st.error(f"No se pudo acceder a la página: {e}")
        st.stop()

    col1, col2 = st.columns([1, 2])

    with col1:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Score SEO estimado"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2563eb"},
                    "steps": [
                        {"range": [0, 50], "color": "#fee2e2"},
                        {"range": [50, 80], "color": "#fef3c7"},
                        {"range": [80, 100], "color": "#dcfce7"},
                    ],
                },
            )
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Enlaces internos", metricas["n_links_internos"])
        st.metric("Enlaces externos", metricas["n_links_externos"])

    with col2:
        df = pd.DataFrame(checks)
        st.subheader("Detalle por criterio")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("Criterio")["Puntos"])

    with st.expander("Datos crudos"):
        st.write(f"**Título:** {metricas['title'] or '(vacío)'}")
        st.write(f"**Meta description:** {metricas['meta_desc'] or '(vacía)'}")
        st.json(metricas)
elif analizar and not url:
    st.warning("Ingresa una URL antes de analizar.")
