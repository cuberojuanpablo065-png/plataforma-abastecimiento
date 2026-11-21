# Operaciones CRUD sobre la base de datos
# TODO (paso 2): implementar juntos
from db.conexion import obtener_conexion


# ---------- usuarios ----------
def crear_usuario(usuario, clave_hash, nombre=None):
    raise NotImplementedError


def buscar_usuario(usuario):
    raise NotImplementedError


# ---------- cargas ----------
def registrar_carga(usuario_id, nombre_archivo, filas, filas_descartadas):
    raise NotImplementedError


def listar_cargas(usuario_id):
    raise NotImplementedError


# ---------- analisis ----------
def guardar_analisis(usuario_id, tipo, sku, tienda, resultado, detalle=None, carga_id=None):
    raise NotImplementedError


def listar_analisis(usuario_id, tipo=None):
    raise NotImplementedError


def actualizar_nota(analisis_id, usuario_id, nota):
    raise NotImplementedError


def eliminar_analisis(analisis_id, usuario_id):
    raise NotImplementedError
