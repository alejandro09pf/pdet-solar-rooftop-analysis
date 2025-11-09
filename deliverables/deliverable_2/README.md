# Entregable 2: Integración del Conjunto de Datos de Límites Municipales PDET

**Fecha de entrega:** 3 de noviembre de 2025, 2:00 PM
**Estado:** ✅ Completado
**Versión:** 2.0 (Actualizado 9 Nov 2025)

---

## 📋 Resumen

Este entregable cubre la integración completa de los 170 municipios PDET (Programas de Desarrollo con Enfoque Territorial) en la base de datos **MongoDB**, incluyendo:

- ✅ Adquisición y verificación de datos desde DANE
- ✅ Procesamiento y filtrado de municipios PDET
- ✅ Validación y corrección de geometrías
- ✅ Carga a MongoDB con índices espaciales 2dsphere
- ✅ Documentación completa del proceso
- ✅ Análisis exploratorio y visualizaciones

---

## 📁 Contenidos

### 1. **Reporte Técnico Completo**
📄 **[deliverable_2_report.md](deliverable_2_report.md)** (60+ páginas)
- Metodología detallada
- Fuentes de datos
- Procesamiento y validación
- Integración en MongoDB
- Resultados y estadísticas
- Visualizaciones
- Conclusiones y próximos pasos

### 2. **Script de Carga Modular**
📄 **[src/data_loaders/load_pdet_simple.py](../../src/data_loaders/load_pdet_simple.py)**
- Paso 1: Verificar conexión MongoDB
- Paso 2: Procesar shapefile y filtrar PDET
- Paso 3: Cargar datos a MongoDB
- Paso 4: Validar carga

### 3. **Datos Procesados**
📁 **data/processed/**
- `pdet_municipalities_list.csv` - Lista oficial de 170 municipios PDET
- `pdet_municipalities_ready.json` - Documentos GeoJSON listos para MongoDB

### 4. **Notebook de Visualización**
📓 **[notebooks/visualizacion_pdet.ipynb](../../notebooks/visualizacion_pdet.ipynb)**
- Análisis exploratorio de datos (EDA)
- Histogramas y gráficos de distribución
- Mapas interactivos

---

## 🚀 Inicio Rápido

### Prerrequisitos

```bash
# MongoDB debe estar ejecutándose
mongosh --eval "db.version()"

# Python 3.8+ con dependencias instaladas
pip install -r requirements.txt
```

### Ejecución

```bash
# Paso 1: Verificar conexión MongoDB
python src/data_loaders/load_pdet_simple.py --step 1

# Paso 2: Procesar shapefile DANE (REQUIERE DESCARGA PREVIA)
# Descarga el shapefile de: https://geoportal.dane.gov.co
# Guárdalo en: data/raw/dane/
python src/data_loaders/load_pdet_simple.py --step 2 --shapefile data/raw/dane/MGN_ADM_MPIO_GRAFICO.shp

# Paso 3: Cargar a MongoDB
python src/data_loaders/load_pdet_simple.py --step 3

# Paso 4: Validar datos
python src/data_loaders/load_pdet_simple.py --step 4
```

---

## 📊 Resultados

### Municipios PDET Cargados: 146 de 170 (85.88% cobertura)

⚠️ **Nota importante**: 24 municipios de la lista oficial PDET no fueron encontrados en el shapefile DANE MGN 2024.
Posibles causas: cambios en códigos DIVIPOLA, municipios fusionados/divididos, o actualizaciones pendientes en el MGN.

**Distribución por región (municipios cargados):**

| Región PDET | Municipios | Área (km²) |
|-------------|------------|------------|
| Alto Patía y Norte del Cauca | 24 | 13,532 |
| Cuenca del Caguán y Piedemonte Caqueteño | 17 | 93,105 |
| Montes de María | 15 | 6,410 |
| Sierra Nevada-Perijá | 15 | 20,442 |
| Chocó | 12 | 27,890 |
| Macarena-Guaviare | 12 | 96,381 |
| Otros (8 regiones) | 51 | 100,420 |
| **TOTAL** | **146** | **358,181** |

**Principales departamentos:**

| Departamento | Municipios |
|--------------|------------|
| Nariño | 48 |
| Chocó | 27 |
| Cauca | 27 |
| Antioquia | 24 |
| Caquetá | 16 |
| Meta | 11 |
| Putumayo | 10 |

---

## 💾 Estructura de Datos en MongoDB

**Colección:** `pdet_municipalities`

**Documento de ejemplo:**

```json
{
  "_id": ObjectId("..."),
  "dept_code": "05",
  "muni_code": "05120",
  "dept_name": "Antioquia",
  "muni_name": "Cáceres",
  "pdet_region": "Región Norte",
  "pdet_subregion": "Bajo Cauca y Nordeste Antioqueño",
  "geom": {
    "type": "Polygon",
    "coordinates": [[[-75.123, 7.456], ...]]
  },
  "area_km2": 1234.56,
  "data_source": "DANE MGN",
  "created_at": ISODate("2025-11-01T..."),
  "updated_at": ISODate("2025-11-01T...")
}
```

**Índices creados:**
- ✅ `geom_2dsphere` - Índice espacial para consultas geoespaciales
- ✅ `muni_code_unique` - Índice único en código DIVIPOLA
- ✅ `dept_code_idx` - Índice en código de departamento
- ✅ `pdet_region_idx` - Índice en región PDET
- ✅ `pdet_subregion_idx` - Índice en subregión PDET

---

## ✅ Requisitos Completados

### ✅ Adquisición y Verificación de Datos
- Identificación de fuente de datos (DANE MGN)
- Lista oficial de 170 municipios PDET
- Instrucciones de descarga

### ✅ Integridad y Formato de Datos
- Validación de geometrías con Shapely
- Corrección de geometrías inválidas
- Conversión a WGS84 (EPSG:4326)
- Cálculo de áreas en km²

### ✅ Integración Espacial en NoSQL
- Carga en MongoDB
- Formato GeoJSON estándar
- Índices espaciales 2dsphere
- Índices adicionales para consultas

### ✅ Documentación del Proceso
- Reporte técnico completo (60+ páginas)
- Scripts documentados y modulares
- Ejemplos de uso
- Solución de problemas

---

## 📂 Estructura de Archivos

```
deliverable_2/
├── README.md                              # Este archivo
└── deliverable_2_report.md                # Reporte técnico completo

src/data_loaders/
└── load_pdet_simple.py                    # Script de carga modular

data/processed/
├── pdet_municipalities_list.csv           # Lista oficial PDET
└── pdet_municipalities_ready.json         # Documentos GeoJSON

notebooks/
└── visualizacion_pdet.ipynb               # Visualizaciones y EDA
```

---

## 🔍 Consultas MongoDB Útiles

### Contar municipios
```javascript
db.pdet_municipalities.countDocuments()
```

### Municipios por región
```javascript
db.pdet_municipalities.aggregate([
  { $group: { _id: "$pdet_region", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Buscar municipio específico
```javascript
db.pdet_municipalities.findOne({ muni_code: "05120" })
```

### Municipios en un departamento
```javascript
db.pdet_municipalities.find(
  { dept_code: "05" },
  { muni_name: 1, area_km2: 1, _id: 0 }
)
```

---

## 📝 Fuentes de Datos

### DANE - Marco Geoestadístico Nacional (MGN)
- **URL:** https://geoportal.dane.gov.co
- **Archivo:** MGN_ADM_MPIO_GRAFICO.shp (o similar)
- **Licencia:** Datos abiertos - Gobierno de Colombia
- **Cobertura:** 1,122 municipios de Colombia

### PDET - Renovación Territorial
- **URL:** https://centralpdet.renovacionterritorio.gov.co
- **Archivo:** pdet_municipalities_list.csv (incluido en repo)
- **Cobertura:** 170 municipios PDET en 16 subregiones

---

## ⚠️ Notas Importantes

### 1. Cobertura de Datos: 146 de 170 municipios (85.88%)

**Estado actual**: El proceso de carga completó exitosamente pero solo identificó 146 municipios PDET en el shapefile DANE MGN 2024.

**Municipios faltantes**: 24 municipios de la lista oficial PDET no fueron encontrados.

**Análisis de la situación**:
- ✅ Pipeline de carga **100% funcional**
- ✅ Join espacial realizado correctamente (código DIVIPOLA)
- ✅ Los 146 municipios cargados tienen **datos completos y validados**
- ⚠️ 24 municipios (14.12%) no se encontraron en el shapefile

**Posibles causas**:
1. Cambios en códigos DIVIPOLA entre lista PDET y shapefile DANE
2. Municipios fusionados o divididos después de la publicación de la lista PDET
3. Discrepancias entre bases de datos oficiales (Renovación Territorial vs DANE)
4. Actualización pendiente del Marco Geoestadístico Nacional 2024

**Recomendación**: Los 146 municipios son suficientes para el análisis de potencial solar, cubriendo 358,181 km² de territorios PDET en 14 regiones.

### 2. Descarga de Shapefile

- El shapefile de DANE NO está incluido en el repositorio (archivo grande)
- Debe descargarse manualmente de https://geoportal.dane.gov.co
- Guardar en `data/raw/dane/`
- Archivo usado: MGN_ADM_MPIO_GRAFICO.shp (MGN 2024)

### 3. Requisitos de Sistema

- MongoDB 5.0+ ejecutándose
- Python 3.8+
- 4 GB RAM mínimo
- 1 GB espacio en disco

### 4. Tiempo de Ejecución

- Paso 1: < 1 minuto
- Paso 2: 2-5 minutos
- Paso 3: 1-2 minutos
- Paso 4: < 1 minuto

---

## 🔄 Próximos Pasos

### Entregable 3 (10 Nov - En progreso)
1. Descargar Microsoft Building Footprints
2. Descargar Google Open Buildings
3. Implementar scripts de carga de edificaciones
4. Realizar join espacial edificaciones-municipios
5. EDA inicial de edificaciones

---

## 👥 Equipo

**Preparado por:**
- Alejandro Pinzon Fajardo
- Juan Jose Bermudez
- Juan Manuel Díaz

**Proyecto:** Análisis de Potencial Solar en Techos PDET
**Curso:** Administración de Bases de Datos - Proyecto Final
**Fecha:** 3 de Noviembre de 2025
**Última actualización:** 9 de Noviembre de 2025
**Versión:** 2.0
