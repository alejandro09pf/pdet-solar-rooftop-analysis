# Entregable 1: Diseño de Esquema de Base de Datos NoSQL y Plan de Implementación

**Fecha de Entrega:** 27 de Octubre de 2025, 2:00 PM
**Estado:** ✅ Completado
**Versión:** 2.0 (Actualizado 9 Nov 2025)

---

## Contenidos

Este entregable contiene:

1. **[deliverable_1_report.md](deliverable_1_report.md)** - Reporte técnico completo
   - Resumen Ejecutivo
   - Selección de Tecnología de Base de Datos (MongoDB)
   - Modelado de Datos
   - Diseño de Esquema
   - Estrategia de Indexación Espacial
   - Plan de Implementación
   - Justificación y Conclusiones
   - Referencias

2. **Scripts MongoDB** (`mongodb_scripts/`)
   - `01_initialize_database.js` - Inicialización de colecciones, índices y validación
   - `02_useful_queries.js` - Colección de consultas de análisis útiles
   - `README.md` - Documentación de scripts

3. **Módulos Python** (en `src/database/`)
   - `connection.py` - Módulo de conexión a MongoDB
   - `__init__.py` - Inicialización de paquete

4. **Configuración** (en `config/`)
   - `database.yml` - Configuración de MongoDB
   - `.env.example` - Plantilla de variables de entorno

---

## Decisiones Clave

### Tecnología Seleccionada: MongoDB con Soporte Geoespacial

**¿Por qué MongoDB?**
- ✅ **Soporte geoespacial nativo:** Índices 2dsphere y operadores espaciales
- ✅ **Escalabilidad horizontal:** Sharding nativo para grandes volúmenes de datos
- ✅ **Esquema flexible:** Documentos JSON/BSON para metadatos heterogéneos
- ✅ **Integración Python:** Excelente soporte con PyMongo y GeoPandas
- ✅ **NoSQL puro:** Cumple con los requisitos del proyecto
- ✅ **Facilidad de desarrollo:** Configuración rápida y curva de aprendizaje corta

### Modelo de Datos

Diseñamos tres colecciones principales:

1. **pdet_municipalities** - Límites territoriales PDET (170 municipios)
2. **buildings_microsoft** - Huellas de edificaciones Microsoft (~millones)
3. **buildings_google** - Huellas de edificaciones Google (~millones)

Todas las geometrías se almacenan en formato **GeoJSON** con coordenadas **WGS84 (EPSG:4326)**.

### Indexación Espacial

- Índices **2dsphere** en todas las columnas de geometría
- **Optimizado** para consultas espaciales: `$geoWithin`, `$geoIntersects`, `$near`
- Índices compuestos para agregaciones por municipio
- **Rendimiento:** Búsquedas espaciales eficientes con geohashing

---

## Cronograma de Implementación

| Fase | Entregable | Cronograma | Estado |
|-------|------------|----------|---------|
| **Fase 1** | Configuración MongoDB y creación de esquema | Oct 23-24 | ✅ Completado |
| **Fase 2** | Carga de datos de municipios PDET | Oct 25-Nov 3 | ✅ Completado |
| **Fase 3** | Carga de datos de huellas de edificaciones | Nov 4-10 | ⏳ En progreso |
| **Fase 4** | Análisis espacial y agregación | Nov 11-17 | ⏳ Futuro |
| **Fase 5** | Reporte final y recomendaciones | Nov 18-24 | ⏳ Futuro |

---

## Cómo Usar Este Entregable

### 1. Revisar el Reporte

Lea **[deliverable_1_report.md](deliverable_1_report.md)** para documentación completa.

### 2. Configurar Base de Datos (Fase 1)

```bash
# Asegúrate de tener MongoDB instalado y ejecutándose
# Windows: Verifica que el servicio MongoDB esté activo
# Linux/Mac: sudo systemctl start mongod

# Verificar que MongoDB está ejecutándose
mongosh --eval "db.version()"

# Configurar entorno
cp ../../.env.example ../../.env
# Editar .env si necesitas autenticación (opcional para desarrollo local)

# Ejecutar script de inicialización
mongosh pdet_solar_analysis < mongodb_scripts/01_initialize_database.js

# Probar conexión desde Python
cd ../..
python src/database/connection.py
```

### 3. Verificar Configuración

```bash
# Ejecutar consultas de exploración (después de cargar datos)
mongosh pdet_solar_analysis < mongodb_scripts/02_useful_queries.js

# O desde mongosh interactivo:
mongosh
use pdet_solar_analysis
db.pdet_municipalities.countDocuments()
db.getCollectionNames()
```

---

## Requisitos Cumplidos

### ✅ Plan de Implementación
- Cronograma detallado de implementación en 5 fases
- Requisitos de recursos especificados
- Estrategias de mitigación de riesgos documentadas

### ✅ Modelado de Datos
- Modelo conceptual de datos con relaciones espaciales
- Modelo físico de datos con esquemas de colecciones
- Validación de esquema con JSON Schema

### ✅ Diseño de Esquema y Apropiación
- Selección de tecnología justificada (MongoDB)
- Esquema integral con indexación espacial 2dsphere
- Optimizado para conjuntos de datos de escala masiva
- Alineado con requisitos NoSQL del proyecto

---

## Estructura de Archivos

```
deliverable_1/
├── README.md                              # Este archivo
├── deliverable_1_report.md                # Reporte técnico principal
└── mongodb_scripts/
    ├── README.md                          # Documentación de scripts
    ├── 01_initialize_database.js          # Inicialización de BD
    └── 02_useful_queries.js               # Consultas de análisis
```

---

## Próximos Pasos

1. ✅ **Revisión y Aprobación** - Presentar al equipo/instructor
2. ✅ **Configuración de Base de Datos** - MongoDB configurado
3. ✅ **Adquisición de Datos** - Descargar conjuntos de datos de DANE
4. ⏳ **Entregable 3** - Carga de huellas de edificaciones (Entrega Nov 10)

---

## Notas del Equipo

- Todos los scripts MongoDB están listos para producción
- Los módulos Python están probados y documentados
- Los archivos de configuración siguen las mejores prácticas
- No se ha enviado información sensible al repositorio
- **Actualización v2.0:** Eliminados scripts SQL de PostgreSQL, reemplazados por scripts MongoDB

---

## Requisitos Técnicos

- **MongoDB:** 5.0 o superior
- **Python:** 3.8 o superior
- **Librerías:** pymongo, geopandas, shapely, fiona
- **Sistema Operativo:** Windows, Linux o macOS
- **Memoria RAM:** Mínimo 8 GB (recomendado 16 GB para carga de edificaciones)
- **Disco:** Mínimo 100 GB libre

---

**Preparado por:** Alejandro Pinzon, Juan Jose Bermudez, Juan Manuel Díaz
**Fecha de Envío:** 27 de Octubre de 2025
**Última Actualización:** 9 de Noviembre de 2025
**Versión:** 2.0
