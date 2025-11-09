"""Verificacion completa sin caracteres especiales"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("="*80)
print("VERIFICACION COMPLETA - PROCESO DE CARGA")
print("="*80)

# Test 1: Archivos
print("\n[1] ARCHIVOS NECESARIOS")
print("-"*80)

zip_file = Path("C:/Users/PcMaster/Downloads/Colombia.geojsonl.zip")
data_file = PROJECT_ROOT / "data/raw/microsoft/Colombia.geojsonl"

zip_ok = zip_file.exists()
print(f"ZIP existe: {zip_ok}")
if zip_ok:
    print(f"  Tamano: {zip_file.stat().st_size / (1024**2):.2f} MB")

data_ok = data_file.exists()
print(f"Data descomprimida: {data_ok}")
if data_ok:
    print(f"  Tamano: {data_file.stat().st_size / (1024**3):.2f} GB")

# Test 2: MongoDB
print("\n[2] DATOS EN MONGODB")
print("-"*80)

try:
    from src.database.connection import get_database
    db = get_database()
    coll = db['microsoft_buildings']
    count = coll.count_documents({})

    print(f"Conexion MongoDB: OK")
    print(f"Coleccion existe: OK")
    print(f"Documentos: {count:,}")

    if count == 6083821:
        print(f"Conteo: CORRECTO")
        mongodb_ok = True
    else:
        print(f"Conteo: DIFERENTE (esperados 6,083,821)")
        mongodb_ok = False

    # Verificar muestra
    sample = coll.find_one()
    print(f"\nMuestra de datos:")
    print(f"  Geometria: {sample['geometry']['type']}")
    print(f"  Area: {sample['properties']['area_m2']} m2")
    print(f"  Data source: {sample['data_source']}")

except Exception as e:
    print(f"Error MongoDB: {e}")
    mongodb_ok = False

# Test 3: Scripts
print("\n[3] SCRIPTS DE CARGA")
print("-"*80)

script = PROJECT_ROOT / "src/data_loaders/load_microsoft_buildings.py"
script_ok = script.exists()
print(f"Script principal: {script_ok}")

if script_ok:
    size = script.stat().st_size / 1024
    print(f"  Tamano: {size:.1f} KB")

# Test 4: Documentacion
print("\n[4] DOCUMENTACION")
print("-"*80)

docs = [
    "deliverables/deliverable_3/README_PERSONA_1.md",
    "deliverables/deliverable_3/microsoft_integration.md",
    "deliverables/deliverable_3/RESUMEN_PERSONA_1.md",
    "COMPARTIR_DATOS_EQUIPO.md"
]

docs_ok = True
for doc in docs:
    exists = (PROJECT_ROOT / doc).exists()
    print(f"{doc.split('/')[-1]}: {exists}")
    if not exists:
        docs_ok = False

# RESUMEN
print("\n" + "="*80)
print("RESUMEN")
print("="*80)

tests = {
    "Archivos (ZIP + Data)": zip_ok and data_ok,
    "MongoDB (6,083,821 docs)": mongodb_ok,
    "Scripts de carga": script_ok,
    "Documentacion completa": docs_ok
}

passed = sum(tests.values())
total = len(tests)

print(f"\nTests: {passed}/{total} pasados\n")

for test, result in tests.items():
    status = "OK" if result else "FAIL"
    print(f"  [{status}] {test}")

print("\n" + "="*80)

if passed == total:
    print("ESTADO: TODO LISTO PARA COMPARTIR")
    print("="*80)
    print("\nPROXIMOS PASOS:")
    print("1. Subir Colombia.geojsonl.zip a Google Drive")
    print("2. Obtener link compartible")
    print("3. Compartir link con el equipo")
    print("4. Enviar archivo COMPARTIR_DATOS_EQUIPO.md con instrucciones")
else:
    print("ESTADO: REVISAR ITEMS FALLIDOS")
    print("="*80)

print("\n" + "="*80)
print("VERIFICACION COMPLETADA")
print("="*80)
