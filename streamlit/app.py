import streamlit as st

st.set_page_config(page_title="Clase IA EAFIT", page_icon="🤖")

st.title("Clase Inteligencia Artificial — EAFIT")
st.write("App base de Streamlit para talleres y demos del curso.")

nombre = st.text_input("Tu nombre")
if nombre:
    st.success(f"¡Hola, {nombre}! Todo listo para empezar a construir.")
