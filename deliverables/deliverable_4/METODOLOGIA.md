# Metodología de Análisis Geoespacial - Deliverable 4

**Proyecto:** PDET Solar Rooftop Analysis
**Fecha:** Noviembre 2025
**Versión:** 1.0

---

## 1. Resumen Ejecutivo

Este documento describe la metodología detallada para el análisis geoespacial de potencial solar en techos de edificaciones en municipios PDET. El análisis se basa en datos de Microsoft Building Footprints y Google Open Buildings, procesados mediante MongoDB y herramientas geoespaciales de Python.

---

## 2. Datos de Entrada

### 2.1 Edificaciones

**Microsoft Building Footprints:**
- Total: 6,083,821 edificaciones
- Formato: GeoJSON (Polygon)
- Atributo clave: `properties.area_m2`
- Colección MongoDB: `microsoft_buildings`

**Google Open Buildings:**
- Total: 16,530,628 edificaciones
- Formato: GeoJSON (Polygon)
- Atributos clave: `properties.area_m2`, `properties.confidence`
- Colección MongoDB: `google_buildings`

### 2.2 Municipios PDET

- Total: 146 municipios
- Formato: GeoJSON (Polygon/MultiPolygon)
- Atributos: código DIVIPOLA, nombre, región PDET, área
- Colección MongoDB: `pdet_municipalities`
- Índice espacial: 2dsphere en campo `geom`

---

## 3. Join Espacial

### 3.1 Método Implementado: Bbox Filtering

**Justificación:**
- Sugerido por el profesor para optimización de tiempo
- MongoDB ejecuta las operaciones pesadas
- Usa primer punto del polígono como referencia

**Pipeline de Agregación MongoDB:**

```javascript
pipeline = [
  {
    $match: {
      'geometry.coordinates.0.0.0': {
        $gte: bbox.min_lon,
        $lte: bbox.max_lon
      },
      'geometry.coordinates.0.0.1': {
        $gte: bbox.min_lat,
        $lte: bbox.max_lat
      }
    }
  },
  {
    $facet: {
      count: [{ $count: 'total' }],
      avg_area: [
        { $limit: 1000 },
        { $match: { 'properties.area_m2': { $gt: 0 } } },
        { $group: {
            _id: null,
            avg: { $avg: '$properties.area_m2' }
          }
        }
      ]
    }
  }
]
```

**Ventajas:**
- ✅ MongoDB ejecuta todo el procesamiento
- ✅ Uso de `allowDiskUse: true` para grandes volúmenes
- ✅ Operaciones paralelas con `$facet`
- ✅ Rápido para 6M+ documentos

**Limitaciones:**
- Aproximación basada en bbox, no intersección geométrica exacta
- Puede incluir edificaciones en bordes del bbox que están fuera del municipio

### 3.2 Resultados del Join Espacial

**Colección de salida:** `buildings_by_municipality`

**Estructura de documento:**
```json
{
  "muni_code": "13001",
  "muni_name": "Cartagena",
  "dept_name": "Bolívar",
  "pdet_region": "Montes de María",
  "pdet_subregion": "Montes de María",
  "area_km2": 572.4,
  "microsoft": {
    "count": 45320,
    "avg_area_m2": 156.32,
    "total_area_m2": 7084470.4,
    "total_area_km2": 7.08
  },
  "google": {
    "count": 52140,
    "avg_area_m2": 142.18,
    "total_area_m2": 7412071.2,
    "total_area_km2": 7.41
  },
  "created_at": ISODate("2025-11-11T...")
}
```

---

## 4. Cálculo de Área Útil para Paneles Solares

### 4.1 Factores de Corrección

El área total de techos no es completamente utilizable para instalación de paneles solares. Se aplican los siguientes factores de corrección:

#### Factor 1: Orientación (α = 0.70)
- **Justificación:** No todos los techos tienen orientación óptima (sur en Colombia)
- **Fuente:** NREL Solar Radiation Data Manual
- **Valor:** 70% del área total

#### Factor 2: Pendiente (β = 0.80)
- **Justificación:** Techos muy inclinados o planos reducen eficiencia
- **Pendiente óptima:** 10-15° en Colombia (latitud ~4°N)
- **Valor:** 80% del área total

#### Factor 3: Obstrucciones (γ = 0.85)
- **Justificación:** Chimeneas, antenas, tanques de agua, sombras de árboles
- **Estudios de referencia:** ~15% de área no utilizable
- **Valor:** 85% del área total

#### Factor Combinado (η)

```
η = α × β × γ
η = 0.70 × 0.80 × 0.85
η = 0.476
```

**Área Útil = Área Total de Techos × 0.476**

### 4.2 Fórmulas de Cálculo

Para cada municipio:

```python
# Área total de techos (ya calculada en join espacial)
area_total_m2 = count × avg_area_m2

# Área útil para paneles solares
area_util_m2 = area_total_m2 × 0.476

# Área útil en km²
area_util_km2 = area_util_m2 / 1_000_000

# Área útil en hectáreas (para reportes)
area_util_ha = area_util_m2 / 10_000
```

### 4.3 Potencial Energético (Opcional para Deliverable 5)

**No requerido en Deliverable 4**, pero preparamos variables:

```python
# Irradiación promedio Colombia: 4.5 kWh/m²/día
irradiacion_promedio = 4.5  # kWh/m²/día

# Eficiencia de panel solar: 18% (tecnología actual)
eficiencia_panel = 0.18

# Potencial energético diario
potencial_kwh_dia = area_util_m2 × irradiacion_promedio × eficiencia_panel

# Potencial energético anual
potencial_kwh_anual = potencial_kwh_dia × 365
```

---

## 5. Estadísticas por Municipio

### 5.1 Métricas Principales

Para cada municipio PDET, calcularemos:

| Métrica | Descripción | Unidad |
|---------|-------------|--------|
| `count_buildings` | Número de edificaciones | unidades |
| `area_total_m2` | Área total de techos | m² |
| `area_total_km2` | Área total de techos | km² |
| `area_util_m2` | Área útil para paneles | m² |
| `area_util_km2` | Área útil para paneles | km² |
| `area_util_ha` | Área útil para paneles | hectáreas |
| `avg_building_area_m2` | Área promedio por edificación | m² |
| `density_buildings_km2` | Densidad de edificaciones | edif/km² |
| `coverage_pct` | % del área municipal con techos | % |

### 5.2 Comparación Microsoft vs Google

```python
comparison_metrics = {
    'difference_count': google_count - ms_count,
    'difference_pct': ((google_count - ms_count) / ms_count) × 100,
    'difference_area_km2': google_area - ms_area,
    'agreement_score': min(ms_count, google_count) / max(ms_count, google_count)
}
```

---

## 6. Agregación por Región PDET

### 6.1 Regiones PDET

Las 16 regiones PDET en el análisis:
1. Alto Patía y Norte del Cauca
2. Arauca
3. Catatumbo
4. Chocó
5. Cuenca del Caguán y Piedemonte Caqueteño
6. Macarena-Guaviare
7. Montes de María
8. Pacífico Medio
9. Pacífico y Frontera Nariñense
10. Putumayo
11. Sierra Nevada-Perijá
12. Sur de Bolívar
13. Sur de Córdoba
14. Sur del Tolima
15. Urabá Antioqueño
16. Bajo Cauca y Nordeste Antioqueño

### 6.2 Estadísticas Regionales

```python
regional_stats = {
    'region_name': str,
    'num_municipalities': int,
    'total_buildings': int,
    'total_area_util_km2': float,
    'avg_buildings_per_municipality': float,
    'top_municipality': str,
    'municipalities': [list of muni codes]
}
```

---

## 7. Validación de Resultados

### 7.1 Validaciones Automáticas

**Check 1: Consistencia de datos**
```python
assert count > 0, "Conteo debe ser positivo"
assert area_total > 0, "Área debe ser positiva"
assert area_util <= area_total, "Área útil no puede exceder área total"
```

**Check 2: Rango razonable**
```python
assert 10 <= avg_area <= 10000, "Área promedio fuera de rango razonable"
assert density >= 0, "Densidad no puede ser negativa"
```

**Check 3: Completitud**
```python
assert len(municipalities_processed) == 146, "Deben procesarse 146 municipios"
```

### 7.2 Métricas de Calidad

```python
quality_metrics = {
    'municipalities_with_data': count of munis with buildings > 0,
    'municipalities_no_data': count of munis with buildings == 0,
    'coverage_pct': (munis_with_data / 146) × 100,
    'total_buildings_analyzed': sum of all counts,
    'total_area_analyzed_km2': sum of all areas
}
```

---

## 8. Formato de Salida

### 8.1 Tabla CSV Principal: `municipalities_stats.csv`

```csv
muni_code,muni_name,dept_name,pdet_region,pdet_subregion,area_muni_km2,
ms_count,ms_area_total_km2,ms_area_util_km2,ms_avg_area_m2,ms_density,
gg_count,gg_area_total_km2,gg_area_util_km2,gg_avg_area_m2,gg_density,
comparison_diff_count,comparison_diff_pct,comparison_agreement
```

### 8.2 Tabla CSV Regional: `regional_summary.csv`

```csv
pdet_region,num_municipalities,total_buildings_ms,total_area_util_km2_ms,
total_buildings_gg,total_area_util_km2_gg,top_municipality,top_municipality_count
```

### 8.3 GeoJSON: `municipalities_with_stats.geojson`

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "properties": {
        "muni_code": "13001",
        "muni_name": "Cartagena",
        "pdet_region": "Montes de María",
        "ms_count": 45320,
        "ms_area_util_km2": 3.37,
        "gg_count": 52140,
        "gg_area_util_km2": 3.53
      }
    }
  ]
}
```

---

## 9. Reproducibilidad

### 9.1 Scripts Ejecutables

**Filosofía de diseño:** Todo el trabajo pesado se ejecuta en MongoDB usando agregaciones nativas.

```bash
# 1. Calcular área útil (MongoDB UPDATE)
python deliverables/deliverable_4/scripts/01_calculate_solar_area.py

# 2. Generar estadísticas (MongoDB $addFields + $project)
python deliverables/deliverable_4/scripts/02_generate_statistics.py

# 3. Resumen regional (MongoDB $group + $sum + $avg)
python deliverables/deliverable_4/scripts/03_regional_summary.py

# 4. Exportar GeoJSON
python deliverables/deliverable_4/scripts/04_export_geojson.py
```

**Nota importante:** Los scripts 02 y 03 usan **pipelines de agregación de MongoDB** para que el servidor haga TODO el cálculo de métricas (densidad, cobertura, totales, promedios). Python solo recibe resultados ya procesados.

### 9.2 Logging

Todos los scripts incluirán logging detallado:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deliverables/deliverable_4/logs/processing.log'),
        logging.StreamHandler()
    ]
)
```

---

## 10. Agregaciones de MongoDB (Trabajo Pesado)

### 10.1 Script 02: Cálculo de Estadísticas

**Pipeline de agregación (3 stages):**

```javascript
// Stage 1: $addFields - Calcula métricas derivadas
{
  $addFields: {
    ms_density: {$divide: ['$microsoft.count', '$area_km2']},
    ms_coverage: {$multiply: [
      {$divide: ['$microsoft.total_area_km2', '$area_km2']},
      100
    ]},
    diff_count: {$subtract: ['$google.count', '$microsoft.count']},
    diff_pct: {$multiply: [
      {$divide: [
        {$subtract: ['$google.count', '$microsoft.count']},
        '$microsoft.count'
      ]},
      100
    ]},
    agreement_score: {$divide: [
      {$min: ['$microsoft.count', '$google.count']},
      {$max: ['$microsoft.count', '$google.count']}
    ]}
  }
}

// Stage 2: $project - Selecciona y formatea campos
{
  $project: {
    muni_code: 1,
    muni_name: 1,
    ms_buildings_count: '$microsoft.count',
    ms_useful_area_km2: {$round: ['$microsoft.area_util_km2', 4]},
    ms_density_buildings_km2: {$round: ['$ms_density', 2]},
    ...
  }
}

// Stage 3: $sort - Ordena resultados
{
  $sort: {pdet_region: 1, muni_name: 1}
}
```

**Ventajas:**
- MongoDB calcula 23 columnas de estadísticas para 146 municipios
- Procesamiento en <0.1 segundos
- Python solo recibe resultados ya calculados

### 10.2 Script 03: Agregación Regional

**Pipeline de agregación (3 stages):**

```javascript
// Stage 1: $group - Agrupa por región PDET
{
  $group: {
    _id: '$pdet_region',
    num_municipalities: {$sum: 1},
    ms_total_buildings: {$sum: '$microsoft.count'},
    ms_total_useful_area_km2: {$sum: '$microsoft.area_util_km2'},
    ms_avg_buildings_per_muni: {$avg: '$microsoft.count'},
    ms_top_muni: {
      $max: {
        name: '$muni_name',
        count: '$microsoft.count'
      }
    }
  }
}

// Stage 2: $project - Formatea y redondea
{
  $project: {
    pdet_region: '$_id',
    ms_total_useful_area_km2: {$round: ['$ms_total_useful_area_km2', 2]},
    ...
  }
}

// Stage 3: $sort - Ordena por total de edificaciones
{
  $sort: {ms_total_buildings: -1}
}
```

**Ventajas:**
- MongoDB agrupa 146 municipios en 14 regiones
- Calcula sumas, promedios, máximos automáticamente
- Procesamiento en <0.1 segundos
- Código declarativo y más mantenible

### 10.3 Consistencia con Deliverable 3

Esta aproximación es **consistente** con el join espacial del Deliverable 3:

**Deliverable 3 - Join Espacial:**
```javascript
pipeline = [
  {$match: {
    'geometry.coordinates.0.0.0': {$gte: bbox.min_lon, $lte: bbox.max_lon}
  }},
  {$facet: {
    count: [{$count: 'total'}],
    avg_area: [{$group: {_id: null, avg: {$avg: '$properties.area_m2'}}}]
  }}
]
```

**Deliverable 4 - Estadísticas y Agregaciones:**
```javascript
// Usa $addFields, $project, $group para cálculos
// MongoDB hace TODO el trabajo pesado
```

**Principio común:** MongoDB ejecuta las operaciones pesadas, Python solo coordina y exporta.

---

## 11. Supuestos y Limitaciones

### 10.1 Supuestos

1. **Área de techos:** Asumimos que el área del polígono de la edificación representa el área del techo
2. **Factor de eficiencia:** Aplicamos un factor uniforme de 0.476 a todos los techos
3. **Join espacial:** Usamos bbox filtering como aproximación eficiente
4. **Calidad de datos:** Asumimos que los datos de Microsoft y Google son precisos

### 10.2 Limitaciones

1. **Geometrías inválidas:** 122 polígonos de Microsoft tienen auto-intersecciones
2. **Sin índice 2dsphere en Microsoft:** Limita operaciones geoespaciales exactas
3. **Bbox filtering:** Puede incluir edificaciones fuera del límite municipal exacto
4. **Factor de eficiencia uniforme:** No considera variaciones locales de pendiente/orientación
5. **Sin datos de altura:** No podemos calcular área de techos inclinados exactamente

### 10.3 Recomendaciones Futuras

1. Validar geometrías con `shapely.make_valid()` antes de análisis
2. Crear índices 2dsphere para operaciones exactas
3. Incorporar datos de elevación (DEM) para cálculo de pendientes
4. Validar con datos de referencia de campo
5. Ajustar factores de eficiencia por región climática

---

## 11. Referencias

1. **NREL Solar Radiation Data Manual for Flat-Plate and Concentrating Collectors**
   https://www.nrel.gov/docs/fy12osti/51465.pdf

2. **UPME Atlas de Radiación Solar de Colombia**
   http://www.upme.gov.co/

3. **Microsoft Building Footprints**
   https://github.com/microsoft/SouthAmericaBuildingFootprints

4. **Google Open Buildings v3**
   https://sites.research.google/gr/open-buildings/

5. **MongoDB Geospatial Queries Documentation**
   https://docs.mongodb.com/manual/geospatial-queries/

---

**Autor:** Equipo PDET Solar Analysis
**Fecha:** Noviembre 2025
**Versión:** 1.0
**Estado:** En desarrollo
