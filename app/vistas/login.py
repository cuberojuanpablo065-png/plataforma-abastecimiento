import streamlit as st


def mostrar():
    st.title("📦 Plataforma de Abastecimiento")
    tab_entrar, tab_registro = st.tabs(["Iniciar sesión", "Registrarse"])

    with tab_entrar:
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            entrar = st.form_submit_button("Entrar")
        if entrar:
            # TODO (paso 3): validar con servicios.auth.iniciar_sesion
            # Por ahora entra cualquiera para poder probar la navegacion
            st.session_state.token = "temporal"
            st.session_state.usuario = usuario or "demo"
            st.rerun()

    with tab_registro:
        with st.form("form_registro"):
            st.text_input("Nombre")
            st.text_input("Usuario nuevo")
            st.text_input("Contraseña nueva", type="password")
            registrar = st.form_submit_button("Crear cuenta")
        if registrar:
            st.info("Pendiente: registro de usuarios (paso 3)")
