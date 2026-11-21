# Operaciones CRUD sobre la base de datos
# C = crear, R = leer, U = actualizar, D = eliminar
import json

from db.conexion import obtener_conexion


# ---------- usuarios ----------
def crear_usuario(usuario, clave_hash, nombre=None):
    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            "INSERT INTO usuarios (usuario, clave_hash, nombre) VALUES (?, ?, ?)",
            (usuario, clave_hash, nombre),
        )
        return cursor.lastrowid


def buscar_usuario(usuario):
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()
        return dict(fila) if fila else None


# ---------- cargas ----------
def registrar_carga(usuario_id, nombre_archivo, filas, filas_descartadas):
    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            """INSERT INTO cargas (usuario_id, nombre_archivo, filas, filas_descartadas)
               VALUES (?, ?, ?, ?)""",
            (usuario_id, nombre_archivo, filas, filas_descartadas),
        )
        return cursor.lastrowid


def listar_cargas(usuario_id):
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            "SELECT * FROM cargas WHERE usuario_id = ? ORDER BY creado_en DESC",
            (usuario_id,),
        ).fetchall()
        return [dict(f) for f in filas]


# ---------- analisis ----------
def guardar_analisis(usuario_id, tipo, sku, tienda, resultado, detalle=None, carga_id=None):
    if tipo not in ("pronostico", "riesgo"):
        raise ValueError("El tipo debe ser 'pronostico' o 'riesgo'")

    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            """INSERT INTO analisis (usuario_id, carga_id, tipo, sku, tienda, resultado, detalle)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (usuario_id, carga_id, tipo, sku, tienda, resultado,
             json.dumps(detalle) if detalle else None),
        )
        return cursor.lastrowid


def listar_analisis(usuario_id, tipo=None):
    consulta = "SELECT * FROM analisis WHERE usuario_id = ?"
    parametros = [usuario_id]
    if tipo:
        consulta += " AND tipo = ?"
        parametros.append(tipo)
    consulta += " ORDER BY creado_en DESC, id DESC"

    with obtener_conexion() as conexion:
        filas = conexion.execute(consulta, parametros).fetchall()
        return [dict(f) for f in filas]


def actualizar_nota(analisis_id, usuario_id, nota):
    # Se filtra tambien por usuario para que nadie edite analisis ajenos
    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            "UPDATE analisis SET nota = ? WHERE id = ? AND usuario_id = ?",
            (nota, analisis_id, usuario_id),
        )
        return cursor.rowcount > 0


def eliminar_analisis(analisis_id, usuario_id):
    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            "DELETE FROM analisis WHERE id = ? AND usuario_id = ?",
            (analisis_id, usuario_id),
        )
        return cursor.rowcount > 0
