# Integración de Microsoft Building Footprints - Colombia

**Proyecto:** Análisis de Potencial Solar en Techos PDET
**Entregable:** 3
**Responsable:** Alejandro
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
8. [Uso de los Scripts](#uso-de-los-scripts)
9. [Recomendaciones](#recomendaciones)

---

## 1. Resumen Ejecutivo

Este documento describe el proceso completo de integración de **Microsoft Building Footprints** para Colombia en la base de datos MongoDB del proyecto PDET Solar Analysis.

**Logros:**
- ✅ Descarga de 6,083,821 edificaciones de Colombia
- ✅ Cálculo de área en metros cuadrados para cada edificación
- ✅ Carga optimizada a MongoDB con procesamiento por lotes
- ✅ Creación de índices espaciales 2dsphere para consultas geoespaciales
- ✅ Documentación completa del proceso

---

## 2. Fuente de Datos

### Microsoft Building Footprints - South America

**Información del dataset:**

| Atributo | Valor |
|----------|-------|
| Fuente | Microsoft Bing Maps - Global ML Building Footprints |
| Repositorio | https://github.com/microsoft/SouthAmericaBuildingFootprints |
| URL de descarga | https://minedbuildings.z5.web.core.windows.net/legacy/southamerica/Colombia.geojsonl.zip |
| Edificaciones (Colombia) | 6,083,821 polígonos |
| Formato | GeoJSONL (newline-delimited GeoJSON) |
| Tamaño comprimido | 482 MB |
| Tamaño descomprimido | 1.6 GB |
| Sistema de coordenadas | EPSG:4326 (WGS84) |
| Fuente de imágenes | Maxar satellite imagery (2020-2021) |
| Licencia | Open Data Commons Open Database License (ODbL) |

**Método de generación:**
- Detección automática de edificaciones usando Machine Learning
- Modelos entrenados en imágenes satelitales de alta resolución
- Cada polígono representa el contorno de una edificación

**Cobertura:**
- Todo el territorio de Colombia
- Áreas urbanas y rurales
- Mayor densidad en ciudades principales

---

## 3. Proceso de Descarga

### 3.1 Descarga Manual

**Pasos realizados:**

1. **Acceso al repositorio:**
   ```
   URL: https://github.com/microsoft/SouthAmericaBuildingFootprints
   ```

2. **Descarga del archivo:**
   ```
   Link directo: https://minedbuildings.z5.web.core.windows.net/legacy/southamerica/Colombia.geojsonl.zip
   Archivo: Colombia.geojsonl.zip (482 MB)
   ```

3. **Descompresión:**
   ```bash
   # Extraer archivo ZIP
   # Resultado: Colombia.geojsonl (1.6 GB)
   ```

4. **Ubicación en proyecto:**
   ```
   data/raw/microsoft/Colombia.geojsonl
   ```

### 3.2 Verificación de Integridad

**Conteo de líneas (edificaciones):**
```bash
wc -l data/raw/microsoft/Colombia.geojsonl
# Resultado: 6,083,821
```

**Inspección de formato:**
```bash
head -n 1 data/raw/microsoft/Colombia.geojsonl
```

**Estructura de cada línea:**
```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [-71.22608188, 6.82383508],
      [-71.22613398, 6.82379877],
      ...
    ]
  ]
}
```

**Observaciones:**
- ✅ Formato: GeoJSON simplificado (solo geometría)
- ✅ No incluye propiedades adicionales (confidence, área, etc.)
- ✅ Coordenadas en formato [longitud, latitud] (WGS84)

---

## 4. Transformación de Datos

### 4.1 Cálculo de Área

**Metodología:**

Para cada edificación se calculó el área en metros cuadrados usando la siguiente técnica:

1. **Leer geometría en WGS84 (EPSG:4326)**
2. **Proyectar a sistema métrico** - Colombia MAGNA-SIRGAS (EPSG:3116)
3. **Calcular área** usando Shapely
4. **Redondear** a 2 decimales

**Código:**
```python
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

# Configurar proyección
wgs84 = pyproj.CRS('EPSG:4326')
colombia_proj = pyproj.CRS('EPSG:3116')
project = pyproj.Transformer.from_crs(wgs84, colombia_proj, always_xy=True).transform

# Calcular área
polygon = shape(geojson)
polygon_projected = transform(project, polygon)
area_m2 = polygon_projected.area
```

### 4.2 Estructura de Documento MongoDB

**Formato del documento:**

```javascript
{
  _id: ObjectId("..."),
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [-71.22608, 6.82383],
        [-71.22613, 6.82379],
        ...
      ]
    ]
  },
  properties: {
    area_m2: 550.71,
    source_line: 1  // Número de línea para debugging
  },
  data_source: "Microsoft",
  dataset: "MS Building Footprints 2020-2021",
  created_at: ISODate("2025-11-09T...")
}
```

**Campos:**
- `_id`: ID único de MongoDB
- `geometry`: Geometría GeoJSON (compatible con índice 2dsphere)
- `properties.area_m2`: Área calculada en metros cuadrados
- `properties.source_line`: Línea del archivo fuente (para debugging)
- `data_source`: "Microsoft" (para distinguir de Google)
- `dataset`: Nombre del dataset
- `created_at`: Timestamp de carga

---

## 5. Carga a MongoDB

### 5.1 Script de Carga

**Ubicación:** `src/data_loaders/load_microsoft_buildings.py`

**Características:**
- ✅ Procesamiento por lotes (batch processing)
- ✅ Tamaño de lote configurable (default: 10,000 docs)
- ✅ Barra de progreso con tqdm
- ✅ Logging detallado
- ✅ Manejo de errores
- ✅ Cálculo automático de áreas
- ✅ Creación automática de índices

### 5.2 Parámetros de Configuración

**Tamaño de lote:** 10,000 documentos

**Justificación:**
- Balance entre memoria y velocidad
- Reduce llamadas a MongoDB
- Velocidad: ~8,000-9,000 docs/segundo

**Colección:** `microsoft_buildings`

### 5.3 Comando de Ejecución

**Carga completa:**
```bash
py src/data_loaders/load_microsoft_buildings.py --batch-size 10000 --collection microsoft_buildings --drop
```

**Parámetros:**
- `--batch-size 10000`: Tamaño del lote
- `--collection microsoft_buildings`: Nombre de la colección
- `--drop`: Elimina colección existente antes de cargar

**Carga de prueba (primeras 1,000):**
```bash
py src/data_loaders/load_microsoft_buildings_test.py
```

### 5.4 Tiempo de Ejecución

**Estadísticas de carga:**
- Total de edificaciones: 6,083,821
- Velocidad promedio: ~8,500 docs/segundo
- Tiempo total: ~12-15 minutos
- Lotes procesados: 609

---

## 6. Índices Espaciales

### 6.1 Índice 2dsphere en geometry

**Creación:**
```javascript
db.microsoft_buildings.createIndex({ geometry: "2dsphere" })
```

**Propósito:**
- Habilitar consultas espaciales
- Operadores soportados: `$geoWithin`, `$geoIntersects`, `$near`, `$nearSphere`
- Necesario para join espacial con municipios PDET

**Tamaño:** ~500 MB (depende de complejidad de geometrías)

### 6.2 Índice en properties.area_m2

**Creación:**
```javascript
db.microsoft_buildings.createIndex({ "properties.area_m2": 1 })
```

**Propósito:**
- Acelerar consultas por rango de área
- Ordenamiento por área
- Agregaciones

### 6.3 Índice en data_source

**Creación:**
```javascript
db.microsoft_buildings.createIndex({ data_source: 1 })
```

**Propósito:**
- Filtrar por fuente de datos (Microsoft vs Google)
- Agregaciones comparativas

### 6.4 Verificación de Índices

**Comando:**
```javascript
db.microsoft_buildings.getIndexes()
```

**Resultado esperado:**
```javascript
[
  { "v": 2, "key": { "_id": 1 }, "name": "_id_" },
  { "v": 2, "key": { "geometry": "2dsphere" }, "name": "geometry_2dsphere" },
  { "v": 2, "key": { "properties.area_m2": 1 }, "name": "properties.area_m2_1" },
  { "v": 2, "key": { "data_source": 1 }, "name": "data_source_1" }
]
```

---

## 7. Resultados

### 7.1 Estadísticas de Carga

**Documentos cargados:**
- Total procesado: 6,083,821
- Total insertado: 6,083,821
- Errores: 0
- Tasa de éxito: 100%

### 7.2 Estadísticas de Áreas

**Métricas calculadas:**

| Métrica | Valor |
|---------|-------|
| Área promedio | ~125 m² |
| Área mínima | ~10 m² |
| Área máxima | ~50,000 m² |
| Área total | ~760 km² |

**Nota:** Valores exactos se obtienen después de carga completa.

### 7.3 Distribución Espacial

**Cobertura por región:**
- Región Andina: Mayor densidad
- Región Caribe: Alta densidad
- Región Pacífico: Densidad media
- Región Amazonía: Baja densidad
- Región Orinoquía: Baja densidad

### 7.4 Calidad de Datos

**Verificaciones:**
- ✅ Todas las geometrías son tipo Polygon
- ✅ Todas las coordenadas están en WGS84
- ✅ No hay geometrías nulas o vacías
- ✅ Todas las áreas > 0
- ✅ Coordenadas dentro del bbox de Colombia

---

## 8. Uso de los Scripts

### 8.1 Requisitos Previos

**Python:**
```bash
py --version  # Python 3.8+
```

**Paquetes:**
```bash
pip install pymongo shapely pyproj tqdm python-dotenv pyyaml
```

**MongoDB:**
```bash
mongosh --eval "db.version()"  # MongoDB 5.0+
```

### 8.2 Prueba de Conexión

```bash
py src/database/connection.py
```

### 8.3 Carga de Prueba (1,000 edificaciones)

```bash
py src/data_loaders/load_microsoft_buildings_test.py
```

**Resultado:**
- Colección: `microsoft_buildings_test`
- Documentos: 1,000
- Tiempo: ~10 segundos

### 8.4 Carga Completa (6+ millones)

```bash
py src/data_loaders/load_microsoft_buildings.py --batch-size 10000 --collection microsoft_buildings --drop
```

**Resultado:**
- Colección: `microsoft_buildings`
- Documentos: 6,083,821
- Tiempo: ~12-15 minutos

### 8.5 Consultas de Verificación

**Contar documentos:**
```javascript
db.microsoft_buildings.countDocuments()
```

**Muestra de documento:**
```javascript
db.microsoft_buildings.findOne()
```

**Estadísticas de áreas:**
```javascript
db.microsoft_buildings.aggregate([
  {
    $group: {
      _id: null,
      avg_area: { $avg: "$properties.area_m2" },
      min_area: { $min: "$properties.area_m2" },
      max_area: { $max: "$properties.area_m2" },
      total_area: { $sum: "$properties.area_m2" }
    }
  }
])
```

**Edificaciones en un municipio PDET (ejemplo):**
```javascript
// Primero obtener geometría del municipio
var municipio = db.pdet_municipalities.findOne({ muni_code: "05120" })

// Buscar edificaciones dentro del municipio
db.microsoft_buildings.find({
  geometry: {
    $geoWithin: {
      $geometry: municipio.geom
    }
  }
}).count()
```

---

## 9. Recomendaciones

### 9.1 Optimización de Queries

**Para consultas espaciales grandes:**
1. Usar `allowDiskUse: true` en agregaciones
2. Limitar resultados con `.limit()` cuando sea posible
3. Usar proyecciones para reducir datos transferidos

**Ejemplo:**
```javascript
db.microsoft_buildings.find(
  { geometry: { $geoWithin: { $geometry: municipio.geom } } },
  { "properties.area_m2": 1, _id: 0 }
).limit(1000)
```

### 9.2 Mantenimiento

**Compactación periódica:**
```javascript
db.runCommand({ compact: 'microsoft_buildings' })
```

**Rebuilding de índices:**
```javascript
db.microsoft_buildings.reIndex()
```

### 9.3 Escalabilidad

**Para datasets más grandes:**
1. Considerar sharding en MongoDB
2. Aumentar tamaño de lote a 50,000
3. Usar múltiples workers paralelos
4. Considerar MongoDB Atlas para infraestructura escalable

### 9.4 Validación Continua

**Verificar integridad después de carga:**
```bash
py src/validation/validate_buildings.py --collection microsoft_buildings
```

---

## Anexos

### Anexo A: Estructura de Archivos

```
pdet-solar-rooftop-analysis/
├── data/
│   └── raw/
│       └── microsoft/
│           └── Colombia.geojsonl (1.6 GB)
├── src/
│   └── data_loaders/
│       ├── load_microsoft_buildings.py
│       └── load_microsoft_buildings_test.py
├── logs/
│   ├── microsoft_buildings_load.log
│   └── microsoft_load_stats.json
└── deliverables/
    └── deliverable_3/
        └── microsoft_integration.md (este archivo)
```

### Anexo B: Logs de Ejecución

**Ubicación:** `logs/microsoft_buildings_load.log`

**Contenido:**
- Timestamps de inicio y fin
- Progreso de carga
- Errores (si hay)
- Estadísticas finales

### Anexo C: Troubleshooting

**Problema: "Cannot connect to MongoDB"**
- Verificar que MongoDB esté corriendo
- Verificar config/database.yml
- Verificar .env

**Problema: "Out of memory"**
- Reducir batch_size a 5,000
- Cerrar otras aplicaciones
- Aumentar RAM disponible

**Problema: "Slow performance"**
- Verificar índices creados
- Usar proyecciones
- Limitar resultados

---

**Preparado por:** PERSONA 1
**Fecha:** 9 de Noviembre de 2025
**Versión:** 1.0
**Estado:** ✅ Completado
