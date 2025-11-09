# 📦 Backup MongoDB - Municipios PDET

**Entrega 2**: Integración de 146 municipios PDET en MongoDB
**Fecha**: 9 de Noviembre de 2025
**Peso total**: ~116 MB

---

## 📋 Contenido del Backup

```
backup_mongo/
├── README.md                           # Este archivo
├── pdet_municipalities_export.json     # 146 municipios PDET (116 MB)
├── indexes_info.json                   # Información de índices MongoDB
├── export_pdet_data.py                 # Script usado para exportar (referencia)
└── import_pdet_data.py                 # Script de importación (USAR ESTE)
```

---

## 🚀 INSTRUCCIONES DE IMPORTACIÓN

### Prerrequisitos

1. **MongoDB instalado y ejecutándose**
   ```bash
   # Verificar que MongoDB esté corriendo
   # Windows: Servicios → MongoDB Server
   # Linux/Mac: sudo systemctl status mongod
   ```

2. **Python 3.8+ con dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Tener el código actualizado**
   ```bash
   git pull origin develop
   ```

---

### Paso a Paso

#### 1. Descargar este backup

- Descarga la carpeta completa `backup_mongo/`
- O el archivo comprimido: `pdet_mongo_backup.zip`
- Colócalo en la raíz del proyecto: `pdet-solar-rooftop-analysis/backup_mongo/`

#### 2. Ejecutar el script de importación

```bash
# Desde la raíz del proyecto
cd backup_mongo
python import_pdet_data.py
```

**Salida esperada:**
```
============================================================
IMPORTANDO DATOS A MONGODB
============================================================

Archivo de datos: pdet_municipalities_export.json
Tamaño: 116.39 MB

Cargando documentos desde JSON...
[OK] Cargados 146 documentos

Insertando 146 documentos...
[OK] Insertados 146 documentos

Creando indices...
  - Indice espacial 2dsphere en 'geom'...
    [OK] Creado
  - Indice unico en 'muni_code'...
    [OK] Creado
  - Indice en 'dept_code'...
    [OK] Creado
  - Indice en 'pdet_region'...
    [OK] Creado
  - Indice en 'pdet_subregion'...
    [OK] Creado

[OK] Todos los indices creados correctamente

============================================================
IMPORTACION COMPLETADA
============================================================

Total de documentos en MongoDB: 146
Indices creados: 6

[OK] Base de datos lista para usar!
```

#### 3. Verificar la importación

```bash
# Regresar a la raíz del proyecto
cd ..

# Verificar que todo esté correcto
python verificar_entrega2.py
```

---

## 📊 Datos Incluidos

- **Colección**: `pdet_municipalities`
- **Base de datos**: `pdet_solar_analysis`
- **Documentos**: 146 municipios PDET
- **Área total**: 358,181 km²
- **Regiones PDET**: 14 regiones
- **Cobertura**: 85.88% (146 de 170 municipios)

### Índices que se crearán automáticamente:

1. `_id_` - Índice automático de MongoDB
2. `geom_2dsphere` - Índice espacial para consultas geoespaciales ⭐
3. `muni_code_1` - Índice único en código DIVIPOLA
4. `dept_code_1` - Índice en código de departamento
5. `pdet_region_1` - Índice en región PDET
6. `pdet_subregion_1` - Índice en subregión PDET

---

## ⚠️ Notas Importantes

### Si ya tienes datos en MongoDB

El script te preguntará si quieres eliminar los datos existentes:
```
[!] La coleccion ya contiene X documentos
Deseas eliminar los datos existentes y recargar? (s/n):
```

- Responde `s` para reemplazar los datos
- Responde `n` para cancelar

### Municipios faltantes

Este backup contiene **146 de 170 municipios PDET** (85.88% cobertura).

**24 municipios no están incluidos** porque no se encontraron en el shapefile DANE MGN 2024.
Ver `deliverables/deliverable_2/README.md` para más detalles sobre esta limitación.

---

## 🆘 Solución de Problemas

### Error: "Archivo no encontrado"
```bash
# Asegúrate de estar en la carpeta correcta
cd pdet-solar-rooftop-analysis/backup_mongo
python import_pdet_data.py
```

### Error: "Cannot connect to MongoDB"
```bash
# Windows: Inicia el servicio
services.msc → MongoDB Server → Iniciar

# Linux/Mac:
sudo systemctl start mongod
```

### Error: "ModuleNotFoundError"
```bash
# Instala las dependencias
pip install -r requirements.txt
```

---

## 📞 Contacto

Si tienes problemas con la importación, contacta al equipo o revisa:
- `deliverables/deliverable_2/README.md` - Documentación completa
- `src/data_loaders/load_pdet_simple.py` - Script original de carga

---

**Última actualización**: 9 de Noviembre de 2025
**Generado por**: Alejandro Pinzon Fajardo
