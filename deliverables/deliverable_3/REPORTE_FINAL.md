# Reporte Final: Join Espacial Edificaciones - Municipios PDET, Validación y Eficiencia

## 1. Resumen Ejecutivo

El presente informe sintetiza los resultados del análisis y comparación entre las edificaciones detectadas en los datasets de Microsoft y Google Open Buildings, haciendo especial énfasis en la integración espacial con los municipios PDET. Se validó la calidad de ambos datasets, se ejecutó un join espacial a nivel MongoDB y Python, y se realizó un análisis comparativo de eficiencia.

## 2. Join Espacial Edificaciones - Municipios PDET (MongoDB)

### Metodología
- Se utiliza $geoWithin para calcular el número de edificaciones dentro de cada municipio PDET usando los índices espaciales 2dsphere de MongoDB. 
- Se compara la cobertura en ambos datasets filtrando, para Google, solo los edificios con confidence >= 0.80.

### Ejemplo de código:
```javascript
var municipio = db.pdet_municipalities.findOne({ muni_code: "05120" });
// Microsoft
var ms_count = db.microsoft_buildings.find({
  geometry: { $geoWithin: { $geometry: municipio.geom } }
}).count();
// Google (alta confianza)
var ggl_count = db.google_buildings.find({
  geometry: { $geoWithin: { $geometry: municipio.geom } },
  "properties.confidence": { $gte: 0.80 }
}).count();
```

### Optimización y notas
- Requiere índices creados (`db.<col>.createIndex({geometry:"2dsphere"})`).
- Para consultas sobre todos los municipios, iterar sobre un cursor de la colección `pdet_municipalities`.
- Se recomienda exportar resultados a CSV para alimentar visualizaciones y reportes.

---

## 3. Validación de Google Open Buildings

- **Script disponible**: `src/validation/validate_google_buildings.py`
- Analiza:
  - Conteo total de edificios y distribución de confianza.
  - Detección de registros con geometría o área inválida.
  - Estadísticas de área: media, min, max, total.
  - Proporción de techos alta confianza (>=0.80): >6.6M (~40.4%).

---

## 4. Análisis de Eficiencia Comparativa

| Métrica        | Microsoft                 | Google                    |
|----------------|--------------------------|---------------------------|
| Volumen total  | 6,083,821                 | 16,530,628                |
| Tiempo carga   | ~13 min                   | ~37 min                   |
| Docs/seg       | 7,800                     | 7,332                     |
| Área media     | ~125 m²                   | ~100 m²                   |
| Índices        | Parcialmente, problemas   | Timeout, recomienda crear |
| Formato fuente | GeoJSONL                  | CSV.gz + WKT              |
| Filtrado útil  | N/A                       | `confidence >= 0.80`      |

- Google requiere mayor tiempo/recursos pero es mucho más completo.
- El join espacial es viable y rápido **si los índices existen**.
- Cuando los índices fallan, filtrar por bounding box y refinar con scripts Python (shapely).

---

## 5. Código Python de ejemplo (exportar por municipio)
```python
from pymongo import MongoClient
client = MongoClient()
db = client.pdet_solar_analysis
ms_counts = {}
gg_counts = {}

for muni in db.pdet_municipalities.find({}, {"muni_code": 1, "geom": 1}):
    ms_count = db.microsoft_buildings.count_documents({
        "geometry": { "$geoWithin": { "$geometry": muni["geom"] } }
    })
    gg_count = db.google_buildings.count_documents({
        "geometry": { "$geoWithin": { "$geometry": muni["geom"] } },
        "properties.confidence": { "$gte": 0.80 }
    })
    ms_counts[muni["muni_code"]] = ms_count
    gg_counts[muni["muni_code"]] = gg_count
print("Ejemplo de conteos por municipio:", ms_counts, gg_counts)
```

---

## 6. Conclusiones y Recomendaciones
- Google Open Buildings es preferido para análisis PDET, especialmente filtrando por `confidence >= 0.80`.
- El join espacial permite análisis detallado de cobertura solar a escalas municipal y regional.
- MongoDB escala bien si se usan correctamente los índices; para EDA local, usa GeoPandas en modo muestra si hay limitación de recursos.
