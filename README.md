# Plataforma de Abastecimiento Retail

Plataforma web para **pronosticar la demanda** y **detectar el riesgo de quiebre de inventario** por tienda y SKU, a partir de archivos de ventas e inventario.

Prueba de Suficiencia — Programación Web, LEAD University.
Autor: Juan Pablo Cubero

## Problema que resuelve

En el retail, quedarse sin producto en góndola (quiebre) significa venta perdida, y tener inventario de más significa capital inmovilizado. Esta plataforma permite a un analista:

1. Subir su archivo de ventas e inventario semanal.
2. Limpiarlo y validarlo automáticamente.
3. Estimar cuántas unidades se van a vender (modelo de regresión).
4. Identificar qué tiendas y productos tienen alto riesgo de quiebre (modelo de clasificación).
5. Guardar, consultar, comentar y eliminar sus análisis.

Los datos son **simulados** (ver `datos/generar_datos.py`), con estacionalidad, promociones y resurtidos incompletos.

## Arquitectura

```
┌──────────────────────┐   HTTP/JSON   ┌──────────────────────┐
│  Streamlit (app/)    │ ────────────► │  FastAPI (api/)      │
│  interfaz + login    │               │  sirve los modelos   │
└─────────┬────────────┘               └─────────┬────────────┘
          │                                      │
          ▼                                      ▼
┌──────────────────────┐               ┌──────────────────────┐
│  SQLite (db/)        │               │  modelos/artefactos/ │
│  usuarios, cargas,   │               │  *.joblib            │
│  análisis            │               └──────────────────────┘
└──────────────────────┘
          ▲
          │ HTTPS
┌──────────────────────┐
│  ExchangeRate-API    │  API pública: tipo de cambio USD → CRC
└──────────────────────┘
```

## Tecnologías

| Componente | Tecnología |
|---|---|
| Interfaz | Streamlit, Plotly |
| API propia | FastAPI, Uvicorn, Pydantic |
| Modelos | scikit-learn (Random Forest, regresión lineal y logística) |
| Base de datos | SQLite |
| Seguridad | bcrypt (hash de contraseñas), PyJWT (tokens de sesión) |
| Datos | pandas, NumPy, openpyxl |
| API externa | ExchangeRate-API (open.er-api.com) |

## Estructura

```
plataforma-abastecimiento/
├── app/
│   ├── main.py              # Navegación y control de sesión
│   └── vistas/              # Una pantalla por archivo
│       ├── login.py         # Inicio de sesión y registro
│       ├── inicio.py        # Resumen, tipo de cambio, estado de la API
│       ├── carga.py         # Subida y limpieza de archivos
│       ├── pronostico.py    # Modelo 1
│       ├── riesgo.py        # Modelo 2
│       ├── historial.py     # CRUD de análisis guardados
│       └── utilidades.py    # Funciones compartidas
├── api/main.py              # API propia con FastAPI
├── db/
│   ├── esquema.sql          # Definición de tablas
│   ├── conexion.py          # Conexión y creación de la base
│   └── crud.py              # Operaciones CRUD
├── servicios/
│   ├── auth.py              # bcrypt + JWT
│   ├── procesamiento.py     # Lectura, validación y limpieza
│   ├── cliente_api.py       # Consumo de la API propia
│   └── tipo_cambio.py       # Consumo de la API externa
├── modelos/
│   ├── entrenar.py          # Entrenamiento y comparación de modelos
│   └── artefactos/          # Modelos entrenados y métricas
├── datos/
│   ├── generar_datos.py     # Generador de datos simulados
│   ├── ventas_limpio.csv    # Datos para entrenar
│   └── ventas_ejemplo.csv   # Datos con errores para probar la limpieza
├── docs/
│   ├── manual_usuario.md
│   └── capturas/
├── config.py
└── requirements.txt
```

## Instalación

Requiere Python 3.11 o superior.

```bash
git clone https://github.com/cuberojuanpablo065-png/plataforma-abastecimiento.git
cd plataforma-abastecimiento

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Mac / Linux

pip install -r requirements.txt
python -m datos.generar_datos    # genera los CSV simulados
python -m db.conexion            # crea la base de datos
python -m modelos.entrenar       # entrena los modelos (~10 segundos)
```

## Ejecución

Se necesitan **dos terminales**, ambas con el entorno virtual activado:

```bash
# Terminal 1: API de modelos
python -m uvicorn api.main:app --reload
```

```bash
# Terminal 2: aplicación web
python -m streamlit run app/main.py
```

- Aplicación: http://localhost:8501
- Documentación interactiva de la API: http://localhost:8000/docs

> En Windows se usa `python -m` porque algunas políticas de seguridad bloquean los `.exe` del entorno virtual.

## Descripción técnica de los componentes

### 1. Interfaz web (Streamlit)
Navegación lateral con 5 pantallas. Usa formularios (`st.form`), carga de archivos, tablas interactivas y gráficos de Plotly (líneas, barras y mapa de calor). Cada pantalla vive en su propio archivo dentro de `app/vistas/`.

### 2. Autenticación (`servicios/auth.py`)
- Las contraseñas se guardan con **bcrypt**, que agrega una sal aleatoria; nunca se guarda la contraseña original.
- Al iniciar sesión se emite un **token JWT** firmado con HS256, que vence a los 60 minutos.
- `app/main.py` valida el token en cada interacción; si es inválido o venció, vuelve al login.
- Validaciones: mínimo 6 caracteres, usuario único, confirmación de contraseña y un mensaje genérico ante credenciales incorrectas.

### 3. Carga y procesamiento (`servicios/procesamiento.py`)
Acepta CSV y Excel (máximo 20 MB). Pasos de limpieza:
1. Normaliza nombres de columnas.
2. Valida columnas obligatorias: `fecha, tienda, sku, unidades_vendidas, inventario, precio`.
3. Elimina duplicados.
4. Convierte tipos (fechas y números); los valores inválidos quedan vacíos.
5. Elimina filas con datos vacíos.
6. Elimina valores negativos.

Muestra un resumen de cuántas filas se quitaron en cada paso. Con `ventas_ejemplo.csv`: 7,956 filas originales → 7,266 válidas.

### 4. Modelos (`modelos/entrenar.py`)
En cada caso se comparan dos algoritmos con una división 80/20 y se guarda el mejor.

**Modelo 1 — Pronóstico de demanda (regresión).**
Variables: tienda, SKU, mes, precio, promoción. Objetivo: unidades vendidas por semana.

| Algoritmo | MAE | R² |
|---|---|---|
| Regresión lineal | 5.51 | 0.764 |
| **Random Forest** ✅ | **5.12** | **0.773** |

**Modelo 2 — Riesgo de quiebre (clasificación).**
Variables: inventario, venta promedio de las 4 semanas anteriores, cobertura (inventario / venta promedio), promoción, mes. Objetivo: quiebre (sí/no).

| Algoritmo | Accuracy | Precision | Recall | F1 | AUC |
|---|---|---|---|---|---|
| Regresión logística | 0.873 | 0.463 | 0.876 | 0.606 | 0.940 |
| **Random Forest** ✅ | **0.906** | **0.552** | 0.812 | **0.657** | **0.955** |

Se elige por **F1** y no por accuracy porque solo el 11% de las semanas tienen quiebre (clases desbalanceadas). Se usa `class_weight="balanced"` para no ignorar la clase minoritaria.

### 5. API propia (`api/main.py`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/salud` | Estado de la API y de los modelos |
| GET | `/metricas` | Métricas del entrenamiento |
| GET | `/catalogo` | Tiendas y SKUs conocidos por el modelo |
| POST | `/predecir/demanda` | Unidades estimadas |
| POST | `/predecir/riesgo` | Probabilidad y nivel de quiebre |
| POST | `/predecir/riesgo/lote` | Evaluación masiva (máx. 5,000 registros) |

La validación de entradas se hace con Pydantic (por ejemplo, mes entre 1 y 12 y valores no negativos). Respuestas de error: 404 (tienda o SKU desconocido), 422 (dato inválido), 400 (lista vacía o demasiado grande), 503 (modelos no entrenados). Regla de negocio: con inventario 0 el riesgo es 100%.

### 6. API externa (`servicios/tipo_cambio.py`)
Consume ExchangeRate-API para obtener el tipo de cambio USD → CRC y mostrar la venta en dólares. Guarda el valor en caché por 1 hora; si la API falla, usa el último valor conocido o muestra "No disponible" sin romper la aplicación.

### 7. Base de datos (`db/`)
SQLite con tres tablas:
- `usuarios`: credenciales (hash) y nombre.
- `cargas`: archivos subidos por cada usuario.
- `analisis`: resultados de los modelos, con una nota editable.

CRUD completo en `db/crud.py`: crear (usuarios, cargas, análisis), leer (listar y buscar), actualizar (nota) y eliminar (análisis). Todas las consultas usan parámetros (`?`) para evitar inyección SQL, y las operaciones de edición y borrado filtran por `usuario_id`.

### 8. Visualización
- Pronóstico de los 12 meses con y sin promoción, comparado con el histórico real.
- Mapa de calor de probabilidad de quiebre por tienda y SKU.
- Riesgo promedio por tienda.
- Comparación de métricas entre algoritmos.
- Historial de análisis por día.

## Manual de uso

Ver [docs/manual_usuario.md](docs/manual_usuario.md).

## Créditos

Tasas de cambio por [ExchangeRate-API](https://www.exchangerate-api.com).
