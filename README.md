# Análisis de Potencial Solar en Techos PDET

## Administración de Bases de Datos - Proyecto Final

**Análisis del Potencial de Energía Solar en Techos de Edificaciones en Territorios PDET, Colombia**

## Introducción

Este proyecto apoya el objetivo de la UPME (Unidad de Planeación Minero Energética) de evaluar la viabilidad de la energía solar en territorios seleccionados de Colombia. El proyecto diseña e implementa un flujo de trabajo de análisis geoespacial reproducible para estimar el potencial de energía solar de los techos de edificaciones en municipios priorizados, particularmente en territorios PDET (Programas de Desarrollo con Enfoque Territorial).

Los territorios PDET representan áreas clave de enfoque para el desarrollo posconflicto y la mejora de infraestructura en Colombia. Al aprovechar conjuntos de datos geoespaciales de acceso abierto que contienen miles de millones de contornos de edificaciones derivados de imágenes satelitales de alta resolución, este proyecto tiene como objetivo cuantificar las superficies potenciales para la captación de energía en contextos urbanos y rurales.

## Objetivos

Los objetivos principales de este proyecto son:

1. **Contar edificaciones** dentro de cada municipio PDET
2. **Estimar el área total de techos** adecuada para instalación de paneles solares
3. **Comparar resultados** de diferentes conjuntos de datos de edificaciones abiertas
4. **Implementar soluciones NoSQL** para almacenamiento escalable y operaciones espaciales eficientes
5. **Proporcionar recomendaciones estratégicas** para ubicaciones de granjas solares como prueba de concepto

## Conjuntos de Datos

### Huellas de Edificaciones

1. **Microsoft Building Footprints**
   - Más de 999 millones de detecciones de edificaciones a partir de imágenes de Bing Maps (2014-2021)
   - Fuentes: Maxar y Airbus
   - Licencia: Open Data Commons Open Database License (ODbL)
   - [Información del Conjunto de Datos](https://planetarycomputer.microsoft.com/dataset/ms-buildings)

2. **Google Open Buildings**
   - 1.8 mil millones de detecciones de edificaciones
   - Cobertura: 58 millones km² (África, Asia del Sur, Sudeste Asiático, América Latina, Caribe)
   - Versión: 3
   - Licencia: CC BY-4.0 y ODbL v1.0
   - [Información del Conjunto de Datos](https://sites.research.google/gr/open-buildings/)

### Límites Administrativos

- **DANE Marco Geoestadístico Nacional (MGN)**
  - Límites administrativos colombianos a nivel municipal
  - Enfoque en municipios designados PDET
  - [DANE Geoportal](https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/?cod=111)

## Estructura del Proyecto

```
pdet-solar-rooftop-analysis/
├── data/
│   ├── raw/              # Conjuntos de datos originales (no rastreados en git)
│   └── processed/        # Datos limpios y procesados
├── src/                  # Código fuente y scripts
├── notebooks/            # Notebooks de Jupyter para análisis
├── docs/                 # Documentación del proyecto
├── deliverables/         # Entregables del proyecto por semana
├── results/              # Resultados de análisis y visualizaciones
├── config/               # Archivos de configuración
└── README.md
```

## Cronograma de Entregables

### Entregable 1 - 27 de Octubre, 2:00 PM ✅
**Diseño de Esquema de Base de Datos NoSQL y Plan de Implementación**
- ✅ Plan de Implementación
- ✅ Modelado de Datos MongoDB
- ✅ Diseño de Esquema y Apropiación
- ✅ Scripts MongoDB de inicialización

### Entregable 2 - 3 de Noviembre, 2:00 PM ✅
**Integración del Conjunto de Datos de Límites Municipales PDET**
- ✅ Adquisición y Verificación de Datos
- ✅ Integridad y Formato de Datos
- ✅ Integración Espacial NoSQL (MongoDB)
- ✅ Documentación del Proceso
- ✅ 146 municipios PDET cargados (85.88% de cobertura)
- ⚠️ Nota: 24 municipios no encontrados en shapefile DANE MGN 2024

### Entregable 3 - 10 de Noviembre, 2:00 PM ⏳
**Reporte de Carga e Integración de Datos de Huellas de Edificaciones**
- ⏳ Integración de Conjuntos de Datos de Microsoft y Google
- ⏳ Indexación Espacial
- ⏳ Eficiencia de Carga de Datos
- ⏳ Auditoría Inicial de Datos (EDA)

### Entregable 4 - 17 de Noviembre, 2:00 PM ✅
**Flujo de Trabajo de Análisis Geoespacial Reproducible**
- ✅ Conteo de Techos y Estimación de Área
- ✅ Reproducibilidad y Metodología
- ✅ Precisión de Operaciones Espaciales
- ✅ Estructura de Datos de Salida (tablas y mapas)
- **Resultado:** 151.13 km² de área útil en 145 municipios PDET

### Entregable 5 - 24 de Noviembre, 2:00 PM ✅
**Reporte Técnico Final y Recomendaciones**
- ✅ Documentación Completa
- ✅ Resultados y Visualizaciones
- ✅ Contenido y Completitud
- ✅ Claridad de las Recomendaciones
- ✅ Alineación con los Objetivos de UPME
- **Resultado:** Reporte técnico completo con 5 municipios prioritarios identificados

## Stack Tecnológico

- **Base de Datos NoSQL**: MongoDB 5.0+ (con soporte geoespacial 2dsphere)
- **Lenguaje de Programación**: Python 3.8+
- **Librerías Geoespaciales**: GeoPandas, Shapely, Fiona, PyProj
- **MongoDB**: PyMongo
- **Procesamiento de Datos**: Pandas, NumPy
- **Visualización**: Matplotlib, Seaborn, Folium, Plotly

## Resultados Principales

### Potencial Solar Identificado

**Área útil total para paneles solares: 151.13 km² (15,113 hectáreas)**
- Equivalente a ~21,158 campos de fútbol
- Distribuido en 145 municipios PDET
- Basado en 2,399,273 edificaciones (Microsoft Buildings)

### Top 5 Municipios Prioritarios

| # | Municipio | Departamento | Área Útil (km²) | Edificaciones |
|---|-----------|--------------|-----------------|---------------|
| 1 | **Santa Marta** | Magdalena | 6.73 | 75,961 |
| 2 | **Valledupar** | Cesar | 5.92 | 62,912 |
| 3 | **Florencia** | Caquetá | 3.95 | 40,233 |
| 4 | **San Vicente del Caguán** | Caquetá | 3.88 | 55,995 |
| 5 | **Montelíbano** | Córdoba | 2.82 | 43,248 |

### Top 3 Regiones PDET

| Región | Municipios | Área Útil (km²) | % del Total |
|--------|------------|-----------------|-------------|
| **Sierra Nevada-Perijá** | 15 | 30.28 | 20.0% |
| **Alto Patía y Norte del Cauca** | 24 | 25.69 | 17.0% |
| **Cuenca del Caguán y Piedemonte** | 17 | 20.71 | 13.7% |

**Las top 3 regiones concentran el 50.7% del potencial solar total de territorios PDET.**

### Comparación de Datasets

| Métrica | Microsoft Buildings | Google Open Buildings |
|---------|---------------------|----------------------|
| Edificaciones en PDET | 2,399,273 | 2,512,484 |
| Cobertura municipal | 99.3% (145/146) | 68.5% (100/146) |
| Área total calculada | 317.50 km² | No disponible |
| **Área útil** | **151.13 km²** | No disponible |

**Recomendación:** Microsoft Buildings es la fuente preferida para estimaciones de área útil debido a su mejor cobertura y disponibilidad de áreas calculadas.

---

## Primeros Pasos

### Prerrequisitos

```bash
# Python 3.8+
# Git
# Base de Datos NoSQL (a determinar en Entregable 1)
```

### Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd pdet-solar-rooftop-analysis

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env si necesitas configuración específica

# Verificar MongoDB está ejecutándose
mongosh --eval "db.version()"

# Inicializar base de datos MongoDB
mongosh pdet_solar_analysis < deliverables/deliverable_1/mongodb_scripts/01_initialize_database.js

# Probar conexión Python - MongoDB
python src/database/connection.py
```

## Licencia

Este proyecto se desarrolla como parte de una tarea académica para el curso de Administración de Bases de Datos.

## Colaboradores

- Alejandro Pinzon Fajardo, Juan Manuel Díaz, Victor Peñaranda Florez, Juan Jose Bermudez Palacios

## Contacto

Para preguntas sobre este proyecto, por favor contacte al equipo del proyecto o consulte al instructor del curso.

---

**Nota**: Este proyecto integra herramientas modernas de ciencia de datos con necesidades reales de políticas energéticas, conectando la innovación técnica y la planeación estratégica en apoyo de la transición energética de Colombia y la equidad territorial.
