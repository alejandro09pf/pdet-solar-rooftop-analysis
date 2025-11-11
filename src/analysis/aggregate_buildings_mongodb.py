"""
Script para agregar edificaciones por municipio usando MongoDB

Este script usa agregaciones nativas de MongoDB para que el servidor
haga el trabajo pesado, no Python.

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
Entregable: 3
"""

import sys
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

def get_municipality_bbox(geom):
    """Extrae bbox de geometría GeoJSON"""
    if geom['type'] == 'Polygon':
        coords = geom['coordinates'][0]
    elif geom['type'] == 'MultiPolygon':
        coords = []
        for polygon in geom['coordinates']:
            coords.extend(polygon[0])
    else:
        return None

    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    return {
        'min_lon': min(lons),
        'max_lon': max(lons),
        'min_lat': min(lats),
        'max_lat': max(lats)
    }

def aggregate_for_municipality(db, muni, dataset='microsoft'):
    """
    Usa agregación de MongoDB para contar edificaciones
    MongoDB hace el trabajo pesado en el servidor
    """
    collection_name = f'{dataset}_buildings'
    collection = db[collection_name]

    geom = muni.get('geom')
    if not geom:
        return {'count': 0, 'avg_area': 0}

    bbox = get_municipality_bbox(geom)
    if not bbox:
        return {'count': 0, 'avg_area': 0}

    # Agregación que MongoDB ejecuta en el servidor
    pipeline = [
        {
            '$match': {
                'geometry.coordinates.0.0.0': {
                    '$gte': bbox['min_lon'],
                    '$lte': bbox['max_lon']
                },
                'geometry.coordinates.0.0.1': {
                    '$gte': bbox['min_lat'],
                    '$lte': bbox['max_lat']
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

    return {'count': 0, 'avg_area': 0}

def main():
    print("=" * 70)
    print("AGREGACION DE EDIFICACIONES POR MUNICIPIO - MONGODB")
    print("=" * 70)
    print()

    db = get_database()

    # Obtener municipios
    municipalities = list(db.pdet_municipalities.find({}))
    print(f"Total municipios PDET: {len(municipalities)}")
    print()

    # Crear o limpiar colección de resultados
    stats_collection = db.buildings_by_municipality
    print("Limpiando colección de estadísticas...")
    stats_collection.delete_many({})

    print("\nProcesando municipios...")
    print("MongoDB hará el trabajo pesado de agregación\n")

    results = []

    for muni in tqdm(municipalities, desc="Agregando"):
        try:
            muni_code = muni.get('muni_code', muni.get('divipola_code', 'unknown'))
            muni_name = muni.get('muni_name', muni.get('municipio', 'Unknown'))
            dept_name = muni.get('dept_name', muni.get('departamento', 'Unknown'))
            pdet_region = muni.get('pdet_region', muni.get('region_pdet', 'Unknown'))

            # Agregaciones en MongoDB (servidor hace el trabajo)
            ms_stats = aggregate_for_municipality(db, muni, 'microsoft')
            gg_stats = aggregate_for_municipality(db, muni, 'google')

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
    print("\n" + "=" * 70)
    print("RESUMEN DE AGREGACION")
    print("=" * 70)

    total_ms = sum(r['microsoft']['count'] for r in results)
    total_gg = sum(r['google']['count'] for r in results)

    print(f"Municipios procesados: {len(results)}")
    print(f"Total edificaciones Microsoft: {total_ms:,}")
    print(f"Total edificaciones Google: {total_gg:,}")

    # Calcular áreas totales
    total_area_ms = sum(r['microsoft'].get('total_area_km2', 0) for r in results)
    total_area_gg = sum(r['google'].get('total_area_km2', 0) for r in results)

    print(f"\nArea total techos Microsoft: {total_area_ms:.2f} km²")
    print(f"Area total techos Google: {total_area_gg:.2f} km²")

    # Top 10 municipios
    print("\nTop 10 municipios (Microsoft):")
    sorted_ms = sorted(results, key=lambda x: x['microsoft']['count'], reverse=True)[:10]
    for i, r in enumerate(sorted_ms, 1):
        print(f"  {i}. {r['muni_name']} ({r['dept_name']}): {r['microsoft']['count']:,} edificaciones")

    print("\nTop 10 municipios (Google):")
    sorted_gg = sorted(results, key=lambda x: x['google']['count'], reverse=True)[:10]
    for i, r in enumerate(sorted_gg, 1):
        print(f"  {i}. {r['muni_name']} ({r['dept_name']}): {r['google']['count']:,} edificaciones")

    # Guardar resumen JSON
    results_dir = PROJECT_ROOT / 'results' / 'deliverable_3'
    results_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_municipalities': len(results),
        'microsoft': {
            'total_buildings': total_ms,
            'total_area_km2': round(total_area_ms, 2)
        },
        'google': {
            'total_buildings': total_gg,
            'total_area_km2': round(total_area_gg, 2)
        },
        'top_10_microsoft': [
            {
                'muni_name': r['muni_name'],
                'dept_name': r['dept_name'],
                'count': r['microsoft']['count']
            } for r in sorted_ms
        ],
        'top_10_google': [
            {
                'muni_name': r['muni_name'],
                'dept_name': r['dept_name'],
                'count': r['google']['count']
            } for r in sorted_gg
        ]
    }

    summary_path = results_dir / 'buildings_aggregation_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nResumen guardado: {summary_path}")
    print(f"Datos guardados en coleccion: buildings_by_municipality")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
