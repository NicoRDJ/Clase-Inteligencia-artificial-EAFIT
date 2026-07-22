import re
import time
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="Dashboard SEO & Marketing", page_icon="🚀", layout="wide")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SEO-Dashboard-EAFIT/1.0)"}

STOPWORDS = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
    "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero",
    "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando",
    "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien",
    "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra",
    "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
    "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos",
    "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas",
    "algunas", "algo", "nosotros", "the", "and", "for", "are", "but", "not",
    "you", "your", "with", "this", "that", "from", "have", "has", "will", "can",
    "our", "all", "was", "were", "their", "its", "into", "more", "about", "how",
    "what", "when", "which", "who", "get", "use", "using",
}


def normalizar_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def check_robots_sitemap(base_url: str):
    parsed = urlparse(base_url)
    dominio = f"{parsed.scheme}://{parsed.netloc}"
    try:
        r = requests.get(f"{dominio}/robots.txt", headers=HEADERS, timeout=5)
        robots_ok = r.status_code == 200
    except requests.exceptions.RequestException:
        robots_ok = False
    try:
        s = requests.get(f"{dominio}/sitemap.xml", headers=HEADERS, timeout=5)
        sitemap_ok = s.status_code == 200
    except requests.exceptions.RequestException:
        sitemap_ok = False
    return robots_ok, sitemap_ok


def analizar_pagina(url: str) -> dict:
    inicio = time.time()
    resp = requests.get(url, headers=HEADERS, timeout=10)
    tiempo_respuesta = time.time() - inicio
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else ""

    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

    meta_robots_tag = soup.find("meta", attrs={"name": "robots"})
    meta_robots = meta_robots_tag.get("content", "").lower() if meta_robots_tag else ""

    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else ""

    html_tag = soup.find("html")
    lang = html_tag.get("lang", "") if html_tag else ""

    favicon = soup.find("link", attrs={"rel": re.compile("icon", re.I)})

    heading_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    niveles = [int(h.name[1]) for h in heading_tags]
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

    html_str = str(soup)
    mixed_content = url.startswith("https://") and ('src="http://' in html_str or 'href="http://' in html_str)

    og_tags = {
        m.get("property", "").replace("og:", ""): m.get("content", "")
        for m in soup.find_all("meta", attrs={"property": re.compile("^og:")})
    }
    twitter_tags = {
        m.get("name", "").replace("twitter:", ""): m.get("content", "")
        for m in soup.find_all("meta", attrs={"name": re.compile("^twitter:")})
    }
    json_ld = soup.find_all("script", attrs={"type": "application/ld+json"})

    texto_links = " ".join(a.get_text().lower() for a in links)
    señales_confianza = {
        "contacto": any(w in texto_links for w in ["contact", "contacto"]),
        "acerca de": any(w in texto_links for w in ["about", "acerca", "nosotros", "quiénes somos"]),
        "privacidad": any(w in texto_links for w in ["privacy", "privacidad"]),
        "términos": any(w in texto_links for w in ["terms", "términos", "condiciones"]),
    }

    parsed_url = urlparse(url)
    url_limpia = (
        parsed_url.path == parsed_url.path.lower()
        and parsed_url.query.count("&") <= 1
        and " " not in url
    )

    palabras = re.findall(r"[a-záéíóúñü]{3,}", texto.lower())
    palabras_filtradas = [w for w in palabras if w not in STOPWORDS]
    top_keywords = Counter(palabras_filtradas).most_common(15)

    robots_ok, sitemap_ok = check_robots_sitemap(url)

    return {
        "status_code": resp.status_code,
        "https": url.startswith("https://"),
        "tiempo_respuesta": tiempo_respuesta,
        "title": title,
        "meta_desc": meta_desc,
        "meta_robots": meta_robots,
        "canonical": canonical,
        "lang": lang,
        "favicon": favicon is not None,
        "niveles_encabezados": niveles,
        "n_h1": len(h1_tags),
        "n_imgs": len(imgs),
        "n_imgs_sin_alt": len(imgs_sin_alt),
        "viewport": viewport_tag is not None,
        "texto": texto,
        "n_palabras": n_palabras,
        "n_links_internos": len(internos),
        "n_links_externos": len(externos),
        "mixed_content": mixed_content,
        "og_tags": og_tags,
        "twitter_tags": twitter_tags,
        "n_json_ld": len(json_ld),
        "señales_confianza": señales_confianza,
        "url_limpia": url_limpia,
        "top_keywords": top_keywords,
        "robots_ok": robots_ok,
        "sitemap_ok": sitemap_ok,
    }


def analizar_keyword_objetivo(m: dict, keyword: str) -> dict:
    kw = keyword.strip().lower()
    texto_lower = m["texto"].lower()
    count_kw = texto_lower.count(kw)
    densidad = (count_kw / m["n_palabras"] * 100) if m["n_palabras"] else 0
    primeras_100 = " ".join(m["texto"].split()[:100]).lower()
    return {
        "keyword": keyword,
        "conteo": count_kw,
        "densidad": densidad,
        "en_titulo": kw in m["title"].lower(),
        "en_meta": kw in m["meta_desc"].lower(),
        "en_h1": kw in texto_lower and m["n_h1"] > 0,
        "en_primeras_100": kw in primeras_100,
    }


def calcular_checks(m: dict):
    checks = []

    def chk(categoria, criterio, puntos, maximo, recomendacion=""):
        estado = "✅" if puntos >= maximo else ("⚠️" if puntos > 0 else "❌")
        checks.append({
            "Categoría": categoria, "Criterio": criterio, "Estado": estado,
            "Puntos": puntos, "Máximo": maximo,
            "Recomendación": "" if estado == "✅" else recomendacion,
        })

    # Técnico y rastreo
    chk("Técnico", "Usa HTTPS", 5 if m["https"] else 0, 5,
        "Migra el sitio a HTTPS; es un factor de ranking y de confianza para el usuario.")
    chk("Técnico", "Responde 200 OK", 5 if m["status_code"] == 200 else 0, 5,
        f"La página respondió con status {m['status_code']}; revisa redirecciones o errores del servidor.")
    t = m["tiempo_respuesta"]
    puntos_t = 5 if t < 1 else (3 if t < 3 else 1)
    chk("Técnico", f"Tiempo de respuesta ({t:.2f}s)", puntos_t, 5,
        "Optimiza el servidor/hosting o usa un CDN; sobre 3s afecta ranking y conversión.")
    chk("Técnico", "robots.txt accesible", 3 if m["robots_ok"] else 0, 3,
        "Crea un robots.txt accesible en la raíz del dominio para guiar el rastreo.")
    chk("Técnico", "sitemap.xml accesible", 3 if m["sitemap_ok"] else 0, 3,
        "Genera y publica un sitemap.xml para facilitar la indexación completa del sitio.")
    bloquea_index = "noindex" in m["meta_robots"]
    chk("Técnico", "Meta robots no bloquea indexación", 0 if bloquea_index else 4, 4,
        "La página tiene noindex: no aparecerá en buscadores. Quítalo si quieres que se indexe.")
    chk("Técnico", "Etiqueta canonical presente", 3 if m["canonical"] else 0, 3,
        "Agrega <link rel=\"canonical\"> para evitar problemas de contenido duplicado.")
    chk("Técnico", "Sin contenido mixto (http en https)", 0 if m["mixed_content"] else 2, 2,
        "Hay recursos http:// cargando en una página https:// (contenido mixto); actualiza esos enlaces.")
    chk("Técnico", "URL limpia (minúsculas, pocos parámetros)", 2 if m["url_limpia"] else 0, 2,
        "Usa URLs en minúsculas, legibles y con pocos parámetros para mejor SEO y usabilidad.")

    # Contenido y keywords
    largo_title = len(m["title"])
    puntos_title = 6 if 50 <= largo_title <= 60 else (3 if largo_title > 0 else 0)
    chk("Contenido", f"Título ({largo_title} caracteres)", puntos_title, 6,
        "El título ideal mide 50-60 caracteres e incluye la keyword principal cerca del inicio.")

    largo_desc = len(m["meta_desc"])
    puntos_desc = 6 if 150 <= largo_desc <= 160 else (3 if largo_desc > 0 else 0)
    chk("Contenido", f"Meta description ({largo_desc} caracteres)", puntos_desc, 6,
        "La meta description ideal mide 150-160 caracteres, con keyword y una llamada a la acción.")

    puntos_h1 = 5 if m["n_h1"] == 1 else (2 if m["n_h1"] > 1 else 0)
    chk("Contenido", f"Un único H1 ({m['n_h1']} encontrado(s))", puntos_h1, 5,
        "Usa exactamente un H1 por página que describa el contenido principal.")

    niveles = m["niveles_encabezados"]
    salto = False
    max_visto = 0
    for n in niveles:
        if n > max_visto + 1:
            salto = True
        max_visto = max(max_visto, n)
    chk("Contenido", "Jerarquía de encabezados sin saltos (H1→H2→H3...)", 0 if salto else 4, 4,
        "Evita saltar niveles de encabezado (p. ej. de H1 directo a H3); afecta accesibilidad y SEO.")

    puntos_contenido = 5 if m["n_palabras"] >= 300 else (2 if m["n_palabras"] >= 100 else 0)
    chk("Contenido", f"Extensión del contenido ({m['n_palabras']} palabras)", puntos_contenido, 5,
        "Amplía el contenido: páginas con menos de 300 palabras suelen rankear peor.")

    if m["n_imgs"] == 0:
        puntos_alt = 5
    else:
        ratio = 1 - (m["n_imgs_sin_alt"] / m["n_imgs"])
        puntos_alt = round(ratio * 5)
    chk("Contenido", f"Imágenes con alt ({m['n_imgs'] - m['n_imgs_sin_alt']}/{m['n_imgs']})", puntos_alt, 5,
        "Agrega texto alternativo descriptivo a todas las imágenes (SEO + accesibilidad).")

    chk("Contenido", "Mobile-friendly (meta viewport)", 4 if m["viewport"] else 0, 4,
        "Agrega <meta name=\"viewport\"> para que el sitio se vea bien en celulares.")
    chk("Contenido", "Idioma declarado (atributo lang)", 2 if m["lang"] else 0, 2,
        "Declara el idioma con <html lang=\"es\"> (o el que corresponda).")
    chk("Contenido", "Favicon presente", 1 if m["favicon"] else 0, 1,
        "Agrega un favicon; mejora el reconocimiento de marca en pestañas y resultados.")
    chk("Contenido", f"Tiene enlaces internos ({m['n_links_internos']})", 2 if m["n_links_internos"] > 0 else 0, 2,
        "Agrega enlaces internos entre tus páginas para repartir autoridad y guiar la navegación.")

    # Social y confianza
    n_og = sum(1 for k in ("title", "description", "image") if m["og_tags"].get(k))
    chk("Social", f"Open Graph ({n_og}/3 etiquetas clave)", n_og * 2, 6,
        "Agrega og:title, og:description y og:image para que se vea bien al compartir en redes.")
    chk("Social", "Twitter Card configurada", 3 if m["twitter_tags"].get("card") else 0, 3,
        "Agrega la etiqueta twitter:card para controlar cómo se ve el link al compartirlo en X/Twitter.")
    chk("Social", "Datos estructurados (JSON-LD / schema.org)", 4 if m["n_json_ld"] > 0 else 0, 4,
        "Agrega datos estructurados (schema.org) para acceder a resultados enriquecidos en Google.")
    n_confianza = sum(1 for v in m["señales_confianza"].values() if v)
    chk("Social", f"Señales de confianza ({n_confianza}/4: contacto, acerca de, privacidad, términos)",
        min(n_confianza, 2), 2,
        "Agrega páginas/enlaces de contacto, acerca de, privacidad y términos: refuerzan la confianza (E-E-A-T).")

    return checks


def color_score(score: int) -> str:
    if score >= 80:
        return "#16a34a"
    if score >= 50:
        return "#d97706"
    return "#dc2626"


st.title("🚀 Dashboard de SEO & Marketing Digital")
st.write(
    "Analiza cualquier página web (tuya o de un tercero) para estimar su salud de SEO, "
    "identificar oportunidades de marketing y llevar seguimiento de varios sitios o negocios."
)

if "historial" not in st.session_state:
    st.session_state.historial = []

with st.sidebar:
    st.header("Analizar página")
    url_input = st.text_input("URL", placeholder="https://tunegocio.com")
    keyword_input = st.text_input("Palabra clave objetivo (opcional)", placeholder="ej. zapatos para correr")
    analizar = st.button("Analizar", type="primary", use_container_width=True)

    st.divider()
    st.header("Historial de esta sesión")
    if st.session_state.historial:
        df_hist = pd.DataFrame(st.session_state.historial)
        st.dataframe(df_hist[["url", "score", "hora"]], hide_index=True, use_container_width=True)
        st.download_button(
            "Descargar historial (CSV)",
            df_hist.to_csv(index=False).encode("utf-8"),
            file_name="historial_seo.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if st.button("Limpiar historial", use_container_width=True):
            st.session_state.historial = []
            st.rerun()
    else:
        st.caption("Aún no has analizado ninguna página.")

if analizar and url_input:
    url = normalizar_url(url_input)
    try:
        with st.spinner(f"Analizando {url}..."):
            metricas = analizar_pagina(url)
            checks = calcular_checks(metricas)
    except requests.exceptions.RequestException as e:
        st.error(f"No se pudo acceder a la página: {e}")
        st.stop()

    df_checks = pd.DataFrame(checks)
    puntos_totales = df_checks["Puntos"].sum()
    maximo_total = df_checks["Máximo"].sum()
    score = round(puntos_totales / maximo_total * 100) if maximo_total else 0

    resumen_categorias = df_checks.groupby("Categoría")[["Puntos", "Máximo"]].sum().reset_index()
    resumen_categorias["Score"] = (resumen_categorias["Puntos"] / resumen_categorias["Máximo"] * 100).round(0)

    st.session_state.historial.append({
        "url": url,
        "score": score,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    tab_resumen, tab_contenido, tab_tecnico, tab_social, tab_historial = st.tabs(
        ["📊 Resumen", "✍️ Contenido y Keywords", "⚙️ Técnico y Rastreo", "📣 Social y Confianza", "🗂️ Historial"]
    )

    with tab_resumen:
        col1, col2 = st.columns([1, 2])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Score SEO general"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": color_score(score)},
                    "steps": [
                        {"range": [0, 50], "color": "#fee2e2"},
                        {"range": [50, 80], "color": "#fef3c7"},
                        {"range": [80, 100], "color": "#dcfce7"},
                    ],
                },
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig_cat = go.Figure(go.Bar(
                x=resumen_categorias["Score"],
                y=resumen_categorias["Categoría"],
                orientation="h",
                marker_color=[color_score(s) for s in resumen_categorias["Score"]],
                text=resumen_categorias["Score"].astype(int).astype(str) + "%",
                textposition="outside",
            ))
            fig_cat.update_layout(
                title="Score por categoría", xaxis_range=[0, 110],
                height=280, margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        st.subheader("📋 Plan de acción prioritario")
        pendientes = df_checks[df_checks["Estado"] != "✅"].copy()
        pendientes["Impacto"] = pendientes["Máximo"] - pendientes["Puntos"]
        pendientes = pendientes.sort_values("Impacto", ascending=False)
        if pendientes.empty:
            st.success("¡Sin pendientes relevantes! La página cumple los criterios evaluados.")
        else:
            for _, fila in pendientes.head(8).iterrows():
                st.markdown(f"**{fila['Estado']} {fila['Criterio']}** — {fila['Recomendación']}")

    with tab_contenido:
        st.subheader("Título y meta description")
        st.write(f"**Título:** {metricas['title'] or '(vacío)'}")
        st.write(f"**Meta description:** {metricas['meta_desc'] or '(vacía)'}")

        st.subheader("Palabras clave más frecuentes")
        if metricas["top_keywords"]:
            df_kw = pd.DataFrame(metricas["top_keywords"], columns=["Palabra", "Conteo"])
            df_kw["Densidad %"] = (df_kw["Conteo"] / metricas["n_palabras"] * 100).round(2)
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.dataframe(df_kw, hide_index=True, use_container_width=True)
            with col_b:
                st.bar_chart(df_kw.set_index("Palabra")["Conteo"])
        else:
            st.caption("No se encontraron suficientes palabras para analizar.")

        if keyword_input:
            st.subheader(f"Análisis de la keyword objetivo: “{keyword_input}”")
            kw_data = analizar_keyword_objetivo(metricas, keyword_input)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Apariciones", kw_data["conteo"])
            c2.metric("Densidad", f"{kw_data['densidad']:.2f}%")
            c3.metric("En título", "✅" if kw_data["en_titulo"] else "❌")
            c4.metric("En meta desc.", "✅" if kw_data["en_meta"] else "❌")
            c5.metric("En primeras 100 palabras", "✅" if kw_data["en_primeras_100"] else "❌")
            if kw_data["densidad"] > 3:
                st.warning("Densidad alta (>3%): riesgo de keyword stuffing, puede penalizar el SEO.")
            elif kw_data["conteo"] == 0:
                st.warning("La keyword objetivo no aparece en el contenido de la página.")

        st.subheader("Detalle de criterios de contenido")
        st.dataframe(
            df_checks[df_checks["Categoría"] == "Contenido"].drop(columns="Categoría"),
            hide_index=True, use_container_width=True,
        )

    with tab_tecnico:
        st.dataframe(
            df_checks[df_checks["Categoría"] == "Técnico"].drop(columns="Categoría"),
            hide_index=True, use_container_width=True,
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Enlaces internos", metricas["n_links_internos"])
        c2.metric("Enlaces externos", metricas["n_links_externos"])
        c3.metric("Tiempo de respuesta", f"{metricas['tiempo_respuesta']:.2f}s")

    with tab_social:
        st.dataframe(
            df_checks[df_checks["Categoría"] == "Social"].drop(columns="Categoría"),
            hide_index=True, use_container_width=True,
        )
        col_og, col_tw = st.columns(2)
        with col_og:
            st.markdown("**Etiquetas Open Graph encontradas**")
            st.json(metricas["og_tags"] or {"info": "ninguna encontrada"})
        with col_tw:
            st.markdown("**Etiquetas Twitter Card encontradas**")
            st.json(metricas["twitter_tags"] or {"info": "ninguna encontrada"})
        st.markdown("**Señales de confianza detectadas**")
        st.write(metricas["señales_confianza"])

    with tab_historial:
        if len(st.session_state.historial) > 1:
            df_hist_full = pd.DataFrame(st.session_state.historial)
            st.bar_chart(df_hist_full.set_index("url")["score"])
            st.dataframe(df_hist_full, hide_index=True, use_container_width=True)
        else:
            st.caption("Analiza más páginas para poder comparar resultados aquí.")

    with st.expander("Ver datos crudos extraídos de la página"):
        st.json({k: v for k, v in metricas.items() if k != "texto"})

elif analizar and not url_input:
    st.warning("Ingresa una URL antes de analizar.")
else:
    st.info("Ingresa una URL en la barra lateral y presiona **Analizar** para comenzar.")
