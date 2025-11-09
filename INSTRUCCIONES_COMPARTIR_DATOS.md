# Guía para Compartir Datos entre el Equipo

**Proyecto:** PDET Solar Analysis - Entregable 3
**Actualizado:** 9 de Noviembre 2025

---

## 📊 DATOS ACTUALES

### Microsoft Building Footprints
- **Total edificaciones:** 6,083,821
- **Tamaño archivo original:** 1.6 GB (Colombia.geojsonl)
- **Colección MongoDB:** `microsoft_buildings`
- **Base de datos:** `pdet_solar_analysis`

---

## 🔄 OPCIÓN 1: Compartir Backup de MongoDB (RECOMENDADO)

### Para PERSONA 1 (crear backup):

```bash
# Crear backup de la colección microsoft_buildings
mongodump --db=pdet_solar_analysis --collection=microsoft_buildings --out=backup_deliverable_3

# Comprimir el backup
tar -czf microsoft_buildings_backup.tar.gz backup_deliverable_3/
```

**Resultado:**
- Archivo comprimido: `microsoft_buildings_backup.tar.gz` (~400-500 MB)
- Compartir vía Google Drive, OneDrive, o USB

### Para otros compañeros (restaurar backup):

```bash
# Descomprimir
tar -xzf microsoft_buildings_backup.tar.gz

# Restaurar en MongoDB
mongorestore --db=pdet_solar_analysis backup_deliverable_3/pdet_solar_analysis/

# Verificar
py src/database/connection.py
```

---

## 🌐 OPCIÓN 2: Cada uno descarga los datos

### Ventajas:
- No requiere compartir archivos grandes
- Proceso reproducible
- Cada uno aprende el flujo completo

### Pasos:

1. **Descargar archivo original:**
   ```
   URL: https://minedbuildings.z5.web.core.windows.net/legacy/southamerica/Colombia.geojsonl.zip
   Tamaño: 482 MB (comprimido)
   ```

2. **Descomprimir:**
   ```bash
   # Extraer a data/raw/microsoft/
   unzip Colombia.geojsonl.zip -d data/raw/microsoft/
   ```

3. **Cargar a MongoDB:**
   ```bash
   # Ejecutar script de carga (~13 minutos)
   py src/data_loaders/load_microsoft_buildings.py --batch-size 10000 --collection microsoft_buildings --drop
   ```

4. **Verificar:**
   ```bash
   py src/database/connection.py
   ```

---

## ☁️ OPCIÓN 3: MongoDB Compartido (Avanzado)

Si tienen acceso a un servidor o MongoDB Atlas:

### 1. Subir datos a MongoDB Atlas (gratis hasta 512 MB)
```bash
# Exportar
mongodump --db=pdet_solar_analysis --collection=microsoft_buildings

# Importar a Atlas
mongorestore --uri="mongodb+srv://usuario:password@cluster.mongodb.net/pdet_solar_analysis" backup_deliverable_3/
```

### 2. Compartir string de conexión con el equipo

**Nota:** MongoDB Atlas tiene límite de 512 MB en plan gratuito, por lo que esta colección (6M+ docs) probablemente exceda el límite.

---

## 📝 OPCIÓN 4: Trabajar con Muestra (Para desarrollo/testing)

Si solo necesitan probar scripts sin todos los datos:

```bash
# Crear colección de prueba con 10,000 edificaciones
py -c "
from src.database.connection import get_database
db = get_database()
sample = list(db.microsoft_buildings.aggregate([{'$sample': {'size': 10000}}]))
db.microsoft_buildings_sample.insert_many(sample)
print(f'Muestra creada: {len(sample)} docs')
"

# Compartir solo la muestra (mucho más pequeña)
mongodump --db=pdet_solar_analysis --collection=microsoft_buildings_sample --out=backup_sample/
```

---

## 🎯 RECOMENDACIÓN PARA EL EQUIPO

### Para trabajar en el Entregable 3:

**PERSONA 1 (tú):**
- ✅ Ya tienes todos los datos cargados
- Crear backup y compartir con el equipo (Opción 1)

**PERSONA 2 (Google Buildings):**
- Descargar datos de Google directamente (Opción 2)
- Usar mismo proceso que PERSONA 1

**PERSONA 3 (EDA):**
- Necesita acceso a ambas colecciones (Microsoft + Google)
- Opción A: Restaurar backups de PERSONA 1 y 2
- Opción B: Trabajar con muestras para desarrollo, datos completos para análisis final

**PERSONA 4 (Reporte):**
- Necesita acceso a todas las colecciones
- Restaurar todos los backups

---

## 💾 CREAR BACKUP AHORA (Recomendado)

```bash
# 1. Crear directorio de backup
mkdir -p backup_deliverable_3

# 2. Exportar microsoft_buildings
mongodump --db=pdet_solar_analysis --collection=microsoft_buildings --out=backup_deliverable_3/

# 3. Comprimir
tar -czf microsoft_buildings_backup.tar.gz backup_deliverable_3/

# Resultado:
# Archivo: microsoft_buildings_backup.tar.gz (~400-500 MB)
```

### Compartir archivo:
- **Google Drive:** Subir y compartir link
- **OneDrive:** Subir y compartir link
- **USB:** Copiar directamente
- **Universidad:** Servidor compartido del curso

---

## 🔍 VERIFICAR QUE TODO FUNCIONA

Después de restaurar, cada compañero debe ejecutar:

```bash
# Ver estado de MongoDB
py src/database/connection.py

# Resultado esperado:
# [OK] microsoft_buildings: 6,083,821 documents
```

---

## 📋 RESUMEN RÁPIDO

| Opción | Tiempo | Tamaño | Recomendado para |
|--------|--------|--------|------------------|
| **1. Backup MongoDB** | 5 min | ~500 MB | Todos - más rápido |
| **2. Descarga directa** | 13 min | 482 MB | Aprender el proceso |
| **3. MongoDB compartido** | Varía | N/A | Equipos con servidor |
| **4. Muestra** | 1 min | ~5 MB | Testing rápido |

---

**Preparado por:** PERSONA 1
**Para:** Todo el equipo del Entregable 3
