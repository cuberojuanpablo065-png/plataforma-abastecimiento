import streamlit as st

from app.vistas.utilidades import obtener_datos_actuales
from db import crud
from servicios import cliente_api, tipo_cambio


def mostrar():
    st.header("Inicio")
    st.write(f"Bienvenido, **{st.session_state.usuario}**.")

    cargas = crud.listar_cargas(st.session_state.usuario_id)
    riesgos = crud.listar_analisis(st.session_state.usuario_id, "riesgo")
    cambio = tipo_cambio.obtener_tipo_cambio()

    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos cargados", len(cargas))
    col2.metric("Análisis de riesgo guardados", len(riesgos))
    col3.metric("Tipo de cambio (₡ por USD)", f"₡{cambio['valor']:,.2f}" if cambio else "No disponible")

    if cambio:
        aviso = " (último valor conocido)" if cambio.get("desactualizado") else ""
        st.caption(f"Actualizado: {cambio['fecha']}{aviso} · "
                   "[Tasas por ExchangeRate-API](https://www.exchangerate-api.com)")
    else:
        st.warning("No se pudo consultar el tipo de cambio en este momento")

    # Venta del archivo cargado, en colones y en dolares
    datos = obtener_datos_actuales()
    if datos is not None:
        venta_colones = float((datos["unidades_vendidas"] * datos["precio"]).sum())
        st.subheader("Archivo actual")
        c1, c2 = st.columns(2)
        c1.metric("Venta total", f"₡{venta_colones:,.0f}")
        if cambio:
            dolares = tipo_cambio.colones_a_dolares(venta_colones, cambio["valor"])
            c2.metric("Venta total en USD", f"${dolares:,.0f}")
    else:
        st.info("Todavía no hay datos cargados. Andá a **Cargar datos**.")

    # Estado de nuestra API
    try:
        estado = cliente_api.salud()
        if estado["modelos_entrenados"]:
            st.success("API de modelos: conectada ✅")
        else:
            st.warning("API conectada, pero falta entrenar: python -m modelos.entrenar")
    except cliente_api.ErrorAPI as e:
        st.error(f"API de modelos: {e}")
