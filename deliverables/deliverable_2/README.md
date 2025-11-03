# Entregable 2: Integración del Conjunto de Datos de Límites Municipales PDET

**Fecha de entrega:** 3 de noviembre, 2:00 PM

---

## Resumen

Este entregable cubre la integración de los 170 municipios PDET (Programas de Desarrollo con Enfoque Territorial) en la base de datos MongoDB, incluyendo:

- Adquisición y verificación de datos desde DANE
- Procesamiento y filtrado de municipios PDET
- Validación y corrección de geometrías
- Carga a MongoDB con índices espaciales
- Documentación completa del proceso

---

## Archivos Preparados

### 1. **Lista de Municipios PDET**
📁 `data/processed/pdet_municipalities_list.csv`
- Lista oficial de 170 municipios PDET
- Incluye: código DIVIPOLA, departamento, municipio, región PDET, subregión PDET

### 2. **Script de Carga Paso a Paso**
📁 `src/data_loaders/load_pdet_simple.py`
- Script modular con 4 pasos bien definidos
- Paso 1: Verificar conexión MongoDB
- Paso 2: Procesar shapefile y filtrar PDET
- Paso 3: Cargar datos a MongoDB
- Paso 4: Validar carga

### 3. **Guía Completa**
📁 `GUIA_PASO_A_PASO.md` (este directorio)
- Instrucciones detalladas para cada paso
- Solución de problemas comunes
- Ejemplos de resultados esperados

### 4. **Configuración Actualizada**
- `config/database.yml` → Configurado para MongoDB
- `.env.example` → Variables de entorno actualizadas
- `src/database/connection.py` → Módulo de conexión MongoDB completo

---

## Cómo Usar

### Quick Start

```bash
# 1. Verifica que MongoDB esté corriendo
python src/database/connection.py

# 2. Descarga datos de DANE manualmente (ver guía)
# Guarda en: data/raw/dane/

# 3. Procesa y filtra municipios PDET
python src/data_loaders/load_pdet_simple.py --step 2 --shapefile data/raw/dane/MGN_MPIO_POLITICO.shp

# 4. Carga a MongoDB
python src/data_loaders/load_pdet_simple.py --step 3

# 5. Valida los datos
python src/data_loaders/load_pdet_simple.py --step 4
```

### Guía Detallada

Para instrucciones paso a paso completas, ver: **[GUIA_PASO_A_PASO.md](./GUIA_PASO_A_PASO.md)**

---

## Descarga y preparación del dataset

1. **Descarga el shapefile oficial de municipios DANE:**
   - Ve a: https://geoportal.dane.gov.co
   - Busca y descarga el archivo “Marco Geoestadístico Nacional (MGN)” (usualmente llamado `MGN_MPIO_POLITICO.zip`).
   - Extrae el contenido en: `data/raw/dane/MGN/`
   - Asegúrate de incluir todos los archivos del shapefile: `.shp`, `.dbf`, `.shx`, `.prj`, etc.

2. **Descarga la lista oficial de municipios PDET:**
   - Ve a: https://centralpdet.renovacionterritorio.gov.co
   - Descarga la lista y guárdala como `data/processed/pdet_municipalities_list.csv` (ya incluida en el repo).

---

## Carga y procesamiento de datos

1. **Verifica la conexión a MongoDB:**
   ```bash
   python src/data_loaders/load_pdet_simple.py --step 1
   ```

2. **Procesa el shapefile y filtra municipios PDET:**
   ```bash
   python src/data_loaders/load_pdet_simple.py --step 2 --shapefile data/raw/dane/MGN/MGN_ADM_MPIO_GRAFICO.shp
   ```
   Esto generará el archivo `data/processed/pdet_municipalities_ready.json`.

3. **Carga los datos procesados a MongoDB:**
   ```bash
   python src/data_loaders/load_pdet_simple.py --step 3
   ```

4. **Valida la carga y revisa estadísticas:**
   ```bash
   python src/data_loaders/load_pdet_simple.py --step 4
   ```

---

## Visualización de los datos

- Abre y ejecuta el notebook:
  ```
  notebooks/visualizacion_pdet.ipynb
  ```
  Aquí verás histogramas, boxplots y gráficos de barras de los municipios PDET.

---

## Estructura de Datos en MongoDB

### Colección: `pdet_municipalities`

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
    "coordinates": [[[...], [...]]]
  },
  "area_km2": 1234.56,
  "data_source": "DANE MGN",
  "created_at": ISODate("2025-11-01T..."),
  "updated_at": ISODate("2025-11-01T...")
}
```

### Índices Creados

- **`geom_2dsphere`**: Índice espacial para consultas geoespaciales
- **`muni_code`**: Índice único en código DIVIPOLA
- **`dept_code`**: Índice en código de departamento
- **`pdet_region`**: Índice en región PDET
- **`pdet_subregion`**: Índice en subregión PDET

---

## Distribución de Municipios PDET

Los 170 municipios se distribuyen en 5 regiones y 16 subregiones:

### Por Región

| Región | Municipios |
|--------|------------|
| Región Pacífico y Frontera | ~90 |
| Región Centro | ~30 |
| Región Orinoquía | ~25 |
| Región Norte | ~15 |
| Región Caribe y Magdalena Medio | ~10 |

### Por Departamento (principales)

- Nariño: 48 municipios
- Chocó: 27 municipios
- Cauca: 27 municipios
- Antioquia: 24 municipios
- Caquetá: 16 municipios
- Meta: 11 municipios
- Putumayo: 10 municipios
- (y otros)

---

## Requisitos Completados ✅

### ✅ Adquisición y Verificación de Datos
- Identificación de fuente de datos (DANE MGN)
- Lista oficial de 170 municipios PDET
- Instrucciones de descarga

### ✅ Integridad y Formato de Datos
- Validación de geometrías
- Corrección de geometrías inválidas
- Conversión a WGS84 (EPSG:4326)
- Cálculo de áreas en km²

### ✅ Integración Espacial en NoSQL
- Carga en MongoDB
- Formato GeoJSON
- Índices espaciales 2dsphere
- Índices adicionales para consultas

### ✅ Documentación del Proceso
- Guía paso a paso completa
- Scripts documentados
- Ejemplos de uso
- Solución de problemas

---

## Próximos Pasos

Una vez completada la carga de datos:

1. **Crear notebook de análisis** (`notebooks/02_pdet_municipalities.ipynb`)
   - Visualización de municipios en mapa interactivo
   - Análisis estadístico por región
   - Gráficos de distribución

2. **Generar reporte de calidad de datos**
   - Validación completa de geometrías
   - Verificación de atributos
   - Estadísticas detalladas

3. **Documentar resultados**
   - Reporte técnico del Entregable 2
   - Mapas y visualizaciones
   - Conclusiones

---

## Fuentes de Datos

- **DANE - Marco Geoestadístico Nacional (MGN)**
  - URL: https://geoportal.dane.gov.co
  - Archivo: MGN_MPIO_POLITICO
  - Licencia: Datos abiertos

- **PDET - Renovación Territorial**
  - URL: https://centralpdet.renovacionterritorio.gov.co
  - Lista oficial de municipios PDET

---

## Soporte y Contacto

Para preguntas o problemas:
- Revisar `GUIA_PASO_A_PASO.md`
- Verificar sección "Solución de Problemas"
- Consultar documentación de MongoDB: https://docs.mongodb.com

---

## Control de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2025-11-01 | Versión inicial - Scripts y guía completa |

---

**Autores:** Alejandro Pinzon Fajardo, Juan Jose Bermudez
**Proyecto:** Análisis de Potencial Solar en Techos PDET
**Curso:** Administración de Bases de Datos - Proyecto Final
