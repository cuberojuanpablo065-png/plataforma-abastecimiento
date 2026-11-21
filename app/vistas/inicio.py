import streamlit as st


def mostrar():
    st.header("Inicio")
    st.write("Resumen general: cargas recientes, alertas de quiebre y tipo de cambio.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos cargados", "—")
    col2.metric("SKUs en riesgo", "—")
    col3.metric("Tipo de cambio (₡/USD)", "—")
    st.info("Pendiente: conectar métricas reales (pasos 2 y 7)")
