import streamlit as st

from servicios import auth


def mostrar():
    st.title("📦 Plataforma de Abastecimiento")
    tab_entrar, tab_registro = st.tabs(["Iniciar sesión", "Registrarse"])

    with tab_entrar:
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            entrar = st.form_submit_button("Entrar")

        if entrar:
            token = auth.iniciar_sesion(usuario, clave)
            if token:
                datos = auth.validar_token(token)
                st.session_state.token = token
                st.session_state.usuario = datos["usuario"]
                st.session_state.usuario_id = int(datos["sub"])
                st.rerun()
            else:
                # Mismo mensaje para usuario o clave incorrectos, por seguridad
                st.error("Usuario o contraseña incorrectos")

    with tab_registro:
        with st.form("form_registro"):
            nombre = st.text_input("Nombre")
            usuario_nuevo = st.text_input("Usuario nuevo")
            clave_nueva = st.text_input("Contraseña nueva", type="password")
            confirmar = st.text_input("Confirmar contraseña", type="password")
            registrar = st.form_submit_button("Crear cuenta")

        if registrar:
            if clave_nueva != confirmar:
                st.error("Las contraseñas no coinciden")
            else:
                exito, mensaje = auth.registrar(usuario_nuevo, clave_nueva, nombre)
                if exito:
                    st.success(mensaje)
                else:
                    st.error(mensaje)
