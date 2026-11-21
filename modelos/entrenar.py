# Entrenamiento de los dos modelos y guardado en modelos/artefactos/
#  1. Regresion: pronostico de demanda semanal por SKU/tienda
#  2. Clasificacion: riesgo de quiebre de inventario (si / no)
# TODO (paso 5): implementar juntos
from config import RUTA_ARTEFACTOS, RUTA_DATOS


def entrenar_pronostico(df):
    raise NotImplementedError


def entrenar_riesgo(df):
    raise NotImplementedError


if __name__ == "__main__":
    RUTA_ARTEFACTOS.mkdir(parents=True, exist_ok=True)
    print("Pendiente: entrenar modelos")
