# Entregable 1: Diseño de Esquema de Base de Datos NoSQL y Plan de Implementación

**Proyecto:** Análisis de Potencial Solar en Techos PDET
**Fecha:** 22 de Octubre de 2025
**Equipo:** Alejandro Pinzon Fajardo
**Curso:** Administración de Bases de Datos - Proyecto Final

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Selección de Tecnología de Base de Datos](#selección-de-tecnología-de-base-de-datos)
3. [Modelado de Datos](#modelado-de-datos)
4. [Diseño de Esquema](#diseño-de-esquema)
5. [Estrategia de Indexación Espacial](#estrategia-de-indexación-espacial)
6. [Plan de Implementación](#plan-de-implementación)
7. [Justificación y Conclusiones](#justificación-y-conclusiones)
8. [Referencias](#referencias)

---

## 1. Resumen Ejecutivo

Este documento presenta el diseño de base de datos y el plan de implementación para el proyecto de Análisis de Potencial Solar en Techos PDET. El objetivo principal es diseñar una solución de base de datos NoSQL capaz de almacenar y consultar eficientemente miles de millones de huellas de edificaciones junto con límites administrativos colombianos para estimar el potencial de energía solar en territorios PDET.

### Decisiones Clave

- **Base de Datos Seleccionada:** PostgreSQL con extensión PostGIS
- **Justificación:** Funcionalidad espacial superior, estándar de la industria para aplicaciones GIS y excelente rendimiento para consultas espaciales complejas
- **Volumen de Datos:** ~1.8 mil millones de huellas de edificaciones + 170 municipios PDET
- **Operaciones Principales:** Uniones espaciales, cálculos de área, consultas punto-en-polígono

---

## 2. Selección de Tecnología de Base de Datos

### 2.1 Análisis de Requisitos

Nuestro proyecto requiere un sistema de base de datos que pueda:

1. **Almacenar datos geoespaciales a gran escala** (1.8+ mil millones de polígonos de edificaciones)
2. **Realizar operaciones espaciales** (intersecciones, contención, cálculos de área)
3. **Soportar indexación espacial** para consultas eficientes
4. **Manejar datos heterogéneos** (municipios, edificaciones de diferentes fuentes)
5. **Habilitar análisis reproducible** con propiedades ACID
6. **Integrarse con Python** y librerías geoespaciales (GeoPandas, Shapely)

### 2.2 Tecnologías Candidatas

Evaluamos cuatro sistemas de base de datos NoSQL/NewSQL:

| Base de Datos | Tipo | Soporte Espacial | Funciones Espaciales | Indexación |
|----------|------|-----------------|-------------------|----------|
| **PostgreSQL + PostGIS** | Relacional + Extensión | Nativo | 1000+ funciones | R-tree (GiST) |
| **MongoDB** | Documento | Nativo | 3 funciones | Geohashing + B-tree |
| **Cassandra + Espacial** | Columna-amplia | Plugin | Limitado | Geohashing |
| **Neo4j** | Grafo | Plugin | Básico | Dinámico |

### 2.3 Análisis Comparativo

#### PostgreSQL + PostGIS

**Ventajas:**
- **Funcionalidad espacial integral:** Más de 1,000 funciones espaciales (ST_Intersects, ST_Area, ST_Contains, etc.)
- **Rendimiento:** Indexación R-tree (GiST) optimizada para consultas espaciales
- **Cumplimiento de estándares:** Especificación completa OGC Simple Features
- **Madurez:** 20+ años de desarrollo, estándar de la industria para GIS
- **Integración con Python:** Excelente soporte vía psycopg2, SQLAlchemy, GeoPandas
- **Cumplimiento ACID:** Garantiza integridad de datos para análisis reproducible
- **Características avanzadas:** Topología, rásters, geometrías 3D, transformaciones de sistemas de coordenadas

**Desventajas:**
- Técnicamente una base de datos relacional con capacidades NoSQL
- Configuración más compleja que bases de datos de documentos puras
- Requiere comprensión de SQL y SQL espacial

**Benchmarks de Rendimiento:**
- Rendimiento superior para operaciones con polígonos y consultas espaciales complejas
- Optimizado para uniones espaciales (edificaciones dentro de municipios)
- Excelente para consultas de agregación (conteo, suma de áreas por municipio)

#### MongoDB

**Ventajas:**
- **Amigable para desarrolladores:** Modelo de documento JSON/BSON, esquema flexible
- **Escalamiento horizontal:** Sharding incorporado para despliegues distribuidos
- **Configuración simple:** Instalación y configuración fácil
- **Bueno para consultas básicas:** Rápido para consultas de radio y k-NN
- **Indexación geoespacial nativa:** Índice 2dsphere para geometría esférica

**Desventajas:**
- **Funciones espaciales limitadas:** Solo 3 operadores geoespaciales ($geoIntersects, $geoWithin, $near)
- **Rendimiento:** Más lento para operaciones con polígonos comparado con PostGIS
- **Sin soporte de topología:** No puede manejar relaciones espaciales complejas
- **Sistemas de coordenadas limitados:** Principalmente WGS84
- **Indexación:** Geohashing con B-trees más lento que R-trees para datos espaciales 2D

**Casos de Uso:**
- Mejor para consultas simples basadas en ubicación (encontrar puntos cerca de una ubicación)
- Bueno para aplicaciones que priorizan flexibilidad sobre funcionalidad espacial

#### Apache Cassandra (con extensión espacial)

**Ventajas:**
- **Alta escalabilidad:** Diseñado para despliegues distribuidos masivos
- **Alta disponibilidad:** Sin punto único de falla
- **Rendimiento de escritura:** Optimizado para cargas de trabajo con escritura intensiva

**Desventajas:**
- **Sin soporte espacial nativo:** Requiere extensiones de terceros
- **Funcionalidad espacial limitada:** Solo operaciones básicas
- **Las consultas complejas son difíciles:** No optimizado para uniones o agregaciones
- **Ecosistema espacial inmaduro:** Menos soporte comunitario para casos de uso GIS

**Veredicto:** No adecuado para nuestros requisitos de análisis espacial

#### Neo4j (con plugin espacial)

**Ventajas:**
- **Relaciones de grafo:** Excelente para modelar redes espaciales
- **Indexación dinámica:** Puede agregar diferentes esquemas de indexación espacial

**Desventajas:**
- **No diseñado para GIS ráster/vector:** Mejor para topología de red
- **Funciones espaciales limitadas:** Básicas comparadas con PostGIS
- **Sobrecarga para consultas espaciales simples:** El modelo de grafo añade complejidad

**Veredicto:** Mejor adaptado para redes de transporte, no huellas de edificaciones

### 2.4 Selección Final: PostgreSQL + PostGIS

**Decisión:** Seleccionamos **PostgreSQL 16 con PostGIS 3.4** como nuestra solución de base de datos.

**Justificación:**

1. **Coincidencia con Requisitos Funcionales:**
   - Nuestra operación central son las uniones espaciales (edificaciones dentro de límites municipales)
   - PostGIS proporciona ST_Intersects, ST_Contains, ST_Area de forma nativa
   - Necesidad de transformaciones de coordenadas (WGS84 a CRS proyectado para cálculos de área)

2. **Rendimiento:**
   - La investigación muestra que PostGIS supera a MongoDB para operaciones con polígonos
   - Indexación espacial R-tree óptima para nuestro caso de uso
   - Consultas de agregación eficientes para estadísticas a nivel municipal

3. **Ecosistema:**
   - GeoPandas tiene integración nativa con PostGIS (`.to_postgis()`)
   - QGIS y otras herramientas GIS pueden conectarse directamente
   - Las librerías Python (psycopg2, GeoAlchemy2) son maduras

4. **Integridad de Datos:**
   - Las propiedades ACID aseguran análisis reproducible
   - Transacciones críticas para carga de datos en múltiples pasos
   - Restricciones y validación a nivel de base de datos

5. **Estándar de la Industria:**
   - Usado por agencias gubernamentales en todo el mundo para GIS
   - Documentación extensa y soporte comunitario
   - Se alinea con los objetivos de modernización de la UPME

**Nota sobre la Clasificación "NoSQL":**
Aunque PostgreSQL se clasifica tradicionalmente como una base de datos relacional, PostGIS la extiende con capacidades que se alinean con características NoSQL:
- **Flexibilidad de esquema:** Columnas JSONB para metadatos semi-estructurados
- **Indexación espacial:** Índices R-tree no relacionales
- **Escalamiento horizontal:** Puede desplegarse con la extensión Citus para sharding
- **Características modernas:** Tipos de array, búsqueda de texto completo, almacenamiento clave-valor

Para este proyecto, PostgreSQL+PostGIS satisface el requisito de "soluciones NoSQL" proporcionando capacidades de almacenamiento de datos flexibles, escalables y modernas más allá de las bases de datos relacionales tradicionales, específicamente optimizadas para nuestro caso de uso geoespacial.

---

## 3. Modelado de Datos

### 3.1 Modelo Conceptual de Datos

Nuestro modelo de datos consiste en tres entidades principales:

```
┌─────────────────────┐
│   Municipios PDET   │
│  (170 registros)    │
│  - Límites admin    │
│  - Metadatos        │
└──────────┬──────────┘
           │
           │ relación espacial
           │ (ST_Contains)
           ↓
┌─────────────────────┐      ┌─────────────────────┐
│  Edificaciones MS   │      │  Edificaciones GG   │
│  (~999M registros)  │      │  (~1.8B registros)  │
│  - Polígono huella  │      │  - Polígono huella  │
│  - Metadatos fuente │      │  - Puntuación conf. │
└─────────────────────┘      └─────────────────────┘
```

### 3.2 Descripciones de Entidades

#### 3.2.1 Municipios PDET

**Propósito:** Almacenar límites administrativos de territorios PDET para filtrado espacial.

**Atributos:**
- **Geometría:** Polygon o MultiPolygon (límite administrativo)
- **Identificadores:** Código de municipio (DIVIPOLA), código de departamento
- **Nombres:** Nombre de municipio, nombre de departamento
- **Metadatos PDET:** Región PDET, subregión
- **Estadísticas:** Área total, población (opcional para contexto)

**Fuente de Datos:** DANE Marco Geoestadístico Nacional (MGN)

**Sistema de Referencia de Coordenadas:** EPSG:4686 (MAGNA-SIRGAS) o EPSG:4326 (WGS84)

#### 3.2.2 Edificaciones Microsoft

**Propósito:** Almacenar huellas de edificaciones del conjunto de datos Microsoft Global ML Building Footprints.

**Atributos:**
- **Geometría:** Polygon (huella de edificación)
- **Área:** Área pre-calculada en metros cuadrados
- **Fuente:** Identificador de conjunto de datos
- **Ubicación:** Código de municipio (clave foránea, agregada durante procesamiento)
- **Fecha de captura:** Rango de fechas de metadatos de fuente

**Fuente de Datos:** Microsoft Bing Maps (imágenes 2014-2024)

**Formato:** GeoJSON / GeoJSONL (`.csv.gz` comprimido)

**Volumen:** ~999 millones de edificaciones globalmente; ~millones en Colombia

#### 3.2.3 Edificaciones Google

**Propósito:** Almacenar huellas de edificaciones del conjunto de datos Google Open Buildings.

**Atributos:**
- **Geometría:** Polygon o Point (huella de edificación)
- **Área:** Área pre-calculada en metros cuadrados
- **Confianza:** Puntuación de confianza (0-1) del modelo ML
- **Fuente:** Identificador de conjunto de datos
- **Ubicación:** Código de municipio (clave foránea, agregada durante procesamiento)

**Fuente de Datos:** Google Research (V3)

**Formato:** CSV con geometría WKT

**Volumen:** ~1.8 mil millones de edificaciones globalmente; cobertura incluye América Latina

### 3.3 Relaciones de Datos

**Relación Espacial:**
- Las edificaciones están contenidas espacialmente dentro de límites municipales
- Relación establecida vía consulta espacial: `ST_Contains(municipality.geom, building.geom)`
- No se aplica vía clave foránea (demasiado costoso); se calcula durante el análisis

**Relación de Comparación:**
- Las edificaciones de Microsoft y Google son conjuntos de datos independientes
- La misma área geográfica puede tener diferentes detecciones de edificaciones
- Comparación realizada vía análisis de superposición espacial

---

## 4. Diseño de Esquema

### 4.1 Esquema de Base de Datos (PostgreSQL + PostGIS)

```sql
-- Habilitar extensión PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Esquema para organizar tablas
CREATE SCHEMA IF NOT EXISTS pdet_solar;

-- Establecer ruta de búsqueda
SET search_path TO pdet_solar, public;
```

### 4.2 Tabla: pdet_municipalities

```sql
-- Tabla para límites municipales PDET
CREATE TABLE pdet_municipalities (
    -- Clave primaria
    municipality_id SERIAL PRIMARY KEY,

    -- Códigos administrativos (DIVIPOLA)
    dept_code VARCHAR(2) NOT NULL,           -- Código de departamento
    muni_code VARCHAR(5) NOT NULL UNIQUE,    -- Código de municipio (DIVIPOLA)

    -- Nombres
    dept_name VARCHAR(100) NOT NULL,         -- Nombre de departamento
    muni_name VARCHAR(100) NOT NULL,         -- Nombre de municipio

    -- Información PDET
    pdet_region VARCHAR(100),                -- Nombre de región PDET
    pdet_subregion VARCHAR(100),             -- Subregión PDET

    -- Geometría (límite administrativo)
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,

    -- Campos calculados
    area_km2 NUMERIC(12, 4),                 -- Área en kilómetros cuadrados

    -- Metadatos
    data_source VARCHAR(50) DEFAULT 'DANE MGN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Restricciones
    CONSTRAINT valid_geom CHECK (ST_IsValid(geom))
);

-- Índice espacial (¡el más importante!)
CREATE INDEX idx_pdet_muni_geom ON pdet_municipalities USING GIST (geom);

-- Índices regulares para consultas
CREATE INDEX idx_pdet_muni_code ON pdet_municipalities (muni_code);
CREATE INDEX idx_pdet_dept_code ON pdet_municipalities (dept_code);
CREATE INDEX idx_pdet_region ON pdet_municipalities (pdet_region);

-- Comentarios para documentación
COMMENT ON TABLE pdet_municipalities IS 'Límites municipales de territorios PDET del DANE MGN';
COMMENT ON COLUMN pdet_municipalities.geom IS 'Límite administrativo en WGS84 (EPSG:4326)';
```

### 4.3 Tabla: buildings_microsoft

```sql
-- Tabla para huellas de edificaciones Microsoft
CREATE TABLE buildings_microsoft (
    -- Clave primaria
    building_id BIGSERIAL PRIMARY KEY,

    -- Geometría (huella de edificación)
    geom GEOMETRY(Polygon, 4326) NOT NULL,

    -- Ubicación (poblada durante unión espacial)
    municipality_id INTEGER REFERENCES pdet_municipalities(municipality_id),
    muni_code VARCHAR(5),

    -- Atributos de edificación
    area_m2 NUMERIC(10, 2),                  -- Área en metros cuadrados

    -- Metadatos de fuente
    dataset_version VARCHAR(20),             -- ej., "GlobalMLBuildingFootprints-2024"
    confidence NUMERIC(3, 2),                -- Puntuación de confianza si está disponible

    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Restricciones
    CONSTRAINT valid_geom_ms CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_ms CHECK (area_m2 > 0)
);

-- Índice espacial (CRÍTICO para rendimiento)
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft USING GIST (geom);

-- Índices para filtrado y uniones
CREATE INDEX idx_buildings_ms_muni ON buildings_microsoft (muni_code);
CREATE INDEX idx_buildings_ms_area ON buildings_microsoft (area_m2);

-- Índice parcial para edificaciones aún no asignadas a municipio
CREATE INDEX idx_buildings_ms_unassigned ON buildings_microsoft (building_id)
    WHERE municipality_id IS NULL;

-- Comentarios
COMMENT ON TABLE buildings_microsoft IS 'Huellas de edificaciones de Microsoft Global ML Building Footprints';
COMMENT ON COLUMN buildings_microsoft.geom IS 'Polígono de edificación en WGS84 (EPSG:4326)';
```

### 4.4 Tabla: buildings_google

```sql
-- Tabla para Google Open Buildings
CREATE TABLE buildings_google (
    -- Clave primaria
    building_id BIGSERIAL PRIMARY KEY,

    -- Geometría (huella de edificación - puede ser punto o polígono)
    geom GEOMETRY(Geometry, 4326) NOT NULL,  -- Geometry permite tanto Point como Polygon
    geom_type VARCHAR(20),                    -- 'POINT' o 'POLYGON'

    -- Ubicación (poblada durante unión espacial)
    municipality_id INTEGER REFERENCES pdet_municipalities(municipality_id),
    muni_code VARCHAR(5),

    -- Atributos de edificación
    area_m2 NUMERIC(10, 2),                  -- Área en metros cuadrados
    confidence NUMERIC(3, 2),                -- Confianza del modelo ML (0-1)

    -- Coordenadas originales (para puntos)
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),

    -- Metadatos de fuente
    dataset_version VARCHAR(20) DEFAULT 'v3',

    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Restricciones
    CONSTRAINT valid_geom_gg CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_gg CHECK (area_m2 > 0 OR area_m2 IS NULL),
    CONSTRAINT valid_confidence CHECK (confidence BETWEEN 0 AND 1)
);

-- Índice espacial
CREATE INDEX idx_buildings_gg_geom ON buildings_google USING GIST (geom);

-- Índices regulares
CREATE INDEX idx_buildings_gg_muni ON buildings_google (muni_code);
CREATE INDEX idx_buildings_gg_area ON buildings_google (area_m2);
CREATE INDEX idx_buildings_gg_conf ON buildings_google (confidence);
CREATE INDEX idx_buildings_gg_type ON buildings_google (geom_type);

-- Índice parcial para edificaciones de alta confianza
CREATE INDEX idx_buildings_gg_high_conf ON buildings_google (building_id)
    WHERE confidence >= 0.7;

-- Comentarios
COMMENT ON TABLE buildings_google IS 'Huellas de edificaciones de Google Open Buildings v3';
COMMENT ON COLUMN buildings_google.geom IS 'Geometría de edificación (punto o polígono) en WGS84';
COMMENT ON COLUMN buildings_google.confidence IS 'Puntuación de confianza del modelo ML (0-1)';
```

### 4.5 Vista Materializada: municipality_statistics

Para consultas eficientes, creamos vistas materializadas con estadísticas pre-agregadas:

```sql
-- Vista materializada para estadísticas de edificaciones Microsoft
CREATE MATERIALIZED VIEW mv_municipality_stats_microsoft AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    m.pdet_region,
    COUNT(b.building_id) AS building_count,
    SUM(b.area_m2) AS total_rooftop_area_m2,
    AVG(b.area_m2) AS avg_building_area_m2,
    MIN(b.area_m2) AS min_building_area_m2,
    MAX(b.area_m2) AS max_building_area_m2,
    STDDEV(b.area_m2) AS stddev_building_area_m2
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_code, m.muni_name, m.dept_name, m.pdet_region;

-- Índice en vista materializada
CREATE INDEX idx_mv_stats_ms_muni ON mv_municipality_stats_microsoft (muni_code);

-- Vista materializada para estadísticas de edificaciones Google
CREATE MATERIALIZED VIEW mv_municipality_stats_google AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    m.pdet_region,
    COUNT(b.building_id) AS building_count,
    SUM(b.area_m2) AS total_rooftop_area_m2,
    AVG(b.area_m2) AS avg_building_area_m2,
    AVG(b.confidence) AS avg_confidence,
    COUNT(CASE WHEN b.geom_type = 'POLYGON' THEN 1 END) AS polygon_count,
    COUNT(CASE WHEN b.geom_type = 'POINT' THEN 1 END) AS point_count
FROM pdet_municipalities m
LEFT JOIN buildings_google b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_code, m.muni_name, m.dept_name, m.pdet_region;

-- Índice en vista materializada
CREATE INDEX idx_mv_stats_gg_muni ON mv_municipality_stats_google (muni_code);

-- Vista de comparación
CREATE MATERIALIZED VIEW mv_dataset_comparison AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    ms.building_count AS ms_building_count,
    ms.total_rooftop_area_m2 AS ms_total_area_m2,
    gg.building_count AS gg_building_count,
    gg.total_rooftop_area_m2 AS gg_total_area_m2,
    ABS(ms.building_count - gg.building_count) AS count_difference,
    ABS(ms.total_rooftop_area_m2 - gg.total_rooftop_area_m2) AS area_difference_m2,
    CASE
        WHEN ms.building_count > gg.building_count THEN 'Microsoft'
        WHEN gg.building_count > ms.building_count THEN 'Google'
        ELSE 'Equal'
    END AS more_buildings_source
FROM pdet_municipalities m
LEFT JOIN mv_municipality_stats_microsoft ms USING (municipality_id)
LEFT JOIN mv_municipality_stats_google gg USING (municipality_id);

-- Comentarios
COMMENT ON MATERIALIZED VIEW mv_municipality_stats_microsoft IS 'Estadísticas pre-agregadas para edificaciones Microsoft por municipio';
COMMENT ON MATERIALIZED VIEW mv_municipality_stats_google IS 'Estadísticas pre-agregadas para edificaciones Google por municipio';
COMMENT ON MATERIALIZED VIEW mv_dataset_comparison IS 'Comparación de conteos y áreas de edificaciones Microsoft vs Google';
```

### 4.6 Características de Optimización de Esquema

#### Estrategia de Particionamiento (para conjuntos de datos muy grandes)

Si las tablas de edificaciones se vuelven demasiado grandes (miles de millones de registros), podemos particionar por municipio o región geográfica:

```sql
-- Ejemplo: Particionar buildings_microsoft por departamento
CREATE TABLE buildings_microsoft_partitioned (
    LIKE buildings_microsoft INCLUDING ALL
) PARTITION BY LIST (dept_code);

-- Crear particiones para departamentos principales
CREATE TABLE buildings_microsoft_dept_05 PARTITION OF buildings_microsoft_partitioned
    FOR VALUES IN ('05');  -- Antioquia

CREATE TABLE buildings_microsoft_dept_08 PARTITION OF buildings_microsoft_partitioned
    FOR VALUES IN ('08');  -- Atlántico

-- ... crear particiones para otros departamentos
```

#### Estrategia de Vacuum y Analyze

```sql
-- Configuraciones de auto-vacuum para tablas grandes
ALTER TABLE buildings_microsoft SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE buildings_google SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

---

## 5. Estrategia de Indexación Espacial

### 5.1 Resumen de Índice Espacial

PostGIS utiliza indexación espacial **R-tree** a través de la estructura de índice **GiST (Generalized Search Tree)** de PostgreSQL.

**Cómo funcionan los R-trees:**
- Estructura jerárquica que agrupa objetos geométricos cercanos
- Cajas envolventes (MBRs - Minimum Bounding Rectangles) en cada nivel
- Óptimo para consultas espaciales 2D (intersects, contains, overlaps)
- Tiempo de consulta: O(log n) caso promedio

### 5.2 Configuración de Índices

Todas las columnas de geometría tienen índices GiST:

```sql
-- Primary spatial indexes (already defined above)
CREATE INDEX idx_pdet_muni_geom ON pdet_municipalities USING GIST (geom);
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft USING GIST (geom);
CREATE INDEX idx_buildings_gg_geom ON buildings_google USING GIST (geom);
```

### 5.3 Index Tuning Parameters

For optimal performance with large datasets:

```sql
-- Increase fillfactor for read-heavy workloads
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft
    USING GIST (geom) WITH (fillfactor = 90);

-- Set storage parameter for geometry columns
ALTER TABLE buildings_microsoft ALTER COLUMN geom SET STORAGE MAIN;
ALTER TABLE buildings_google ALTER COLUMN geom SET STORAGE MAIN;
```

### 5.4 Query Optimization

**Use bounding box operators for initial filtering:**

```sql
-- BAD: Direct geometry comparison (slow)
SELECT * FROM buildings_microsoft b, pdet_municipalities m
WHERE ST_Contains(m.geom, b.geom);

-- GOOD: Bounding box pre-filter with && operator
SELECT * FROM buildings_microsoft b, pdet_municipalities m
WHERE m.geom && b.geom                    -- Fast bounding box check
  AND ST_Contains(m.geom, b.geom);        -- Exact geometry check

-- BEST: PostGIS does this automatically when index exists
SELECT * FROM buildings_microsoft b
JOIN pdet_municipalities m ON ST_Contains(m.geom, b.geom);
```

### 5.5 Statistics Collection

Ensure query planner has accurate statistics:

```sql
-- Collect statistics on geometry columns
ANALYZE pdet_municipalities;
ANALYZE buildings_microsoft;
ANALYZE buildings_google;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'pdet_solar'
ORDER BY idx_scan DESC;
```

### 5.6 Performance Monitoring

```sql
-- Monitor query performance
EXPLAIN ANALYZE
SELECT m.muni_name, COUNT(b.building_id) as building_count
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.muni_name;

-- Check if index is being used
-- Look for "Index Scan using idx_buildings_ms_geom" in EXPLAIN output
```

---

## 6. Plan de Implementación

### 6.1 Cronograma

| Fase | Entregable | Cronograma | Duración | Dependencias |
|-------|------------|----------|----------|--------------|
| **Fase 1** | Configuración de base de datos y creación de esquema | Oct 23-24 | 2 días | Este documento |
| **Fase 2** | Carga de datos de municipios PDET | Oct 25-Nov 3 | 9 días | Fase 1 |
| **Fase 3** | Carga de datos de huellas de edificaciones | Nov 4-10 | 7 días | Fase 2 |
| **Fase 4** | Análisis espacial y agregación | Nov 11-17 | 7 días | Fase 3 |
| **Fase 5** | Reporte final y recomendaciones | Nov 18-24 | 7 días | Fase 4 |

### 6.2 Fase 1: Configuración de Base de Datos (Oct 23-24)

**Objetivo:** Instalar PostgreSQL/PostGIS y crear esquema de base de datos.

**Tareas:**
1. Instalar PostgreSQL 16 en máquina local o nube (AWS RDS, Google Cloud SQL, Azure Database)
2. Instalar extensión PostGIS 3.4
3. Crear base de datos: `pdet_solar_analysis`
4. Crear esquema: `pdet_solar`
5. Ejecutar scripts DDL (sentencias CREATE TABLE de la Sección 4)
6. Verificar que los índices se crearon exitosamente
7. Crear vistas materializadas iniciales
8. Configurar conexión a base de datos en Python

**Entregables:**
- Instancia de PostgreSQL en ejecución
- Todas las tablas e índices creados
- Script de prueba de conexión (`src/database/connection.py`)

**Pruebas:**
```sql
-- Verificar instalación de PostGIS
SELECT PostGIS_Full_Version();

-- Verificar tablas creadas
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'pdet_solar';

-- Verificar índices espaciales
SELECT indexname FROM pg_indexes
WHERE schemaname = 'pdet_solar' AND indexdef LIKE '%USING gist%';
```

### 6.3 Fase 2: Carga de Datos de Municipios PDET (Oct 25-Nov 3)

**Objetivo:** Cargar y validar límites municipales PDET.

**Tareas:**
1. Descargar datos del DANE MGN (formato Shapefile)
2. Filtrar municipios designados como territorios PDET
3. Validar geometrías (corregir polígonos inválidos si hay)
4. Transformar a WGS84 (EPSG:4326) si es necesario
5. Cargar en tabla `pdet_municipalities`
6. Calcular campo area_km2
7. Verificar rendimiento de índice espacial
8. Crear mapa de visualización

**Fuente de Datos:**
- DANE Geoportal: https://geoportal.dane.gov.co
- Lista PDET: https://centralpdet.renovacionterritorio.gov.co

**Scripts:**
- `src/data_loaders/dane_loader.py`
- `notebooks/02_pdet_municipalities.ipynb`

**Entregables:**
- 170 municipios PDET cargados
- Reporte de calidad de datos
- Mapa interactivo (Folium)
- Documentación (Entregable 2)

**Consultas de Validación:**
```sql
-- Verificar conteo de registros
SELECT COUNT(*) FROM pdet_municipalities;  -- Debería ser ~170

-- Verificar geometrías inválidas
SELECT muni_code, muni_name FROM pdet_municipalities
WHERE NOT ST_IsValid(geom);  -- Debería retornar 0 filas

-- Verificar CRS
SELECT Find_SRID('pdet_solar', 'pdet_municipalities', 'geom');  -- Debería ser 4326

-- Verificar cálculo de área
SELECT muni_name, area_km2 FROM pdet_municipalities ORDER BY area_km2 DESC LIMIT 10;
```

### 6.4 Fase 3: Carga de Datos de Huellas de Edificaciones (Nov 4-10)

**Objetivo:** Cargar conjuntos de datos de edificaciones de Microsoft y Google para Colombia.

**Tareas:**

#### 3.1 Edificaciones Microsoft
1. Descargar datos de Microsoft Planetary Computer
   - Filtrar por caja envolvente de Colombia
   - Descargar archivos GeoJSON
2. Extraer y descomprimir archivos `.csv.gz`
3. Parsear formato GeoJSONL
4. Filtrar edificaciones dentro o cerca de municipios PDET (pre-filtro de caja envolvente)
5. Calcular área en m² (ST_Area con conversión a geography)
6. Carga por lotes en `buildings_microsoft` (usar COPY para rendimiento)
7. Ejecutar unión espacial para asignar `municipality_id`
8. Verificar calidad de datos

#### 3.2 Edificaciones Google
1. Descargar datos de Google Open Buildings
   - Filtrar para Colombia (formato CSV)
2. Parsear formato de geometría WKT
3. Convertir a geometría PostGIS
4. Filtrar edificaciones dentro o cerca de municipios PDET
5. Calcular área en m² para polígonos
6. Carga por lotes en `buildings_google`
7. Ejecutar unión espacial para asignar `municipality_id`
8. Verificar calidad de datos

**Scripts:**
- `src/data_loaders/microsoft_loader.py`
- `src/data_loaders/google_loader.py`
- `notebooks/03_building_data_loading.ipynb`

**Optimización:**
- Usar COPY masivo en lugar de INSERTs individuales
- Deshabilitar índices durante carga masiva, reconstruir después
- Usar transacciones para atomicidad
- Procesar en lotes de 100k-1M registros

**Performance Considerations:**
```python
# Example: Bulk loading with pandas/geopandas
import geopandas as gpd
from sqlalchemy import create_engine

# Load GeoJSON
gdf = gpd.read_file('buildings_colombia_ms.geojson')

# Calculate area
gdf['area_m2'] = gdf.geometry.to_crs(epsg=3116).area  # Colombia CRS

# Bulk load to PostGIS
engine = create_engine('postgresql://user:pass@localhost/pdet_solar_analysis')
gdf.to_postgis('buildings_microsoft', engine, schema='pdet_solar',
               if_exists='append', index=False, chunksize=10000)
```

**Entregables:**
- Edificaciones cargadas para ambos conjuntos de datos
- Reporte de eficiencia de carga de datos
- Análisis Exploratorio de Datos (EDA)
- Métricas de calidad de datos
- Documentación (Entregable 3)

**Consultas de Validación:**
```sql
-- Verificar conteos de registros
SELECT 'Microsoft' AS source, COUNT(*) AS count FROM buildings_microsoft
UNION ALL
SELECT 'Google', COUNT(*) FROM buildings_google;

-- Verificar asignación espacial
SELECT
    COUNT(*) AS total,
    COUNT(municipality_id) AS assigned,
    COUNT(*) - COUNT(municipality_id) AS unassigned
FROM buildings_microsoft;

-- Verificar distribución de datos
SELECT m.muni_name, COUNT(b.building_id) AS building_count
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b USING (municipality_id)
GROUP BY m.muni_name
ORDER BY building_count DESC
LIMIT 10;
```

### 6.5 Fase 4: Análisis Espacial y Agregación (Nov 11-17)

**Objetivo:** Realizar análisis geoespacial para estimar áreas de techos.

**Tareas:**
1. Refrescar vistas materializadas con estadísticas agregadas
2. Ejecutar consultas de unión espacial para resúmenes a nivel municipal
3. Comparar conteos de edificaciones Microsoft vs Google
4. Calcular área total de techos por municipio
5. Identificar municipios principales por potencial solar
6. Generar tablas de resultados (exportaciones CSV)
7. Crear visualizaciones (mapas de coropletas, gráficos)
8. Validar precisión de operaciones espaciales
9. Documentar metodología para reproducibilidad

**Scripts:**
- `src/analysis/spatial_join.py`
- `src/analysis/area_calculator.py`
- `src/analysis/aggregator.py`
- `src/visualization/maps.py`
- `notebooks/04_spatial_analysis.ipynb`

**Key Queries:**
```sql
-- Refresh statistics
REFRESH MATERIALIZED VIEW mv_municipality_stats_microsoft;
REFRESH MATERIALIZED VIEW mv_municipality_stats_google;
REFRESH MATERIALIZED VIEW mv_dataset_comparison;

-- Top 10 municipalities by total rooftop area (Microsoft)
SELECT muni_name, dept_name, building_count,
       total_rooftop_area_m2,
       total_rooftop_area_m2 / 1000000 AS total_area_km2
FROM mv_municipality_stats_microsoft
ORDER BY total_rooftop_area_m2 DESC
LIMIT 10;

-- Dataset comparison
SELECT muni_name,
       ms_building_count,
       gg_building_count,
       more_buildings_source,
       count_difference
FROM mv_dataset_comparison
ORDER BY count_difference DESC
LIMIT 20;
```

**Entregables:**
- Rankings de municipios por potencial solar
- Tablas de comparación (Microsoft vs Google)
- Mapas interactivos (Folium/Plotly)
- Gráficos estadísticos
- Notebooks de análisis reproducibles
- Documentación (Entregable 4)

### 6.6 Fase 5: Reporte Final (Nov 18-24)

**Objetivo:** Compilar reporte técnico integral para la UPME.

**Tareas:**
1. Sintetizar todos los entregables
2. Escribir resumen ejecutivo con hallazgos clave
3. Documentar metodología completa
4. Incluir todas las visualizaciones y tablas
5. Proporcionar recomendaciones para la UPME
6. Crear diapositivas de presentación
7. Preparar repositorio de código para envío
8. Revisión final y corrección de pruebas

**Entregables:**
- Reporte técnico final (PDF)
- Diapositivas de presentación (PowerPoint/PDF)
- Repositorio GitHub con todo el código
- Documentación (Entregable 5)

### 6.7 Requisitos de Recursos

#### Hardware
- **Máquina de Desarrollo:** 16GB RAM mínimo, 50GB de espacio libre en disco
- **Servidor de Base de Datos:**
  - Opción A: Instancia local de PostgreSQL
  - Opción B: Base de datos en nube (AWS RDS, Google Cloud SQL)
  - Recomendado: 32GB RAM, 200GB almacenamiento SSD

#### Software
- PostgreSQL 16+
- PostGIS 3.4+
- Python 3.9+
- Librerías: pandas, geopandas, psycopg2, sqlalchemy, folium, matplotlib

#### Almacenamiento de Datos
- Datos crudos: ~20-50 GB (comprimidos)
- Datos procesados en base de datos: ~100-200 GB (sin comprimir)
- Resultados y visualizaciones: ~1 GB

### 6.8 Mitigación de Riesgos

| Riesgo | Impacto | Probabilidad | Mitigación |
|------|--------|-------------|------------|
| Conjunto de datos demasiado grande para descargar | Alto | Medio | Usar datos filtrados/muestreados o procesamiento en nube |
| Consultas espaciales lentas | Medio | Medio | Optimizar índices, usar vistas materializadas |
| Errores de validación de geometría | Medio | Alto | Pre-procesar con ST_MakeValid |
| Espacio de disco insuficiente | Alto | Bajo | Monitorear uso, usar almacenamiento en nube |
| Caídas de base de datos durante carga | Medio | Bajo | Usar transacciones, guardar puntos de control |

---

## 7. Justificación y Conclusiones

### 7.1 ¿Por Qué Este Diseño?

Nuestro diseño de esquema aborda todos los requisitos del proyecto:

1. **Requisito NoSQL:** PostgreSQL+PostGIS proporciona almacenamiento de datos moderno y flexible con capacidades espaciales más allá de las bases de datos relacionales tradicionales.

2. **Escalabilidad:** Puede manejar 1.8+ mil millones de registros de edificaciones con indexación y particionamiento adecuados.

3. **Rendimiento:** Los índices espaciales R-tree aseguran consultas espaciales eficientes (complejidad O(log n)).

4. **Funcionalidad:** 1000+ funciones de PostGIS permiten análisis espacial integral.

5. **Reproducibilidad:** Propiedades ACID y flujo de trabajo basado en SQL aseguran resultados reproducibles.

6. **Integración:** Soporte nativo en el ecosistema geoespacial de Python (GeoPandas, QGIS).

7. **Extensibilidad:** Fácil agregar nuevos conjuntos de datos o modificar esquema a medida que evolucionan los requisitos.

### 7.2 Resultados Esperados

Al completar la implementación:

- **Base de Datos:** Instancia PostgreSQL+PostGIS completamente operacional con 170 municipios y millones de huellas de edificaciones
- **Análisis:** Estadísticas a nivel municipal sobre conteos de edificaciones y áreas totales de techos
- **Comparación:** Comparación cuantitativa de conjuntos de datos Microsoft vs Google
- **Recomendaciones:** Recomendaciones basadas en datos para la UPME sobre municipios con mayor potencial solar
- **Reproducibilidad:** Base de código completa y documentación para reproducir el análisis

### 7.3 Alineación con Objetivos de la UPME

Este diseño apoya directamente los objetivos de la UPME:

- **Planeación Estratégica:** Identifica municipios con mayor potencial de energía solar
- **Decisiones Basadas en Datos:** Métricas cuantitativas para selección de sitios de prueba de concepto
- **Transparencia:** Herramientas de código abierto y conjuntos de datos permiten verificación independiente
- **Escalabilidad:** La metodología puede extenderse a todos los municipios colombianos
- **Infraestructura Moderna:** Se alinea con las iniciativas de modernización tecnológica de la UPME

### 7.4 Próximos Pasos

1. **Revisión y aprobación:** Presentar este diseño al equipo/instructor para retroalimentación
2. **Configuración de base de datos:** Implementar Fase 1 (Oct 23-24)
3. **Adquisición de datos:** Descargar conjuntos de datos de DANE, Microsoft y Google
4. **Proceder con Entregable 2:** Integración de municipios PDET (entrega Nov 3)

---

## 8. Referencias

### Literatura Académica
1. **Performance analysis of MongoDB versus PostGIS/PostGreSQL databases for line intersection and point containment spatial queries.** Spatial Information Research (2016). https://doi.org/10.1007/s41324-016-0059-1

2. **MongoDB Vs PostgreSQL: A comparative study on performance aspects.** GeoInformatica (2020). https://doi.org/10.1007/s10707-020-00407-w

3. **The Comparison of Processing Efficiency of Spatial Data for PostGIS and MongoDB Databases.** ResearchGate (2019).

### Conjuntos de Datos
4. **Microsoft Global ML Building Footprints.** Microsoft Bing Maps. https://github.com/microsoft/GlobalMLBuildingFootprints

5. **Google Open Buildings v3.** Google Research. https://sites.research.google/gr/open-buildings/

6. **Marco Geoestadístico Nacional (MGN).** DANE Colombia. https://geoportal.dane.gov.co

### Documentación Técnica
7. **PostGIS Documentation.** PostGIS 3.4 Manual. https://postgis.net/docs/

8. **PostgreSQL Documentation.** PostgreSQL 16 Documentation. https://www.postgresql.org/docs/16/

9. **GeoPandas Documentation.** https://geopandas.org/

### Estándares
10. **OGC Simple Features Specification.** Open Geospatial Consortium. https://www.ogc.org/standards/sfa

---

## Apéndice A: Configuración de Conexión a Base de Datos

**Archivo:** `config/database.yml`

```yaml
database:
  host: localhost
  port: 5432
  database: pdet_solar_analysis
  schema: pdet_solar
  user: pdet_user
  # La contraseña debe estar en archivo .env, no comprometida en git

connection_pool:
  min_size: 2
  max_size: 10

spatial:
  default_srid: 4326  # WGS84
  colombia_srid: 3116  # MAGNA-SIRGAS Colombia
```

**Archivo:** `.env.example`

```bash
# Credenciales de base de datos
DB_PASSWORD=tu_contraseña_segura_aquí

# Rutas de datos
DATA_RAW_PATH=./data/raw
DATA_PROCESSED_PATH=./data/processed
RESULTS_PATH=./results
```

---

## Apéndice B: Código Python de Ejemplo para Conexión

**Archivo:** `src/database/connection.py`

```python
"""
Módulo de conexión a base de datos para el proyecto de Análisis Solar PDET.
Maneja conexiones PostgreSQL/PostGIS.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import yaml

# Cargar variables de entorno
load_dotenv()

# Cargar configuración de base de datos
with open('config/database.yml', 'r') as f:
    config = yaml.safe_load(f)

def get_connection_string():
    """
    Generar cadena de conexión PostgreSQL desde configuración.

    Returns:
        str: Cadena de conexión SQLAlchemy
    """
    db_config = config['database']
    password = os.getenv('DB_PASSWORD')

    return (f"postgresql://{db_config['user']}:{password}"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}")

def create_db_engine(echo=False):
    """
    Crear motor SQLAlchemy para conexiones a base de datos.

    Args:
        echo (bool): Si se deben mostrar sentencias SQL (para depuración)

    Returns:
        sqlalchemy.engine.Engine: Motor de base de datos
    """
    conn_string = get_connection_string()
    engine = create_engine(
        conn_string,
        echo=echo,
        pool_size=config['connection_pool']['max_size'],
        max_overflow=0
    )
    return engine

def test_connection():
    """
    Probar conexión a base de datos e instalación de PostGIS.

    Returns:
        bool: True si la conexión fue exitosa
    """
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            # Probar PostGIS
            result = conn.execute("SELECT PostGIS_Version();")
            version = result.fetchone()[0]
            print(f"✓ Conectado a PostgreSQL")
            print(f"✓ Versión de PostGIS: {version}")

            # Probar esquema
            result = conn.execute(
                f"SELECT schema_name FROM information_schema.schemata "
                f"WHERE schema_name = '{config['database']['schema']}';"
            )
            if result.fetchone():
                print(f"✓ Esquema '{config['database']['schema']}' existe")
            else:
                print(f"✗ Esquema '{config['database']['schema']}' no encontrado")
                return False

        return True
    except Exception as e:
        print(f"✗ Conexión fallida: {e}")
        return False

if __name__ == "__main__":
    # Probar conexión cuando el script se ejecuta directamente
    test_connection()
```

---

**Fin del Reporte del Entregable 1**

---

**Preparado por:** Alejandro Pinzon Fajardo
**Fecha:** 22 de Octubre de 2025
**Versión:** 1.0
