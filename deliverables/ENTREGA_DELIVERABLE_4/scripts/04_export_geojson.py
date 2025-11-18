"""
Script para exportar datos geoespaciales con estadísticas

Exporta municipios PDET con todas las estadísticas calculadas en formato GeoJSON

Autor: Equipo PDET Solar Analysis
Fecha: Noviembre 2025
Deliverable: 4
"""

import sys
from pathlib import Path
import json
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_geojson(db):
    """Exporta municipios con estadísticas en formato GeoJSON"""
    logger.info("=" * 70)
    logger.info("EXPORTACIÓN GEOJSON")
    logger.info("=" * 70)

    # Leer municipios con geometrías
    munis_coll = db.pdet_municipalities
    stats_coll = db.buildings_by_municipality

    # Crear diccionario de estadísticas por código de municipio
    stats_dict = {}
    for doc in stats_coll.find({}):
        muni_code = doc.get('muni_code', '')
        stats_dict[muni_code] = doc

    # Construir GeoJSON
    features = []

    for muni in munis_coll.find({}):
        muni_code = muni.get('muni_code', '')
        muni_name = muni.get('muni_name', '')
        geom = muni.get('geom')

        if not geom:
            logger.warning(f"Sin geometría: {muni_name}")
            continue

        # Obtener estadísticas
        stats = stats_dict.get(muni_code, {})
        ms = stats.get('microsoft', {})
        gg = stats.get('google', {})

        # Crear feature
        feature = {
            'type': 'Feature',
            'geometry': geom,
            'properties': {
                # Identificación
                'muni_code': muni_code,
                'muni_name': muni_name,
                'dept_name': stats.get('dept_name', muni.get('dept_name', '')),
                'pdet_region': stats.get('pdet_region', muni.get('pdet_region', '')),
                'pdet_subregion': stats.get('pdet_subregion', muni.get('pdet_subregion', '')),
                'area_muni_km2': round(muni.get('area_km2', 0), 2),

                # Microsoft
                'ms_buildings_count': ms.get('count', 0),
                'ms_avg_area_m2': round(ms.get('avg_area_m2', 0), 2),
                'ms_total_area_km2': round(ms.get('total_area_km2', 0), 4),
                'ms_useful_area_km2': round(ms.get('area_util_km2', 0), 4),
                'ms_useful_area_ha': round(ms.get('area_util_ha', 0), 2),

                # Google
                'gg_buildings_count': gg.get('count', 0),
                'gg_avg_area_m2': round(gg.get('avg_area_m2', 0), 2),
                'gg_total_area_km2': round(gg.get('total_area_km2', 0), 4),
                'gg_useful_area_km2': round(gg.get('area_util_km2', 0), 4),
                'gg_useful_area_ha': round(gg.get('area_util_ha', 0), 2)
            }
        }

        features.append(feature)

    # Crear FeatureCollection
    geojson = {
        'type': 'FeatureCollection',
        'name': 'municipios_pdet_with_stats',
        'crs': {
            'type': 'name',
            'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}
        },
        'features': features
    }

    # Exportar
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'geojson'
    output_dir.mkdir(parents=True, exist_ok=True)

    geojson_path = output_dir / 'municipalities_with_stats.geojson'

    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    logger.info(f"GeoJSON exportado: {geojson_path}")
    logger.info(f"   Features: {len(features)}")
    logger.info(f"   Tamaño: {geojson_path.stat().st_size / 1024:.1f} KB")
    logger.info("")
    logger.info("=" * 70)


def main():
    """Función principal"""
    try:
        db = get_database()
        export_geojson(db)
        logger.info("Exportación completada exitosamente")
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
