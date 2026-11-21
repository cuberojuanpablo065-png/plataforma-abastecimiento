# Carga, limpieza y validacion de archivos CSV / Excel
import pandas as pd

COLUMNAS_REQUERIDAS = ["fecha", "tienda", "sku", "unidades_vendidas", "inventario", "precio"]
COLUMNAS_NUMERICAS = ["unidades_vendidas", "inventario", "precio"]
TAMANO_MAXIMO_MB = 20


class ErrorArchivo(Exception):
    # Error controlado para mostrarle al usuario un mensaje claro
    pass


def leer_archivo(archivo):
    # Recibe el archivo subido en Streamlit y devuelve un DataFrame
    if archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024:
        raise ErrorArchivo(f"El archivo pesa más de {TAMANO_MAXIMO_MB} MB")

    nombre = archivo.name.lower()
    try:
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo)
        elif nombre.endswith((".xlsx", ".xls")):
            df = pd.read_excel(archivo)
        else:
            raise ErrorArchivo("Formato no soportado, subí un CSV o Excel")
    except ErrorArchivo:
        raise
    except pd.errors.EmptyDataError:
        raise ErrorArchivo("El archivo está vacío")
    except Exception as e:
        raise ErrorArchivo(f"No se pudo leer el archivo: {e}")

    if df.empty:
        raise ErrorArchivo("El archivo está vacío")
    return df


def normalizar_columnas(df):
    # "Unidades Vendidas " -> "unidades_vendidas"
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def validar_columnas(df):
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ErrorArchivo("Faltan columnas: " + ", ".join(faltantes))


def limpiar_datos(df):
    # Devuelve (df_limpio, resumen) con cuantas filas se quitaron en cada paso
    resumen = {"filas_originales": len(df)}
    df = normalizar_columnas(df)
    validar_columnas(df)

    # 1. Duplicados exactos
    antes = len(df)
    df = df.drop_duplicates()
    resumen["duplicados"] = antes - len(df)

    # 2. Convertir tipos (lo que no se pueda convertir queda vacio)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    for columna in COLUMNAS_NUMERICAS:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
    df["tienda"] = df["tienda"].astype(str).str.strip().str.upper()
    df["sku"] = df["sku"].astype(str).str.strip().str.upper()

    # 3. Filas con datos vacios en columnas clave
    antes = len(df)
    df = df.dropna(subset=COLUMNAS_REQUERIDAS)
    resumen["vacios"] = antes - len(df)

    # 4. Valores negativos (no tienen sentido en ventas, inventario o precio)
    antes = len(df)
    df = df[(df[COLUMNAS_NUMERICAS] >= 0).all(axis=1)]
    resumen["negativos"] = antes - len(df)

    # Columna opcional: si no viene promocion se asume 0
    if "promocion" not in df.columns:
        df["promocion"] = 0
    df["promocion"] = pd.to_numeric(df["promocion"], errors="coerce").fillna(0).astype(int)

    df = df.sort_values(["tienda", "sku", "fecha"]).reset_index(drop=True)
    resumen["filas_finales"] = len(df)
    resumen["filas_descartadas"] = resumen["filas_originales"] - len(df)

    if df.empty:
        raise ErrorArchivo("Después de limpiar no quedó ninguna fila válida")
    return df, resumen


def resumen_general(df):
    # Datos rapidos para mostrar despues de la carga
    return {
        "tiendas": df["tienda"].nunique(),
        "skus": df["sku"].nunique(),
        "desde": df["fecha"].min().date(),
        "hasta": df["fecha"].max().date(),
        "unidades": int(df["unidades_vendidas"].sum()),
    }
