# API propia con FastAPI: sirve los modelos entrenados
# Ejecutar: python -m uvicorn api.main:app --reload
# Documentacion interactiva: http://localhost:8000/docs
import json

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import RUTA_ARTEFACTOS

app = FastAPI(title="API Abastecimiento", version="1.0",
              description="Pronóstico de demanda y riesgo de quiebre de inventario")

modelos = {}


def cargar_modelos():
    # Se cargan una sola vez y quedan en memoria
    if not modelos:
        try:
            modelos["pronostico"] = joblib.load(RUTA_ARTEFACTOS / "modelo_pronostico.joblib")
            modelos["riesgo"] = joblib.load(RUTA_ARTEFACTOS / "modelo_riesgo.joblib")
        except FileNotFoundError:
            raise HTTPException(status_code=503,
                                detail="Modelos no entrenados, ejecutá: python -m modelos.entrenar")
    return modelos


def categorias_conocidas():
    # Tiendas y SKUs que el modelo vio durante el entrenamiento
    codificador = cargar_modelos()["pronostico"].named_steps["prep"].named_transformers_["categorias"]
    return {"tiendas": list(codificador.categories_[0]), "skus": list(codificador.categories_[1])}


# ---------- esquemas de entrada (validacion automatica) ----------
class EntradaPronostico(BaseModel):
    tienda: str = Field(examples=["T01"])
    sku: str = Field(examples=["SKU-001"])
    mes: int = Field(ge=1, le=12, examples=[12])
    precio: float = Field(gt=0, examples=[3500])
    promocion: bool = False


class EntradaRiesgo(BaseModel):
    inventario: float = Field(ge=0, examples=[20])
    venta_promedio: float = Field(ge=0, description="Venta semanal promedio de las últimas 4 semanas",
                                  examples=[25])
    mes: int = Field(ge=1, le=12, examples=[12])
    promocion: bool = False


# ---------- funciones de prediccion ----------
def calcular_cobertura(inventario, venta_promedio):
    # Igual que en el entrenamiento: maximo 10 semanas
    if inventario == 0:
        return 0.0
    if venta_promedio == 0:
        return 10.0
    return min(inventario / venta_promedio, 10.0)


def nivel_riesgo(probabilidad):
    if probabilidad >= 0.6:
        return "alto"
    if probabilidad >= 0.3:
        return "medio"
    return "bajo"


def predecir_riesgo_varios(entradas):
    filas = [{
        "inventario": e.inventario,
        "venta_promedio": e.venta_promedio,
        "cobertura": calcular_cobertura(e.inventario, e.venta_promedio),
        "promocion": int(e.promocion),
        "mes": e.mes,
    } for e in entradas]
    probabilidades = cargar_modelos()["riesgo"].predict_proba(pd.DataFrame(filas))[:, 1]

    # Regla de negocio: sin inventario el quiebre es seguro
    # (el modelo nunca vio inventario 0 en el entrenamiento)
    probabilidades = [1.0 if f["inventario"] == 0 else p for p, f in zip(probabilidades, filas)]

    return [{
        "probabilidad_quiebre": round(float(p), 3),
        "nivel": nivel_riesgo(p),
        "cobertura_semanas": round(f["cobertura"], 2),
    } for p, f in zip(probabilidades, filas)]


# ---------- endpoints ----------
@app.get("/salud")
def salud():
    entrenados = (RUTA_ARTEFACTOS / "modelo_pronostico.joblib").exists()
    return {"estado": "ok", "modelos_entrenados": entrenados}


@app.get("/metricas")
def metricas():
    ruta = RUTA_ARTEFACTOS / "metricas.json"
    if not ruta.exists():
        raise HTTPException(status_code=503, detail="Todavía no hay métricas")
    return json.loads(ruta.read_text(encoding="utf-8"))


@app.get("/catalogo")
def catalogo():
    return categorias_conocidas()


@app.post("/predecir/demanda")
def predecir_demanda(entrada: EntradaPronostico):
    tienda = entrada.tienda.strip().upper()
    sku = entrada.sku.strip().upper()

    conocidas = categorias_conocidas()
    if tienda not in conocidas["tiendas"]:
        raise HTTPException(status_code=404, detail=f"Tienda desconocida: {tienda}")
    if sku not in conocidas["skus"]:
        raise HTTPException(status_code=404, detail=f"SKU desconocido: {sku}")

    datos = pd.DataFrame([{"tienda": tienda, "sku": sku, "mes": entrada.mes,
                           "precio": entrada.precio, "promocion": int(entrada.promocion)}])
    unidades = float(cargar_modelos()["pronostico"].predict(datos)[0])

    return {"tienda": tienda, "sku": sku, "mes": entrada.mes,
            "unidades_estimadas": round(max(unidades, 0), 1)}


@app.post("/predecir/riesgo")
def predecir_riesgo(entrada: EntradaRiesgo):
    return predecir_riesgo_varios([entrada])[0]


@app.post("/predecir/riesgo/lote")
def predecir_riesgo_lote(entradas: list[EntradaRiesgo]):
    # Para evaluar muchas tiendas/SKUs de una sola vez
    if not entradas:
        raise HTTPException(status_code=400, detail="La lista está vacía")
    if len(entradas) > 5000:
        raise HTTPException(status_code=400, detail="Máximo 5000 registros por solicitud")
    return predecir_riesgo_varios(entradas)
