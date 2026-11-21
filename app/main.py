# Interfaz principal en Streamlit
# Ejecutar: streamlit run app/main.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from db.conexion import inicializar_db
from app.vistas import login, inicio, carga, pronostico, riesgo, historial

st.set_page_config(page_title="Plataforma de Abastecimiento", page_icon="📦", layout="wide")
inicializar_db()

from servicios import auth


def cerrar_sesion():
    st.session_state.token = None
    st.session_state.usuario = None
    st.session_state.usuario_id = None


if "token" not in st.session_state:
    cerrar_sesion()

# Si no hay sesion o el token vencio, solo se muestra el login
if not st.session_state.token or not auth.validar_token(st.session_state.token):
    if st.session_state.token:
        st.warning("Tu sesión expiró, volvé a iniciar sesión")
    cerrar_sesion()
    login.mostrar()
    st.stop()

vistas = {
    "Inicio": inicio,
    "Cargar datos": carga,
    "Pronóstico de demanda": pronostico,
    "Riesgo de quiebre": riesgo,
    "Historial": historial,
}

with st.sidebar:
    st.title("📦 Abastecimiento")
    st.caption(f"Usuario: {st.session_state.usuario}")
    opcion = st.radio("Menú", list(vistas.keys()))
    if st.button("Cerrar sesión"):
        cerrar_sesion()
        st.rerun()

vistas[opcion].mostrar()
