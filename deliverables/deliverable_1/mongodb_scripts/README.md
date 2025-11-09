# MongoDB Scripts - PDET Solar Rooftop Analysis

Scripts de inicialización y consultas para MongoDB.

## Archivos

### 01_initialize_database.js
Script de inicialización de la base de datos que crea:
- Colecciones con validación de esquema
- Índices espaciales 2dsphere
- Índices adicionales para rendimiento

**Uso:**
```bash
mongosh pdet_solar_analysis < 01_initialize_database.js
```

O desde mongosh:
```javascript
use pdet_solar_analysis
load("01_initialize_database.js")
```

### 02_useful_queries.js
Colección de consultas útiles para:
- Estadísticas básicas
- Consultas espaciales
- Análisis de edificaciones
- Comparación de datasets
- Validación de calidad de datos

**Uso:**
```bash
mongosh pdet_solar_analysis < 02_useful_queries.js
```

## Colecciones Creadas

### pdet_municipalities
Municipios PDET con límites administrativos.

**Campos:**
- `muni_code`: Código DIVIPOLA (5 dígitos)
- `dept_code`: Código de departamento (2 dígitos)
- `muni_name`: Nombre del municipio
- `dept_name`: Nombre del departamento
- `pdet_region`: Región PDET
- `pdet_subregion`: Subregión PDET
- `geom`: Geometría GeoJSON (Polygon o MultiPolygon)
- `area_km2`: Área en km²
- `data_source`: Fuente de datos
- `created_at`: Fecha de creación
- `updated_at`: Fecha de actualización

**Índices:**
- `geom_2dsphere`: Índice espacial
- `muni_code_unique`: Índice único
- `dept_code_idx`: Índice simple
- `pdet_region_idx`: Índice simple
- `pdet_subregion_idx`: Índice simple

### buildings_microsoft
Huellas de edificaciones de Microsoft Building Footprints.

**Campos:**
- `muni_code`: Código del municipio
- `geom`: Geometría GeoJSON (Polygon o MultiPolygon)
- `area_m2`: Área en m²
- `data_source`: Fuente de datos
- `source_date`: Fecha de la imagen fuente
- `created_at`: Fecha de creación

**Índices:**
- `geom_2dsphere`: Índice espacial
- `muni_code_idx`: Índice simple
- `area_m2_idx`: Índice simple
- `muni_code_area_idx`: Índice compuesto

### buildings_google
Huellas de edificaciones de Google Open Buildings.

**Campos:**
- `muni_code`: Código del municipio
- `geom`: Geometría GeoJSON (Polygon o MultiPolygon)
- `area_m2`: Área en m²
- `confidence`: Puntuación de confianza (0-1)
- `data_source`: Fuente de datos
- `created_at`: Fecha de creación

**Índices:**
- `geom_2dsphere`: Índice espacial
- `muni_code_idx`: Índice simple
- `area_m2_idx`: Índice simple
- `confidence_idx`: Índice simple
- `muni_code_area_idx`: Índice compuesto

## Requisitos

- MongoDB 5.0+
- mongosh (MongoDB Shell)

## Notas

- Todos los scripts usan GeoJSON con coordenadas WGS84 (EPSG:4326)
- Los índices 2dsphere soportan consultas espaciales como `$geoWithin`, `$geoIntersects`, `$near`
- La validación de esquema asegura integridad de datos
