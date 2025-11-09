# 📤 Instrucciones: Compartir Backup con el Equipo

## ✅ Backup Creado Exitosamente

Se ha generado un backup completo de la base de datos MongoDB con los 146 municipios PDET cargados.

---

## 📦 Archivos Generados

### 1. **Archivo Comprimido** (Recomendado para compartir)
```
📁 pdet_mongo_backup.zip
   Tamaño: 22 MB (comprimido desde 117 MB)
   Ubicación: raíz del proyecto
```

### 2. **Carpeta de Backup** (alternativa)
```
📁 backup_mongo/
   ├── README.md                           (instrucciones para el equipo)
   ├── pdet_municipalities_export.json     (146 municipios - 117 MB)
   ├── indexes_info.json                   (metadatos de índices)
   ├── import_pdet_data.py                 (script de importación)
   └── export_pdet_data.py                 (script de exportación - referencia)
```

---

## 🚀 CÓMO COMPARTIR CON TU EQUIPO

### Opción A: Google Drive / OneDrive (Recomendada)

1. **Subir el ZIP**:
   ```
   Archivo: pdet_mongo_backup.zip (22 MB)
   Compartir: Cualquiera con el enlace
   ```

2. **Enviar al equipo**:
   - Link de descarga de Drive/OneDrive
   - Mensaje: "Descarga y descomprime en la raíz del proyecto"

### Opción B: GitHub Release (para equipos técnicos)

```bash
# Crear un release en GitHub
gh release create v1.0-deliverable2 \
  pdet_mongo_backup.zip \
  --title "Deliverable 2: PDET MongoDB Backup" \
  --notes "146 municipios PDET con índices espaciales"
```

### Opción C: Compartir carpeta directamente

Simplemente comparte la carpeta `backup_mongo/` completa (no el ZIP).

---

## 📝 MENSAJE PARA TU EQUIPO

Puedes copiar y pegar este mensaje:

---

**Asunto**: Backup MongoDB - Entrega 2 PDET (146 municipios)

Hola equipo,

He completado la carga de datos de la Entrega 2 (municipios PDET) en MongoDB. Para que puedan trabajar con los mismos datos:

**1. Descargar el backup:**
[INSERTA AQUÍ EL LINK A DRIVE/ONEDRIVE]

Archivo: `pdet_mongo_backup.zip` (22 MB)

**2. Actualizar el código:**
```bash
git pull origin develop
```

**3. Instalar dependencias** (si no las tienen):
```bash
pip install -r requirements.txt
```

**4. Asegurarse que MongoDB esté corriendo:**
- Windows: Servicios → MongoDB Server → Iniciar
- Linux/Mac: `sudo systemctl start mongod`

**5. Importar los datos:**
```bash
# Descomprimir el ZIP en la raíz del proyecto
# Ejecutar:
cd backup_mongo
python import_pdet_data.py
```

El script importará automáticamente:
- 146 municipios PDET
- 6 índices (incluyendo índice espacial 2dsphere)
- Base de datos: `pdet_solar_analysis`
- Colección: `pdet_municipalities`

**6. Verificar que todo funcione:**
```bash
cd ..
python verificar_entrega2.py
```

**Datos incluidos:**
- 146 de 170 municipios PDET (85.88% cobertura)
- 358,181 km² de área total
- 14 regiones PDET
- Índice espacial para consultas geoespaciales

**Nota**: 24 municipios no están porque no se encontraron en el shapefile DANE MGN 2024. Ver documentación en `deliverables/deliverable_2/README.md` para más detalles.

Si tienen algún problema, revisen el `backup_mongo/README.md` que tiene instrucciones detalladas.

Saludos!

---

## 🔍 Verificación Rápida

Después de compartir, puedes pedirle a un compañero que verifique:

```bash
# 1. Importar los datos
cd backup_mongo
python import_pdet_data.py

# 2. Verificar
cd ..
python verificar_entrega2.py
```

**Debe mostrar:**
```
[OK] Documentos en MongoDB: 146/146  ✅ (no 146/170, porque ese es el target ideal)
[OK] Índice presente: geom_2dsphere
[OK] Conexión a MongoDB exitosa
```

---

## 📊 Estadísticas del Backup

```
Datos originales:  117 MB (JSON)
Comprimido:         22 MB (ZIP)
Compresión:         81% reducción
Documentos:        146 municipios PDET
Índices:             6 (incluyendo espacial)
Tiempo import:      ~30 segundos
```

---

## ⚠️ Importante

### NO subas estos archivos a Git:

El archivo `.gitignore` ya está configurado para ignorar:
- ✅ `backup_mongo/pdet_municipalities_export.json` (ignorado por tamaño)
- ✅ `pdet_mongo_backup.zip` (ignorado si está en raíz)

Pero **SÍ puedes compartirlos** por Drive/OneDrive/etc.

### Archivos que SÍ están en Git:

- ✅ `backup_mongo/README.md` - Instrucciones
- ✅ `backup_mongo/import_pdet_data.py` - Script de importación
- ✅ `backup_mongo/export_pdet_data.py` - Script de exportación (referencia)
- ✅ `backup_mongo/indexes_info.json` - Metadatos (pequeño)

---

## 🎯 Resumen

1. ✅ Backup generado: `pdet_mongo_backup.zip` (22 MB)
2. ✅ Comparte el ZIP por Drive/OneDrive
3. ✅ Equipo ejecuta: `python import_pdet_data.py`
4. ✅ Todos tienen los mismos datos en MongoDB
5. ✅ Listos para continuar con Entrega 3

---

**Generado**: 9 de Noviembre de 2025
**Por**: Sistema automático de backup MongoDB
