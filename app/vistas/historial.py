import json

import pandas as pd
import plotly.express as px
import streamlit as st

from app.vistas.utilidades import a_hora_local
from db import crud


def mostrar():
    st.header("Historial de análisis")
    usuario_id = st.session_state.usuario_id

    filtro = st.radio("Tipo", ["Todos", "Pronóstico", "Riesgo"], horizontal=True)
    tipo = {"Todos": None, "Pronóstico": "pronostico", "Riesgo": "riesgo"}[filtro]
    registros = crud.listar_analisis(usuario_id, tipo)

    if not registros:
        st.info("Todavía no hay análisis guardados.")
        return

    tabla = pd.DataFrame(registros)
    tabla["detalle"] = tabla["detalle"].apply(lambda d: resumir_detalle(d))

    tabla["creado_en"] = a_hora_local(tabla["creado_en"]).dt.strftime("%Y-%m-%d %H:%M")

    # Grafico: cuantos analisis por dia y tipo
    tabla["dia"] = tabla["creado_en"].str[:10]
    por_dia = tabla.groupby(["dia", "tipo"]).size().reset_index(name="cantidad")
    fig = px.bar(por_dia, x="dia", y="cantidad", color="tipo", barmode="group",
                 title="Análisis guardados por día",
                 labels={"dia": "Día", "cantidad": "Cantidad", "tipo": "Tipo"})
    fig.update_xaxes(type="category")
    st.plotly_chart(fig)

    st.dataframe(
        tabla[["id", "tipo", "tienda", "sku", "resultado", "detalle", "nota", "creado_en"]],
        hide_index=True,
        column_config={"resultado": st.column_config.NumberColumn("Resultado", format="%.2f"),
                       "creado_en": "Fecha"},
    )

    # ---------- editar / eliminar ----------
    st.subheader("Editar o eliminar")
    opciones = {f"#{r['id']} · {r['tipo']} · {r['tienda']} · {r['sku']}": r for r in registros}
    elegido = opciones[st.selectbox("Elegí un análisis", list(opciones.keys()))]

    nota = st.text_area("Nota", value=elegido["nota"] or "", max_chars=300)
    col1, col2 = st.columns(2)
    if col1.button("💾 Guardar nota"):
        if crud.actualizar_nota(elegido["id"], usuario_id, nota.strip() or None):
            st.success("Nota actualizada")
            st.rerun()

    confirmar = col2.checkbox("Confirmo que quiero eliminarlo")
    if col2.button("🗑️ Eliminar", disabled=not confirmar):
        if crud.eliminar_analisis(elegido["id"], usuario_id):
            st.success("Análisis eliminado")
            st.rerun()


def resumir_detalle(detalle):
    # El detalle se guarda como JSON; se muestra como texto corto
    if not detalle:
        return ""
    try:
        datos = json.loads(detalle)
    except ValueError:
        return detalle
    return ", ".join(f"{k}: {v}" for k, v in datos.items())
