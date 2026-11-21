# Conexion a SQLite y creacion de tablas
import sqlite3

from config import RUTA_DB, RUTA_ESQUEMA


def obtener_conexion():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_db():
    with obtener_conexion() as conexion:
        conexion.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))


if __name__ == "__main__":
    inicializar_db()
    print(f"Base de datos lista en {RUTA_DB}")
