# Metodología y Pipeline de Auditoría (EDA)

## 1. Pre-procesamiento y carga

- **Microsoft:** Se cargan polígonos del GeoJSONL, cálculo de área reproyectando a EPSG:3116, parsing robusto y validación con Shapely.
- **Google:** Se cargan CSV.gz con polígonos en WKT, conversión automática a GeoJSON (Shapely), filtrado flexible por score de confianza.
- **Municipios PDET:** Importados desde backup_mongo para reproducibilidad en equipos sin acceso a DANE.

## 2. Validación y calidad

- Scripts para detectar y cuantificar geometrías inválidas, áreas nulas, y otros edge-cases.
- Muestras y agregados exportados para revisión manual y comparación visual.

## 3. Análisis Exploratorio (EDA)

- Notebook principal: `notebooks/03_buildings_eda.ipynb`
    - Conteos por municipio (spatial join).
    - Histogramas y heatmaps de densidad por área.
    - Comparación directa de conteos y área por PDET entre ambas fuentes.
    - Exportación de tablas comparativas para el reporte.

## 4. Reproducibilidad

- Todos los scripts aceptan argumentos y funcionan con batch processing. Parámetros de ejemplo incluidos en los README de cada script.
- Artefactos reproducibles: logs JSON/CSV, scripts y notebooks auto-contenidos.
- Scripts de respaldo/restauración para MongoDB en `backup_mongo/`.

---

> Para más detalles o instrucciones de ejecución, ver los archivos README de scripts (`src/data_loaders/`, `backup_mongo/`).
