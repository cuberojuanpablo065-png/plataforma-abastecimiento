import pandas as pd
import plotly.express as px
import streamlit as st

from app.vistas.utilidades import COLORES_RIESGO, MESES, obtener_datos_actuales
from db import crud
from servicios import cliente_api


def mostrar():
    st.header("Riesgo de quiebre")
    st.write("Modelo 2 — clasificación: probabilidad de quedarse sin inventario en la semana.")

    tab_archivo, tab_manual = st.tabs(["Evaluar archivo cargado", "Consulta individual"])
    with tab_archivo:
        evaluar_archivo()
    with tab_manual:
        consulta_individual()

    mostrar_metricas_modelo()


# ---------- evaluacion de todo el archivo ----------
def preparar_ultima_semana(datos):
    # Para cada tienda/SKU: inventario de la ultima semana y promedio de las 4 anteriores
    datos = datos.sort_values(["tienda", "sku", "fecha"])
    filas = []
    for (tienda, sku), grupo in datos.groupby(["tienda", "sku"]):
        if len(grupo) < 2:
            continue
        ultima = grupo.iloc[-1]
        anteriores = grupo.iloc[-5:-1]
        filas.append({
            "tienda": tienda, "sku": sku,
            "inventario": float(ultima["inventario"]),
            "venta_promedio": float(anteriores["unidades_vendidas"].mean()),
            "mes": int(pd.to_datetime(ultima["fecha"]).month),
            "promocion": bool(ultima["promocion"]),
        })
    return pd.DataFrame(filas)


def evaluar_archivo():
    datos = obtener_datos_actuales()
    if datos is None:
        st.info("Primero cargá un archivo en **Cargar datos**.")
        return

    ultima_fecha = pd.to_datetime(datos["fecha"]).max().date()
    st.caption(f"Se evalúa la última semana del archivo ({ultima_fecha}) para cada tienda y SKU.")

    if st.button("Evaluar riesgo"):
        base = preparar_ultima_semana(datos)
        if base.empty:
            st.warning("No hay suficiente historial (mínimo 2 semanas por tienda/SKU)")
            return
        registros = base[["inventario", "venta_promedio", "mes", "promocion"]].to_dict("records")
        try:
            resultados = cliente_api.predecir_riesgo_lote(registros)
        except cliente_api.ErrorAPI as e:
            st.error(str(e))
            return
        st.session_state.evaluacion_riesgo = pd.concat([base, pd.DataFrame(resultados)], axis=1)

    if "evaluacion_riesgo" in st.session_state:
        mostrar_evaluacion(st.session_state.evaluacion_riesgo)


def mostrar_evaluacion(tabla):
    conteo = tabla["nivel"].value_counts()
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Riesgo alto", int(conteo.get("alto", 0)))
    col2.metric("🟠 Riesgo medio", int(conteo.get("medio", 0)))
    col3.metric("🟢 Riesgo bajo", int(conteo.get("bajo", 0)))

    # Mapa de calor tienda x SKU
    matriz = tabla.pivot(index="sku", columns="tienda", values="probabilidad_quiebre")
    fig = px.imshow(matriz, color_continuous_scale="RdYlGn_r", zmin=0, zmax=1, aspect="auto",
                    title="Probabilidad de quiebre por tienda y SKU",
                    labels={"color": "Probabilidad"})
    st.plotly_chart(fig)

    # Riesgo promedio por tienda
    por_tienda = tabla.groupby("tienda")["probabilidad_quiebre"].mean().reset_index()
    fig2 = px.bar(por_tienda.sort_values("probabilidad_quiebre", ascending=False),
                  x="tienda", y="probabilidad_quiebre", title="Riesgo promedio por tienda",
                  labels={"probabilidad_quiebre": "Probabilidad promedio", "tienda": "Tienda"})
    st.plotly_chart(fig2)

    st.subheader("Detalle")
    nivel = st.multiselect("Filtrar por nivel", ["alto", "medio", "bajo"], default=["alto", "medio"])
    filtrada = tabla[tabla["nivel"].isin(nivel)].sort_values("probabilidad_quiebre", ascending=False)
    st.dataframe(
        filtrada[["tienda", "sku", "inventario", "venta_promedio", "cobertura_semanas",
                  "probabilidad_quiebre", "nivel"]].round(2),
        hide_index=True,
        column_config={"probabilidad_quiebre": st.column_config.ProgressColumn(
            "Probabilidad", min_value=0, max_value=1, format="%.2f")},
    )

    altos = tabla[tabla["nivel"] == "alto"]
    if not altos.empty and st.button(f"Guardar los {len(altos)} casos de riesgo alto en el historial"):
        for _, fila in altos.iterrows():
            crud.guardar_analisis(
                st.session_state.usuario_id, "riesgo", fila["sku"], fila["tienda"],
                fila["probabilidad_quiebre"],
                {"inventario": fila["inventario"], "venta_promedio": round(fila["venta_promedio"], 2),
                 "nivel": fila["nivel"]},
                st.session_state.get("carga_id"),
            )
        st.success("Casos guardados ✅")


# ---------- consulta de un solo caso ----------
def consulta_individual():
    with st.form("form_riesgo"):
        col1, col2 = st.columns(2)
        tienda = col1.text_input("Tienda (opcional)", "T01")
        sku = col2.text_input("SKU (opcional)", "SKU-001")
        inventario = col1.number_input("Inventario actual (unidades)", min_value=0.0, value=20.0)
        venta_promedio = col2.number_input("Venta semanal promedio (últimas 4 semanas)",
                                           min_value=0.0, value=25.0)
        mes = col1.select_slider("Mes", options=list(range(1, 13)),
                                 format_func=lambda m: MESES[m - 1], value=12)
        promocion = col2.checkbox("Con promoción")
        calcular = st.form_submit_button("Calcular riesgo")

    if calcular:
        try:
            r = cliente_api.predecir_riesgo(inventario, venta_promedio, mes, promocion)
        except cliente_api.ErrorAPI as e:
            st.error(str(e))
            return

        color = COLORES_RIESGO[r["nivel"]]
        st.markdown(f"### Riesgo <span style='color:{color}'>{r['nivel'].upper()}</span>",
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Probabilidad de quiebre", f"{r['probabilidad_quiebre']:.0%}")
        col2.metric("Cobertura", f"{r['cobertura_semanas']} semanas")
        st.progress(r["probabilidad_quiebre"])

        crud.guardar_analisis(
            st.session_state.usuario_id, "riesgo", sku.strip().upper(), tienda.strip().upper(),
            r["probabilidad_quiebre"],
            {"inventario": inventario, "venta_promedio": venta_promedio, "nivel": r["nivel"]},
        )
        st.caption("Consulta guardada en el historial.")


def mostrar_metricas_modelo():
    with st.expander("¿Qué tan bueno es el modelo?"):
        try:
            metricas = cliente_api.metricas()["riesgo"]
        except cliente_api.ErrorAPI as e:
            st.warning(str(e))
            return
        tabla = pd.DataFrame(metricas["comparacion"]).T.reset_index()
        tabla.columns = ["Algoritmo", "Accuracy", "Precision", "Recall", "F1", "AUC"]
        st.write(f"Se compararon dos algoritmos y se eligió **{metricas['elegido']}** por tener mejor F1.")
        st.dataframe(tabla, hide_index=True)
        fig = px.bar(tabla.melt(id_vars="Algoritmo", var_name="Métrica", value_name="Valor"),
                     x="Métrica", y="Valor", color="Algoritmo", barmode="group",
                     title="Comparación de algoritmos")
        st.plotly_chart(fig)
        st.caption(f"Solo el {metricas['porcentaje_quiebres']:.0%} de las semanas tienen quiebre, "
                   "por eso se usa F1 y no accuracy: un modelo que siempre diga 'no hay quiebre' "
                   "tendría accuracy alto pero no serviría.")
