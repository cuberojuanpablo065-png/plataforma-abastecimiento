import pandas as pd
import plotly.express as px
import streamlit as st

from app.vistas.utilidades import MESES, obtener_datos_actuales
from db import crud
from servicios import cliente_api


def mostrar():
    st.header("Pronóstico de demanda")
    st.write("Modelo 1 — regresión: unidades semanales esperadas por SKU y tienda.")

    try:
        catalogo = cliente_api.catalogo()
    except cliente_api.ErrorAPI as e:
        st.error(str(e))
        return

    datos = obtener_datos_actuales()

    # ---------- formulario ----------
    with st.form("form_pronostico"):
        col1, col2 = st.columns(2)
        tienda = col1.selectbox("Tienda", catalogo["tiendas"])
        sku = col2.selectbox("SKU", catalogo["skus"])
        mes = col1.select_slider("Mes", options=list(range(1, 13)),
                                 format_func=lambda m: MESES[m - 1], value=12)
        precio = col2.number_input("Precio (₡)", min_value=1.0,
                                   value=precio_sugerido(datos, tienda, sku), step=50.0)
        promocion = st.checkbox("Con promoción")
        calcular = st.form_submit_button("Pronosticar")

    if calcular:
        try:
            resultado = cliente_api.predecir_demanda(tienda, sku, mes, precio, promocion)
            anual = pronostico_anual(tienda, sku, precio)
        except cliente_api.ErrorAPI as e:
            st.error(str(e))
            return
        st.session_state.ultimo_pronostico = {
            "tienda": tienda, "sku": sku, "mes": mes, "precio": precio,
            "promocion": promocion, "unidades": resultado["unidades_estimadas"], "anual": anual,
        }

    if "ultimo_pronostico" in st.session_state:
        mostrar_resultado(st.session_state.ultimo_pronostico, datos)

    mostrar_metricas_modelo()


def precio_sugerido(datos, tienda, sku):
    # Si hay datos cargados, sugiere el precio normal del producto
    if datos is not None:
        filtro = datos[(datos["sku"] == sku) & (datos["promocion"] == 0)]
        if not filtro.empty:
            return float(filtro["precio"].median())
    return 3000.0


def pronostico_anual(tienda, sku, precio):
    # Pronostico de los 12 meses, sin y con promocion, para el grafico
    filas = []
    for mes in range(1, 13):
        for promocion in (False, True):
            r = cliente_api.predecir_demanda(tienda, sku, mes, precio, promocion)
            filas.append({"mes": mes, "escenario": "Con promoción" if promocion else "Sin promoción",
                          "unidades": r["unidades_estimadas"]})
    return filas


def mostrar_resultado(p, datos):
    st.subheader("Resultado")
    col1, col2, col3 = st.columns(3)
    col1.metric("Unidades estimadas por semana", f"{p['unidades']:.1f}")
    col2.metric("Unidades estimadas en el mes", f"{p['unidades'] * 4.33:.0f}")
    col3.metric("Venta estimada en el mes", f"₡{p['unidades'] * 4.33 * p['precio']:,.0f}")

    # Grafico: pronostico de todo el anio vs historico real
    grafico = pd.DataFrame(p["anual"])
    if datos is not None:
        real = datos[(datos["tienda"] == p["tienda"]) & (datos["sku"] == p["sku"])].copy()
        if not real.empty:
            real["mes"] = pd.to_datetime(real["fecha"]).dt.month
            historico = real.groupby("mes")["unidades_vendidas"].mean().reset_index()
            historico = historico.rename(columns={"unidades_vendidas": "unidades"})
            historico["escenario"] = "Histórico real"
            grafico = pd.concat([grafico, historico])

    grafico["Mes"] = grafico["mes"].apply(lambda m: MESES[m - 1])
    fig = px.line(grafico.sort_values("mes"), x="Mes", y="unidades", color="escenario",
                  markers=True, title=f"Demanda semanal estimada — {p['sku']} en {p['tienda']}",
                  labels={"unidades": "Unidades por semana", "escenario": ""})
    st.plotly_chart(fig)

    if st.button("Guardar pronóstico"):
        crud.guardar_analisis(
            st.session_state.usuario_id, "pronostico", p["sku"], p["tienda"], p["unidades"],
            {"mes": p["mes"], "precio": p["precio"], "promocion": p["promocion"]},
            st.session_state.get("carga_id"),
        )
        st.success("Pronóstico guardado en el historial ✅")


def mostrar_metricas_modelo():
    with st.expander("¿Qué tan bueno es el modelo?"):
        try:
            metricas = cliente_api.metricas()["pronostico"]
        except cliente_api.ErrorAPI as e:
            st.warning(str(e))
            return
        tabla = pd.DataFrame(metricas["comparacion"]).T.reset_index()
        tabla.columns = ["Algoritmo", "Error medio (MAE)", "R²"]
        st.write(f"Se compararon dos algoritmos y se eligió **{metricas['elegido']}** "
                 "por tener el menor error.")
        st.dataframe(tabla, hide_index=True)
        st.caption("MAE: cuántas unidades se equivoca en promedio. "
                   "R²: qué porcentaje de la variación de las ventas explica (1 = perfecto).")
