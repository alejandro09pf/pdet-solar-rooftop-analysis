#!/usr/bin/env python3
"""
Script de verificación de completitud de Entrega 2
Verifica todos los requisitos antes de considerar la entrega completa
"""

import os
import sys
from pathlib import Path
import json

print("=" * 80)
print("VERIFICACIÓN DE ENTREGA 2 - INTEGRACIÓN MUNICIPIOS PDET")
print("=" * 80)

# Colores para terminal
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(condition, message):
    """Helper para verificar condiciones"""
    if condition:
        print(f"{GREEN}[OK]{RESET} {message}")
        return True
    else:
        print(f"{RED}[ERROR]{RESET} {message}")
        return False

def warning(message):
    """Helper para advertencias"""
    print(f"{YELLOW}[!]{RESET} {message}")

all_checks_passed = True

# ============================================================================
# 1. VERIFICAR ESTRUCTURA DE DIRECTORIOS
# ============================================================================
print("\n1. VERIFICANDO ESTRUCTURA DE DIRECTORIOS\n")

data_raw_dane = Path("data/raw/dane")
data_processed = Path("data/processed")

all_checks_passed &= check(data_raw_dane.exists(), f"Directorio existe: {data_raw_dane}")
all_checks_passed &= check(data_processed.exists(), f"Directorio existe: {data_processed}")

# ============================================================================
# 2. VERIFICAR SHAPEFILE DANE
# ============================================================================
print("\n2. VERIFICANDO SHAPEFILE DANE\n")

if data_raw_dane.exists():
    shapefiles = list(data_raw_dane.glob("*.shp"))

    if len(shapefiles) > 0:
        check(True, f"Shapefile encontrado: {shapefiles[0].name}")

        # Verificar archivos componentes del shapefile
        shp_base = shapefiles[0].stem
        required_extensions = ['.shp', '.shx', '.dbf', '.prj']

        for ext in required_extensions:
            file_path = data_raw_dane / (shp_base + ext)
            check(file_path.exists(), f"Archivo componente: {shp_base}{ext}")
    else:
        all_checks_passed = False
        check(False, "No se encontró archivo .shp en data/raw/dane/")
        warning("Descarga el shapefile de DANE siguiendo GUIA_DESCARGA_DANE.md")
else:
    all_checks_passed = False
    warning("El directorio data/raw/dane/ no existe")

# ============================================================================
# 3. VERIFICAR LISTA DE MUNICIPIOS PDET
# ============================================================================
print("\n3. VERIFICANDO LISTA DE MUNICIPIOS PDET\n")

pdet_list = data_processed / "pdet_municipalities_list.csv"

if check(pdet_list.exists(), f"Lista PDET existe: {pdet_list}"):
    try:
        import pandas as pd
        df = pd.read_csv(pdet_list)
        count = len(df)
        check(count == 170, f"Municipios en lista: {count}/170")
        if count != 170:
            all_checks_passed = False
            warning(f"Se esperaban 170 municipios, se encontraron {count}")
    except Exception as e:
        warning(f"Error leyendo CSV: {e}")
else:
    all_checks_passed = False

# ============================================================================
# 4. VERIFICAR DATOS PROCESADOS (JSON)
# ============================================================================
print("\n4. VERIFICANDO DATOS PROCESADOS (JSON)\n")

pdet_json = data_processed / "pdet_municipalities_ready.json"

if pdet_json.exists():
    try:
        with open(pdet_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = len(data)
        check(count == 170, f"Municipios en JSON: {count}/170")

        if count != 170:
            all_checks_passed = False
            warning(f"Se esperaban 170 municipios, se encontraron {count}")
            warning("Necesitas re-ejecutar el Paso 2 del script de carga")

        # Verificar estructura del primer documento
        if len(data) > 0:
            first = data[0]
            required_fields = ['muni_code', 'dept_code', 'muni_name', 'dept_name',
                             'pdet_region', 'pdet_subregion', 'geom', 'area_km2']

            for field in required_fields:
                if field in first:
                    check(True, f"Campo requerido presente: {field}")
                else:
                    all_checks_passed = False
                    check(False, f"Campo faltante: {field}")
    except Exception as e:
        all_checks_passed = False
        check(False, f"Error leyendo JSON: {e}")
else:
    all_checks_passed = False
    check(False, "Archivo pdet_municipalities_ready.json no existe")
    warning("Ejecuta: python src/data_loaders/load_pdet_simple.py --step 2 --shapefile <ruta>")

# ============================================================================
# 5. VERIFICAR MONGODB
# ============================================================================
print("\n5. VERIFICANDO CONEXIÓN A MONGODB\n")

try:
    from src.database.connection import test_connection, get_database, load_config

    if test_connection(verbose=False):
        check(True, "Conexión a MongoDB exitosa")

        try:
            config = load_config()
            db = get_database()
            collection = db['pdet_municipalities']

            count = collection.count_documents({})
            check(count == 170, f"Documentos en MongoDB: {count}/170")

            if count != 170:
                all_checks_passed = False
                if count == 0:
                    warning("MongoDB está vacío. Ejecuta el Paso 3 de carga")
                else:
                    warning(f"Se esperaban 170 documentos, se encontraron {count}")
                    warning("Re-ejecuta el Paso 2 y Paso 3")

            # Verificar índices
            indexes = list(collection.list_indexes())
            index_names = [idx['name'] for idx in indexes]

            required_indexes = ['_id_', 'geom_2dsphere', 'muni_code_unique']
            for idx_name in required_indexes:
                if idx_name in index_names:
                    check(True, f"Índice presente: {idx_name}")
                else:
                    warning(f"Índice faltante: {idx_name}")

        except Exception as e:
            all_checks_passed = False
            check(False, f"Error accediendo a colección: {e}")
    else:
        all_checks_passed = False
        check(False, "No se pudo conectar a MongoDB")
        warning("Asegúrate de que MongoDB esté ejecutándose")
        warning("Windows: Verifica servicios | Linux/Mac: sudo systemctl start mongod")

except ImportError as e:
    all_checks_passed = False
    check(False, f"Error importando módulos: {e}")
    warning("Instala dependencias: pip install -r requirements.txt")

# ============================================================================
# 6. VERIFICAR DOCUMENTACIÓN
# ============================================================================
print("\n6. VERIFICANDO DOCUMENTACIÓN\n")

deliverable2_readme = Path("deliverables/deliverable_2/README.md")
deliverable2_report = Path("deliverables/deliverable_2/deliverable_2_report.md")

check(deliverable2_readme.exists(), "README de Entrega 2 existe")
check(deliverable2_report.exists(), "Reporte técnico de Entrega 2 existe")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE VERIFICACIÓN")
print("=" * 80)

if all_checks_passed:
    print(f"\n{GREEN}[OK] TODAS LAS VERIFICACIONES PASARON{RESET}")
    print(f"\n{GREEN}[EXITO] LA ENTREGA 2 ESTA COMPLETA AL 100%{RESET}")
    print("\nProximos pasos:")
    print("  1. Hacer commit de los cambios")
    print("  2. Comenzar con Entrega 3 (Building Footprints)")
else:
    print(f"\n{RED}[ERROR] ALGUNAS VERIFICACIONES FALLARON{RESET}")
    print(f"\n{YELLOW}[!] LA ENTREGA 2 NO ESTA COMPLETA{RESET}")
    print("\nPendientes:")
    print("  1. Revisar las verificaciones fallidas arriba")
    print("  2. Seguir la guía GUIA_DESCARGA_DANE.md si falta el shapefile")
    print("  3. Ejecutar los pasos de carga con load_pdet_simple.py")
    print("  4. Re-ejecutar este script hasta que todo pase")

print("\n" + "=" * 80)

sys.exit(0 if all_checks_passed else 1)
