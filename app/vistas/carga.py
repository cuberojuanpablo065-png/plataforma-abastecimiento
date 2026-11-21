import streamlit as st


def mostrar():
    st.header("Cargar datos")
    archivo = st.file_uploader("Subí un archivo CSV o Excel", type=["csv", "xlsx"])
    if archivo:
        st.info("Pendiente: lectura, validación y limpieza (paso 4)")
