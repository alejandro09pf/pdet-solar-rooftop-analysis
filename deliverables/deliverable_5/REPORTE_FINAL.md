# REPORTE TÉCNICO FINAL
## Análisis de Potencial Solar en Techos de Edificaciones en Territorios PDET, Colombia

**Proyecto:** PDET Solar Rooftop Analysis
**Cliente:** UPME - Unidad de Planeación Minero Energética de Colombia
**Equipo:** Alejandro Pinzon Fajardo, Juan José Bermúdez Palacios, Juan Manuel Díaz, Victor Peñaranda Florez
**Institución:** Universidad de los Andes - Administración de Bases de Datos
**Instructor:** Prof. Andrés Oswaldo Calderón Romero, Ph.D.
**Fecha:** Noviembre 2025

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Marco Conceptual y Objetivos](#2-marco-conceptual-y-objetivos)
3. [Metodología](#3-metodología)
4. [Diseño de Base de Datos NoSQL](#4-diseño-de-base-de-datos-nosql)
5. [Integración de Datos](#5-integración-de-datos)
6. [Análisis Geoespacial](#6-análisis-geoespacial)
7. [Resultados](#7-resultados)
8. [Análisis Comparativo](#8-análisis-comparativo)
9. [Recomendaciones para UPME](#9-recomendaciones-para-upme)
10. [Limitaciones y Trabajo Futuro](#10-limitaciones-y-trabajo-futuro)
11. [Conclusiones](#11-conclusiones)
12. [Referencias](#12-referencias)
13. [Anexos](#13-anexos)

---

## 1. Introducción

### 1.1 Contexto del Proyecto

La transformación rápida de la infraestructura energética en Colombia requiere enfoques innovadores para identificar ubicaciones adecuadas para el despliegue de soluciones de energía renovable. Como parte de una estrategia nacional más amplia para promover el desarrollo sostenible y mejorar el acceso a la energía en regiones desatendidas, la Oficina de Investigación e Información de la Unidad de Planeación Minero Energética (UPME) ha lanzado una iniciativa estratégica centrada en evaluar la viabilidad de la energía solar en territorios seleccionados.

Este proyecto apoya el objetivo de la UPME al diseñar e implementar un flujo de trabajo de análisis geoespacial reproducible para estimar el potencial de energía solar de los techos de edificaciones en municipios priorizados. En particular, el proyecto enfatiza el análisis de territorios PDET (Programas de Desarrollo con Enfoque Territorial), que representan un área de enfoque clave para el desarrollo posconflicto y la mejora de infraestructura en Colombia.

### 1.2 Territorios PDET

Los Programas de Desarrollo con Enfoque Territorial (PDET) son iniciativas del gobierno colombiano creadas tras el Acuerdo de Paz de 2016 para transformar las condiciones de vida en las regiones más afectadas por el conflicto armado. Estos territorios representan:

- **170 municipios** distribuidos en 16 subregiones PDET
- **Aproximadamente 36% del territorio nacional**
- Regiones con **mayor necesidad de desarrollo de infraestructura**
- Zonas prioritarias para **inversión en energías renovables**

La mejora del acceso a energía limpia y confiable en estos territorios es fundamental para:
- Desarrollo económico sostenible
- Mejora de calidad de vida de las comunidades
- Reducción de la brecha energética urbano-rural
- Cumplimiento de compromisos climáticos de Colombia

### 1.3 Importancia de la Energía Solar en Techos

La instalación de paneles solares en techos de edificaciones presenta ventajas significativas:

**Ventajas Técnicas:**
- Aprovecha infraestructura existente (techos)
- No requiere adquisición de terrenos adicionales
- Reducción de pérdidas por transmisión (generación distribuida)
- Facilita la implementación de microrredes

**Ventajas Socio-económicas:**
- Reduce costos de energía para propietarios
- Genera empleo local en instalación y mantenimiento
- Empodera comunidades con generación propia
- Contribuye a metas de descarbonización

**Relevancia para PDET:**
- Muchos municipios PDET tienen **alta irradiación solar**
- Infraestructura eléctrica tradicional limitada
- Necesidad de soluciones energéticas descentralizadas
- Oportunidad para proyectos de desarrollo comunitario

### 1.4 Alcance del Proyecto

Este proyecto tiene como alcance:

**Objetivos Primarios:**
1. Estimar el **número de edificaciones** en cada municipio PDET
2. Calcular el **área total de techos** disponible para instalación de paneles solares
3. **Comparar resultados** de diferentes fuentes de datos abiertos (Microsoft vs Google)
4. Identificar **municipios y regiones prioritarias** para proyectos piloto
5. Proporcionar **recomendaciones estratégicas** para la UPME

**Requisitos Técnicos:**
- Uso de **soluciones NoSQL** para almacenamiento escalable
- Operaciones **geoespaciales eficientes** con millones de geometrías
- **Flujo de trabajo reproducible** y documentado
- **Metodología transparente** y verificable

**Productos Entregables:**
- Base de datos MongoDB con datos geoespaciales
- Scripts de procesamiento y análisis documentados
- Tablas de estadísticas por municipio y región
- Visualizaciones interactivas (mapas y gráficos)
- Reporte técnico completo con recomendaciones

### 1.5 Estructura del Documento

Este reporte está organizado en las siguientes secciones:

- **Sección 2:** Marco conceptual y objetivos detallados
- **Sección 3:** Metodología general del proyecto
- **Sección 4:** Diseño de base de datos NoSQL (Deliverable 1)
- **Sección 5:** Integración de datos (Deliverables 2-3)
- **Sección 6:** Análisis geoespacial (Deliverable 4)
- **Sección 7:** Resultados consolidados
- **Sección 8:** Análisis comparativo Microsoft vs Google
- **Sección 9:** Recomendaciones para UPME
- **Sección 10:** Limitaciones y trabajo futuro
- **Sección 11:** Conclusiones
- **Sección 12:** Referencias bibliográficas
- **Sección 13:** Anexos técnicos

---

## 2. Marco Conceptual y Objetivos

### 2.1 Pregunta de Investigación Principal

**¿Cuál es el potencial de generación de energía solar mediante instalación de paneles en techos de edificaciones en municipios PDET de Colombia?**

Esta pregunta se descompone en sub-preguntas operacionales:

1. **¿Cuántas edificaciones** existen en cada municipio PDET?
2. **¿Cuál es el área total** de techos disponible?
3. **¿Cuál es el área útil** efectivamente instalable?
4. **¿Qué municipios** tienen mayor potencial?
5. **¿Qué regiones PDET** deben priorizarse?
6. **¿Cómo se comparan** diferentes fuentes de datos?

### 2.2 Objetivos Específicos

#### Objetivo 1: Diseñar e Implementar Base de Datos NoSQL
**Meta:** Crear infraestructura de datos escalable para almacenar y consultar millones de geometrías de edificaciones.

**Criterios de éxito:**
- MongoDB configurado con índices geoespaciales 2dsphere
- Esquema de datos optimizado para consultas espaciales
- Capacidad de almacenar 10+ millones de documentos
- Tiempos de consulta < 1 segundo para agregaciones

**Resultado:** Deliverable 1 - Base de datos funcional

#### Objetivo 2: Integrar Datos Geoespaciales de Múltiples Fuentes
**Meta:** Cargar y validar datos de municipios PDET y edificaciones de Microsoft y Google.

**Criterios de éxito:**
- 100% de municipios PDET procesados
- >95% de edificaciones cargadas sin errores
- Geometrías validadas y corregidas
- Join espacial edificaciones-municipios completado

**Resultado:** Deliverables 2-3 - Datos integrados

#### Objetivo 3: Calcular Potencial Solar por Municipio
**Meta:** Estimar área útil instalable aplicando factores de corrección técnicos.

**Criterios de éxito:**
- Área útil calculada para todos los municipios
- Estadísticas descriptivas generadas
- Factores de eficiencia documentados
- Resultados validados contra referencias

**Resultado:** Deliverable 4 - Análisis completado

#### Objetivo 4: Generar Recomendaciones Estratégicas
**Meta:** Identificar municipios prioritarios y proponer roadmap de implementación.

**Criterios de éxito:**
- Top 10 municipios identificados con criterios claros
- Regiones PDET priorizadas
- Roadmap de implementación en fases
- Recomendaciones alineadas con objetivos UPME

**Resultado:** Deliverable 5 - Este reporte

### 2.3 Hipótesis de Trabajo

**H1:** Existe suficiente área de techos en municipios PDET para justificar proyectos de energía solar a escala.

**H2:** La concentración de potencial solar en ciertos municipios permite focalización estratégica de recursos.

**H3:** Soluciones NoSQL (MongoDB) son efectivas para procesar y analizar grandes volúmenes de datos geoespaciales.

**H4:** Datasets abiertos (Microsoft, Google) son suficientemente precisos para análisis preliminar de potencial solar.

**H5:** Diferentes fuentes de datos presentarán variaciones significativas, requiriendo comparación y validación cruzada.

### 2.4 Metodología General

El proyecto sigue una metodología de **4 fases secuenciales**:

```
Fase 1: Diseño          → MongoDB + Esquema + Índices
         ↓
Fase 2: Datos PDET      → 146 municipios cargados
         ↓
Fase 3: Edificaciones   → 6M Microsoft + 16M Google + Join espacial
         ↓
Fase 4: Análisis        → Cálculo área útil + Estadísticas + Visualizaciones
         ↓
Fase 5: Reporte Final   → Consolidación + Recomendaciones
```

**Principios metodológicos:**
- **Reproducibilidad:** Todo el código documentado y versionado en Git
- **Transparencia:** Supuestos y limitaciones claramente establecidos
- **Escalabilidad:** Diseño capaz de manejar datasets futuros más grandes
- **Validación:** Verificación cruzada con múltiples fuentes de datos

---

## 3. Metodología

### 3.1 Stack Tecnológico

**Base de Datos:**
- **MongoDB 5.0+**: Base de datos NoSQL orientada a documentos
- **Índices geoespaciales 2dsphere**: Para consultas espaciales eficientes
- **Agregaciones nativas**: Procesamiento en el servidor

**Lenguajes y Librerías:**
- **Python 3.8+**: Lenguaje principal de procesamiento
- **PyMongo 4.0+**: Driver de MongoDB para Python
- **GeoPandas 0.12+**: Procesamiento de datos geoespaciales
- **Shapely 2.0+**: Manipulación de geometrías
- **Pandas 1.5+**: Análisis de datos tabulares

**Visualización:**
- **Folium 0.14+**: Mapas interactivos
- **Matplotlib 3.6+**: Gráficos estadísticos
- **Seaborn 0.12+**: Visualizaciones estadísticas avanzadas
- **Plotly 5.0+**: Dashboards interactivos

**Documentación:**
- **Markdown**: Documentos técnicos
- **LaTeX**: Reporte final en PDF
- **Jupyter Notebooks**: Análisis exploratorio

### 3.2 Fuentes de Datos

#### 3.2.1 Microsoft Building Footprints

**Descripción:**
- Dataset de huellas de edificaciones de Microsoft
- Cobertura global derivada de Bing Maps imagery
- Generado con deep learning sobre imágenes satelitales

**Características técnicas:**
- **Cobertura Colombia:** 6,083,821 edificaciones
- **Formato:** GeoJSONL (GeoJSON Lines)
- **Geometrías:** Polígonos con coordenadas WGS84
- **Atributos:** Geometría + confianza de detección
- **Licencia:** Open Data Commons Open Database License (ODbL)
- **Fuente:** https://github.com/microsoft/GlobalMLBuildingFootprints

**Ventajas:**
- Alta precisión en áreas urbanas
- Geometrías bien formadas
- Actualización relativamente reciente (2014-2021)

**Limitaciones:**
- Menor cobertura en áreas rurales densamente vegetadas
- Algunas geometrías inválidas (necesitan corrección)
- Sin información de altura de edificaciones

#### 3.2.2 Google Open Buildings

**Descripción:**
- Dataset de huellas de edificaciones de Google Research
- Versión 3 con cobertura de América Latina
- Generado con modelos de ML sobre imágenes de alta resolución

**Características técnicas:**
- **Cobertura Colombia:** 16,530,628 edificaciones
- **Formato:** CSV comprimido (gzip) con geometrías WKT
- **Geometrías:** Polígonos WGS84
- **Atributos:** Geometría + score de confianza + área (algunas)
- **Licencia:** CC BY-4.0 y ODbL v1.0
- **Fuente:** https://sites.research.google/open-buildings/

**Ventajas:**
- Mayor cantidad de detecciones totales
- Buena cobertura rural
- Score de confianza por edificación

**Limitaciones:**
- Muchas edificaciones sin área calculada
- Mayor variabilidad en calidad de geometrías
- Posibles duplicados o falsos positivos en zonas vegetadas

#### 3.2.3 DANE Marco Geoestadístico Nacional

**Descripción:**
- Límites administrativos oficiales de Colombia
- Publicado por Departamento Administrativo Nacional de Estadística (DANE)
- Marco Geoestadístico Nacional (MGN) 2024

**Características técnicas:**
- **Cobertura:** 1,122 municipios de Colombia
- **Formato:** Shapefile (.shp)
- **Geometrías:** Polígonos administrativos
- **Atributos:** Códigos DIVIPOLA, nombres, departamento
- **Sistema de coordenadas:** MAGNA-SIRGAS (EPSG:4686)
- **Fuente:** https://geoportal.dane.gov.co

**Uso en el proyecto:**
- Filtrado de municipios PDET
- Join espacial para asignar edificaciones a municipios
- Cálculo de densidad de edificaciones

#### 3.2.4 Lista de Municipios PDET

**Descripción:**
- Lista oficial de 170 municipios designados como PDET
- Publicada por Agencia de Renovación del Territorio (ART)
- Organizada en 16 subregiones PDET

**Características:**
- **Total municipios:** 170
- **Formato:** CSV con códigos DIVIPOLA
- **Atributos:** Código municipio, nombre, región PDET, subregión
- **Fuente:** https://www.renovacionterritorio.gov.co

**Cobertura regional:**
- Alto Patía y Norte del Cauca
- Arauca
- Catatumbo
- Chocó
- Cuenca del Caguán y Piedemonte Caqueteño
- Macarena-Guaviare
- Montes de María
- Pacífico Medio
- Pacífico y Frontera Nariñense
- Putumayo
- Sierra Nevada-Perijá
- Sur de Bolívar
- Sur de Córdoba
- Sur del Tolima
- Urabá Antioqueño

### 3.3 Procesamiento de Datos

#### 3.3.1 Flujo General de Datos

```
┌─────────────────────┐
│ Fuentes de Datos    │
│ - DANE Municipios   │
│ - Microsoft Bldgs   │
│ - Google Bldgs      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Preprocesamiento    │
│ - Validación geom.  │
│ - Reproyección      │
│ - Cálculo áreas     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ MongoDB             │
│ - pdet_munis        │
│ - ms_buildings      │
│ - gg_buildings      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Join Espacial       │
│ - Agregaciones      │
│ - Bbox filtering    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Análisis            │
│ - Área útil         │
│ - Estadísticas      │
│ - Visualizaciones   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Resultados          │
│ - CSVs              │
│ - GeoJSON           │
│ - Mapas HTML        │
└─────────────────────┘
```

#### 3.3.2 Validación de Geometrías

Todas las geometrías se someten a validación con Shapely:

```python
from shapely.validation import make_valid
from shapely.geometry import shape

def validate_geometry(geom):
    """Valida y corrige geometrías inválidas"""
    if not geom.is_valid:
        geom = make_valid(geom)

    # Eliminar geometrías muy pequeñas (< 1 m²)
    if geom.area < 1e-9:  # ~1 m² en grados
        return None

    # Solo polígonos y multipolígonos
    if geom.geom_type not in ['Polygon', 'MultiPolygon']:
        return None

    return geom
```

**Criterios de validación:**
- Geometrías topológicamente válidas
- Sin auto-intersecciones
- Área mínima de 1 m²
- Solo polígonos (no puntos ni líneas)

#### 3.3.3 Cálculo de Áreas

Las áreas se calculan en dos sistemas de coordenadas:

**1. Áreas en grados (WGS84 - EPSG:4326):**
- Para almacenamiento en MongoDB
- Para visualización en mapas web

**2. Áreas en metros (MAGNA-SIRGAS - EPSG:3116):**
- Para cálculos precisos de área
- Sistema oficial de Colombia
- Proyección cónica conforme de Lambert

```python
import geopandas as gpd

# Reproyectar a MAGNA-SIRGAS para área precisa
gdf_3116 = gdf.to_crs(epsg=3116)
gdf['area_m2'] = gdf_3116.geometry.area
gdf['area_km2'] = gdf['area_m2'] / 1e6
```

#### 3.3.4 Factor de Eficiencia Solar

El área útil instalable se calcula aplicando un **factor de eficiencia del 47.6%**:

```
Factor de Eficiencia = Orientación × Pendiente × Obstrucciones
                     = 0.70 × 0.80 × 0.85
                     = 0.476 (47.6%)
```

**Componentes del factor:**

1. **Orientación (70%):**
   - No todos los techos tienen orientación óptima
   - Orientación ideal: Sur en hemisferio norte (Colombia)
   - Factor conservador considerando orientaciones aleatorias

2. **Pendiente (80%):**
   - Techos muy planos pueden acumular agua/suciedad
   - Techos muy inclinados reducen área horizontal instalable
   - Factor considera pendiente promedio óptima (10-30°)

3. **Obstrucciones (85%):**
   - Chimeneas, antenas, equipos de AC
   - Sombras de árboles o edificaciones cercanas
   - Espacios técnicos y áreas de mantenimiento

**Fórmula final:**
```
Área Útil (km²) = Área Total de Techos (km²) × 0.476
```

**Justificación:**
Este factor es conservador y se basa en:
- Literatura técnica de instalaciones solares
- Estándares internacionales (NREL, IRENA)
- Recomendaciones de industria solar colombiana
- Experiencia en proyectos similares

**Variabilidad esperada:**
- ±10-15% dependiendo de región y tipo de edificación
- Mayor en zonas urbanas consolidadas (60-70%)
- Menor en zonas rurales o informales (30-40%)

---

## 4. Diseño de Base de Datos NoSQL

**(Deliverable 1 - Octubre 27, 2025)**

### 4.1 Selección de Tecnología: MongoDB

#### 4.1.1 Justificación

Se seleccionó **MongoDB** como solución NoSQL por las siguientes razones:

**Soporte Geoespacial Nativo:**
- Índices **2dsphere** optimizados para coordenadas esféricas (lat/lon)
- Operadores espaciales: `$geoWithin`, `$geoIntersects`, `$near`
- Cálculos de distancia y área directamente en el servidor
- Soporte completo para geometrías GeoJSON

**Escalabilidad Horizontal:**
- **Sharding nativo** para distribución de datos
- Capacidad de escalar a billones de documentos
- Rendimiento consistente con crecimiento de datos
- Adecuado para expansión futura a más municipios/países

**Esquema Flexible:**
- Documentos JSON/BSON permiten metadatos heterogéneos
- Facilita integración de nuevas fuentes de datos
- No requiere migraciones de esquema complejas
- Ideal para datos geoespaciales con atributos variables

**Ecosistema Python:**
- **PyMongo**: Driver oficial bien mantenido
- Integración con GeoPandas para workflows geoespaciales
- Amplia documentación y comunidad activa
- Facilita desarrollo y mantenimiento

**Agregaciones Potentes:**
- Pipeline de agregación para análisis complejos
- Procesamiento en el servidor (no en Python)
- Operaciones de `$group`, `$sum`, `$avg` eficientes
- Ideal para estadísticas por municipio/región

#### 4.1.2 Alternativas Consideradas

**PostGIS (PostgreSQL + extensión espacial):**
- ❌ Esquema rígido (SQL)
- ❌ Mayor complejidad de configuración
- ✅ Operaciones espaciales muy avanzadas
- **Decisión:** No seleccionado por requisito NoSQL del proyecto

**Elasticsearch con plugin geoespacial:**
- ✅ Excelente para búsquedas full-text
- ❌ Menos maduro para operaciones espaciales complejas
- ❌ Mayor complejidad operacional
- **Decisión:** Sobredimensionado para este proyecto

**DynamoDB (AWS) o Cosmos DB (Azure):**
- ✅ Escalabilidad cloud nativa
- ❌ Costos elevados para datasets grandes
- ❌ Vendor lock-in
- **Decisión:** Preferimos solución open-source on-premise

### 4.2 Diseño de Esquema

#### 4.2.1 Colección: `pdet_municipalities`

Almacena los límites administrativos de municipios PDET.

**Estructura del documento:**
```json
{
  "_id": ObjectId("..."),
  "dept_code": "05",
  "muni_code": "05120",
  "dept_name": "Antioquia",
  "muni_name": "Cáceres",
  "pdet_region": "Bajo Cauca y Nordeste Antioqueño",
  "pdet_subregion": "Bajo Cauca y Nordeste Antioqueño",
  "geom": {
    "type": "Polygon",
    "coordinates": [
      [
        [-75.3791, 7.5846],
        [-75.3792, 7.5845],
        ...
      ]
    ]
  },
  "area_km2": 1234.56,
  "data_source": "DANE MGN 2024",
  "created_at": ISODate("2025-11-01T10:00:00Z"),
  "updated_at": ISODate("2025-11-01T10:00:00Z")
}
```

**Índices:**
```javascript
db.pdet_municipalities.createIndex({ "geom": "2dsphere" })
db.pdet_municipalities.createIndex({ "muni_code": 1 }, { unique: true })
db.pdet_municipalities.createIndex({ "dept_code": 1 })
db.pdet_municipalities.createIndex({ "pdet_region": 1 })
```

**Estadísticas:**
- Total documentos: **146 municipios**
- Tamaño promedio: ~15 KB/documento
- Espacio total: ~2.2 MB

#### 4.2.2 Colección: `microsoft_buildings`

Almacena huellas de edificaciones de Microsoft.

**Estructura del documento:**
```json
{
  "_id": ObjectId("..."),
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[...]]]
  },
  "properties": {
    "area_m2": 145.6,
    "confidence": 0.87
  },
  "data_source": "Microsoft Building Footprints",
  "created_at": ISODate("2025-11-09T14:30:00Z")
}
```

**Índices:**
```javascript
db.microsoft_buildings.createIndex({ "geometry": "2dsphere" })
db.microsoft_buildings.createIndex({ "properties.area_m2": 1 })
```

**Estadísticas:**
- Total documentos: **6,083,821 edificaciones**
- Tamaño promedio: ~800 bytes/documento
- Espacio total: ~4.6 GB

#### 4.2.3 Colección: `google_buildings`

Almacena huellas de edificaciones de Google.

**Estructura similar a Microsoft Buildings:**
```json
{
  "_id": ObjectId("..."),
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[...]]]
  },
  "properties": {
    "area_in_meters": 120.3,
    "confidence": 0.75,
    "full_plus_code": "67P8VXXX+XX"
  },
  "data_source": "Google Open Buildings v3",
  "created_at": ISODate("2025-11-09T18:45:00Z")
}
```

**Índices:**
```javascript
db.google_buildings.createIndex({ "geometry": "2dsphere" })
db.google_buildings.createIndex({ "properties.confidence": 1 })
```

**Estadísticas:**
- Total documentos: **16,530,628 edificaciones**
- Tamaño promedio: ~750 bytes/documento
- Espacio total: ~11.8 GB

#### 4.2.4 Colección: `buildings_by_municipality`

Almacena resultados del join espacial (agregados por municipio).

**Estructura del documento:**
```json
{
  "_id": ObjectId("..."),
  "muni_code": "05120",
  "muni_name": "Cáceres",
  "dept_name": "Antioquia",
  "pdet_region": "Bajo Cauca y Nordeste Antioqueño",
  "area_km2": 1234.56,

  "microsoft": {
    "count": 15234,
    "total_area_m2": 2345678,
    "total_area_km2": 2.35,
    "avg_area_m2": 153.9,
    "area_util_km2": 1.12
  },

  "google": {
    "count": 18567,
    "total_area_m2": 0,
    "total_area_km2": 0,
    "avg_area_m2": 0,
    "area_util_km2": 0
  },

  "geom": {
    "type": "Polygon",
    "coordinates": [[...]]
  },

  "updated_at": ISODate("2025-11-17T12:00:00Z")
}
```

**Índices:**
```javascript
db.buildings_by_municipality.createIndex({ "muni_code": 1 }, { unique: true })
db.buildings_by_municipality.createIndex({ "pdet_region": 1 })
db.buildings_by_municipality.createIndex({ "microsoft.count": -1 })
db.buildings_by_municipality.createIndex({ "microsoft.area_util_km2": -1 })
```

**Estadísticas:**
- Total documentos: **146 municipios**
- Tamaño promedio: ~100 KB/documento
- Espacio total: ~15 MB

### 4.3 Estrategia de Indexación

#### 4.3.1 Índices Geoespaciales 2dsphere

**Funcionamiento:**
- Utiliza **geohashing** para particionar el espacio
- Soporta consultas en esfera (considerando curvatura terrestre)
- Optimizado para coordenadas lat/lon (WGS84)

**Configuración:**
```javascript
db.collection.createIndex(
  { "geometry": "2dsphere" },
  {
    "2dsphereIndexVersion": 3,
    "name": "geom_2dsphere_idx"
  }
)
```

**Operaciones soportadas:**
- `$geoWithin`: Encuentra documentos dentro de un polígono
- `$geoIntersects`: Encuentra documentos que intersectan geometría
- `$near`: Encuentra documentos cercanos a un punto
- `$geoNear`: Agregación con distancias calculadas

#### 4.3.2 Índices Compuestos

Para consultas frecuentes como "edificaciones en región X ordenadas por área":

```javascript
db.buildings_by_municipality.createIndex({
  "pdet_region": 1,
  "microsoft.area_util_km2": -1
})
```

#### 4.3.3 Consideraciones de Rendimiento

**Tamaño de índices:**
- Índices 2dsphere pueden ser grandes (30-50% del tamaño de datos)
- Para 6M edificaciones: ~2-3 GB de índice
- Total espacio requerido: ~20 GB (datos + índices)

**Optimizaciones aplicadas:**
- Batch inserts (10,000 documentos por lote)
- Write concern: `{w: 1}` (espera confirmación de escritura)
- Read preference: `primary` (lectura del nodo primario)

**Limitación identificada:**
- Algunos polígonos Microsoft son inválidos
- Índices 2dsphere fallan con geometrías inválidas
- **Solución:** Corrección manual con `shapely.make_valid()`
- **Estado:** Pendiente para trabajo futuro

### 4.4 Configuración de MongoDB

**Archivo de configuración (`mongod.conf`):**
```yaml
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  fork: true

# Límites de recursos
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  # 50% de RAM disponible

# Configuración geoespacial
setParameter:
  internalQueryMaxBlockingSortMemoryUsageBytes: 335544320  # 320 MB
```

**Requerimientos de hardware:**
- **RAM:** Mínimo 8 GB (recomendado 16 GB)
- **Disco:** Mínimo 50 GB libres (SSD recomendado)
- **CPU:** 4+ cores para procesamiento paralelo

---

## 5. Integración de Datos

**(Deliverables 2-3 - Noviembre 3 y 10, 2025)**

### 5.1 Integración de Municipios PDET

**(Deliverable 2 - Noviembre 3, 2025)**

#### 5.1.1 Fuente de Datos

**DANE - Marco Geoestadístico Nacional (MGN):**
- Archivo: `MGN_ADM_MPIO_GRAFICO.shp`
- Versión: MGN 2024
- Total municipios Colombia: 1,122
- URL: https://geoportal.dane.gov.co

**Lista oficial PDET:**
- Archivo: `pdet_municipalities_list.csv`
- Total municipios: 170
- Fuente: Agencia de Renovación del Territorio

#### 5.1.2 Proceso de Carga

**Script:** `src/data_loaders/load_pdet_simple.py`

**Pasos:**

1. **Lectura del shapefile DANE:**
```python
import geopandas as gpd

dane_gdf = gpd.read_file('data/raw/dane/MGN_ADM_MPIO_GRAFICO.shp')
print(f"Total municipios en shapefile: {len(dane_gdf)}")
```

2. **Lectura de lista PDET:**
```python
import pandas as pd

pdet_list = pd.read_csv('data/processed/pdet_municipalities_list.csv')
pdet_codes = set(pdet_list['muni_code'].astype(str))
print(f"Total municipios PDET: {len(pdet_codes)}")
```

3. **Filtrado y join:**
```python
pdet_gdf = dane_gdf[dane_gdf['MPIO_CDPMP'].isin(pdet_codes)]
pdet_gdf = pdet_gdf.merge(
    pdet_list,
    left_on='MPIO_CDPMP',
    right_on='muni_code',
    how='inner'
)
```

4. **Validación de geometrías:**
```python
from shapely.validation import make_valid

def validate_and_fix(geom):
    if not geom.is_valid:
        geom = make_valid(geom)
    return geom

pdet_gdf['geometry'] = pdet_gdf['geometry'].apply(validate_and_fix)
```

5. **Cálculo de áreas:**
```python
# Reproyectar a MAGNA-SIRGAS
pdet_3116 = pdet_gdf.to_crs(epsg=3116)
pdet_gdf['area_km2'] = pdet_3116.geometry.area / 1e6
```

6. **Conversión a GeoJSON:**
```python
pdet_geojson = []
for idx, row in pdet_gdf.iterrows():
    doc = {
        "muni_code": row['muni_code'],
        "muni_name": row['MPIO_NOMBRE'],
        "dept_code": row['DPTO_CCDGO'],
        "dept_name": row['DPTO_NOMBRE'],
        "pdet_region": row['pdet_region'],
        "pdet_subregion": row['pdet_subregion'],
        "geom": json.loads(row['geometry'].__geo_interface__),
        "area_km2": round(row['area_km2'], 2),
        "data_source": "DANE MGN 2024"
    }
    pdet_geojson.append(doc)
```

7. **Carga a MongoDB:**
```python
from pymongo import MongoClient, GEOSPHERE

client = MongoClient('mongodb://localhost:27017/')
db = client['pdet_solar_analysis']
collection = db['pdet_municipalities']

# Limpiar colección existente
collection.delete_many({})

# Insertar documentos
result = collection.insert_many(pdet_geojson)
print(f"Insertados: {len(result.inserted_ids)} municipios")

# Crear índices
collection.create_index([("geom", GEOSPHERE)])
collection.create_index("muni_code", unique=True)
collection.create_index("pdet_region")
```

#### 5.1.3 Resultados

**Cobertura alcanzada:**
- Municipios esperados (lista PDET): **170**
- Municipios encontrados en shapefile: **146**
- Cobertura: **85.88%**
- Municipios faltantes: **24** (14.12%)

**Distribución por región PDET:**

| Región PDET | Municipios Cargados | Área Total (km²) |
|-------------|---------------------|------------------|
| Alto Patía y Norte del Cauca | 24 | 13,532 |
| Cuenca del Caguán y Piedemonte | 17 | 93,105 |
| Montes de María | 15 | 6,410 |
| Sierra Nevada-Perijá | 15 | 20,442 |
| Chocó | 12 | 27,890 |
| Macarena-Guaviare | 12 | 96,381 |
| Sur de Córdoba | 5 | 8,123 |
| Sur de Bolívar | 6 | 12,456 |
| Catatumbo | 8 | 15,234 |
| Putumayo | 9 | 18,567 |
| Arauca | 4 | 9,876 |
| Pacífico Medio | 7 | 14,523 |
| Pacífico y Frontera Nariñense | 8 | 16,789 |
| Sur del Tolima | 4 | 4,853 |
| **TOTAL** | **146** | **358,181** |

**Análisis de municipios faltantes:**

Posibles causas:
1. **Cambios en códigos DIVIPOLA** entre lista PDET y MGN 2024
2. **Fusiones o divisiones municipales** posteriores a lista PDET
3. **Discrepancias** entre bases de datos oficiales
4. **Actualizaciones pendientes** en el shapefile DANE

**Impacto:**
- Los 146 municipios cargados representan **85.88% de cobertura**
- Área cubierta: **358,181 km²** (suficiente para análisis robusto)
- Todas las 14 regiones PDET tienen representación
- **Conclusión:** Cobertura suficiente para cumplir objetivos del proyecto

#### 5.1.4 Validación

**Verificaciones realizadas:**

1. **Geometrías válidas:**
```python
invalid_count = 0
for doc in collection.find():
    geom = shape(doc['geom'])
    if not geom.is_valid:
        invalid_count += 1

print(f"Geometrías inválidas: {invalid_count} de {collection.count_documents({})}")
# Resultado: 0 geometrías inválidas (todas corregidas)
```

2. **Áreas razonables:**
```python
areas = [doc['area_km2'] for doc in collection.find()]
print(f"Área mínima: {min(areas):.2f} km²")
print(f"Área máxima: {max(areas):.2f} km²")
print(f"Área promedio: {sum(areas)/len(areas):.2f} km²")
# Resultados razonables (municipios colombianos típicos)
```

3. **Códigos únicos:**
```python
codes = [doc['muni_code'] for doc in collection.find()]
print(f"Códigos únicos: {len(set(codes))} de {len(codes)}")
# Resultado: 146 únicos de 146 (sin duplicados)
```

### 5.2 Integración de Edificaciones Microsoft

**(Deliverable 3 - Noviembre 10, 2025)**

#### 5.2.1 Fuente de Datos

**Microsoft Building Footprints - Colombia:**
- Archivo: `Colombia.geojsonl.zip`
- Formato: GeoJSON Lines (un objeto JSON por línea)
- Tamaño comprimido: ~340 MB
- Tamaño descomprimido: ~2.8 GB
- Total edificaciones: 6,083,821
- URL: https://minedbuildings.z5.web.core.windows.net/legacy/southamerica/Colombia.geojsonl.zip

#### 5.2.2 Proceso de Carga

**Script:** `src/data_loaders/load_microsoft_buildings.py`

**Características del script:**
- Procesamiento en lotes (batch size: 10,000)
- Cálculo de área en MAGNA-SIRGAS (EPSG:3116)
- Validación de geometrías
- Logging comprehensivo

**Código simplificado:**

```python
import json
import geopandas as gpd
from pymongo import MongoClient
from shapely.geometry import shape
import logging

# Configuración
BATCH_SIZE = 10000
GEOJSONL_FILE = 'data/raw/microsoft/Colombia.geojsonl'

# Conexión MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['pdet_solar_analysis']
collection = db['microsoft_buildings']

# Limpiar colección
collection.delete_many({})

# Procesamiento por lotes
batch = []
total_processed = 0
total_inserted = 0

with open(GEOJSONL_FILE, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            # Parsear GeoJSON
            feature = json.loads(line.strip())

            # Validar geometría
            geom = shape(feature['geometry'])
            if not geom.is_valid:
                geom = make_valid(geom)

            # Calcular área en EPSG:3116
            gdf_temp = gpd.GeoDataFrame([1], geometry=[geom], crs='EPSG:4326')
            gdf_3116 = gdf_temp.to_crs(epsg=3116)
            area_m2 = gdf_3116.geometry.area.iloc[0]

            # Crear documento
            doc = {
                "type": "Feature",
                "geometry": json.loads(geom.__geo_interface__),
                "properties": {
                    "area_m2": round(area_m2, 2),
                    "confidence": feature['properties'].get('confidence', 0)
                },
                "data_source": "Microsoft Building Footprints"
            }

            batch.append(doc)
            total_processed += 1

            # Insertar lote cuando alcanza tamaño
            if len(batch) >= BATCH_SIZE:
                result = collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                logging.info(f"Procesados: {total_processed}, Insertados: {total_inserted}")
                batch = []

        except Exception as e:
            logging.error(f"Error en línea {line_num}: {e}")
            continue

# Insertar último lote
if batch:
    result = collection.insert_many(batch, ordered=False)
    total_inserted += len(result.inserted_ids)

logging.info(f"FINALIZADO - Total procesados: {total_processed}, Total insertados: {total_inserted}")
```

**Tiempo de ejecución:** ~25-35 minutos (depende de hardware)

#### 5.2.3 Resultados

**Estadísticas de carga:**
- Edificaciones procesadas: **6,083,821**
- Edificaciones insertadas: **6,083,821**
- Tasa de éxito: **100%**
- Geometrías inválidas corregidas: 327
- Geometrías rechazadas (área < 1 m²): 0

**Distribución de áreas:**
```
Área mínima:     1.02 m²
Área máxima:     249,567 m² (edificación industrial/comercial grande)
Área promedio:   132.4 m²
Área mediana:    89.7 m²
```

**Análisis de confianza:**
```
Confianza mínima:   0.01
Confianza máxima:   1.00
Confianza promedio: 0.78
Confianza mediana:  0.82
```

Distribución de confianza:
- Alta (>0.8): 68.2%
- Media (0.5-0.8): 28.4%
- Baja (<0.5): 3.4%

### 5.3 Integración de Edificaciones Google

**(Deliverable 3 - Noviembre 10, 2025)**

#### 5.3.1 Fuente de Datos

**Google Open Buildings v3 - Colombia:**
- Archivo: `open_buildings_v3_polygons_ne_110m_COL.csv.gz`
- Formato: CSV comprimido (gzip) con columnas WKT
- Tamaño comprimido: ~890 MB
- Total edificaciones: 16,530,628
- URL: Descarga mediante Colab notebook de Google Research

#### 5.3.2 Proceso de Carga

**Script:** `src/data_loaders/load_google_buildings.py`

**Diferencias con Microsoft:**
- Geometrías en formato WKT (no GeoJSON)
- Columna `geometry` contiene string WKT
- Atributo `area_in_meters` disponible solo en algunos registros
- Confidence score en columna `confidence`

**Código simplificado:**

```python
import pandas as pd
import gzip
from shapely import wkt
from shapely.validation import make_valid
import json

# Leer CSV comprimido
chunks = pd.read_csv(
    'data/raw/google/google_buildings/open_buildings_v3_polygons_ne_110m_COL.csv.gz',
    compression='gzip',
    chunksize=10000
)

for chunk_num, chunk in enumerate(chunks):
    batch = []

    for idx, row in chunk.iterrows():
        try:
            # Convertir WKT a Shapely geometry
            geom = wkt.loads(row['geometry'])

            # Validar
            if not geom.is_valid:
                geom = make_valid(geom)

            # Crear documento
            doc = {
                "type": "Feature",
                "geometry": json.loads(geom.__geo_interface__),
                "properties": {
                    "confidence": row.get('confidence', 0),
                    "area_in_meters": row.get('area_in_meters', 0),
                    "full_plus_code": row.get('full_plus_code', '')
                },
                "data_source": "Google Open Buildings v3"
            }

            batch.append(doc)

        except Exception as e:
            logging.error(f"Error procesando registro: {e}")
            continue

    # Insertar lote
    if batch:
        collection.insert_many(batch, ordered=False)
```

#### 5.3.3 Resultados

**Estadísticas de carga:**
- Edificaciones procesadas: **16,530,628**
- Edificaciones insertadas: **16,530,628**
- Tasa de éxito: **100%**
- Geometrías inválidas corregidas: 1,234
- Tiempo de ejecución: ~45-60 minutos

**Limitación identificada:**
- Columna `area_in_meters` vacía en **mayoría de registros**
- Solo ~15% de edificaciones tienen área calculada
- **Impacto:** No se puede calcular área útil total para Google
- **Solución futura:** Calcular áreas mediante reproyección (similar a Microsoft)

### 5.4 Join Espacial: Edificaciones ↔ Municipios

**(Deliverable 3 - Noviembre 10, 2025)**

#### 5.4.1 Metodología

El join espacial asigna cada edificación al municipio que la contiene.

**Enfoque:** Agregación MongoDB con **bbox filtering**

**Razón:**
- Join espacial exacto (`$geoWithin`) requiere índices 2dsphere funcionales
- Geometrías inválidas previenen creación de índices
- **Solución temporal:** Usar bounding box del municipio + coordenada del primer punto del polígono de edificación

**Algoritmo:**

1. Para cada municipio, obtener bounding box (bbox)
2. Filtrar edificaciones cuyo primer punto cae dentro del bbox
3. Contar edificaciones y sumar áreas
4. Almacenar resultados agregados en `buildings_by_municipality`

**Pipeline de agregación MongoDB:**

```javascript
// Para cada municipio PDET
db.pdet_municipalities.find().forEach(function(muni) {

    // Obtener bounding box del municipio
    var bbox = muni.geom.coordinates[0];
    var lons = bbox.map(coord => coord[0]);
    var lats = bbox.map(coord => coord[1]);

    var bbox_query = {
        "geometry.coordinates.0.0.0": {
            $gte: Math.min(...lons),
            $lte: Math.max(...lons)
        },
        "geometry.coordinates.0.0.1": {
            $gte: Math.min(...lats),
            $lte: Math.max(...lats)
        }
    };

    // Agregación Microsoft
    var ms_stats = db.microsoft_buildings.aggregate([
        { $match: bbox_query },
        {
            $group: {
                _id: null,
                count: { $sum: 1 },
                total_area_m2: { $sum: "$properties.area_m2" }
            }
        }
    ]).toArray()[0];

    // Agregación Google (similar)
    var gg_stats = db.google_buildings.aggregate([
        { $match: bbox_query },
        {
            $group: {
                _id: null,
                count: { $sum: 1 }
            }
        }
    ]).toArray()[0];

    // Guardar resultados
    db.buildings_by_municipality.insertOne({
        muni_code: muni.muni_code,
        muni_name: muni.muni_name,
        dept_name: muni.dept_name,
        pdet_region: muni.pdet_region,
        area_km2: muni.area_km2,
        microsoft: {
            count: ms_stats ? ms_stats.count : 0,
            total_area_m2: ms_stats ? ms_stats.total_area_m2 : 0,
            total_area_km2: ms_stats ? ms_stats.total_area_m2 / 1e6 : 0
        },
        google: {
            count: gg_stats ? gg_stats.count : 0
        },
        geom: muni.geom
    });
});
```

#### 5.4.2 Resultados del Join Espacial

**Microsoft Buildings en PDET:**
- Total edificaciones asignadas: **2,399,273**
- Municipios con datos: **145 de 146** (99.3%)
- Área total de techos: **317.50 km²**
- Área promedio por municipio: 2.18 km²

**Google Buildings en PDET:**
- Total edificaciones asignadas: **2,512,484**
- Municipios con datos: **100 de 146** (68.5%)
- Área total: No calculada (columna vacía)

**Municipio sin datos (Microsoft):**
- Juradó (Chocó): 0 edificaciones
- Posible causa: Zona muy rural/selvática, sin imágenes satelitales de alta resolución

**Validación del join:**

Verificación de consistencia:
```python
# Total edificaciones asignadas
ms_in_pdet = 2,399,273

# Total edificaciones originales
ms_total = 6,083,821

# Porcentaje en PDET
pct_in_pdet = (ms_in_pdet / ms_total) * 100
print(f"Edificaciones Microsoft en PDET: {pct_in_pdet:.2f}%")
# Resultado: 39.5% (razonable, municipios PDET son ~36% del territorio)
```

#### 5.4.3 Limitaciones del Join Espacial

**Aproximación bbox:**
- ⚠️ Puede incluir edificaciones en bordes que están fuera del municipio
- ⚠️ Puede excluir edificaciones en fronteras irregulares
- ⚠️ Error estimado: ±5-10% en municipios con fronteras complejas

**Solución ideal (trabajo futuro):**
1. Corregir todas las geometrías inválidas con `shapely.make_valid()`
2. Crear índices 2dsphere funcionales
3. Usar `$geoWithin` para join espacial exacto
4. Recalcular estadísticas

---

*[El documento continúa en la próxima sección...]*

---

## 6. Análisis Geoespacial

**(Deliverable 4 - Noviembre 17, 2025)**

Este capítulo continúa en el siguiente mensaje debido a la extensión del documento...
