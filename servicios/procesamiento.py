# Carga, limpieza y validacion de archivos CSV / Excel
# TODO (paso 4): implementar juntos

COLUMNAS_REQUERIDAS = ["fecha", "tienda", "sku", "unidades_vendidas", "inventario", "precio"]


def leer_archivo(archivo):
    # Recibe el archivo subido en Streamlit y devuelve un DataFrame
    raise NotImplementedError


def validar_columnas(df):
    raise NotImplementedError


def limpiar_datos(df):
    # Quitar duplicados, nulos, negativos, convertir fechas, etc.
    # Devuelve (df_limpio, resumen_de_cambios)
    raise NotImplementedError
