"""
Validación integral para Google Open Buildings
"""
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

def validate_google_buildings():
    print("="*80)
    print("VALIDACIÓN GOOGLE OPEN BUILDINGS")
    print("="*80)
    db = get_database()
    coll = db['google_buildings']

    # Conteo total
    print("\n1. CONTEO DE DOCUMENTOS\n" + "-"*80)
    total = coll.count_documents({})
    print(f"Total de edificaciones: {total:,}")

    # Índices
    print("\n2. ÍNDICES\n" + "-"*80)
    indexes = list(coll.list_indexes())
    print(f"Total de índices: {len(indexes)}")
    has_2dsphere = any('2dsphere' in str(idx['key']) for idx in indexes)
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['key']}")
    if not has_2dsphere:
        print("\n⚠️  [ADVERTENCIA] El índice 2dsphere no está creado, queries espaciales serán lentas.")

    # Estadísticas de confianza
    print("\n3. ESTADÍSTICAS DE CONFIANZA\n" + "-"*80)
    pipeline = [
        { "$bucket": {
            "groupBy": "$properties.confidence",
            "boundaries": [0.65, 0.70, 0.80, 0.90, 1.0],
            "default": "Mayor a 1.0",
            "output": { "count": { "$sum": 1 } }
        }}
    ]
    for b in coll.aggregate(pipeline):
        print(f"  {b['_id']}: {b['count']:,}")

    # Estadísticas de áreas
    print("\n4. ESTADÍSTICAS DE ÁREAS\n" + "-"*80)
    agg = list(coll.aggregate([
        {
            "$group": {
                "_id": None,
                "prom": { "$avg": "$properties.area_in_meters" },
                "min": { "$min": "$properties.area_in_meters" },
                "max": { "$max": "$properties.area_in_meters" },
                "total": { "$sum": "$properties.area_in_meters" }
            }
        }
    ]))
    if agg:
        s = agg[0]
        print(f"  Área promedio: {s['prom']:.2f} m²")
        print(f"  Área mínima: {s['min']:.2f} m²")
        print(f"  Área máxima: {s['max']:.2f} m²")
        print(f"  Área total: {s['total'] / 1e6:.2f} km²")
    else:
        print("No se pudo calcular estadísticas de área.")

    # Campos requeridos
    print("\n5. VALIDACIÓN DE CAMPOS REQUERIDOS\n" + "-"*80)
    req_fields = ['geometry', 'properties.area_in_meters', 'properties.confidence', 'data_source', 'dataset', 'created_at']
    for field in req_fields:
        missing = coll.count_documents({field: {'$exists': False}})
        nulls = coll.count_documents({field: None})
        if missing == 0 and nulls == 0:
            print(f"✓ {field}: OK")
        else:
            print(f"✗ {field}: Faltantes={missing}, Nulos={nulls}")

    # Muestra
    print("\n6. MUESTRA DE DOCUMENTOS\n" + "-"*80)
    for i, doc in enumerate(coll.find({}, {"geometry": 1, "properties": 1, "_id": 0}).limit(2), 1):
        print(f"\nDocumento {i}:\n  Área: {doc.get('properties', {}).get('area_in_meters', '-')} m²\n  Confianza: {doc.get('properties', {}).get('confidence', '-')}\n  Coordenadas: {str(doc.get('geometry', ''))[:100]}...")

    print("\n" + "="*80)
    print("✓ VALIDACIÓN COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    validate_google_buildings()
