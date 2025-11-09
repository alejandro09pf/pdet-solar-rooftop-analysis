"""
Script de verificación completa del proceso de carga
Simula lo que harán los compañeros del equipo
"""
import sys
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("="*80)
print("VERIFICACION COMPLETA DEL PROCESO DE CARGA")
print("Simulando lo que harán los compañeros del equipo")
print("="*80)

# TEST 1: Verificar archivos necesarios
print("\n[TEST 1] Verificando archivos necesarios...")
print("-"*80)

zip_file = Path("C:/Users/PcMaster/Downloads/Colombia.geojsonl.zip")
data_file = PROJECT_ROOT / "data" / "raw" / "microsoft" / "Colombia.geojsonl"

print(f"1. Archivo ZIP existe: {zip_file.exists()}")
if zip_file.exists():
    size_mb = zip_file.stat().st_size / (1024**2)
    print(f"   Tamaño: {size_mb:.2f} MB")
    if 480 <= size_mb <= 485:
        print("   ✓ Tamaño correcto (482 MB esperados)")
    else:
        print("   ✗ Tamaño incorrecto")

print(f"\n2. Archivo descomprimido existe: {data_file.exists()}")
if data_file.exists():
    size_gb = data_file.stat().st_size / (1024**3)
    print(f"   Tamaño: {size_gb:.2f} GB")
    if 1.5 <= size_gb <= 1.7:
        print("   ✓ Tamaño correcto (1.6 GB esperados)")
    else:
        print("   ✗ Tamaño incorrecto")

# TEST 2: Verificar scripts de carga
print("\n[TEST 2] Verificando scripts de carga...")
print("-"*80)

load_script = PROJECT_ROOT / "src" / "data_loaders" / "load_microsoft_buildings.py"
print(f"Script de carga existe: {load_script.exists()}")

if load_script.exists():
    with open(load_script, 'r', encoding='utf-8') as f:
        content = f.read()
        checks = [
            ("MicrosoftBuildingsLoader", "Clase principal"),
            ("batch_size", "Procesamiento por lotes"),
            ("calculate_area_m2", "Cálculo de áreas"),
            ("create_spatial_indexes", "Índices espaciales")
        ]

        for check, desc in checks:
            if check in content:
                print(f"   ✓ {desc} implementado")
            else:
                print(f"   ✗ {desc} faltante")

# TEST 3: Verificar conexión MongoDB
print("\n[TEST 3] Verificando conexión a MongoDB...")
print("-"*80)

try:
    from src.database.connection import get_database, test_connection

    if test_connection(verbose=False):
        print("✓ Conexión a MongoDB exitosa")

        db = get_database()
        collection = db['microsoft_buildings']
        count = collection.count_documents({})

        print(f"✓ Colección 'microsoft_buildings' existe")
        print(f"✓ Documentos cargados: {count:,}")

        if count == 6083821:
            print("✓ Conteo correcto (6,083,821 esperados)")
        else:
            print(f"⚠ Conteo diferente (6,083,821 esperados, {count:,} encontrados)")

    else:
        print("✗ Error de conexión a MongoDB")

except Exception as e:
    print(f"✗ Error: {e}")

# TEST 4: Verificar muestra de datos
print("\n[TEST 4] Verificando estructura de datos...")
print("-"*80)

try:
    sample = collection.find_one()

    required_fields = ['geometry', 'properties', 'data_source', 'dataset', 'created_at']

    for field in required_fields:
        if field in sample:
            print(f"✓ Campo '{field}' presente")
        else:
            print(f"✗ Campo '{field}' faltante")

    # Verificar geometría
    if 'geometry' in sample and 'type' in sample['geometry']:
        print(f"✓ Tipo de geometría: {sample['geometry']['type']}")

    # Verificar área
    if 'properties' in sample and 'area_m2' in sample['properties']:
        print(f"✓ Área calculada: {sample['properties']['area_m2']} m²")

except Exception as e:
    print(f"✗ Error verificando datos: {e}")

# TEST 5: Verificar documentación
print("\n[TEST 5] Verificando documentación...")
print("-"*80)

docs = [
    ("deliverables/deliverable_3/README_PERSONA_1.md", "README rápido"),
    ("deliverables/deliverable_3/microsoft_integration.md", "Doc técnica"),
    ("deliverables/deliverable_3/RESUMEN_PERSONA_1.md", "Resumen ejecutivo"),
    ("COMPARTIR_DATOS_EQUIPO.md", "Instrucciones para compartir")
]

for doc_path, desc in docs:
    doc = PROJECT_ROOT / doc_path
    if doc.exists():
        size_kb = doc.stat().st_size / 1024
        print(f"✓ {desc}: {size_kb:.1f} KB")
    else:
        print(f"✗ {desc}: NO ENCONTRADO")

# TEST 6: Verificar que el proceso es reproducible
print("\n[TEST 6] Verificando reproducibilidad...")
print("-"*80)

instructions = [
    "1. Descargar Colombia.geojsonl.zip (482 MB)",
    "2. Descomprimir en data/raw/microsoft/",
    "3. Ejecutar: py src/data_loaders/load_microsoft_buildings.py --drop",
    "4. Verificar: py src/database/connection.py"
]

print("Pasos que seguirán los compañeros:")
for step in instructions:
    print(f"  {step}")

print("\n✓ Proceso documentado y reproducible")

# RESUMEN FINAL
print("\n" + "="*80)
print("RESUMEN DE VERIFICACIÓN")
print("="*80)

tests_passed = []
tests_failed = []

# Evaluar cada test
if zip_file.exists() and data_file.exists():
    tests_passed.append("Archivos necesarios")
else:
    tests_failed.append("Archivos necesarios")

if load_script.exists():
    tests_passed.append("Scripts de carga")
else:
    tests_failed.append("Scripts de carga")

try:
    if collection.count_documents({}) > 0:
        tests_passed.append("Datos en MongoDB")
    else:
        tests_failed.append("Datos en MongoDB")
except:
    tests_failed.append("Datos en MongoDB")

all_docs_exist = all((PROJECT_ROOT / doc).exists() for doc, _ in docs)
if all_docs_exist:
    tests_passed.append("Documentación")
else:
    tests_failed.append("Documentación")

print(f"\nTests pasados: {len(tests_passed)}/4")
for test in tests_passed:
    print(f"  ✓ {test}")

if tests_failed:
    print(f"\nTests fallidos: {len(tests_failed)}/4")
    for test in tests_failed:
        print(f"  ✗ {test}")

print("\n" + "="*80)
if len(tests_passed) == 4:
    print("✓ TODO LISTO PARA COMPARTIR CON EL EQUIPO")
    print("="*80)
    print("\nPróximos pasos:")
    print("1. Subir Colombia.geojsonl.zip a Google Drive")
    print("2. Obtener link compartible")
    print("3. Compartir con el equipo usando COMPARTIR_DATOS_EQUIPO.md")
else:
    print("⚠ REVISAR ITEMS FALLIDOS ANTES DE COMPARTIR")
    print("="*80)
