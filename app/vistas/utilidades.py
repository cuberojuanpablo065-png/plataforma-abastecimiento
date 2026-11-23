# Funciones compartidas entre pantallas
import pandas as pd
import streamlit as st

from config import RUTA_DATOS
from db import crud

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
COLORES_RIESGO = {"alto": "#d62728", "medio": "#ff7f0e", "bajo": "#2ca02c"}
ZONA_HORARIA = "America/Costa_Rica"


def obtener_datos_actuales():
    # Usa los datos de la sesion; si no hay, carga la ultima carga guardada del usuario
    if "datos" in st.session_state:
        return st.session_state.datos

    for carga in crud.listar_cargas(st.session_state.usuario_id):
        ruta = RUTA_DATOS / "cargas" / f"carga_{carga['id']}.csv"
        if ruta.exists():
            datos = pd.read_csv(ruta, parse_dates=["fecha"])
            st.session_state.datos = datos
            st.session_state.carga_id = carga["id"]
            return datos
    return None


def a_hora_local(fechas):
    # SQLite guarda la hora en UTC; se convierte a la hora de Costa Rica para mostrarla
    return (pd.to_datetime(fechas).dt.tz_localize("UTC")
              .dt.tz_convert(ZONA_HORARIA).dt.tz_localize(None))
