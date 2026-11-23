# Consumo de API externa publica: tipo de cambio USD -> CRC
# Fuente: ExchangeRate-API (https://www.exchangerate-api.com), sin API key
import time

import requests

from config import URL_TIPO_CAMBIO

TIEMPO_ESPERA = 10
DURACION_CACHE = 3600  # la API se actualiza 1 vez al dia, no hace falta llamarla seguido

_cache = {"valor": None, "fecha": None, "guardado_en": 0}


def obtener_tipo_cambio():
    # Devuelve {"valor": colones por dolar, "fecha": ultima actualizacion}
    # o None si la API no responde
    if _cache["valor"] and time.time() - _cache["guardado_en"] < DURACION_CACHE:
        return {"valor": _cache["valor"], "fecha": _cache["fecha"]}

    try:
        respuesta = requests.get(URL_TIPO_CAMBIO, timeout=TIEMPO_ESPERA)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except (requests.RequestException, ValueError):
        return ultimo_valor_conocido()

    # Validar que la respuesta tenga lo que esperamos
    if datos.get("result") != "success":
        return ultimo_valor_conocido()
    valor = datos.get("rates", {}).get("CRC")
    if not isinstance(valor, (int, float)) or valor <= 0:
        return ultimo_valor_conocido()

    _cache.update(valor=round(valor, 2), fecha=datos.get("time_last_update_utc"),
                  guardado_en=time.time())
    return {"valor": _cache["valor"], "fecha": _cache["fecha"]}


def ultimo_valor_conocido():
    # Si la API falla pero ya habiamos consultado antes, se usa ese valor
    if _cache["valor"]:
        return {"valor": _cache["valor"], "fecha": _cache["fecha"], "desactualizado": True}
    return None


def colones_a_dolares(monto_colones, tipo_cambio):
    if not tipo_cambio:
        return None
    return round(monto_colones / tipo_cambio, 2)
