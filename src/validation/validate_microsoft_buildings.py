"""
Script de validación para Microsoft Building Footprints

Verifica la integridad de la carga y genera estadísticas finales.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database


def validate_microsoft_buildings():
    """Valida la colección microsoft_buildings"""

    print("="*80)
    print("VALIDACIÓN DE MICROSOFT BUILDING FOOTPRINTS")
    print("="*80)

    db = get_database()
    collection = db['microsoft_buildings']

    # 1. Conteo de documentos
    print("\n1. CONTEO DE DOCUMENTOS")
    print("-"*80)
    count = collection.count_documents({})
    print(f"Total de edificaciones: {count:,}")
    expected = 6_083_821
    if count == expected:
        print(f"✓ Conteo correcto ({expected:,} edificaciones)")
    else:
        print(f"✗ Conteo incorrecto. Esperado: {expected:,}, Encontrado: {count:,}")

    # 2. Verificar índices
    print("\n2. ÍNDICES")
    print("-"*80)
    indexes = list(collection.list_indexes())
    print(f"Total de índices: {len(indexes)}")

    for idx in indexes:
        print(f"\n  Índice: {idx['name']}")
        print(f"    Campos: {idx['key']}")
        if 'unique' in idx:
            print(f"    Único: {idx['unique']}")

    # Verificar índice 2dsphere
    has_2dsphere = any('2dsphere' in str(idx['key']) for idx in indexes)
    if has_2dsphere:
        print("\n✓ Índice 2dsphere encontrado")
    else:
        print("\n✗ Índice 2dsphere NO encontrado")
        print("  Creando índice 2dsphere...")
        collection.create_index([('geometry', '2dsphere')])
        collection.create_index('properties.area_m2')
        collection.create_index('data_source')
        print("  ✓ Índices creados")

    # 3. Estadísticas de áreas
    print("\n3. ESTADÍSTICAS DE ÁREAS")
    print("-"*80)
    pipeline = [
        {
            '$group': {
                '_id': None,
                'avg_area': {'$avg': '$properties.area_m2'},
                'min_area': {'$min': '$properties.area_m2'},
                'max_area': {'$max': '$properties.area_m2'},
                'total_area_m2': {'$sum': '$properties.area_m2'}
            }
        }
    ]

    print("Calculando estadísticas (puede tomar 1-2 minutos)...")
    result = list(collection.aggregate(pipeline))

    if result:
        stats = result[0]
        print(f"\nÁrea promedio: {stats['avg_area']:.2f} m²")
        print(f"Área mínima: {stats['min_area']:.2f} m²")
        print(f"Área máxima: {stats['max_area']:.2f} m²")
        print(f"Área total: {stats['total_area_m2']/1_000_000:.2f} km²")

    # 4. Muestra de documentos
    print("\n4. MUESTRA DE DOCUMENTOS")
    print("-"*80)
    samples = collection.find().limit(3)

    for i, doc in enumerate(samples, 1):
        print(f"\nDocumento {i}:")
        print(f"  _id: {doc['_id']}")
        print(f"  Geometría: {doc['geometry']['type']}")
        print(f"  Área: {doc['properties']['area_m2']} m²")
        print(f"  Data source: {doc['data_source']}")
        print(f"  Dataset: {doc['dataset']}")
        print(f"  Coordenadas (primeras 2): {doc['geometry']['coordinates'][0][:2]}")

    # 5. Validación de campos requeridos
    print("\n5. VALIDACIÓN DE CAMPOS REQUERIDOS")
    print("-"*80)

    fields_to_check = [
        'geometry',
        'properties.area_m2',
        'data_source',
        'dataset',
        'created_at'
    ]

    for field in fields_to_check:
        missing = collection.count_documents({field: {'$exists': False}})
        null_count = collection.count_documents({field: None})

        if missing == 0 and null_count == 0:
            print(f"✓ {field}: OK (sin valores faltantes o nulos)")
        else:
            print(f"✗ {field}: Faltantes={missing}, Nulos={null_count}")

    # 6. Validar geometrías
    print("\n6. VALIDACIÓN DE GEOMETRÍAS")
    print("-"*80)

    # Tipos de geometría
    geom_types = collection.distinct("geometry.type")
    print(f"Tipos de geometría: {geom_types}")

    # Geometrías sin coordenadas
    no_coords = collection.count_documents({"geometry.coordinates": {"$exists": False}})
    print(f"Geometrías sin coordenadas: {no_coords}")

    if no_coords == 0:
        print("✓ Todas las geometrías tienen coordenadas")

    # Áreas <= 0
    invalid_area = collection.count_documents({"properties.area_m2": {"$lte": 0}})
    print(f"Áreas <= 0: {invalid_area}")

    if invalid_area == 0:
        print("✓ Todas las áreas > 0")

    print("\n" + "="*80)
    print("✓ VALIDACIÓN COMPLETADA")
    print("="*80)

    return True


if __name__ == "__main__":
    validate_microsoft_buildings()
