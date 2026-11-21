# Autenticacion: hash de claves con bcrypt y tokens JWT
# TODO (paso 3): implementar juntos


def generar_hash(clave):
    raise NotImplementedError


def verificar_clave(clave, clave_hash):
    raise NotImplementedError


def crear_token(usuario_id, usuario):
    raise NotImplementedError


def validar_token(token):
    raise NotImplementedError


def registrar(usuario, clave, nombre=None):
    raise NotImplementedError


def iniciar_sesion(usuario, clave):
    # Debe devolver un token si las credenciales son correctas, o None
    raise NotImplementedError
