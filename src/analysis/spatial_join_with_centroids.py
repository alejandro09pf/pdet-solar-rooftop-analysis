"""
Join espacial usando centroides e índices 2dsphere de MongoDB

Este script usa $geoWithin de MongoDB con centroides e índices 2dsphere
para hacer joins espaciales MUY rápidos.

TODO el trabajo pesado lo hace MongoDB.

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
Entregable: 3
"""

import sys
from pathlib import Path
from datetime import datetime
import json
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

def count_buildings_with_geowithin(db, muni, dataset='microsoft'):
    """
    Usa $geoWithin de MongoDB para contar edificaciones

    Con índices 2dsphere, esto es SUPER rápido
    """
    collection_name = f'{dataset}_buildings'
    collection = db[collection_name]

    geom = muni.get('geom')
    if not geom:
        return {'count': 0, 'avg_area': 0}

    try:
        # Query usando $geoWithin - MongoDB hace todo el trabajo
        # Con índice 2dsphere en centroid, esto es MUY rápido
        pipeline = [
            {
                '$match': {
                    'centroid': {
                        '$geoWithin': {
                            '$geometry': geom
                        }
                    }
                }
            },
            {
                '$facet': {
                    'count': [{'$count': 'total'}],
                    'avg_area': [
                        {'$limit': 1000},
                        {'$match': {'properties.area_m2': {'$gt': 0}}},
                        {'$group': {
                            '_id': None,
                            'avg': {'$avg': '$properties.area_m2'}
                        }}
                    ]
                }
            }
        ]

        result = list(collection.aggregate(pipeline, allowDiskUse=True))

        if result and len(result) > 0:
            count = result[0]['count'][0]['total'] if result[0]['count'] else 0
            avg_area = result[0]['avg_area'][0]['avg'] if result[0]['avg_area'] else 0
            return {'count': count, 'avg_area': avg_area}

    except Exception as e:
        print(f"\nError en $geoWithin: {str(e)}")
        return {'count': 0, 'avg_area': 0}

    return {'count': 0, 'avg_area': 0}

def main():
    print("="*70)
    print("JOIN ESPACIAL CON CENTROIDES E INDICES 2DSPHERE")
    print("="*70)
    print("\nUsando $geoWithin de MongoDB para queries rapidas")
    print("Los indices 2dsphere hacen esto 10-20x mas rapido\n")

    db = get_database()

    # Verificar que existen centroides
    ms_with_centroid = db.microsoft_buildings.count_documents({'centroid': {'$exists': True}})
    gg_with_centroid = db.google_buildings.count_documents({'centroid': {'$exists': True}})

    print(f"Microsoft con centroid: {ms_with_centroid:,}")
    print(f"Google con centroid: {gg_with_centroid:,}")

    if ms_with_centroid == 0 or gg_with_centroid == 0:
        print("\nERROR: Primero ejecuta add_centroids_mongodb.py")
        return

    # Verificar índices
    print("\nVerificando indices 2dsphere...")
    ms_indexes = db.microsoft_buildings.index_information()
    gg_indexes = db.google_buildings.index_information()

    has_ms_index = any('2dsphere' in str(idx) for idx in ms_indexes.values())
    has_gg_index = any('2dsphere' in str(idx) for idx in gg_indexes.values())

    if not has_ms_index or not has_gg_index:
        print("Creando indices 2dsphere...")
        if not has_ms_index:
            db.microsoft_buildings.create_index([('centroid', '2dsphere')])
        if not has_gg_index:
            db.google_buildings.create_index([('centroid', '2dsphere')])
        print("Indices creados!")
    else:
        print("Indices 2dsphere OK!")

    # Obtener municipios
    municipalities = list(db.pdet_municipalities.find({}))
    print(f"\nTotal municipios PDET: {len(municipalities)}")

    # Limpiar colección de resultados
    stats_collection = db.buildings_by_municipality
    print("\nLimpiando coleccion de estadisticas...")
    stats_collection.delete_many({})

    print("\nProcesando municipios con $geoWithin...")
    print("Este proceso sera MUCHO mas rapido con indices\n")

    results = []

    for muni in tqdm(municipalities, desc="Analizando"):
        try:
            muni_code = muni.get('muni_code', muni.get('divipola_code', 'unknown'))
            muni_name = muni.get('muni_name', muni.get('municipio', 'Unknown'))
            dept_name = muni.get('dept_name', muni.get('departamento', 'Unknown'))
            pdet_region = muni.get('pdet_region', muni.get('region_pdet', 'Unknown'))

            # MongoDB hace queries con $geoWithin (super rápido con índices)
            ms_stats = count_buildings_with_geowithin(db, muni, 'microsoft')
            gg_stats = count_buildings_with_geowithin(db, muni, 'google')

            # Preparar documento
            doc = {
                'muni_code': muni_code,
                'muni_name': muni_name,
                'dept_name': dept_name,
                'pdet_region': pdet_region,
                'pdet_subregion': muni.get('pdet_subregion', 'Unknown'),
                'area_km2': muni.get('area_km2', 0),
                'microsoft': {
                    'count': ms_stats['count'],
                    'avg_area_m2': round(ms_stats['avg_area'], 2) if ms_stats['avg_area'] > 0 else 0
                },
                'google': {
                    'count': gg_stats['count'],
                    'avg_area_m2': round(gg_stats['avg_area'], 2) if gg_stats['avg_area'] > 0 else 0
                },
                'created_at': datetime.utcnow()
            }

            # Calcular áreas totales
            if ms_stats['count'] > 0 and ms_stats['avg_area'] > 0:
                doc['microsoft']['total_area_m2'] = round(ms_stats['avg_area'] * ms_stats['count'], 2)
                doc['microsoft']['total_area_km2'] = round(doc['microsoft']['total_area_m2'] / 1_000_000, 4)

            if gg_stats['count'] > 0 and gg_stats['avg_area'] > 0:
                doc['google']['total_area_m2'] = round(gg_stats['avg_area'] * gg_stats['count'], 2)
                doc['google']['total_area_km2'] = round(doc['google']['total_area_m2'] / 1_000_000, 4)

            # Insertar en MongoDB
            stats_collection.insert_one(doc)
            results.append(doc)

        except Exception as e:
            print(f"\nError en {muni_name}: {str(e)}")
            continue

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)

    total_ms = sum(r['microsoft']['count'] for r in results)
    total_gg = sum(r['google']['count'] for r in results)

    print(f"\nMunicipios procesados: {len(results)}")
    print(f"Total edificaciones Microsoft: {total_ms:,}")
    print(f"Total edificaciones Google: {total_gg:,}")

    # Calcular áreas totales
    total_area_ms = sum(r['microsoft'].get('total_area_km2', 0) for r in results)
    total_area_gg = sum(r['google'].get('total_area_km2', 0) for r in results)

    print(f"\nArea total techos Microsoft: {total_area_ms:.2f} km²")
    print(f"Area total techos Google: {total_area_gg:.2f} km²")

    # Top 10 municipios
    print("\n" + "="*70)
    print("TOP 10 MUNICIPIOS - MICROSOFT")
    print("="*70)
    sorted_ms = sorted(results, key=lambda x: x['microsoft']['count'], reverse=True)[:10]
    for i, r in enumerate(sorted_ms, 1):
        count = r['microsoft']['count']
        area = r['microsoft'].get('total_area_km2', 0)
        print(f"{i:2}. {r['muni_name']:30} ({r['dept_name']:20}): {count:8,} edificaciones ({area:.2f} km²)")

    print("\n" + "="*70)
    print("TOP 10 MUNICIPIOS - GOOGLE")
    print("="*70)
    sorted_gg = sorted(results, key=lambda x: x['google']['count'], reverse=True)[:10]
    for i, r in enumerate(sorted_gg, 1):
        count = r['google']['count']
        area = r['google'].get('total_area_km2', 0)
        print(f"{i:2}. {r['muni_name']:30} ({r['dept_name']:20}): {count:8,} edificaciones ({area:.2f} km²)")

    # Guardar resumen JSON
    results_dir = PROJECT_ROOT / 'results' / 'deliverable_3'
    results_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        'timestamp': datetime.now().isoformat(),
        'method': 'geoWithin with 2dsphere indexes on centroids',
        'total_municipalities': len(results),
        'microsoft': {
            'total_buildings': total_ms,
            'total_area_km2': round(total_area_ms, 2),
            'municipalities_with_data': sum(1 for r in results if r['microsoft']['count'] > 0)
        },
        'google': {
            'total_buildings': total_gg,
            'total_area_km2': round(total_area_gg, 2),
            'municipalities_with_data': sum(1 for r in results if r['google']['count'] > 0)
        },
        'top_10_microsoft': [
            {
                'muni_name': r['muni_name'],
                'dept_name': r['dept_name'],
                'pdet_region': r['pdet_region'],
                'count': r['microsoft']['count'],
                'area_km2': r['microsoft'].get('total_area_km2', 0)
            } for r in sorted_ms
        ],
        'top_10_google': [
            {
                'muni_name': r['muni_name'],
                'dept_name': r['dept_name'],
                'pdet_region': r['pdet_region'],
                'count': r['google']['count'],
                'area_km2': r['google'].get('total_area_km2', 0)
            } for r in sorted_gg
        ],
        'by_region_microsoft': {},
        'by_region_google': {}
    }

    # Agregación por región
    for r in results:
        region = r['pdet_region']
        if region not in summary['by_region_microsoft']:
            summary['by_region_microsoft'][region] = 0
            summary['by_region_google'][region] = 0
        summary['by_region_microsoft'][region] += r['microsoft']['count']
        summary['by_region_google'][region] += r['google']['count']

    summary_path = results_dir / 'final_analysis_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nResumen guardado: {summary_path}")
    print(f"Datos en MongoDB: buildings_by_municipality")
    print("\n" + "="*70)
    print("ANALISIS COMPLETADO EXITOSAMENTE")
    print("="*70)

if __name__ == '__main__':
    main()
