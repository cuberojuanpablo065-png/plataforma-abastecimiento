import streamlit as st

import pandas as pd

from app.vistas.utilidades import a_hora_local
from config import RUTA_DATOS
from db import crud
from servicios import procesamiento


def mostrar():
    st.header("Cargar datos")
    st.write("Columnas necesarias: " + ", ".join(procesamiento.COLUMNAS_REQUERIDAS))

    archivo = st.file_uploader("Subí un archivo CSV o Excel", type=["csv", "xlsx"])
    if not archivo:
        mostrar_cargas_anteriores()
        return

    try:
        crudo = procesamiento.leer_archivo(archivo)
        limpio, resumen = procesamiento.limpiar_datos(crudo)
    except procesamiento.ErrorArchivo as e:
        st.error(str(e))
        return

    st.subheader("Resultado de la limpieza")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Filas originales", resumen["filas_originales"])
    col2.metric("Duplicados", resumen["duplicados"])
    col3.metric("Con datos vacíos", resumen["vacios"])
    col4.metric("Negativos", resumen["negativos"])
    st.success(f"Quedaron {resumen['filas_finales']} filas válidas")

    general = procesamiento.resumen_general(limpio)
    st.caption(f"{general['tiendas']} tiendas · {general['skus']} SKUs · "
               f"del {general['desde']} al {general['hasta']}")

    with st.expander("Ver datos limpios"):
        st.dataframe(limpio.head(100), width="stretch")

    if st.button("Guardar carga"):
        carga_id = crud.registrar_carga(
            st.session_state.usuario_id, archivo.name,
            resumen["filas_finales"], resumen["filas_descartadas"],
        )
        # Se guarda el archivo limpio para usarlo en las otras pantallas
        carpeta = RUTA_DATOS / "cargas"
        carpeta.mkdir(exist_ok=True)
        limpio.to_csv(carpeta / f"carga_{carga_id}.csv", index=False)

        st.session_state.datos = limpio
        st.session_state.carga_id = carga_id
        # Se borran resultados viejos que eran de otro archivo
        st.session_state.pop("evaluacion_riesgo", None)
        st.success("Carga guardada ✅")


def mostrar_cargas_anteriores():
    cargas = crud.listar_cargas(st.session_state.usuario_id)
    if cargas:
        st.subheader("Cargas anteriores")
        tabla = pd.DataFrame(cargas)
        tabla["creado_en"] = a_hora_local(tabla["creado_en"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(
            tabla[["nombre_archivo", "filas", "filas_descartadas", "creado_en"]].rename(columns={
                "nombre_archivo": "Archivo", "filas": "Filas",
                "filas_descartadas": "Descartadas", "creado_en": "Fecha"}),
            hide_index=True,
            width="stretch",
        )
