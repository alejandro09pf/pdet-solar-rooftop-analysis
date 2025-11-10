# Reporte de Join Espacial Edificaciones-Municipios PDET

**Fecha:** 2025-11-10 13:19:08
**Método:** Optimizado (bbox + sampling)

---

## Resumen General

- **Municipios analizados:** 146
- **Edificaciones Microsoft:** 2,399,273
- **Edificaciones Google:** 0
- **Municipios con datos MS:** 145
- **Municipios con datos Google:** 0

## Top 10 Municipios - Microsoft Buildings

| # | Municipio | Departamento | Edificaciones | Área Total (km²) |
|---|-----------|--------------|---------------|------------------|
| 1 | Santa Marta | Magdalena | 75,961 | 14.43 |
| 2 | Valledupar | Cesar | 62,912 | 11.95 |
| 3 | San Vicente del Caguán | Caquetá | 55,995 | 8.06 |
| 4 | El Tambo | Cauca | 55,201 | 5.56 |
| 5 | Tierralta | Córdoba | 46,090 | 4.82 |
| 6 | San Juan del Cesar | La Guajira | 43,686 | 5.40 |
| 7 | San Andres de Tumaco | Nariño | 43,466 | 4.84 |
| 8 | Montelíbano | Córdoba | 43,248 | 5.89 |
| 9 | Florencia | Caquetá | 40,233 | 8.21 |
| 10 | La Paz | Cesar | 40,148 | 6.27 |

## Distribución por Región PDET

| Región PDET | Municipios | Edificaciones |
|-------------|------------|---------------|
| Alto Patía y Norte del Cauca | 24 | 441,309 |
| Sierra Nevada-Perijá | 15 | 425,062 |
| Cuenca del Caguán y Piedemonte Caqueteño | 17 | 269,971 |
| Catatumbo | 8 | 167,515 |
| Sur de Córdoba | 5 | 151,548 |
| Montes de María | 15 | 146,187 |
| Putumayo | 9 | 142,611 |
| Macarena-Guaviare | 12 | 137,651 |
| Pacífico y Frontera Nariñense | 11 | 115,421 |
| Sur de Bolívar | 6 | 93,027 |
| Arauca | 4 | 87,364 |
| Chocó | 12 | 79,341 |
| Pacífico Medio | 4 | 71,394 |
| Sur del Tolima | 4 | 70,872 |

## Notas Metodológicas

- **Método:** Bbox filtering + sampling para velocidad
- **Limitación:** Sin índices espaciales, se usa aproximación por bbox
- **Área:** Calculada por promedio de muestra × conteo total
- **Google Buildings:** No disponible en esta base de datos
