# Manual de uso básico

Antes de empezar, la API y la aplicación deben estar corriendo (ver "Ejecución" en el README).

## 1. Crear una cuenta e iniciar sesión
1. Abrí http://localhost:8501.
2. En la pestaña **Registrarse**, escribí tu nombre, un usuario y una contraseña de al menos 6 caracteres, y confirmala.
3. Pasá a **Iniciar sesión** y entrá con ese usuario.

La sesión dura 60 minutos. Para salir, usá **Cerrar sesión** en el menú lateral.

## 2. Inicio
Muestra cuántos archivos cargaste, cuántos análisis de riesgo guardaste, el tipo de cambio del día, la venta del archivo actual en colones y dólares, y si la API de modelos está conectada.

## 3. Cargar datos
1. Andá a **Cargar datos**.
2. Subí un archivo CSV o Excel con las columnas `fecha, tienda, sku, unidades_vendidas, inventario, precio` (y opcionalmente `promocion`). Para probar podés usar `datos/ventas_ejemplo.csv`.
3. Revisá el resumen de la limpieza: duplicados, datos vacíos y negativos eliminados.
4. Clic en **Guardar carga**.

## 4. Pronóstico de demanda
1. Andá a **Pronóstico de demanda**.
2. Elegí tienda, SKU, mes, precio y si hay promoción.
3. Clic en **Pronosticar**. Vas a ver las unidades estimadas por semana y por mes, la venta estimada y un gráfico del año completo comparado con el histórico real.
4. Si querés conservarlo, clic en **Guardar pronóstico**.

En **¿Qué tan bueno es el modelo?** se ven las métricas de los algoritmos comparados.

## 5. Riesgo de quiebre
**Evaluar el archivo cargado:**
1. Andá a **Riesgo de quiebre** → pestaña **Evaluar archivo cargado**.
2. Clic en **Evaluar riesgo**.
3. Revisá el conteo por nivel (alto, medio y bajo), el mapa de calor, el riesgo por tienda y la tabla de detalle.
4. Opcional: guardá los casos de riesgo alto en el historial.

**Consulta individual:** en la pestaña **Consulta individual**, ingresá el inventario, la venta promedio, el mes y la promoción, y luego **Calcular riesgo**. La consulta se guarda sola en el historial.

Niveles: **alto** (60% o más), **medio** (de 30% a 60%), **bajo** (menos de 30%).

## 6. Historial
1. Andá a **Historial** y filtrá por tipo si querés.
2. Para **editar**: elegí un análisis, escribí una nota y clic en **Guardar nota**.
3. Para **eliminar**: elegí un análisis, marcá la confirmación y clic en **Eliminar**.

## Mensajes comunes

| Mensaje | Qué hacer |
|---|---|
| "No se pudo conectar con la API" | Encender la API: `python -m uvicorn api.main:app --reload` |
| "Modelos no entrenados" | Ejecutar `python -m modelos.entrenar` |
| "Faltan columnas: …" | Revisar que el archivo tenga las columnas obligatorias |
| "Tu sesión expiró" | Volver a iniciar sesión |
| Tipo de cambio "No disponible" | Sin internet o la API externa no respondió; el resto funciona igual |

## Capturas de pantalla

Están en la carpeta `docs/capturas`:

| Archivo | Pantalla |
|---|---|
| `Screenshot 2026-11-22 183055.png` | Inicio de sesión |
| `Screenshot 2026-11-22 180719.png` | Inicio (tipo de cambio y estado de la API) |
| `Screenshot 2026-11-22 181029.png` | Formulario de pronóstico |
| `Screenshot 2026-11-22 181121.png` | Resultado y gráfico del pronóstico |
| `Screenshot 2026-11-22 181238.png` | Riesgo promedio por tienda |
| `Screenshot 2026-11-22 181230.png` | Detalle de riesgo de quiebre |
| `Screenshot 2026-11-22 182251.png` | Historial de análisis |
