# Entregable 3: Integración y Auditoría de Edificaciones (Microsoft & Google)

Este entregable documenta la integración en MongoDB y la auditoría inicial (EDA) de las huellas de edificios de Microsoft Building Footprints y Google Open Buildings, enfocado en los municipios PDET de Colombia.

**Contenido:**
- [Metodología reproductible](#metodología-reproductible)
- [Documentación de ingesta y filtrados](#documentación-de-ingesta-y-filtrado-de-datos)
- [Guía de ejecución y descarga de datos](#guía-de-ejecución-y-descarga-de-datos)
- [Carga eficiente y scripts usados](#carga-eficiente-de-datos)
- [EDA inicial y validación](#eda-inicial)
- [Instrucciones técnicas y reproducibilidad](#instrucciones-técnicas)

---

## Metodología Reproductible
- Pre-procesamiento de datos: filtros, validaciones y conversión de geometrías de DANE, Microsoft y Google.
- Uso de bases NoSQL (MongoDB 5+) con indexación espacial.
- Validaciones y métricas de calidad integradas vía scripts de Python.

### Fuentes de Datos
- Microsoft Building Footprints (GeoJSONL)
- Google Open Buildings (CSV.gz/WKT)
- DANE MGN y lista PDET para fronteras municipales

---

## Documentación de Ingesta y Filtrado de Datos

### Microsoft Building Footprints
**Script:** `src/data_loaders/load_microsoft_buildings.py`
- Lee el archivo `GeoJSONL` en `data/raw/microsoft/Colombia.geojsonl`. Descarga oficial:
  - Repositorio: https://github.com/microsoft/SouthAmericaBuildingFootprints
  - Descarga directa Colombia: https://minedbuildings.z5.web.core.windows.net/legacy/southamerica/Colombia.geojsonl.zip
- Procesamiento en lotes (`batch_size`, default 10,000). Calcula área reproyectando a EPSG:3116.
- Argumentos CLI: `--batch-size`, `--collection`, `--drop`.

### Google Open Buildings
**Script:** `src/data_loaders/load_google_buildings.py`
- Lee el archivo CSV comprimido en gzip: `data/raw/google/google_buildings/open_buildings_v3_polygons_ne_110m_COL.csv.gz`.
- Descarga recomendada:
  - Desde Google Open Buildings v3: https://sites.research.google/gr/open-buildings/
  - Utilizando el notebook de Colab: https://colab.research.google.com/github/google-research/google-research/blob/master/building_detection/open_buildings_download_region_polygons.ipynb
- Argumentos CLI: `--batch-size`, `--collection`, `--drop`, `--min-confidence` (para filtro de confianza)

---

## Guía de Ejecución y Descarga de Datos

### 1. Descarga y preparación de archivos brutos
- **Microsoft:** Descarga y descomprime `Colombia.geojsonl.zip` en `data/raw/microsoft/Colombia.geojsonl`.
- **Google:** Descarga y mueve el archivo `.csv.gz` a `data/raw/google/google_buildings/open_buildings_v3_polygons_ne_110m_COL.csv.gz`.
- **Requisitos:**
  - Espacio en disco: 1-2 GB por dataset.
  - Suficiente RAM (para batch processing y validación espacial).
  - MongoDB en ejecución y acceso de escritura.

### 2. Ejecución de scripts de carga

#### Cargar Microsoft Buildings:
```bash
python src/data_loaders/load_microsoft_buildings.py --batch-size 10000 --collection microsoft_buildings --drop
```
- Inserta los 6M+ edificios. El log se guarda en `/logs/microsoft_buildings_load.log`.

#### Cargar Google Open Buildings:
```bash
python src/data_loaders/load_google_buildings.py --batch-size 10000 --collection google_buildings --drop --min-confidence 0.65
```
- El argumento `--min-confidence` permite filtrar por calidad (ej. usar 0.80 para solo edificios de confianza alta).
- El log se guarda en `/logs/google_buildings_load.log`.

### 3. Consideraciones y advertencias
- Tener directorios y datos en las rutas esperadas.
- El proceso puede tomar entre 15-40 minutos según recursos y tamaño de los archivos.
- Para iniciar MongoDB:
  - Linux/Mac: `sudo systemctl start mongod`
  - Windows: Iniciar servicio MongoDB o usar MongoDB Compass.
- Los logs y estadísticas de ejecución ayudan a auditar los procesos y reproducir los resultados.

---

## Carga Eficiente de Datos
- Todos los scripts aceptan argumentos y procesan los datos en batch.
- Conversión y cálculo de áreas con MAGNA-SIRGAS (EPSG:3116).
- Respaldo/restauración de municipios PDET reproducible con script `backup_mongo/import_pdet_data.py`.

## EDA Inicial (Auditoría)
- [notebooks/03_buildings_eda.ipynb](../../notebooks/03_buildings_eda.ipynb): Comparativa por municipio, validación de geometrías y áreas.
- Scripts de validación rápida:  
  - `src/validation/check_microsoft.py`  
  - `src/validation/check_invalid_geometries.py`  
  - `src/validation/validate_microsoft_buildings.py`

## Instrucciones Técnicas
- Ver instrucciones detalladas en cada README y scripts de backup.
- Consultar `README_PERSONA_1.md` y `README_PERSONA_2.md` para comando rápido de carga y validación.

---

**Autores originales y contactos:**  
Alejandro P. (Microsoft), Juan José B. (Google), y Equipo PDET Solar Analysis.

> Para reproducir o revisar detalles, consultar los archivos ejecutivos, técnicos y los notebooks incluidos.
