# Comparación Inicial Microsoft vs Google Open Buildings

## Métricas clave

| Métrica            | Microsoft               | Google                      |
|--------------------|------------------------|-----------------------------|
| Total edificios    | 6,083,821              | 16,530,628 (2.7x más)       |
| Fuente             | Bing Maps (2020-2021)  | Google Research (2023)      |
| Formato original   | GeoJSONL               | CSV.gz + WKT                |
| Áreas precalculadas| ❌ (se calculó)         | ✅ (incluida)                |
| Score confianza    | ❌                     | ✅ (0.65-1.0)                |
| Plus Code          | ❌                     | ✅                           |
| Índices espaciales | ❌ (por geometría)      | ⚠️ (timeout, requiere ajuste)|

## Hallazgos clave

- **Calidad de geometrías:** Microsoft reporta ~0.002% de auto-intersecciones, Google aún pendiente de cuantificación (no crítica).
- **Recomendación:** Usar Google como dataset principal para análisis espacial y de potencial solar en PDET.
- **Distribución de confianza (Google):** 40.4% ≥ 0.80 (alta calidad), ver detalles en los scripts EDA y reportes.
- **Validez de datos:** Todos los scripts de validación muestran 0 áreas negativas, todas las huellas en Colombia, y presencia de campos clave.

## Análisis espacial y EDA

- Resultados del análisis EDA en `notebooks/03_buildings_eda.ipynb` y archivos CSV/HTML en `results/figures/deliverable_3`.
- Muestra de artefactos comparativos: conteos por municipio (`*_buildings_by_municipio_sample.csv`), histogramas de áreas, visualizaciones heatmap.

> Para reproducir el análisis y comparar cobertura, usar los scripts y notebooks proporcionados.
