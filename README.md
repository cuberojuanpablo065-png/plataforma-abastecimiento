# Plataforma de Abastecimiento Retail

Plataforma web para pronosticar la demanda y detectar el riesgo de quiebre de inventario por tienda y SKU, a partir de archivos de ventas e inventario.

Prueba de Suficiencia — Programación Web, LEAD University.

## Arquitectura

```
Streamlit (interfaz)  ──►  FastAPI (modelos)  ──►  modelos/artefactos/*.joblib
        │
        ├──►  SQLite (usuarios, cargas, análisis)
        └──►  API pública de tipo de cambio (USD → CRC)
```

## Estructura

```
plataforma-abastecimiento/
├── app/                 # Interfaz en Streamlit
│   ├── main.py          # Navegación y control de sesión
│   └── vistas/          # Una vista por pantalla
├── api/main.py          # API propia con FastAPI
├── db/                  # Esquema SQL, conexión y CRUD
├── servicios/           # Auth, procesamiento de archivos, tipo de cambio
├── modelos/             # Entrenamiento y artefactos de los modelos
├── datos/               # Generador de datos simulados
├── docs/                # Manual de uso
├── config.py
└── requirements.txt
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m datos.generar_datos    # genera los CSV simulados
python -m db.conexion           # crea la base de datos
```

## Ejecución

> En Windows se usa `python -m` para evitar que el sistema bloquee los `.exe` del entorno virtual.

En dos terminales distintas:

```bash
python -m uvicorn api.main:app --reload   # API en http://localhost:8000/docs
python -m streamlit run app/main.py       # App en http://localhost:8501
```

## Componentes

| Componente | Descripción |
|---|---|
| Autenticación | _pendiente_ |
| Carga de archivos | _pendiente_ |
| Modelo 1 — Pronóstico | _pendiente_ |
| Modelo 2 — Riesgo de quiebre | _pendiente_ |
| API propia | _pendiente_ |
| API externa | _pendiente_ |
| Base de datos | _pendiente_ |
| Visualizaciones | _pendiente_ |
