# Autenticacion: hash de claves con bcrypt y tokens JWT
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import CLAVE_JWT, MINUTOS_TOKEN
from db import crud

LARGO_MINIMO_CLAVE = 6


def generar_hash(clave):
    # bcrypt agrega una "sal" aleatoria, asi dos claves iguales dan hashes distintos
    return bcrypt.hashpw(clave.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_clave(clave, clave_hash):
    return bcrypt.checkpw(clave.encode("utf-8"), clave_hash.encode("utf-8"))


def crear_token(usuario_id, usuario):
    expira = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_TOKEN)
    datos = {"sub": str(usuario_id), "usuario": usuario, "exp": expira}
    return jwt.encode(datos, CLAVE_JWT, algorithm="HS256")


def validar_token(token):
    # Devuelve los datos del token, o None si es invalido o ya vencio
    try:
        return jwt.decode(token, CLAVE_JWT, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


def registrar(usuario, clave, nombre=None):
    # Devuelve (exito, mensaje)
    usuario = (usuario or "").strip().lower()

    if not usuario or not clave:
        return False, "Usuario y contraseña son obligatorios"
    if len(clave) < LARGO_MINIMO_CLAVE:
        return False, f"La contraseña debe tener al menos {LARGO_MINIMO_CLAVE} caracteres"
    if crud.buscar_usuario(usuario):
        return False, "Ese usuario ya existe"

    crud.crear_usuario(usuario, generar_hash(clave), nombre)
    return True, "Cuenta creada, ya podés iniciar sesión"


def iniciar_sesion(usuario, clave):
    # Devuelve un token si las credenciales son correctas, o None
    usuario = (usuario or "").strip().lower()
    datos = crud.buscar_usuario(usuario)

    if not datos or not clave or not verificar_clave(clave, datos["clave_hash"]):
        return None
    return crear_token(datos["id"], datos["usuario"])
