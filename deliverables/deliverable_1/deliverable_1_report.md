# Entregable 1: Diseño de Esquema de Base de Datos NoSQL y Plan de Implementación

**Proyecto:** Análisis de Potencial Solar en Techos PDET
**Fecha:** 22 de Octubre de 2025
**Equipo:** Alejandro Pinzon Fajardo, Juan Jose Bermudez
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

Este documento presenta el diseño de base de datos y el plan de implementación para el proyecto **Análisis de Potencial Solar en Techos PDET**, con el objetivo de diseñar una solución **NoSQL con MongoDB** capaz de almacenar y consultar eficientemente millones de huellas de edificaciones junto con límites administrativos colombianos, para estimar el potencial de energía solar en los territorios PDET.

### Decisiones Clave

- **Base de Datos Seleccionada:** MongoDB  
- **Justificación:** Escalabilidad horizontal, soporte nativo de datos geoespaciales, esquema flexible y facilidad de integración con herramientas modernas de análisis.  
- **Volumen de Datos:** ~1.8 mil millones de huellas de edificaciones + 170 municipios PDET.  
- **Operaciones Principales:** Consultas espaciales ($geoWithin, $geoIntersects), cálculos de área, y análisis geoespacial distribuido.

---

## 2. Selección de Tecnología de Base de Datos

### 2.1 Análisis de Requisitos

Nuestro proyecto requiere un sistema de base de datos que pueda:

1. **Almacenar datos geoespaciales a gran escala.**  
2. **Ejecutar operaciones espaciales** (intersección, contención, distancia).  
3. **Implementar indexación geoespacial 2dsphere.**  
4. **Soportar datos heterogéneos** (municipios, edificaciones, fuentes distintas).  
5. **Integrarse con Python y librerías geoespaciales** (PyMongo, GeoPandas).  
6. **Escalar horizontalmente** con replicación y particionamiento (sharding).

### 2.2 Tecnologías Candidatas

| Base de Datos | Tipo | Soporte Espacial | Indexación | Escalabilidad |
|---------------|------|------------------|-------------|----------------|
| **MongoDB** | Documento | Nativo ($geoWithin, $geoIntersects, $near) | 2dsphere | Sharding nativo |
| **Cassandra (con Spatial)** | Columna-amplia | Limitado | Geohashing | Alta |
| **Neo4j** | Grafo | Plugin | Dinámico | Media |
| **PostgreSQL + PostGIS** | Relacional | Extensión | GiST R-tree | Media |

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

### 2.4 Selección Final: MongoDB (GeoJSON + 2dsphere)

**Decisión:** Seleccionamos **MongoDB** (con documentos GeoJSON y índices `2dsphere`) como la solución de base de datos para este proyecto.

**Justificación:**

1. **Coincidencia con Requisitos Funcionales:**
   - La operación central es detectar relaciones espaciales (por ejemplo, edificaciones dentro de límites municipales). MongoDB soporta consultas geométricas sobre GeoJSON como `$geoIntersects`, `$geoWithin` y `$near` para resolver consultas de tipo “¿esta geometría intersecta/está dentro de…?” de forma nativa.
   - MongoDB almacena geometrías en formato **GeoJSON** (y asume WGS84), lo que facilita el intercambio con librerías GIS y con formatos web estándar.
   - Para transformaciones de coordenadas (p. ej. WGS84 a CRS proyectado para cálculos de área), la conversión se realiza en etapa de ingestión o en la capa de aplicación usando herramientas como PROJ, PyProj, Shapely o Turf.js; es recomendable transformar/normalizar coordenadas al cargar los datos si se requieren áreas en un CRS proyectado.

2. **Rendimiento:**
   - MongoDB ofrece índices espaciales `2dsphere` optimizados para consultas geo-json y escala bien en conjuntos de datos grandes, especialmente cuando se combina con **sharding** horizontal.
   - Consultas de pertenencia espacial (point-in-polygon, intersection) son rápidas con índices `2dsphere`. Para operaciones geométricas vectoriales complejas (uniones espaciales pesadas, topología avanzada, cálculos precisos de área en CRS proyectados) será necesario delegar parte del trabajo a la aplicación o a un motor GIS especializado si se requiere la máxima precisión/velocidad en esas operaciones.
   - El pipeline de agregación de MongoDB permite realizar agregaciones y estadísticas a nivel municipal (por ejemplo, sumar superficie por grupo, contar edificaciones por polígono) directamente en la base de datos, reduciendo movimiento de datos.

3. **Ecosistema:**
   - Integración madura con Python: `pymongo`, `mongoengine` y herramientas para trabajar con GeoJSON. GeoPandas escribe/lee GeoJSON de forma nativa, por lo que el flujo GeoPandas ⇄ MongoDB es directo mediante exportación/importación de GeoJSON o mediante pequeñas funciones que serialicen geometrías.
   - MongoDB Atlas (servicio gestionado) ofrece dashboards, copias de seguridad, y soporte para despliegues distribuidos y georredundantes; MongoDB Compass facilita la inspección de documentos GeoJSON.
   - Para visualización y análisis GIS, se puede exportar GeoJSON desde MongoDB a QGIS o consumirlo desde aplicaciones web (Leaflet, Mapbox). Existen plugins y conectores y, cuando no hay conector directo, el flujo via GeoJSON funciona sin problemas.

4. **Integridad de Datos:**
   - MongoDB soporta operaciones ACID a nivel de documento y desde versiones recientes también soporta **transacciones multi-documento** dentro de réplicas y clusters sharded, lo que permite cargas de datos en múltiples pasos con garantías cuando sea necesario.
   - La naturaleza documental facilita validar esquemas parcial o dinámicamente (JSON Schema en validadores de colección) y almacenar metadatos semi-estructurados (por ejemplo, propiedades, atributos y trazas históricas) junto con la geometría.

5. **Estándar de la Industria y Escalabilidad:**
   - MongoDB es ampliamente usado en aplicaciones geoespaciales modernas (servicios de localización, catálogos de activos, aplicaciones web con grandes volúmenes de documentos con geometría).
   - Soporta **sharding** nativo para escalamiento horizontal y políticas de réplica para alta disponibilidad.
   - Documentación y comunidad amplias; Atlas ofrece soporte empresarial y características gestionadas (monitoring, alertas, performance advisor).

**Nota sobre Limitaciones y Consideraciones Operativas:**
- MongoDB trabaja internamente con GeoJSON en WGS84; si necesita cálculos de áreas precisos en unidades métricas (m²), debe transformar geometrías a un CRS proyectado **antes** de almacenar o calcular el área en la capa de aplicación con librerías GIS (Shapely + PyProj, Turf.js, etc.). MongoDB no expone una función equivalente a `ST_Area` en un CRS proyectado.
- Operaciones espaciales avanzadas (p. ej. joins espaciales complejos, topología y análisis vectorial avanzado) pueden ser más eficientemente realizadas en un motor GIS especializado (PostGIS, o procesado batch con GDAL/OGR/GeoPandas) y almacenar resultados en MongoDB para consultas rápidas por documento.
- Recomendación práctica: almacenar geometrías como GeoJSON, crear índices `2dsphere` sobre los campos geométricos, y combinar consultas espaciales nativas de MongoDB con procesamiento externo cuando se requieran operaciones geométricas complejas o cálculos de áreas en CRS proyectados.

**Nota sobre la Clasificación "NoSQL":**
MongoDB es una base de datos NoSQL por diseño y aporta al proyecto características esperadas de soluciones NoSQL:
- **Flexibilidad de esquema:** documentos BSON/JSON para metadatos semi-estructurados sin esquema rígido.
- **Indexación espacial:** índices `2dsphere` para consultas geoespaciales basadas en GeoJSON.
- **Escalamiento horizontal:** sharding nativo para distribuir datos y carga.
- **Características modernas:** agregation framework potente (`$group`, `$match`, `$project`, `$geoNear`), validación por colección (JSON Schema), y soporte para transacciones multi-documento cuando se requieren garantías ACID en procesos complejos.

**Conclusión:**  
MongoDB satisface los requisitos de flexibilidad, escalabilidad y geoconsultas necesarias para el Análisis de Potencial Solar en Techos PDET, especialmente si priorizamos un modelo documental con metadatos ricos y necesidad de escalar horizontalmente. Para operaciones geoespaciales analíticas muy avanzadas (uniones espaciales masivas y cálculos topológicos precisos), recomendamos un enfoque híbrido: usar MongoDB como datastore principal (GeoJSON + índices `2dsphere`) y delegar procesamiento GIS intensivo a pipelines especializados (GeoPandas/GDAL/Post-processing) según sea necesario.

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

### 4.1 Esquema de Base de Datos (MongoDB)

En MongoDB no existen **esquemas SQL** ni **vistas materializadas** en sentido tradicional.  
La estructura de datos se define mediante **colecciones** (collections) que almacenan documentos JSON/BSON.  
Cada colección representará una entidad principal del proyecto:

- `pdet_municipalities` → límites municipales PDET  
- `buildings_microsoft` → huellas de edificaciones Microsoft  
- `buildings_google` → huellas de edificaciones Google  
- `municipality_statistics` → colección generada por procesos de agregación periódicos  

Las geometrías se almacenarán en formato **GeoJSON**, y cada colección tendrá un índice espacial **2dsphere**  
para soportar consultas geoespaciales eficientes (`$geoWithin`, `$geoIntersects`, `$near`).

---


### 4.2 Colección: `pdet_municipalities`

```js
// Ejemplo de documento en MongoDB
{
  _id: ObjectId("..."),
  dept_code: "73",                        // Código de departamento (DIVIPOLA)
  muni_code: "73001",                     // Código de municipio
  dept_name: "Tolima",
  muni_name: "Ibagué",
  pdet_region: "Central Sur",
  pdet_subregion: "Tolima",
  geom: {
    type: "MultiPolygon",
    coordinates: [
      [[[ -75.230, 4.439 ], [ -75.210, 4.449 ], [ -75.220, 4.459 ], [ -75.230, 4.439 ]]]
    ]
  },
  area_km2: 1498.23,
  data_source: "DANE MGN",
  created_at: ISODate("2025-10-22T12:00:00Z"),
  updated_at: ISODate("2025-10-22T12:00:00Z")
}

// Índices
db.pdet_municipalities.createIndex({ geom: "2dsphere" });
db.pdet_municipalities.createIndex({ muni_code: 1 });
db.pdet_municipalities.createIndex({ dept_code: 1 });
db.pdet_municipalities.createIndex({ pdet_region: 1 });
```

### 4.3 Coleccion: buildings_microsoft

// Colección para huellas de edificaciones Microsoft en MongoDB

db.createCollection("buildings_microsoft", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["geom", "area_m2", "dataset_version", "created_at"],
      properties: {
        _id: {
          bsonType: "objectId",
          description: "Identificador único del edificio (clave primaria)"
        },
        geom: {
          bsonType: "object",
          required: ["type", "coordinates"],
          properties: {
            type: {
              enum: ["Polygon"],
              description: "Tipo de geometría: polígono representando la huella de la edificación"
            },
            coordinates: {
              bsonType: "array",
              description: "Coordenadas del polígono en formato GeoJSON (EPSG:4326)"
            }
          }
        },
        municipality_id: {
          bsonType: ["objectId", "null"],
          description: "Referencia al municipio en la colección pdet_municipalities"
        },
        muni_code: {
          bsonType: ["string", "null"],
          description: "Código del municipio (DANE)"
        },
        area_m2: {
          bsonType: "double",
          minimum: 0,
          description: "Área en metros cuadrados de la edificación"
        },
        dataset_version: {
          bsonType: "string",
          description: "Versión del conjunto de datos, ej. 'GlobalMLBuildingFootprints-2024'"
        },
        confidence: {
          bsonType: ["double", "null"],
          minimum: 0,
          maximum: 1,
          description: "Nivel de confianza del dato (si está disponible)"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación del registro"
        }
      }
    }
  }
});

// Índice geoespacial (CRÍTICO para rendimiento en consultas espaciales)
db.buildings_microsoft.createIndex({ geom: "2dsphere" });

// Índices adicionales para filtrado y uniones
db.buildings_microsoft.createIndex({ muni_code: 1 });
db.buildings_microsoft.createIndex({ area_m2: 1 });

// Índice parcial para edificaciones aún no asignadas a municipio
db.buildings_microsoft.createIndex(
  { _id: 1 },
  { partialFilterExpression: { municipality_id: { $exists: false } } }
);

// Comentario general (no soportado nativamente, se documenta aquí)
// Descripción: Colección que almacena las huellas de edificaciones del dataset
// Microsoft Global ML Building Footprints, en formato GeoJSON.


// Colección para edificaciones del dataset Google Open Buildings v3 en MongoDB

db.createCollection("buildings_google", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["geom", "geom_type", "dataset_version", "created_at"],
      properties: {
        _id: {
          bsonType: "objectId",
          description: "Identificador único del edificio (clave primaria)"
        },
        geom: {
          bsonType: "object",
          required: ["type", "coordinates"],
          properties: {
            type: {
              enum: ["Point", "Polygon"],
              description: "Tipo de geometría (punto o polígono) representando la edificación"
            },
            coordinates: {
              bsonType: "array",
              description: "Coordenadas en formato GeoJSON (EPSG:4326)"
            }
          }
        },
        geom_type: {
          bsonType: "string",
          enum: ["POINT", "POLYGON"],
          description: "Tipo de geometría de la edificación"
        },
        municipality_id: {
          bsonType: ["objectId", "null"],
          description: "Referencia al municipio en la colección pdet_municipalities"
        },
        muni_code: {
          bsonType: ["string", "null"],
          description: "Código del municipio (DANE)"
        },
        area_m2: {
          bsonType: ["double", "null"],
          minimum: 0,
          description: "Área de la edificación en metros cuadrados (puede ser nula para puntos)"
        },
        confidence: {
          bsonType: ["double", "null"],
          minimum: 0,
          maximum: 1,
          description: "Nivel de confianza del modelo ML (0-1)"
        },
        latitude: {
          bsonType: ["double", "null"],
          description: "Latitud original (solo para geometrías tipo punto)"
        },
        longitude: {
          bsonType: ["double", "null"],
          description: "Longitud original (solo para geometrías tipo punto)"
        },
        dataset_version: {
          bsonType: "string",
          description: "Versión del dataset, por defecto 'v3'"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación del registro"
        }
      }
    }
  }
});

// Índice geoespacial (para consultas espaciales de puntos o polígonos)
db.buildings_google.createIndex({ geom: "2dsphere" });

// Índices adicionales para consultas y rendimiento
db.buildings_google.createIndex({ muni_code: 1 });
db.buildings_google.createIndex({ area_m2: 1 });
db.buildings_google.createIndex({ confidence: 1 });
db.buildings_google.createIndex({ geom_type: 1 });

// Índice parcial para edificaciones de alta confianza (confidence >= 0.7)
db.buildings_google.createIndex(
  { _id: 1 },
  { partialFilterExpression: { confidence: { $gte: 0.7 } } }
);

// Comentario (documentado dentro del código)
// Descripción: Colección que almacena las huellas de edificaciones del dataset
// Google Open Buildings v3. Incluye geometrías tipo punto o polígono en formato GeoJSON.

### 4.5 Vista Materializada: municipality_statistics (MongoDB)

Para consultas eficientes en MongoDB, se crean colecciones materializadas con estadísticas pre-agregadas usando `aggregate()` y operadores como `$lookup`, `$group` y `$out`.  
Estas colecciones reemplazan las vistas materializadas de PostgreSQL/PostGIS.

```js
// ================================================================
// Vista materializada: mv_municipality_stats_microsoft
// ================================================================

db.pdet_municipalities.aggregate([
  {
    $lookup: {
      from: "buildings_microsoft",
      localField: "municipality_id",
      foreignField: "municipality_id",
      as: "buildings"
    }
  },
  { $unwind: { path: "$buildings", preserveNullAndEmptyArrays: true } },
  {
    $group: {
      _id: {
        municipality_id: "$municipality_id",
        muni_code: "$muni_code",
        muni_name: "$muni_name",
        dept_name: "$dept_name",
        pdet_region: "$pdet_region"
      },
      building_count: { $sum: { $cond: [{ $ifNull: ["$buildings.building_id", false] }, 1, 0] } },
      total_rooftop_area_m2: { $sum: "$buildings.area_m2" },
      avg_building_area_m2: { $avg: "$buildings.area_m2" },
      min_building_area_m2: { $min: "$buildings.area_m2" },
      max_building_area_m2: { $max: "$buildings.area_m2" },
      stddev_building_area_m2: { $stdDevSamp: "$buildings.area_m2" }
    }
  },
  {
    $project: {
      _id: 0,
      municipality_id: "$_id.municipality_id",
      muni_code: "$_id.muni_code",
      muni_name: "$_id.muni_name",
      dept_name: "$_id.dept_name",
      pdet_region: "$_id.pdet_region",
      building_count: 1,
      total_rooftop_area_m2: 1,
      avg_building_area_m2: 1,
      min_building_area_m2: 1,
      max_building_area_m2: 1,
      stddev_building_area_m2: 1
    }
  },
  { $out: "mv_municipality_stats_microsoft" }
]);

db.mv_municipality_stats_microsoft.createIndex({ muni_code: 1 });

// ================================================================
// Vista materializada: mv_municipality_stats_google
// ================================================================

db.pdet_municipalities.aggregate([
  {
    $lookup: {
      from: "buildings_google",
      localField: "municipality_id",
      foreignField: "municipality_id",
      as: "buildings"
    }
  },
  { $unwind: { path: "$buildings", preserveNullAndEmptyArrays: true } },
  {
    $group: {
      _id: {
        municipality_id: "$municipality_id",
        muni_code: "$muni_code",
        muni_name: "$muni_name",
        dept_name: "$dept_name",
        pdet_region: "$pdet_region"
      },
      building_count: { $sum: { $cond: [{ $ifNull: ["$buildings.building_id", false] }, 1, 0] } },
      total_rooftop_area_m2: { $sum: "$buildings.area_m2" },
      avg_building_area_m2: { $avg: "$buildings.area_m2" },
      avg_confidence: { $avg: "$buildings.confidence" },
      polygon_count: { $sum: { $cond: [{ $eq: ["$buildings.geom_type", "POLYGON"] }, 1, 0] } },
      point_count: { $sum: { $cond: [{ $eq: ["$buildings.geom_type", "POINT"] }, 1, 0] } }
    }
  },
  {
    $project: {
      _id: 0,
      municipality_id: "$_id.municipality_id",
      muni_code: "$_id.muni_code",
      muni_name: "$_id.muni_name",
      dept_name: "$_id.dept_name",
      pdet_region: "$_id.pdet_region",
      building_count: 1,
      total_rooftop_area_m2: 1,
      avg_building_area_m2: 1,
      avg_confidence: 1,
      polygon_count: 1,
      point_count: 1
    }
  },
  { $out: "mv_municipality_stats_google" }
]);

db.mv_municipality_stats_google.createIndex({ muni_code: 1 });

// ================================================================
// Vista materializada: mv_dataset_comparison (Microsoft vs Google)
// ================================================================

db.mv_municipality_stats_microsoft.aggregate([
  {
    $lookup: {
      from: "mv_municipality_stats_google",
      localField: "municipality_id",
      foreignField: "municipality_id",
      as: "google"
    }
  },
  { $unwind: { path: "$google", preserveNullAndEmptyArrays: true } },
  {
    $project: {
      municipality_id: 1,
      muni_code: 1,
      muni_name: 1,
      dept_name: 1,
      ms_building_count: "$building_count",
      ms_total_area_m2: "$total_rooftop_area_m2",
      gg_building_count: "$google.building_count",
      gg_total_area_m2: "$google.total_rooftop_area_m2",
      count_difference: { $abs: { $subtract: ["$building_count", "$google.building_count"] } },
      area_difference_m2: { $abs: { $subtract: ["$total_rooftop_area_m2", "$google.total_rooftop_area_m2"] } },
      more_buildings_source: {
        $switch: {
          branches: [
            { case: { $gt: ["$building_count", "$google.building_count"] }, then: "Microsoft" },
            { case: { $gt: ["$google.building_count", "$building_count"] }, then: "Google" }
          ],
          default: "Equal"
        }
      }
    }
  },
  { $out: "mv_dataset_comparison" }
]);

// ================================================================
// Comentarios descriptivos (documentación interna)
// ================================================================

db.system.js.save({
  _id: "metadata_mv_municipality_stats_microsoft",
  value: function() {
    return "Estadísticas pre-agregadas para edificaciones Microsoft por municipio";
  }
});

db.system.js.save({
  _id: "metadata_mv_municipality_stats_google",
  value: function() {
    return "Estadísticas pre-agregadas para edificaciones Google por municipio";
  }
});

db.system.js.save({
  _id: "metadata_mv_dataset_comparison",
  value: function() {
    return "Comparación de conteos y áreas de edificaciones Microsoft vs Google";
  }
});

// ================================================================
// Resumen de colecciones materializadas
// ================================================================
//
// mv_municipality_stats_microsoft → Estadísticas de edificaciones detectadas por Microsoft
// mv_municipality_stats_google    → Estadísticas de edificaciones detectadas por Google
// mv_dataset_comparison           → Comparación de conteos y áreas entre Microsoft y Google
//

```

### 4.6 Características de Optimización de Esquema (MongoDB)

#### Estrategia de Particionamiento (para conjuntos de datos muy grandes)

En MongoDB, el particionamiento se logra mediante **sharding**, que distribuye los documentos en múltiples nodos de un clúster según una clave de fragmentación.  
Esto permite escalar horizontalmente y manejar grandes volúmenes de datos (por ejemplo, millones de edificaciones).

**Ejemplo: Sharding por código de municipio o departamento**

```javascript
// Habilitar el sharding en la base de datos
sh.enableSharding("solar_pdet");

// Definir índice en el campo de partición
db.buildings_microsoft.createIndex({ dept_code: 1 });

// Habilitar el sharding en la colección por departamento
sh.shardCollection("solar_pdet.buildings_microsoft", { dept_code: "hashed" });

// También se puede usar el código de municipio como clave alternativa
db.buildings_google.createIndex({ muni_code: 1 });
sh.shardCollection("solar_pdet.buildings_google", { muni_code: "hashed" });
```




## 5. Optimización Espacial y de Consultas (MongoDB)

### 5.1 Resumen de Índice Espacial

En MongoDB, los índices espaciales se implementan mediante el tipo **2dsphere**, que permite realizar consultas geoespaciales eficientes sobre coordenadas en formato GeoJSON.  
Estos índices son equivalentes funcionales a los **R-tree / GiST** de PostGIS, optimizados para consultas de intersección, contención y distancia.

**Características principales de los índices 2dsphere:**
- Basados en jerarquías geográficas similares a R-tree.
- Soportan geometrías en 2D y esferas (latitud/longitud).
- Ideales para operaciones como `$geoWithin`, `$near`, `$intersects`.
- Complejidad de consulta promedio: **O(log n)**.

---

### 5.2 Configuración de Índices

En MongoDB, los índices se crean directamente sobre los campos de tipo GeoJSON (`Point`, `Polygon`, `MultiPolygon`), que reemplazan el tipo `geometry` de PostGIS.

```javascript
// Índice espacial para municipios (geometría de límites)
db.pdet_municipalities.createIndex({ geom: "2dsphere" });

// Índices espaciales para edificaciones detectadas por Microsoft y Google
db.buildings_microsoft.createIndex({ geom: "2dsphere" });
db.buildings_google.createIndex({ geom: "2dsphere" });

// Índices complementarios para búsqueda rápida por municipio o departamento
db.buildings_microsoft.createIndex({ muni_code: 1 });
db.buildings_google.createIndex({ muni_code: 1 });
db.pdet_municipalities.createIndex({ muni_code: 1 });
```

### 5.3 Parámetros de Ajuste de Índices (MongoDB)

Para lograr un rendimiento óptimo con grandes volúmenes de datos, MongoDB ofrece herramientas que reemplazan configuraciones como `fillfactor` o parámetros de almacenamiento de PostGIS.

**Estrategias equivalentes:**

```javascript
// 1. Verificar tamaño y estado de índices
db.buildings_microsoft.stats().indexSizes;
db.buildings_google.stats().indexSizes;

// 2. Reconstruir índices para mejorar rendimiento en colecciones con alta rotación de datos
db.buildings_microsoft.reIndex();
db.buildings_google.reIndex();

// 3. Crear índices adicionales para optimizar consultas espaciales y por municipio
db.buildings_microsoft.createIndex({ geom: "2dsphere" });
db.buildings_google.createIndex({ geom: "2dsphere" });
db.pdet_municipalities.createIndex({ geom: "2dsphere" });

db.buildings_microsoft.createIndex({ muni_code: 1 });
db.buildings_google.createIndex({ muni_code: 1 });
```

### 5.4 Optimización de Consultas Espaciales en MongoDB

MongoDB utiliza **índices geoespaciales 2dsphere** para optimizar consultas que involucran geometrías complejas (puntos, polígonos, líneas).  
Esto permite realizar operaciones espaciales directamente sobre los documentos sin necesidad de prefiltrado manual.

#### Creación de Índices Espaciales

```js
// Crear índices 2dsphere en las colecciones geoespaciales
db.buildings_microsoft.createIndex({ location: "2dsphere" });
db.pdet_municipalities.createIndex({ geometry: "2dsphere" });
```
### 5.5 Recolección de Estadísticas y Monitoreo de Índices en MongoDB

En MongoDB, no se utiliza `ANALYZE` como en PostgreSQL.  
En su lugar, se emplean **comandos de diagnóstico y estadísticas de índice** para monitorear el rendimiento y el uso de los índices geoespaciales y de otros tipos.

#### Verificar Estadísticas de Colección

```js
// Obtener estadísticas generales de una colección
db.pdet_municipalities.stats();
db.buildings_microsoft.stats();
db.buildings_google.stats();
```

### 5.6 Monitoreo del Rendimiento en MongoDB

En MongoDB no se utiliza `EXPLAIN ANALYZE` como en PostgreSQL.  
En su lugar, se emplea el método **`.explain()`** para analizar el plan de ejecución de una consulta y verificar si los índices están siendo utilizados correctamente.

---

#### Analizar el Plan de Ejecución de una Consulta

```js
// Analizar una consulta geoespacial con .explain()
db.buildings_microsoft.find({
  location: {
    $geoWithin: {
      $geometry: municipioGeom
    }
  }
}).explain("executionStats");
```

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

**Objetivo:** Instalar y configurar MongoDB, crear la base de datos y las colecciones necesarias para el proyecto.

---

#### **Tareas:**

1. Instalar **MongoDB Community Server** o usar un servicio en la nube (MongoDB Atlas, AWS DocumentDB, Azure Cosmos DB con API MongoDB).  
2. Crear base de datos: `pdet_solar_analysis`.  
3. Crear colecciones principales:
   - `pdet_municipalities`
   - `buildings_microsoft`
   - `buildings_google`
   - `municipality_statistics`
4. Insertar documentos de prueba o cargar los datos iniciales.  
5. Crear índices geoespaciales (`2dsphere`) para las colecciones con geometría.  
6. Verificar la creación de índices y estructuras de datos.  
7. Configurar la conexión desde Python con la librería **PyMongo** (`src/database/connection.py`).  
8. Probar operaciones básicas de lectura y escritura en la base de datos.  

---

#### **Entregables:**

- Instancia de **MongoDB** en ejecución (local o nube).  
- Colecciones e índices creados correctamente.  
- Script de conexión funcional en Python (`src/database/connection.py`).  

---

#### **Pruebas:**

```js
// Verificar conexión a MongoDB
use pdet_solar_analysis;

// Verificar colecciones creadas
show collections;

// Verificar índices geoespaciales
db.buildings_microsoft.getIndexes();
db.buildings_google.getIndexes();

// Crear índice 2dsphere si no existe
db.buildings_microsoft.createIndex({ location: "2dsphere" });
db.buildings_google.createIndex({ location: "2dsphere" });

// Prueba de conexión desde Python (PyMongo)
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["pdet_solar_analysis"]
print(db.list_collection_names())
```
### 6.3 Fase 2: Carga de Datos de Municipios PDET (Oct 25 - Nov 3)

**Objetivo:** Cargar y validar los límites municipales PDET dentro de la base de datos MongoDB.

---

#### **Tareas:**

1. Descargar los datos del **DANE MGN** en formato **Shapefile (.shp)**.  
2. Filtrar únicamente los municipios designados como territorios **PDET**.  
3. Validar geometrías y corregir polígonos inválidos (usando herramientas como `geopandas` o `shapely`).  
4. Asegurar que el sistema de coordenadas esté en **WGS84 (EPSG:4326)**.  
5. Convertir los datos a formato **GeoJSON**.  
6. Insertar los documentos en la colección `pdet_municipalities` en MongoDB.  
7. Calcular el campo `area_km2` a partir de la geometría.  
8. Crear un índice geoespacial `2dsphere` para mejorar el rendimiento en consultas espaciales.  
9. Generar un **mapa de visualización interactivo** (por ejemplo, con Folium o Kepler.gl).  

---

#### **Fuente de Datos:**

- [DANE Geoportal](https://geoportal.dane.gov.co)  
- [Lista oficial de Municipios PDET](https://centralpdet.renovacionterritorio.gov.co)

---

#### **Scripts:**

- `src/data_loaders/dane_loader.py`  
- `notebooks/02_pdet_municipalities.ipynb`

---

#### **Entregables:**

- **170 municipios PDET** cargados en MongoDB.  
- **Reporte de calidad de datos** con geometrías validadas.  
- **Mapa interactivo** mostrando límites municipales.  
- **Documentación** del proceso (Entregable 2).  

---

#### **Consultas de Validación en MongoDB:**

```js
// Contar municipios cargados
db.pdet_municipalities.countDocuments();  // Debería ser ~170

// Verificar si existen documentos sin geometría
db.pdet_municipalities.find({ geometry: { $exists: false } }).count();  // Debería ser 0

// Verificar sistema de coordenadas (CRS)
db.pdet_municipalities.findOne({}, { "geometry.crs": 1 });

// Calcular áreas (puede hacerse con Python + GeoPandas o en un pipeline de agregación)
db.pdet_municipalities.aggregate([
  {
    $project: {
      muni_name: 1,
      area_km2: {
        $divide: [
          { $multiply: [{ $meta: "geoNearDistance" }, 1] }, 1000000
        ]
      }
    }
  }
]);

// Crear índice geoespacial si no existe
db.pdet_municipalities.createIndex({ geometry: "2dsphere" });

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

### 3.2 Edificaciones Google

**Objetivo:** Cargar, procesar y validar los datos de edificaciones provenientes de **Google Open Buildings** para los municipios PDET en MongoDB.

---

#### **Tareas:**

1. Descargar los datos de **Google Open Buildings** en formato **CSV**.  
2. Filtrar los registros correspondientes a **Colombia**.  
3. Convertir la columna de geometría (formato WKT) a formato **GeoJSON** compatible con MongoDB.  
4. Filtrar edificaciones ubicadas dentro o cercanas a los **municipios PDET**.  
5. Calcular el área en **m²** para las edificaciones tipo polígono.  
6. Cargar los datos procesados en la colección `buildings_google`.  
7. Ejecutar una **asignación espacial** para vincular cada edificación con su `municipality_id`.  
8. Validar la **calidad de los datos** (geometrías válidas, duplicados, áreas nulas, etc.).  

---

#### **Scripts:**

- `src/data_loaders/microsoft_loader.py`  
- `src/data_loaders/google_loader.py`  
- `notebooks/03_building_data_loading.ipynb`

---

#### **Optimización:**

- Utilizar **inserciones masivas** (`insert_many()`) en lugar de cargas documento por documento.  
- Deshabilitar índices durante la carga masiva y reconstruirlos después.  
- Procesar los datos en **lotes** de entre **100.000 y 1.000.000 registros** para mejorar el rendimiento.  
- Validar que los datos mantengan coherencia espacial y consistencia de atributos.  

---

#### **Ejemplo de Carga Masiva con Python + PyMongo**

```python
import pandas as pd
from shapely import wkt
from shapely.geometry import mapping
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pdet_solar_analysis"]
collection = db["buildings_google"]

# Cargar CSV de Google Open Buildings
df = pd.read_csv("google_open_buildings_colombia.csv")

# Convertir WKT a GeoJSON
df["geometry"] = df["geometry"].apply(lambda x: mapping(wkt.loads(x)))

# Calcular área (solo si es polígono)
df["area_m2"] = df["geometry"].apply(
    lambda g: wkt.loads(g["coordinates"]) if g["type"] == "Polygon" else None
)

# Convertir a documentos MongoDB
docs = df.to_dict("records")

# Inserción masiva
collection.insert_many(docs)

# Crear índice geoespacial 2dsphere
collection.create_index([("geometry", "2dsphere")])

```
### 6.5 Fase 4: Análisis Espacial y Agregación (Nov 11–17)

**Objetivo:**  
Realizar análisis geoespacial en MongoDB para estimar áreas de techos y comparar resultados entre fuentes (Google y Microsoft).

---

#### **Tareas:**
1. Actualizar colecciones agregadas con estadísticas recientes.  
2. Ejecutar **consultas geoespaciales** usando operadores como `$geoWithin` y `$geoIntersects` para unir edificaciones con municipios.  
3. Comparar conteos de edificaciones entre **Microsoft y Google** por municipio.  
4. Calcular el **área total de techos** por municipio.  
5. Identificar municipios con **mayor potencial solar** según el área acumulada.  
6. Exportar tablas de resultados a **CSV/JSON**.  
7. Crear **visualizaciones** (mapas de coropletas y gráficos).  
8. Validar precisión de las operaciones geoespaciales.  
9. Documentar la metodología para **reproducibilidad** del análisis.  

---

#### **Scripts:**
- `src/analysis/spatial_join.py`  
- `src/analysis/area_calculator.py`  
- `src/analysis/aggregator.py`  
- `src/visualization/maps.py`  
- `notebooks/04_spatial_analysis.ipynb`  

---

#### **Consultas y Agregaciones en MongoDB**

```python
from pymongo import MongoClient
import pandas as pd

# Conexión a la base de datos
client = MongoClient("mongodb://localhost:27017/")
db = client["pdet_solar_analysis"]

# Agregación: área total de techos por municipio (Google)
pipeline_google = [
    {
        "$group": {
            "_id": "$municipality_name",
            "building_count": {"$sum": 1},
            "total_rooftop_area_m2": {"$sum": "$area_m2"}
        }
    },
    {"$sort": {"total_rooftop_area_m2": -1}},
    {"$limit": 10}
]

google_results = list(db.buildings_google.aggregate(pipeline_google))
df_google = pd.DataFrame(google_results)

# Agregación: comparación entre Microsoft y Google
pipeline_comparison = [
    {
        "$lookup": {
            "from": "buildings_microsoft",
            "localField": "municipality_name",
            "foreignField": "municipality_name",
            "as": "microsoft_data"
        }
    },
    {
        "$project": {
            "municipality_name": 1,
            "google_count": {"$literal": 1},
            "microsoft_count": {"$size": "$microsoft_data"},
            "count_difference": {
                "$subtract": [{"$size": "$microsoft_data"}, 1]
            }
        }
    },
    {"$sort": {"count_difference": -1}},
    {"$limit": 20}
]

comparison_results = list(db.buildings_google.aggregate(pipeline_comparison))
df_comparison = pd.DataFrame(comparison_results)

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

#### **Hardware**
- **Máquina de Desarrollo:** 16 GB de RAM mínimo, 50 GB de espacio libre en disco.  
- **Servidor de Base de Datos:**
  - **Opción A:** Instancia local de **MongoDB**.  
  - **Opción B:** Base de datos en la nube (**MongoDB Atlas**, AWS, Google Cloud, Azure).  
  - **Recomendado:** 32 GB de RAM, 200 GB de almacenamiento SSD.  

---

#### **Software**
- **MongoDB 7.0+**
- **Python 3.9+**
- **Librerías:**  
  - `pandas`, `geopandas`, `pymongo`, `dnspython`, `folium`, `matplotlib`, `plotly`, `numpy`  
  - (Opcional) `mongoengine` o `motor` para manejo ORM/asíncrono.  

---

#### **Almacenamiento de Datos**
- **Datos crudos:** ~20–50 GB (comprimidos).  
- **Datos procesados en MongoDB:** ~100–200 GB (sin comprimir).  
- **Resultados y visualizaciones:** ~1 GB.  
- **Índices geoespaciales (2dsphere):** consumo adicional de almacenamiento (~10–15 % del total de datos).  

---

### 6.8 Mitigación de Riesgos

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|----------|--------------|-------------|
| Volumen de datos demasiado grande para importar | Alto | Medio | Usar importación por lotes (`mongoimport --batchSize`), filtrado previo con `GeoPandas`, o procesamiento en la nube (MongoDB Atlas). |
| Consultas geoespaciales lentas | Medio | Medio | Crear índices `2dsphere`, particionar por municipio o departamento y usar agregaciones con `$geoNear` o `$geoWithin`. |
| Errores en geometrías o datos inconsistentes | Medio | Alto | Validar geometrías antes de carga con `GeoPandas.is_valid` y corrección automática usando `buffer(0)`. |
| Espacio de disco insuficiente | Alto | Bajo | Monitorear con `db.stats()`, habilitar compresión WiredTiger y usar almacenamiento en la nube. |
| Caídas durante la carga de datos masiva | Medio | Bajo | Implementar transacciones (`session.start_transaction()`), checkpoints por lote y respaldo automático (`mongodump`). |

---

---

## 7. Justificación y Conclusiones

### 7.1 ¿Por Qué Este Diseño?

Nuestro diseño de esquema con **MongoDB** aborda todos los requisitos del proyecto de manera eficiente y escalable:

1. **Requisito NoSQL:**  
   MongoDB ofrece un modelo de documentos flexible basado en JSON que permite almacenar datos estructurados y no estructurados, ideal para la gestión de información geoespacial sin las limitaciones de un esquema rígido.

2. **Escalabilidad:**  
   MongoDB es altamente escalable horizontalmente mediante *sharding*, lo que permite manejar volúmenes masivos de datos (por ejemplo, más de 1.8 mil millones de registros de edificaciones) distribuidos entre múltiples nodos.

3. **Rendimiento:**  
   Las consultas geoespaciales se optimizan mediante **índices 2dsphere**, que permiten cálculos espaciales eficientes con complejidad aproximada **O(log n)**, mejorando la velocidad en búsquedas por ubicación y proximidad.

4. **Funcionalidad:**  
   MongoDB integra operaciones geoespaciales nativas como `$geoWithin`, `$near`, `$geoIntersects`, y `$geometry`, que permiten análisis de cobertura, proximidad y contención sin depender de herramientas externas.

5. **Reproducibilidad:**  
   El uso de colecciones bien estructuradas y pipelines de agregación permite mantener un flujo de trabajo reproducible y fácilmente automatizable dentro del ecosistema NoSQL.

6. **Integración:**  
   MongoDB se integra de forma nativa con el ecosistema de desarrollo de **Python** (mediante `pymongo`, `mongoengine` o `geopandas` con conectores), así como con herramientas de análisis y visualización geográfica como **QGIS** y **Kepler.gl**.

7. **Extensibilidad:**  
   Su estructura flexible permite agregar nuevos conjuntos de datos, atributos o tipos de geometrías sin necesidad de redefinir el esquema general, adaptándose fácilmente a cambios en los requisitos del proyecto.

---

### 7.2 Resultados Esperados

Al completar la implementación con **MongoDB**, se esperan los siguientes resultados:

- **Base de Datos:**  
  Instancia de **MongoDB** totalmente operacional que contenga información de los **170 municipios PDET**, incluyendo millones de registros de edificaciones con sus respectivas geometrías y atributos asociados (coordenadas, área de techo, orientación, etc.).

- **Análisis:**  
  Generación de estadísticas a nivel municipal mediante *pipelines* de agregación, incluyendo conteos de edificaciones, áreas totales de techos y distribución espacial de potencial solar.

- **Comparación:**  
  Evaluación comparativa entre los conjuntos de datos de **Microsoft Building Footprints** y **Google Open Buildings**, identificando diferencias en cobertura, precisión y densidad de edificaciones.

- **Recomendaciones:**  
  Elaboración de recomendaciones técnicas basadas en los resultados obtenidos, dirigidas a la **UPME**, destacando los municipios con **mayor potencial solar** y priorización para instalación de sistemas fotovoltaicos.

- **Reproducibilidad:**  
  Entrega de un repositorio con el **código fuente, scripts de carga, consultas MongoDB y documentación técnica**, garantizando la trazabilidad y posibilidad de reproducir el análisis completo en distintos entornos.

---


### 7.3 Alineación con Objetivos de la UPME

Este diseño basado en **MongoDB** apoya directamente los objetivos estratégicos de la **Unidad de Planeación Minero Energética (UPME)**, al proporcionar una infraestructura moderna, escalable y orientada a datos para la planeación energética del país:

- **Planeación Estratégica:**  
  Permite identificar y priorizar los municipios con **mayor potencial de generación de energía solar**, facilitando la toma de decisiones informadas en la expansión de proyectos fotovoltaicos.

- **Decisiones Basadas en Datos:**  
  Genera métricas cuantitativas y reportes automatizados mediante consultas y agregaciones en MongoDB, que sirven como soporte técnico para la **selección de sitios piloto** y validación de escenarios energéticos.

- **Transparencia:**  
  El uso de **herramientas de código abierto**, bases de datos NoSQL y conjuntos de datos públicos garantiza **verificación independiente** y reproducibilidad de los resultados.

- **Escalabilidad:**  
  La arquitectura NoSQL permite procesar grandes volúmenes de datos geoespaciales y extender el análisis a **todos los municipios de Colombia**, sin comprometer el rendimiento ni la integridad de la información.

- **Infraestructura Moderna:**  
  Se alinea con las **iniciativas de modernización tecnológica** de la UPME, promoviendo la adopción de tecnologías basadas en la nube, análisis distribuido y gestión eficiente de datos masivos.

---


### 7.4 Próximos Pasos

1. **Revisión y aprobación:** Presentar este diseño al equipo/instructor para retroalimentación
2. **Configuración de base de datos:** Implementar Fase 1 (Oct 23-24)
3. **Adquisición de datos:** Descargar conjuntos de datos de DANE, Microsoft y Google
4. **Proceder con Entregable 2:** Integración de municipios PDET (entrega Nov 3)

---

## 8. Referencias

### Literatura Académica
1. **Performance analysis of MongoDB versus PostGIS/PostgreSQL databases for line intersection and point containment spatial queries.**  
   *Spatial Information Research* (2016). [https://doi.org/10.1007/s41324-016-0059-1](https://doi.org/10.1007/s41324-016-0059-1)

2. **MongoDB Vs PostgreSQL: A comparative study on performance aspects.**  
   *GeoInformatica* (2020). [https://doi.org/10.1007/s10707-020-00407-w](https://doi.org/10.1007/s10707-020-00407-w)

3. **The Comparison of Processing Efficiency of Spatial Data for PostGIS and MongoDB Databases.**  
   *ResearchGate* (2019). [https://www.researchgate.net/publication/336289725](https://www.researchgate.net/publication/336289725)

### Conjuntos de Datos
4. **Microsoft Global ML Building Footprints.**  
   Microsoft Bing Maps. [https://github.com/microsoft/GlobalMLBuildingFootprints](https://github.com/microsoft/GlobalMLBuildingFootprints)

5. **Google Open Buildings v3.**  
   Google Research. [https://sites.research.google/gr/open-buildings/](https://sites.research.google/gr/open-buildings/)

6. **Marco Geoestadístico Nacional (MGN).**  
   DANE Colombia. [https://geoportal.dane.gov.co](https://geoportal.dane.gov.co)

### Documentación Técnica
7. **MongoDB Documentation.**  
   MongoDB Manual 7.0. [https://www.mongodb.com/docs/manual/](https://www.mongodb.com/docs/manual/)

8. **PyMongo Documentation.**  
   Official Python Driver for MongoDB. [https://pymongo.readthedocs.io](https://pymongo.readthedocs.io)

9. **GeoPandas Documentation.**  
   [https://geopandas.org/](https://geopandas.org/)

10. **Folium Documentation.**  
    [https://python-visualization.github.io/folium/](https://python-visualization.github.io/folium/)

11. **Matplotlib Documentation.**  
    [https://matplotlib.org/stable/contents.html](https://matplotlib.org/stable/contents.html)


### Estándares
10. **OGC Simple Features Specification.** Open Geospatial Consortium. https://www.ogc.org/standards/sfa

---

### Estándares
10. **OGC Simple Features Specification.** Open Geospatial Consortium. [https://www.ogc.org/standards/sfa](https://www.ogc.org/standards/sfa)

---

## Apéndice A: Configuración de Conexión a Base de Datos

**Archivo:** `config/database.yml`

```yaml
database:
  host: localhost
  port: 27017
  name: pdet_solar_analysis
  user: pdet_user
  # La contraseña debe estar en el archivo .env (no debe subirse a git)

connection_pool:
  min_size: 2
  max_size: 10

spatial:
  default_crs: EPSG:4326   # WGS84
  colombia_crs: EPSG:3116  # MAGNA-SIRGAS Colombia
```

**Archivo:** `.env.example`

```bash
# Credenciales de base de datos MongoDB
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
Maneja conexiones MongoDB.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import yaml

# Cargar variables de entorno
load_dotenv()

# Cargar configuración desde archivo YAML
with open('config/database.yml', 'r') as f:
    config = yaml.safe_load(f)

def get_connection_string():
    """
    Generar cadena de conexión MongoDB desde configuración.

    Returns:
        str: URI de conexión MongoDB
    """
    db_config = config['database']
    password = os.getenv('DB_PASSWORD')

    # Conexión local o remota
    return (f"mongodb://{db_config['user']}:{password}"
            f"@{db_config['host']}:{db_config['port']}/"
            f"{db_config['name']}")

def create_mongo_client():
    """
    Crear cliente MongoDB.

    Returns:
        pymongo.MongoClient: Cliente de base de datos MongoDB
    """
    conn_string = get_connection_string()
    client = MongoClient(conn_string,
                         minPoolSize=config['connection_pool']['min_size'],
                         maxPoolSize=config['connection_pool']['max_size'])
    return client

def test_connection():
    """
    Probar conexión a MongoDB y listar bases de datos.

    Returns:
        bool: True si la conexión fue exitosa
    """
    try:
        client = create_mongo_client()
        db_list = client.list_database_names()
        print("✓ Conectado exitosamente a MongoDB")
        print(f"✓ Bases de datos disponibles: {db_list}")

        db = client[config['database']['name']]
        print(f"✓ Base de datos activa: {db.name}")

        # Crear colección de prueba
        db['test_connection'].insert_one({"status": "ok"})
        print("✓ Operación de escritura de prueba completada")
        db['test_connection'].drop()
        print("✓ Colección temporal eliminada")

        return True
    except Exception as e:
        print(f"✗ Conexión fallida: {e}")
        return False

if __name__ == "__main__":
    # Probar conexión cuando se ejecuta directamente
    test_connection()
```

---

**Fin del Reporte del Entregable 1**

---

**Preparado por:** Alejandro Pinzon Fajardo , Juan Jose Bermudez
**Fecha:** 22 de Octubre de 2025
**Versión:** 1.0
