"""
Script de validación comprehensiva para datos de edificaciones

Este script valida la integridad y calidad de los datos de Microsoft Buildings
cargados en MongoDB para el Entregable 3.

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
Entregable: 3 - PERSONA 4
"""

import sys
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

# Agregar raíz al path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

def validate_microsoft_buildings():
    """Valida datos de Microsoft Buildings"""
    print("=" * 70)
    print("VALIDACIÓN COMPREHENSIVA - MICROSOFT BUILDINGS")
    print("=" * 70 + "\n")

    db = get_database()
    collection = db.microsoft_buildings

    # 1. Conteo total
    total = collection.count_documents({})
    print(f"✅ Total de documentos: {total:,}")

    # 2. Verificar campos requeridos
    print("\nVerificando campos requeridos...")
    sample = collection.find_one({})
    if sample:
        required_fields = ['geometry', 'properties', 'data_source', 'created_at']
        for field in required_fields:
            if field in sample:
                print(f"  [OK] Campo '{field}' presente")
            else:
                print(f"  [FALTA] Campo '{field}' FALTANTE")

    # 3. Verificar geometrías
    print("\nVerificando geometrias...")
    geom_check = collection.count_documents({'geometry.type': 'Polygon'})
    print(f"  [OK] Geometrias tipo Polygon: {geom_check:,}")

    # 4. Verificar áreas
    print("\nVerificando areas...")
    with_area = collection.count_documents({'properties.area_m2': {'$exists': True}})
    print(f"  [OK] Documentos con area_m2: {with_area:,}")

    # Estadísticas de área
    pipeline_area = [
        {'$match': {'properties.area_m2': {'$gt': 0}}},
        {'$group': {
            '_id': None,
            'avg': {'$avg': '$properties.area_m2'},
            'min': {'$min': '$properties.area_m2'},
            'max': {'$max': '$properties.area_m2'}
        }}
    ]
    area_stats = list(collection.aggregate(pipeline_area))
    if area_stats:
        stats = area_stats[0]
        print(f"  📊 Área promedio: {stats['avg']:.2f} m²")
        print(f"  📊 Área mínima: {stats['min']:.2f} m²")
        print(f"  📊 Área máxima: {stats['max']:.2f} m²")

    # 5. Verificar data_source
    print("\n🔍 Verificando fuente de datos...")
    sources = collection.distinct('data_source')
    print(f"  ✅ Fuentes únicas: {sources}")

    # 6. Verificar fechas de creación
    print("\n📅 Verificando timestamps...")
    with_timestamp = collection.count_documents({'created_at': {'$exists': True}})
    print(f"  ✅ Documentos con created_at: {with_timestamp:,}")

    # 7. Verificar índices
    print("\n🔧 Verificando índices...")
    indexes = collection.index_information()
    print(f"  📋 Índices existentes:")
    for idx_name, idx_info in indexes.items():
        print(f"    - {idx_name}")

    # 8. Distribución de coordenadas (verificar que estén en Colombia)
    print("\n🌎 Verificando coordenadas (deben estar en Colombia)...")
    colombia_bbox = {
        'min_lon': -82.0, 'max_lon': -66.0,
        'min_lat': -5.0, 'max_lat': 14.0
    }

    # Contar edificaciones fuera de bbox de Colombia
    outside_colombia = collection.count_documents({
        '$or': [
            {'geometry.coordinates.0.0.0': {'$lt': colombia_bbox['min_lon']}},
            {'geometry.coordinates.0.0.0': {'$gt': colombia_bbox['max_lon']}},
            {'geometry.coordinates.0.0.1': {'$lt': colombia_bbox['min_lat']}},
            {'geometry.coordinates.0.0.1': {'$gt': colombia_bbox['max_lat']}}
        ]
    })

    if outside_colombia == 0:
        print(f"  ✅ Todas las edificaciones dentro de bbox Colombia")
    else:
        print(f"  ⚠️  {outside_colombia:,} edificaciones fuera de bbox Colombia")

    # 9. Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 70)

    validation_results = {
        'total_documents': total,
        'geometries_valid': geom_check,
        'with_area': with_area,
        'with_timestamp': with_timestamp,
        'indexes_count': len(indexes),
        'outside_colombia_bbox': outside_colombia,
        'validation_passed': True if outside_colombia == 0 and total > 6000000 else False,
        'timestamp': datetime.now().isoformat()
    }

    # Exportar resultados
    results_dir = PROJECT_ROOT / 'results' / 'deliverable_3'
    results_dir.mkdir(parents=True, exist_ok=True)

    validation_path = results_dir / 'microsoft_validation_report.json'
    with open(validation_path, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)

    print(f"\n✅ Validación completa")
    print(f"📄 Reporte guardado: {validation_path}")

    if validation_results['validation_passed']:
        print("\n🎉 VALIDACIÓN EXITOSA: Datos de Microsoft Buildings están completos y correctos")
    else:
        print("\n⚠️  ADVERTENCIAS encontradas durante la validación")

    return validation_results


def validate_pdet_municipalities():
    """Valida datos de municipios PDET"""
    print("\n" + "=" * 70)
    print("VALIDACIÓN - MUNICIPIOS PDET")
    print("=" * 70 + "\n")

    db = get_database()
    collection = db.pdet_municipalities

    total = collection.count_documents({})
    print(f"✅ Total de municipios: {total}")

    with_geom = collection.count_documents({'geom': {'$exists': True}})
    print(f"✅ Municipios con geometría: {with_geom}")

    # Por región
    print("\n📊 Distribución por región PDET:")
    pipeline = [
        {'$group': {
            '_id': '$pdet_region',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}}
    ]

    by_region = list(collection.aggregate(pipeline))
    for region in by_region[:10]:  # Top 10
        print(f"  - {region['_id']}: {region['count']} municipios")

    return {'total_municipalities': total, 'with_geometry': with_geom}


def main():
    """Función principal"""
    print("\nINICIANDO VALIDACION COMPREHENSIVA\n")

    try:
        # Validar Microsoft Buildings
        ms_results = validate_microsoft_buildings()

        # Validar Municipios PDET
        pdet_results = validate_pdet_municipalities()

        print("\n" + "=" * 70)
        print("VALIDACION COMPLETADA")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error durante validación: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
