# Genera un CSV simulado de ventas e inventario por tienda y SKU
# Ejecutar: python -m datos.generar_datos
import numpy as np
import pandas as pd

from config import RUTA_DATOS

CATEGORIAS = ["Shampoo", "Acondicionador", "Jabón", "Crema corporal", "Desodorante"]


def crear_catalogo(skus, rng):
    # Cada SKU tiene categoria, precio y una venta base semanal
    catalogo = []
    for i in range(skus):
        catalogo.append({
            "sku": f"SKU-{i + 1:03d}",
            "categoria": CATEGORIAS[i % len(CATEGORIAS)],
            "precio_base": round(rng.uniform(1200, 4500), -1),
            "venta_base": rng.uniform(8, 40),
        })
    return catalogo


def factor_estacional(fecha):
    # Diciembre sube, febrero baja, el resto normal
    if fecha.month == 12:
        return 1.5
    if fecha.month == 2:
        return 0.85
    return 1.0


def generar(semanas=52, tiendas=10, skus=15, semilla=42):
    rng = np.random.default_rng(semilla)
    catalogo = crear_catalogo(skus, rng)
    lista_tiendas = [f"T{t + 1:02d}" for t in range(tiendas)]
    tamano_tienda = {t: rng.uniform(0.6, 1.6) for t in lista_tiendas}
    fechas = pd.date_range("2025-01-06", periods=semanas, freq="W-MON")

    filas = []
    for tienda in lista_tiendas:
        for producto in catalogo:
            # Inventario objetivo: unas 2 semanas de venta
            objetivo = producto["venta_base"] * tamano_tienda[tienda] * 2
            inventario = objetivo

            for fecha in fechas:
                promocion = rng.random() < 0.10
                precio = producto["precio_base"] * (0.85 if promocion else 1.0)

                demanda = (producto["venta_base"] * tamano_tienda[tienda]
                           * factor_estacional(fecha)
                           * (1.4 if promocion else 1.0)
                           * rng.normal(1, 0.2))
                demanda = max(0, round(demanda))

                # No se puede vender mas de lo que hay
                vendidas = min(demanda, round(inventario))

                filas.append({
                    "fecha": fecha.date(),
                    "tienda": tienda,
                    "sku": producto["sku"],
                    "categoria": producto["categoria"],
                    "precio": round(precio, 2),
                    "promocion": int(promocion),
                    "inventario": round(inventario),
                    "unidades_vendidas": vendidas,
                })

                # Resurtido: a veces llega incompleto
                inventario = inventario - vendidas
                faltante = max(0, objetivo - inventario)
                cumplimiento = rng.choice([1.0, 0.6, 0.3], p=[0.6, 0.25, 0.15])
                inventario = inventario + faltante * cumplimiento

    return pd.DataFrame(filas)


def ensuciar(df, rng, porcentaje=0.02):
    # Mete errores a proposito para practicar la limpieza en el paso 4
    df = df.copy()
    n = int(len(df) * porcentaje)

    # Celdas vacias
    for columna in ["unidades_vendidas", "precio", "inventario"]:
        indices = rng.choice(df.index, n, replace=False)
        df.loc[indices, columna] = np.nan

    # Valores negativos
    indices = rng.choice(df.index, n // 2, replace=False)
    df.loc[indices, "unidades_vendidas"] = -df.loc[indices, "unidades_vendidas"]

    # Filas duplicadas
    duplicadas = df.sample(n, random_state=1)
    df = pd.concat([df, duplicadas]).sample(frac=1, random_state=2).reset_index(drop=True)
    return df


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    datos = generar()

    RUTA_DATOS.mkdir(exist_ok=True)
    datos.to_csv(RUTA_DATOS / "ventas_limpio.csv", index=False)
    ensuciar(datos, rng).to_csv(RUTA_DATOS / "ventas_ejemplo.csv", index=False)

    quiebres = (datos["unidades_vendidas"] == datos["inventario"]).mean()
    print(f"Filas generadas: {len(datos)}")
    print(f"Semanas con quiebre: {quiebres:.1%}")
    print("Archivos: datos/ventas_limpio.csv y datos/ventas_ejemplo.csv")
