# Entrenamiento de los dos modelos y guardado en modelos/artefactos/
#  1. Regresion: pronostico de unidades vendidas por SKU/tienda
#  2. Clasificacion: riesgo de quiebre de inventario (si / no)
# Ejecutar: python -m modelos.entrenar
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                             precision_score, r2_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import RUTA_ARTEFACTOS, RUTA_DATOS

SEMILLA = 42

COLUMNAS_PRONOSTICO = ["tienda", "sku", "mes", "precio", "promocion"]
COLUMNAS_RIESGO = ["inventario", "venta_promedio", "cobertura", "promocion", "mes"]


# ---------- preparacion de variables ----------
def preparar_pronostico(df):
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.month
    return df[COLUMNAS_PRONOSTICO], df["unidades_vendidas"]


def preparar_riesgo(df):
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values(["tienda", "sku", "fecha"])
    df["mes"] = df["fecha"].dt.month

    # Promedio de las 4 semanas ANTERIORES (shift evita usar la semana actual)
    df["venta_promedio"] = (df.groupby(["tienda", "sku"])["unidades_vendidas"]
                              .transform(lambda s: s.shift(1).rolling(4, min_periods=1).mean()))
    df = df.dropna(subset=["venta_promedio"])

    # Cuantas semanas alcanza el inventario
    df["cobertura"] = df["inventario"] / df["venta_promedio"].replace(0, np.nan)
    df["cobertura"] = df["cobertura"].fillna(10).clip(upper=10)

    # Hay quiebre si se vendio todo lo que habia
    df["quiebre"] = (df["unidades_vendidas"] >= df["inventario"]).astype(int)
    return df[COLUMNAS_RIESGO], df["quiebre"]


# ---------- modelo 1: pronostico ----------
def entrenar_pronostico(df):
    X, y = preparar_pronostico(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEMILLA)

    transformador = ColumnTransformer([
        ("categorias", OneHotEncoder(handle_unknown="ignore"), ["tienda", "sku", "mes"]),
        ("numeros", StandardScaler(), ["precio", "promocion"]),
    ])
    candidatos = {
        "Regresión lineal": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=3,
                                               random_state=SEMILLA, n_jobs=-1),
    }

    resultados = {}
    mejor_nombre, mejor_modelo = None, None
    for nombre, algoritmo in candidatos.items():
        modelo = Pipeline([("prep", transformador), ("modelo", algoritmo)])
        modelo.fit(X_train, y_train)
        prediccion = modelo.predict(X_test)
        resultados[nombre] = {
            "mae": round(mean_absolute_error(y_test, prediccion), 2),
            "r2": round(r2_score(y_test, prediccion), 3),
        }
        # Gana el de menor error absoluto medio
        if mejor_nombre is None or resultados[nombre]["mae"] < resultados[mejor_nombre]["mae"]:
            mejor_nombre, mejor_modelo = nombre, modelo

    return mejor_modelo, {"elegido": mejor_nombre, "comparacion": resultados,
                          "filas_entrenamiento": len(X_train), "filas_prueba": len(X_test)}


# ---------- modelo 2: riesgo de quiebre ----------
def entrenar_riesgo(df):
    X, y = preparar_riesgo(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEMILLA, stratify=y)

    candidatos = {
        "Regresión logística": Pipeline([
            ("escala", StandardScaler()),
            ("modelo", LogisticRegression(class_weight="balanced", max_iter=1000)),
        ]),
        "Random Forest": Pipeline([
            ("modelo", RandomForestClassifier(n_estimators=200, min_samples_leaf=5,
                                              class_weight="balanced",
                                              random_state=SEMILLA, n_jobs=-1)),
        ]),
    }

    resultados = {}
    mejor_nombre, mejor_modelo = None, None
    for nombre, modelo in candidatos.items():
        modelo.fit(X_train, y_train)
        prediccion = modelo.predict(X_test)
        probabilidad = modelo.predict_proba(X_test)[:, 1]
        resultados[nombre] = {
            "accuracy": round(accuracy_score(y_test, prediccion), 3),
            "precision": round(precision_score(y_test, prediccion), 3),
            "recall": round(recall_score(y_test, prediccion), 3),
            "f1": round(f1_score(y_test, prediccion), 3),
            "auc": round(roc_auc_score(y_test, probabilidad), 3),
        }
        # Gana el de mejor F1 (balancea no fallar quiebres y no dar falsas alarmas)
        if mejor_nombre is None or resultados[nombre]["f1"] > resultados[mejor_nombre]["f1"]:
            mejor_nombre, mejor_modelo = nombre, modelo

    return mejor_modelo, {"elegido": mejor_nombre, "comparacion": resultados,
                          "porcentaje_quiebres": round(y.mean(), 3),
                          "filas_entrenamiento": len(X_train), "filas_prueba": len(X_test)}


if __name__ == "__main__":
    RUTA_ARTEFACTOS.mkdir(parents=True, exist_ok=True)
    datos = pd.read_csv(RUTA_DATOS / "ventas_limpio.csv")

    modelo_pronostico, metricas_pronostico = entrenar_pronostico(datos)
    modelo_riesgo, metricas_riesgo = entrenar_riesgo(datos)

    joblib.dump(modelo_pronostico, RUTA_ARTEFACTOS / "modelo_pronostico.joblib")
    joblib.dump(modelo_riesgo, RUTA_ARTEFACTOS / "modelo_riesgo.joblib")

    metricas = {"pronostico": metricas_pronostico, "riesgo": metricas_riesgo}
    with open(RUTA_ARTEFACTOS / "metricas.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)

    print(json.dumps(metricas, ensure_ascii=False, indent=2))
