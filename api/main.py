# API propia con FastAPI: sirve los modelos entrenados
# Ejecutar: uvicorn api.main:app --reload
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="API Abastecimiento", version="0.1")


class EntradaPronostico(BaseModel):
    sku: str
    tienda: str
    semana: int
    precio: float


class EntradaRiesgo(BaseModel):
    sku: str
    tienda: str
    inventario: float
    venta_promedio_diaria: float


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/predecir/demanda")
def predecir_demanda(entrada: EntradaPronostico):
    # TODO (paso 6): cargar modelo y devolver prediccion
    raise HTTPException(status_code=501, detail="Pendiente de implementar")


@app.post("/predecir/riesgo")
def predecir_riesgo(entrada: EntradaRiesgo):
    # TODO (paso 6): cargar modelo y devolver probabilidad de quiebre
    raise HTTPException(status_code=501, detail="Pendiente de implementar")
