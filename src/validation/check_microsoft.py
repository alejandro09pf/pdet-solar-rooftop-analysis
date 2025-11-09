"""Quick check for Microsoft buildings"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.database.connection import get_database

db = get_database()
coll = db['microsoft_buildings']

print("="*60)
print("MICROSOFT BUILDINGS - VERIFICACION RAPIDA")
print("="*60)

# Conteo
count = coll.count_documents({})
print(f"\n1. Total edificaciones: {count:,}")

# Indices
print(f"\n2. Indices:")
for idx in coll.list_indexes():
    print(f"   - {idx['name']}: {idx['key']}")

# Si no hay indice 2dsphere, crearlo
has_2dsphere = any('2dsphere' in str(idx['key']) for idx in coll.list_indexes())
if not has_2dsphere:
    print("\n   Creando indices espaciales...")
    coll.create_index([('geometry', '2dsphere')])
    coll.create_index('properties.area_m2')
    coll.create_index('data_source')
    print("   OK - Indices creados")

# Muestra
print(f"\n3. Muestra:")
sample = coll.find_one()
print(f"   Geometria: {sample['geometry']['type']}")
print(f"   Area: {sample['properties']['area_m2']} m2")
print(f"   Data source: {sample['data_source']}")

# Stats rapidas
print(f"\n4. Estadisticas (muestra de 10,000):")
pipeline = [
    {'$sample': {'size': 10000}},
    {'$group': {
        '_id': None,
        'avg_area': {'$avg': '$properties.area_m2'},
        'min_area': {'$min': '$properties.area_m2'},
        'max_area': {'$max': '$properties.area_m2'}
    }}
]
result = list(coll.aggregate(pipeline))
if result:
    s = result[0]
    print(f"   Area promedio: {s['avg_area']:.2f} m2")
    print(f"   Area minima: {s['min_area']:.2f} m2")
    print(f"   Area maxima: {s['max_area']:.2f} m2")

print("\n" + "="*60)
print("OK - Coleccion lista para usar")
print("="*60)
