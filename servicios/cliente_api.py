# Cliente para consumir nuestra API desde Streamlit
import requests

from config import URL_API

TIEMPO_ESPERA = 15


class ErrorAPI(Exception):
    pass


def _llamar(metodo, ruta, datos=None):
    try:
        respuesta = requests.request(metodo, f"{URL_API}{ruta}", json=datos, timeout=TIEMPO_ESPERA)
    except requests.ConnectionError:
        raise ErrorAPI("No se pudo conectar con la API. ¿Está corriendo uvicorn?")
    except requests.Timeout:
        raise ErrorAPI("La API tardó demasiado en responder")

    if respuesta.status_code != 200:
        try:
            detalle = respuesta.json().get("detail", respuesta.text)
        except ValueError:
            detalle = respuesta.text
        # FastAPI devuelve una lista cuando falla la validacion (error 422)
        if isinstance(detalle, list):
            detalle = "; ".join(d.get("msg", "") for d in detalle)
        raise ErrorAPI(f"Error {respuesta.status_code}: {detalle}")
    return respuesta.json()


def salud():
    return _llamar("GET", "/salud")


def metricas():
    return _llamar("GET", "/metricas")


def catalogo():
    return _llamar("GET", "/catalogo")


def predecir_demanda(tienda, sku, mes, precio, promocion):
    return _llamar("POST", "/predecir/demanda", {
        "tienda": tienda, "sku": sku, "mes": mes, "precio": precio, "promocion": promocion})


def predecir_riesgo(inventario, venta_promedio, mes, promocion):
    return _llamar("POST", "/predecir/riesgo", {
        "inventario": inventario, "venta_promedio": venta_promedio,
        "mes": mes, "promocion": promocion})


def predecir_riesgo_lote(registros):
    return _llamar("POST", "/predecir/riesgo/lote", registros)
