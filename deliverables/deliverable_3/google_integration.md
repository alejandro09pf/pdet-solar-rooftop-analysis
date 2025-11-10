# Integración de Google Open Buildings - Colombia

**Proyecto:** Análisis de Potencial Solar en Techos PDET
**Entregable:** 3
**Responsable:** Juan José Bermúdez
**Fecha:** Noviembre 2025
**Estado:** ✅ Completado

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Fuente de Datos](#fuente-de-datos)
3. [Proceso de Descarga](#proceso-de-descarga)
4. [Transformación de Datos](#transformación-de-datos)
5. [Carga a MongoDB](#carga-a-mongodb)
6. [Índices Espaciales](#índices-espaciales)
7. [Resultados](#resultados)
8. [Comparación con Microsoft](#comparación-con-microsoft)
9. [Uso de los Scripts](#uso-de-los-scripts)
10. [Recomendaciones](#recomendaciones)

---

## 1. Resumen Ejecutivo

Este documento describe el proceso completo de integración de **Google Open Buildings v3** para Colombia en la base de datos MongoDB del proyecto PDET Solar Analysis.

**Logros:**
- ✅ Descarga de 16,530,628 edificaciones de Colombia
- ✅ Conversión automática de WKT a GeoJSON
- ✅ Filtrado por nivel de confianza (confidence)
- ✅ Carga optimizada a MongoDB con procesamiento por lotes
- ✅ Manejo de campos específicos de Google (confidence, plus_code, área)
- ✅ 2.7x más edificaciones que Microsoft (16.5M vs 6M)

---

## 2. Fuente de Datos

### Google Open Buildings v3

**Información del dataset:**

| Atributo | Valor |
|----------|-------|
| Fuente | Google Research - Open Buildings |
| Versión | v3 (Mayo 2023) |
| Sitio web | https://sites.research.google/gr/open-buildings/ |
| Método de descarga | Google Colab Notebook |
| Edificaciones (Colombia) | 16,530,628 polígonos |
| Formato original | CSV.gz (comprimido) |
| Tamaño comprimido | 1.6 GB |
| Sistema de coordenadas | EPSG:4326 (WGS84) |
| Licencia | CC BY-4.0 / ODbL v1.0 (dual license) |

**Método de generación:**
- Detección automática usando Deep Learning
- Entrenado en imágenes satelitales de alta resolución
- Cada polígono incluye score de confianza (0.65-1.0)
- Área calculada por Google en metros cuadrados

**Cobertura:**
- América Latina completa (v3)
- Colombia incluida en totalidad
- Cobertura urbana y rural
- 2.7x más edificaciones que Microsoft

---

## 3. Proceso de Descarga

### 3.1 Descarga mediante Google Colab

**Método utilizado:**

1. **Acceso al Colab Notebook:**
   ```
   URL: https://colab.research.google.com/github/google-research/google-research/blob/master/building_detection/open_buildings_download_region_polygons.ipynb
   ```

2. **Configuración en el notebook:**
   - **Region Border Source:** Natural Earth (Low Res 110m)
   - **Region:** COL (Colombia)
   - **Data Type:** polygons

3. **Descarga directa desde Colab:**
   - Método elegido: Download directly (slow pero sin autenticación)
   - Archivo generado: `open_buildings_v3_polygons_ne_110m_COL.csv.gz`
   - Tamaño: 1.6 GB comprimido

4. **Ubicación en proyecto:**
   ```
   data/raw/google/google_buildings/open_buildings_v3_polygons_ne_110m_COL.csv.gz
   ```

### 3.2 Campos del CSV

**Estructura de datos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| latitude | float | Latitud del centroide del edificio |
| longitude | float | Longitud del centroide del edificio |
| area_in_meters | float | Área en metros cuadrados (calculada por Google) |
| confidence | float | Score de confianza del modelo ML [0.65-1.0] |
| geometry | string | Geometría en formato WKT (POLYGON o MULTIPOLYGON) |
| full_plus_code | string | Código Plus Code completo del centroide |

**Ejemplo de fila CSV:**
```csv
latitude,longitude,area_in_meters,confidence,geometry,full_plus_code
4.123456,-73.654321,125.45,0.87,"POLYGON ((-73.654 4.123, ...))",67GX4PHW+ABC
```

---

## 4. Transformación de Datos

### 4.1 Conversión WKT a GeoJSON

**Proceso implementado:**

Google proporciona geometrías en formato **WKT** (Well-Known Text), que necesitan convertirse a **GeoJSON** para MongoDB.

**Código de conversión:**
```python
from shapely import wkt

def wkt_to_geojson(wkt_string):
    # Parsear WKT con Shapely
    geom = wkt.loads(wkt_string)
    
    # Convertir a GeoJSON
    geojson = {
        'type': geom.geom_type,
        'coordinates': extract_coords(geom)
    }
    
    return geojson
```

**Ventajas:**
- Conversión automática durante la carga
- Sin archivos intermedios
- Validación de geometrías incluida

### 4.2 Estructura de Documento MongoDB

**Formato del documento:**

```javascript
{
  _id: ObjectId("..."),
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [-73.654321, 4.123456],
        [-73.654890, 4.123789],
        ...
      ]
    ]
  },
  properties: {
    latitude: 4.123456,
    longitude: -73.654321,
    area_in_meters: 125.45,
    confidence: 0.87,
    full_plus_code: "67GX4PHW+ABC",
    source_row: 1
  },
  data_source: "Google",
  dataset: "Google Open Buildings v3",
  created_at: ISODate("2025-11-09T...")
}
```

**Campos clave:**
- `geometry`: GeoJSON compatible con índice 2dsphere
- `properties.confidence`: Score de confianza del modelo ML
- `properties.area_in_meters`: Área calculada por Google
- `properties.full_plus_code`: Código Plus Code para geolocalización
- `data_source`: "Google" (para distinguir de Microsoft)

---

## 5. Carga a MongoDB

### 5.1 Script de Carga

**Ubicación:** `src/data_loaders/load_google_buildings.py`

**Características principales:**
- ✅ Lee CSV.gz directamente (sin descomprimir en disco)
- ✅ Convierte WKT a GeoJSON automáticamente
- ✅ Procesamiento por lotes (batch processing)
- ✅ Filtrado por nivel de confianza
- ✅ Barra de progreso con tqdm
- ✅ Logging detallado
- ✅ Estadísticas de distribución de confianza
- ✅ Creación automática de índices

### 5.2 Parámetros de Configuración

**Configuración utilizada:**

| Parámetro | Valor |
|-----------|-------|
| Tamaño de lote | 10,000 documentos |
| Confianza mínima | 0.65 |
| Colección | google_buildings |
| Drop existing | True |

**Justificación:**
- **Lote 10,000:** Balance óptimo entre memoria y velocidad
- **Confianza 0.65:** Incluir todas las detecciones de Google
- **Drop existing:** Carga limpia sin duplicados

### 5.3 Comando de Ejecución

**Carga completa con confianza mínima 0.65:**
```bash
python src/data_loaders/load_google_buildings.py --drop --min-confidence 0.65
```

**Opciones disponibles:**
```bash
--drop                    # Eliminar colección existente
--min-confidence 0.80     # Solo edificios alta confianza
--batch-size 5000         # Ajustar tamaño de lote
--collection nombre       # Cambiar nombre de colección
```

### 5.4 Tiempo de Ejecución

**Estadísticas de carga:**

| Métrica | Valor |
|---------|-------|
| Total edificaciones | 16,530,628 |
| Duración | 37 minutos 34 segundos |
| Velocidad promedio | 7,332 docs/segundo |
| Lotes procesados | 1,654 |
| Errores | 0 |
| Tasa de éxito | 100% |

---

## 6. Índices Espaciales

### 6.1 Índice 2dsphere en geometry

**Estado:** ⚠️ Timeout durante creación (colección muy grande)

**Comando de creación:**
```javascript
db.google_buildings.createIndex({ geometry: "2dsphere" })
```

**Problema encontrado:**
- La creación del índice superó el timeout de 30 segundos
- Colección con 16.5M documentos es muy grande
- MongoDB necesita más tiempo para construir el índice

**Solución aplicada:**
```javascript
// Aumentar timeout de socketTimeoutMS
db.adminCommand({
  setParameter: 1,
  socketTimeoutMS: 300000  // 5 minutos
})

// Luego crear índice
db.google_buildings.createIndex(
  { geometry: "2dsphere" },
  { background: true }
)
```

### 6.2 Índices Adicionales

**Índices creados automáticamente:**

```javascript
// Índice en confianza (para filtrado por calidad)
db.google_buildings.createIndex({ "properties.confidence": -1 })

// Índice en área (para consultas por tamaño)
db.google_buildings.createIndex({ "properties.area_in_meters": -1 })

// Índice en Plus Code (para búsquedas por ubicación)
db.google_buildings.createIndex({ "properties.full_plus_code": 1 })

// Índice en fuente de datos
db.google_buildings.createIndex({ data_source: 1 })

// Índice compuesto (queries comunes)
db.google_buildings.createIndex([
  { "properties.confidence": -1 },
  { "properties.area_in_meters": -1 }
])
```

**Estado:** ⚠️ Pendientes por timeout (se pueden crear manualmente después)

### 6.3 Crear Índices Manualmente (Post-carga)

**Script recomendado:**
```bash
# Conectar a MongoDB
mongosh pdet_solar_analysis

# Crear índices con timeout extendido
db.adminCommand({ setParameter: 1, socketTimeoutMS: 600000 })

db.google_buildings.createIndex(
  { geometry: "2dsphere" },
  { background: true, name: "geometry_2dsphere" }
)

db.google_buildings.createIndex(
  { "properties.confidence": -1 },
  { background: true }
)

db.google_buildings.createIndex(
  { "properties.area_in_meters": -1 },
  { background: true }
)
```

---

## 7. Resultados

### 7.1 Estadísticas de Carga

**Datos cargados exitosamente:**

| Métrica | Valor |
|---------|-------|
| **Edificaciones procesadas** | 16,530,628 |
| **Edificaciones insertadas** | 16,530,628 |
| **Omitidas (baja confianza)** | 0 |
| **Errores** | 0 |
| **Tasa de éxito** | 100% |
| **Velocidad promedio** | 7,332 docs/seg |
| **Duración total** | 37min 34seg |

### 7.2 Distribución de Confianza

**Análisis del confidence score:**

| Rango | Cantidad | Porcentaje |
|-------|----------|------------|
| 0.65 - 0.70 | 2,677,910 | 16.2% |
| 0.70 - 0.80 | 7,177,579 | 43.4% |
| 0.80 - 0.90 | 6,168,400 | 37.3% |
| 0.90 - 1.00 | 506,739 | 3.1% |

**Observaciones:**
- ✅ 40.4% tienen confianza ≥ 0.80 (alta calidad)
- ✅ Solo 16.2% están en el rango mínimo (0.65-0.70)
- ✅ 3.1% tienen confianza excepcional (≥ 0.90)
- ⚠️ Mayor concentración en rango medio (0.70-0.80)

**Recomendación:** Para análisis críticos, usar `confidence >= 0.80`

### 7.3 Estadísticas de Áreas

**Métricas (estimadas, pendiente calcular por timeout):**

| Métrica | Valor Estimado |
|---------|----------------|
| Área promedio | ~80-120 m² |
| Área mínima | ~5 m² |
| Área máxima | ~20,000 m² |
| Área total | ~1,300-1,600 km² |

**Nota:** Valores exactos disponibles después de crear índices y ejecutar agregaciones.

### 7.4 Almacenamiento MongoDB

**Tamaño en MongoDB Compass:**

| Métrica | Valor |
|---------|-------|
| Storage size | 2.92 GB |
| Documents | 17M (redondeado en UI) |
| Avg. document size | 474 bytes |
| Total index size | 185 MB |
| Indexes | 2 (default _id + intentos) |

---

## 8. Comparación con Microsoft

### 8.1 Comparativa de Datasets

| Característica | Microsoft | Google |
|----------------|-----------|--------|
| **Total edificaciones** | 6,083,821 | 16,530,628 |
| **Diferencia** | - | **+171.7%** (2.7x más) |
| **Fecha de datos** | 2020-2021 | Mayo 2023 |
| **Confianza incluida** | No | **Sí (0.65-1.0)** |
| **Área incluida** | No (calculada) | **Sí (por Google)** |
| **Plus Code** | No | **Sí** |
| **Formato original** | GeoJSONL | CSV con WKT |
| **Tamaño archivo** | 1.6 GB | 1.6 GB |
| **Tiempo de carga** | ~13 min | 37 min |
| **Velocidad** | 7,800 docs/s | 7,332 docs/s |
| **Geometrías inválidas** | Sí (~0.002%) | Pendiente verificar |
| **Índices creados** | No (por geometrías) | Pendiente (timeout) |

### 8.2 Análisis de Diferencias

**¿Por qué Google tiene 2.7x más edificaciones?**

1. **Fecha más reciente:** 2023 vs 2020-2021 (más construcciones)
2. **Modelo más sensible:** Detecta edificaciones más pequeñas
3. **Mayor cobertura rural:** Google detecta más edificios rurales
4. **Umbral de confianza:** Google incluye desde 0.65 (más permisivo)

**Ventajas de Google:**
- ✅ Más completo (2.7x más edificaciones)
- ✅ Incluye score de confianza
- ✅ Área ya calculada por Google
- ✅ Plus Codes incluidos
- ✅ Datos más recientes (2023)

**Ventajas de Microsoft:**
- ✅ Carga más rápida (menos datos)
- ✅ Geometrías ya en GeoJSON
- ⚠️ Problema con geometrías inválidas

### 8.3 Recomendación de Uso

**Para el proyecto PDET:**

| Propósito | Dataset Recomendado |
|-----------|---------------------|
| **Análisis exploratorio** | Google (más completo) |
| **Join espacial con municipios** | Google (más cobertura) |
| **Cálculo de potencial solar** | Google (más techos) |
| **Validación cruzada** | Ambos (comparar) |
| **Reporte final** | Google (datos más recientes) |

**Conclusión:** **Usar Google Open Buildings como dataset principal**

---

## 9. Uso de los Scripts

### 9.1 Requisitos Previos

**Python y paquetes:**
```bash
python --version  # Python 3.8+

pip install pymongo shapely pyproj tqdm python-dotenv pyyaml
```

**MongoDB:**
```bash
mongosh --eval "db.version()"  # MongoDB 5.0+
```

### 9.2 Verificar Datos Cargados

**Conectar a MongoDB y verificar:**
```bash
# Opción 1: Desde Python
python -c "from src.database.connection import get_database; print(f'Google Buildings: {get_database()[\"google_buildings\"].count_documents({}):,}')"

# Resultado esperado: Google Buildings: 16,530,628
```

**Opción 2: Desde mongosh:**
```javascript
mongosh pdet_solar_analysis

db.google_buildings.countDocuments()
// Resultado: 16530628
```

### 9.3 Consultas de Ejemplo

**Muestra de documento:**
```javascript
db.google_buildings.findOne()
```

**Edificios de alta confianza:**
```javascript
db.google_buildings.find({
  "properties.confidence": { $gte: 0.90 }
}).limit(10)
```

**Edificios grandes (>500 m²):**
```javascript
db.google_buildings.find({
  "properties.area_in_meters": { $gte: 500 }
}).limit(10)
```

**Contar por rango de confianza:**
```javascript
db.google_buildings.aggregate([
  {
    $bucket: {
      groupBy: "$properties.confidence",
      boundaries: [0.65, 0.70, 0.80, 0.90, 1.0],
      default: "Other",
      output: {
        count: { $sum: 1 }
      }
    }
  }
])
```

### 9.4 Crear Índices Manualmente

**Si los índices no se crearon (por timeout):**

```bash
mongosh pdet_solar_analysis

// Aumentar timeout
db.adminCommand({ setParameter: 1, socketTimeoutMS: 600000 })

// Crear índices en background (no bloquea)
db.google_buildings.createIndex(
  { geometry: "2dsphere" },
  { background: true }
)

db.google_buildings.createIndex(
  { "properties.confidence": -1 },
  { background: true }
)

db.google_buildings.createIndex(
  { "properties.area_in_meters": -1 },
  { background: true }
)

// Verificar progreso
db.currentOp({
  "command.createIndexes": "google_buildings"
})
```

---

## 10. Recomendaciones

### 10.1 Para Análisis Subsecuentes

**Filtrado por confianza:**
```javascript
// Solo edificios alta calidad (80%+)
db.google_buildings.find({
  "properties.confidence": { $gte: 0.80 }
})
```

**Join espacial con municipios PDET:**
```javascript
// Obtener municipio
var municipio = db.pdet_municipalities.findOne({ muni_code: "05120" })

// Buscar edificios dentro
db.google_buildings.find({
  geometry: {
    $geoWithin: {
      $geometry: municipio.geom
    }
  }
}).count()
```

### 10.2 Optimización de Queries

**Para consultas espaciales grandes:**

1. **Usar allowDiskUse:**
```javascript
db.google_buildings.aggregate(
  [ ... pipeline ... ],
  { allowDiskUse: true }
)
```

2. **Proyectar solo campos necesarios:**
```javascript
db.google_buildings.find(
  { ... filtros ... },
  {
    "properties.area_in_meters": 1,
    "properties.confidence": 1,
    _id: 0
  }
)
```

3. **Usar límites cuando sea posible:**
```javascript
db.google_buildings.find({ ... }).limit(1000)
```

### 10.3 Mantenimiento

**Compactación periódica:**
```javascript
db.runCommand({ compact: 'google_buildings', force: true })
```

**Rebuilding de índices:**
```javascript
db.google_buildings.reIndex()
```

### 10.4 Para el Reporte Final

**Incluir en el documento:**

1. **Métricas clave:**
   - 16,530,628 edificaciones de Google
   - 2.7x más que Microsoft
   - 40.4% con confianza ≥ 0.80

2. **Distribución de confianza:**
   - Gráfico de barras con los 4 rangos

3. **Comparación con Microsoft:**
   - Tabla comparativa completa

4. **Recomendación:**
   - Usar Google como dataset principal
   - Filtrar por confidence ≥ 0.80 para análisis críticos

---

## Anexos

### Anexo A: Estructura de Archivos

```
pdet-solar-rooftop-analysis/
├── data/
│   └── raw/
│       └── google/
│           └── google_buildings/
│               └── open_buildings_v3_polygons_ne_110m_COL.csv.gz
├── src/
│   └── data_loaders/
│       └── load_google_buildings.py
├── logs/
│   ├── google_buildings_load.log
│   └── google_load_stats.json
└── deliverables/
    └── deliverable_3/
        ├── google_integration.md (este archivo)
        ├── RESUMEN_JUAN_JOSE.md
        └── README_JUAN_JOSE.md
```

### Anexo B: Troubleshooting

**Problema: "Timeout creating indexes"**
- Solución: Crear índices manualmente con timeout extendido
- Ver sección 9.4

**Problema: "Out of memory"**
- Reducir batch_size a 5,000
- Cerrar otras aplicaciones

**Problema: "Slow spatial queries"**
- Asegurarse de que índice 2dsphere esté creado
- Usar proyecciones y límites

---

**Preparado por:** Juan José Bermúdez
**Fecha:** 9 de Noviembre de 2025
**Versión:** 1.0
**Estado:** ✅ Completado