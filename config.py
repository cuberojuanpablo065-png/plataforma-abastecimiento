# Configuracion general del proyecto
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

RUTA_DB = RAIZ / "db" / "abastecimiento.db"
RUTA_ESQUEMA = RAIZ / "db" / "esquema.sql"
RUTA_ARTEFACTOS = RAIZ / "modelos" / "artefactos"
RUTA_DATOS = RAIZ / "datos"

# URL de nuestra API propia (FastAPI)
URL_API = os.getenv("URL_API", "http://127.0.0.1:8000")

# Clave para firmar los tokens JWT (en produccion va en una variable de entorno)
CLAVE_JWT = os.getenv("CLAVE_JWT", "clave-de-desarrollo-cambiar-en-produccion-2026")
MINUTOS_TOKEN = 60

# API externa publica de tipo de cambio
URL_TIPO_CAMBIO = "https://open.er-api.com/v6/latest/USD"
