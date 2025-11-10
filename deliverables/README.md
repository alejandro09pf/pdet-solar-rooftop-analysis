# Seguimiento de Entregables

## Descripción General

Este directorio contiene todos los entregables del proyecto presentados de acuerdo con el cronograma del proyecto.

## Cronograma de Entregables

### Entregable 1: Diseño de Esquema de Base de Datos NoSQL y Plan de Implementación
**Entrega: 27 de octubre, 2:00 PM**

**Requisitos:**
- [x] Plan de Implementación
- [x] Modelado de Datos
- [x] Diseño del Esquema y Pertinencia

**Estado:** ✅ Completado

**Entregado:** [x] 27 de Octubre 2025

---

### Entregable 2: Integración del Conjunto de Datos de Límites Municipales PDET
**Entrega: 3 de noviembre, 2:00 PM**

**Requisitos:**
- [x] Adquisición y Verificación de Datos
- [x] Integridad y Formato de los Datos
- [x] Integración Espacial en NoSQL
- [x] Documentación del Proceso

**Estado:** ✅ Completado

**Entregado:** [x] 3 de Noviembre 2025

**Resultados:**
- 146 municipios PDET cargados (85.88% de cobertura)
- Índices espaciales 2dsphere implementados
- Documentación completa del proceso

---

### Entregable 3: Carga e Integración de Datos de Huellas de Edificaciones (Informe)
**Entrega: 10 de noviembre, 2:00 PM**

**Requisitos:**
- [x] Integración de Conjuntos de Datos de Microsoft y Google
- [~] Indexación Espacial
- [x] Eficiencia en la Carga de Datos
- [x] Auditoría Inicial de Datos (EDA)

**Estado:** ✅ Completado

**Entregado:** [x] 10 de Noviembre 2025

**Resultados:**
- **Microsoft Buildings:** 6,083,821 edificaciones cargadas
- **Google Buildings:** Trabajado en equipo paralelo (16,530,628 edificaciones documentadas)
- **Join Espacial:** Análisis completo edificaciones × municipios PDET
- **EDA:** Notebooks y documentación técnica completa
- **Limitación:** Índices espaciales no implementados por geometrías inválidas (documentado)

**Equipo:**
- PERSONA 1 (Alejandro): Microsoft Buildings integration ✅
- PERSONA 2 (Juan José): Google Buildings integration ✅ (equipo paralelo)
- PERSONA 3: EDA y visualizaciones ✅
- PERSONA 4: Join espacial y validación ✅

---

### Entregable 4: Flujo de Trabajo Reproducible para Análisis Geoespacial
**Entrega: Noviembre 17, 2:00 PM**

**Requisitos:**
- [ ] Conteo de Techos y Estimación de Áreas
- [ ] Reproducibilidad y Metodología
- [ ] Precisión de las Operaciones Espaciales
- [ ] Estructura de Salida de Datos (tablas y mapas)

**Estado:** No Iniciado

**Entregado:** [ ]

---

### Entregable 5: Informe Técnico Final y Recomendaciones
**Entrega: Noviembre 24, 2:00 PM**

**Requisitos:**
- [ ] Documentación de todo el proceso
- [ ] Resultados y Visualizaciones de Datos
- [ ] Contenido y Completitud
- [ ] Claridad de las Recomendaciones
- [ ] Alineación con los Objetivos de la UPME

**Estado:** No Iniciado

**Entregado:** [ ]

---

## Proceso de Entrega

1. Completar todos los requisitos del entregable
2. Crear el documento del entregable en este directorio (por ejemplo, `deliverable_1.md` o `deliverable_1.pdf`)
3. Actualizar la lista de verificación anterior
4. Realizar commit y push en GitHub
5. Marcar como entregado y anotar la fecha de entrega

## Estructura del Directorio

```
deliverables/
├── README.md              # Este archivo
├── deliverable_1/         # Archivos del Entregable 1 
├── deliverable_2/         # Archivos del Entregable 2 
├── deliverable_3/         # Archivos del Entregable 3 
├── deliverable_4/         # Archivos del Entregable 4 
└── deliverable_5/         # Archivos del Entregable 5  (Reporte Final)
```
