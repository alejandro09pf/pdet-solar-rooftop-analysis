"""
Script para generar resumen agregado por región PDET usando MongoDB

Usa $group y agregaciones de MongoDB para calcular totales por región.
MongoDB hace el trabajo pesado en el servidor.

Autor: Equipo PDET Solar Analysis
Fecha: Noviembre 2025
Deliverable: 4
"""

import sys
from pathlib import Path
import pandas as pd
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_regional_summary_mongodb(db):
    """Genera resumen regional usando agregaciones de MongoDB"""
    logger.info("=" * 70)
    logger.info("RESUMEN REGIONAL PDET - AGREGACIONES MONGODB")
    logger.info("=" * 70)
    logger.info("MongoDB hará TODO el trabajo pesado con $group")
    logger.info("")

    buildings_coll = db.buildings_by_municipality

    # Pipeline de agregación - MongoDB agrupa por región
    pipeline = [
        {
            # Agrupar por región PDET
            '$group': {
                '_id': '$pdet_region',
                # Contar municipios
                'num_municipalities': {'$sum': 1},

                # Microsoft - totales
                'ms_total_buildings': {'$sum': '$microsoft.count'},
                'ms_total_roof_area_km2': {'$sum': '$microsoft.total_area_km2'},
                'ms_total_useful_area_km2': {'$sum': '$microsoft.area_util_km2'},

                # Microsoft - promedios
                'ms_avg_buildings_per_muni': {'$avg': '$microsoft.count'},

                # Microsoft - municipio top
                'ms_top_muni': {
                    '$max': {
                        'name': '$muni_name',
                        'count': '$microsoft.count'
                    }
                },

                # Google - totales
                'gg_total_buildings': {'$sum': '$google.count'},
                'gg_total_roof_area_km2': {'$sum': '$google.total_area_km2'},
                'gg_total_useful_area_km2': {'$sum': '$google.area_util_km2'},

                # Google - promedios
                'gg_avg_buildings_per_muni': {'$avg': '$google.count'},

                # Google - municipio top
                'gg_top_muni': {
                    '$max': {
                        'name': '$muni_name',
                        'count': '$google.count'
                    }
                }
            }
        },
        {
            # Proyectar y formatear
            '$project': {
                '_id': 0,
                'pdet_region': '$_id',
                'num_municipalities': 1,

                # Microsoft
                'ms_total_buildings': 1,
                'ms_total_roof_area_km2': {'$round': ['$ms_total_roof_area_km2', 2]},
                'ms_total_useful_area_km2': {'$round': ['$ms_total_useful_area_km2', 2]},
                'ms_avg_buildings_per_muni': {'$round': ['$ms_avg_buildings_per_muni', 0]},
                'ms_top_municipality': '$ms_top_muni.name',
                'ms_top_municipality_count': '$ms_top_muni.count',

                # Google
                'gg_total_buildings': 1,
                'gg_total_roof_area_km2': {'$round': ['$gg_total_roof_area_km2', 2]},
                'gg_total_useful_area_km2': {'$round': ['$gg_total_useful_area_km2', 2]},
                'gg_avg_buildings_per_muni': {'$round': ['$gg_avg_buildings_per_muni', 0]},
                'gg_top_municipality': '$gg_top_muni.name',
                'gg_top_municipality_count': '$gg_top_muni.count'
            }
        },
        {
            # Ordenar por total de edificaciones MS (descendente)
            '$sort': {'ms_total_buildings': -1}
        }
    ]

    logger.info("Ejecutando pipeline de agregación con $group...")
    logger.info(f"Stages: {len(pipeline)}")

    # MongoDB hace TODO el trabajo de agregación
    results = list(buildings_coll.aggregate(pipeline, allowDiskUse=True))

    logger.info(f"MongoDB agrupó {len(results)} regiones PDET")
    logger.info("")

    # Convertir a DataFrame
    df = pd.DataFrame(results)

    # Exportar CSV
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'tables'
    csv_path = output_dir / 'regional_summary.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    logger.info(f"CSV regional exportado: {csv_path}")
    logger.info(f"   Regiones: {len(df)}")
    logger.info("")

    # Mostrar resumen
    logger.info("=" * 70)
    logger.info("RANKING DE REGIONES PDET (por edificaciones Microsoft)")
    logger.info("=" * 70)

    for i, (_, row) in enumerate(df.iterrows(), 1):
        logger.info(f"{i:2}. {row['pdet_region']:45} - {row['ms_total_buildings']:8,} edif ({row['num_municipalities']:2} munis) - {row['ms_total_useful_area_km2']:7.2f} km²")
        logger.info(f"    Top: {row['ms_top_municipality']} ({row['ms_top_municipality_count']:,} edif)")

    logger.info("")
    logger.info("=" * 70)
    logger.info("TOTALES GENERALES")
    logger.info("=" * 70)
    logger.info(f"Total regiones: {len(df)}")
    logger.info(f"Total municipios: {df['num_municipalities'].sum()}")
    logger.info(f"Total edificaciones MS: {df['ms_total_buildings'].sum():,}")
    logger.info(f"Total edificaciones Google: {df['gg_total_buildings'].sum():,}")
    logger.info(f"Área útil total MS: {df['ms_total_useful_area_km2'].sum():.2f} km²")
    logger.info(f"Área útil total Google: {df['gg_total_useful_area_km2'].sum():.2f} km²")
    logger.info("")
    logger.info("=" * 70)
    logger.info("NOTA: Todas las agregaciones hechas por MongoDB con $group")
    logger.info("=" * 70)

    return df


def main():
    """Función principal"""
    try:
        db = get_database()
        df = generate_regional_summary_mongodb(db)
        logger.info("Proceso completado exitosamente")
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
