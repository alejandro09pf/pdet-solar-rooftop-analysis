"""
Join espacial RAPIDO usando primer punto de geometría directamente

En lugar de calcular y guardar centroides, usamos el primer punto
de cada polígono directamente en las queries MongoDB.

MongoDB hace TODO el trabajo pesado.

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

def get_muni_bounds(geom):
    """Extrae bounding box simple de geometría"""
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

def count_buildings_fast(db, muni, dataset='microsoft'):
    """
    Usa agregación de MongoDB con bbox

    Estrategia:
    - MongoDB filtra por bbox (rápido con índices en coordinates)
    - Usa primer punto de cada polígono (coordinates.0.0)
    """
    collection = db[f'{dataset}_buildings']

    geom = muni.get('geom')
    if not geom:
        return {'count': 0, 'avg_area': 0}

    bounds = get_muni_bounds(geom)
    if not bounds:
        return {'count': 0, 'avg_area': 0}

    try:
        # Pipeline de agregación - MongoDB hace el trabajo
        pipeline = [
            {
                '$match': {
                    # Filtrar por bbox usando primer punto del polígono
                    'geometry.coordinates.0.0.0': {
                        '$gte': bounds['min_lon'],
                        '$lte': bounds['max_lon']
                    },
                    'geometry.coordinates.0.0.1': {
                        '$gte': bounds['min_lat'],
                        '$lte': bounds['max_lat']
                    }
                }
            },
            {
                '$facet': {
                    'count': [{'$count': 'total'}],
                    'avg_area': [
                        {'$limit': 500},  # Muestra más pequeña para velocidad
                        {'$match': {'properties.area_m2': {'$gt': 0}}},
                        {'$group': {
                            '_id': None,
                            'avg': {'$avg': '$properties.area_m2'}
                        }}
                    ]
                }
            }
        ]

        result = list(collection.aggregate(pipeline, allowDiskUse=True, maxTimeMS=60000))

        if result and len(result) > 0:
            count = result[0]['count'][0]['total'] if result[0]['count'] else 0
            avg_area = result[0]['avg_area'][0]['avg'] if result[0]['avg_area'] else 0
            return {'count': count, 'avg_area': avg_area}

    except Exception as e:
        print(f"\nError: {str(e)}")
        return {'count': 0, 'avg_area': 0}

    return {'count': 0, 'avg_area': 0}

def main():
    print("="*70)
    print("JOIN ESPACIAL RAPIDO - MONGODB")
    print("="*70)
    print("\nUsando primer punto de geometría directamente")
    print("MongoDB hace agregaciones con bbox filtering\n")

    db = get_database()

    # Obtener municipios
    municipalities = list(db.pdet_municipalities.find({}))
    print(f"Total municipios PDET: {len(municipalities)}")

    # Limpiar colección de resultados
    stats_collection = db.buildings_by_municipality
    print("\nLimpiando coleccion de estadisticas...")
    stats_collection.delete_many({})

    print("\nProcesando municipios...\n")

    results = []

    for muni in tqdm(municipalities, desc="Analizando"):
        try:
            muni_code = muni.get('muni_code', muni.get('divipola_code', 'unknown'))
            muni_name = muni.get('muni_name', muni.get('municipio', 'Unknown'))
            dept_name = muni.get('dept_name', muni.get('departamento', 'Unknown'))
            pdet_region = muni.get('pdet_region', muni.get('region_pdet', 'Unknown'))

            # MongoDB hace agregaciones
            ms_stats = count_buildings_fast(db, muni, 'microsoft')
            gg_stats = count_buildings_fast(db, muni, 'google')

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

            # Calcular áreas totales estimadas
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
        print(f"{i:2}. {r['muni_name']:30} ({r['dept_name']:20}): {count:8,} ({area:.2f} km²)")

    print("\n" + "="*70)
    print("TOP 10 MUNICIPIOS - GOOGLE")
    print("="*70)
    sorted_gg = sorted(results, key=lambda x: x['google']['count'], reverse=True)[:10]
    for i, r in enumerate(sorted_gg, 1):
        count = r['google']['count']
        area = r['google'].get('total_area_km2', 0)
        print(f"{i:2}. {r['muni_name']:30} ({r['dept_name']:20}): {count:8,} ({area:.2f} km²)")

    # Por región
    print("\n" + "="*70)
    print("DISTRIBUCION POR REGION PDET")
    print("="*70)
    by_region = {}
    for r in results:
        region = r['pdet_region']
        if region not in by_region:
            by_region[region] = {'microsoft': 0, 'google': 0}
        by_region[region]['microsoft'] += r['microsoft']['count']
        by_region[region]['google'] += r['google']['count']

    for region in sorted(by_region.keys()):
        ms = by_region[region]['microsoft']
        gg = by_region[region]['google']
        print(f"{region:40}: MS={ms:8,}  GG={gg:8,}")

    # Guardar resumen JSON
    results_dir = PROJECT_ROOT / 'results' / 'deliverable_3'
    results_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        'timestamp': datetime.now().isoformat(),
        'method': 'bbox filtering with first point',
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
        'by_region_microsoft': {r: by_region[r]['microsoft'] for r in by_region},
        'by_region_google': {r: by_region[r]['google'] for r in by_region}
    }

    summary_path = results_dir / 'final_analysis_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nResumen guardado: {summary_path}")
    print(f"Datos en MongoDB: buildings_by_municipality")
    print("\n" + "="*70)
    print("ANALISIS COMPLETADO!")
    print("="*70)

if __name__ == '__main__':
    main()
