# Entregable 3: Integración y Auditoría de Edificaciones (Microsoft & Google)

Este entregable documenta la integración en MongoDB y la auditoría inicial (EDA) de las huellas de edificios de Microsoft Building Footprints y Google Open Buildings, enfocado en los municipios PDET de Colombia.

**Contenido:**
- [Metodología reproductible](#metodología-reproductible)
- [Carga eficiente y scripts usados](#carga-eficiente-de-datos)
- [Resultados de auditoría y validación](#eda-inicial)
- [Comparación entre fuentes](#resultados-comparativos)
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

## Carga Eficiente de Datos

- Scripts principales:  
  - `src/data_loaders/load_microsoft_buildings.py`
  - `src/data_loaders/load_google_buildings.py`
  - `src/data_loaders/load_pdet_simple.py`  
  - `backup_mongo/import_pdet_data.py` (para recuperación de municipios PDET)
- Carga en lotes (`batch_size=10,000`)
- Conversión y cálculo de áreas empleando MAGNA-SIRGAS (EPSG:3116)

## EDA Inicial (Auditoría)

- [notebooks/03_buildings_eda.ipynb](../../notebooks/03_buildings_eda.ipynb): Comparativa por municipio, validación de geometrías y áreas.
- Resúmenes estadísticos: áreas, conteos por municipio, distribución de confianza (Google).
- Scripts de validación rápida y específica por colección:  
  - `src/validation/check_microsoft.py`  
  - `src/validation/check_invalid_geometries.py`  
  - `src/validation/validate_microsoft_buildings.py`

## Resultados Comparativos Microsoft vs Google

- Google tiene 2.7x más edificios detectados en Colombia.
- Microsoft entrega 99.998% de geometrías válidas, pero con mínimas fallas impidiendo índices 2dsphere globales.
- Google incluye área, score de confianza y plus codes.
- Ejemplo de hallazgos y tablas comparativas están en `RESUMEN_PERSONA_1.md`, `RESUMEN_PERSONA_2.md`, y notebooks de EDA.

## Instrucciones Técnicas

- Ver instrucciones detalladas de carga/exportación/importación en cada README específico y en scripts de backup.
- Para consulta rápida de scripts o muestras ver `README_PERSONA_1.md` y `README_PERSONA_2.md`.

---

**Autores originales y contactos:**  
Alejandro P. (Microsoft), Juan José B. (Google), y Equipo PDET Solar Analysis.

> Para reproducir o revisar detalles, consultar los archivos ejecutivos, técnicos y los notebooks incluidos.
