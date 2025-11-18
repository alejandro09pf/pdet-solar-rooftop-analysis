"""
Script para generar estadísticas completas por municipio usando MongoDB

Usa agregaciones de MongoDB para calcular todas las métricas.
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


def generate_statistics_mongodb(db):
    """Genera estadísticas usando agregaciones de MongoDB"""
    logger.info("=" * 70)
    logger.info("GENERACIÓN DE ESTADÍSTICAS - AGREGACIONES MONGODB")
    logger.info("=" * 70)
    logger.info("MongoDB hará TODO el trabajo pesado en el servidor")
    logger.info("")

    buildings_coll = db.buildings_by_municipality

    # Pipeline de agregación - MongoDB calcula TODAS las métricas
    pipeline = [
        {
            # Agregar campos calculados
            '$addFields': {
                # Densidad Microsoft (edificaciones por km²)
                'ms_density': {
                    '$cond': [
                        {'$gt': ['$area_km2', 0]},
                        {'$divide': ['$microsoft.count', '$area_km2']},
                        0
                    ]
                },
                # Densidad Google
                'gg_density': {
                    '$cond': [
                        {'$gt': ['$area_km2', 0]},
                        {'$divide': ['$google.count', '$area_km2']},
                        0
                    ]
                },
                # Cobertura Microsoft (% área municipal con techos)
                'ms_coverage': {
                    '$cond': [
                        {'$gt': ['$area_km2', 0]},
                        {
                            '$multiply': [
                                {'$divide': ['$microsoft.total_area_km2', '$area_km2']},
                                100
                            ]
                        },
                        0
                    ]
                },
                # Cobertura Google
                'gg_coverage': {
                    '$cond': [
                        {'$gt': ['$area_km2', 0]},
                        {
                            '$multiply': [
                                {'$divide': ['$google.total_area_km2', '$area_km2']},
                                100
                            ]
                        },
                        0
                    ]
                },
                # Diferencia de conteo
                'diff_count': {
                    '$subtract': ['$google.count', '$microsoft.count']
                },
                # Diferencia porcentual
                'diff_pct': {
                    '$cond': [
                        {'$gt': ['$microsoft.count', 0]},
                        {
                            '$multiply': [
                                {
                                    '$divide': [
                                        {'$subtract': ['$google.count', '$microsoft.count']},
                                        '$microsoft.count'
                                    ]
                                },
                                100
                            ]
                        },
                        0
                    ]
                },
                # Agreement score
                'agreement_score': {
                    '$cond': [
                        {
                            '$and': [
                                {'$gt': ['$microsoft.count', 0]},
                                {'$gt': ['$google.count', 0]}
                            ]
                        },
                        {
                            '$divide': [
                                {'$min': ['$microsoft.count', '$google.count']},
                                {'$max': ['$microsoft.count', '$google.count']}
                            ]
                        },
                        0
                    ]
                }
            }
        },
        {
            # Proyectar solo los campos necesarios
            '$project': {
                '_id': 0,
                # Identificación
                'muni_code': 1,
                'muni_name': 1,
                'dept_name': 1,
                'pdet_region': 1,
                'pdet_subregion': 1,
                'area_municipal_km2': {'$round': ['$area_km2', 2]},

                # Microsoft
                'ms_buildings_count': '$microsoft.count',
                'ms_avg_building_area_m2': {'$round': ['$microsoft.avg_area_m2', 2]},
                'ms_total_roof_area_km2': {'$round': ['$microsoft.total_area_km2', 4]},
                'ms_useful_area_km2': {'$round': ['$microsoft.area_util_km2', 4]},
                'ms_useful_area_ha': {'$round': ['$microsoft.area_util_ha', 2]},
                'ms_density_buildings_km2': {'$round': ['$ms_density', 2]},
                'ms_coverage_pct': {'$round': ['$ms_coverage', 4]},

                # Google
                'gg_buildings_count': '$google.count',
                'gg_avg_building_area_m2': {'$round': ['$google.avg_area_m2', 2]},
                'gg_total_roof_area_km2': {'$round': ['$google.total_area_km2', 4]},
                'gg_useful_area_km2': {'$round': ['$google.area_util_km2', 4]},
                'gg_useful_area_ha': {'$round': ['$google.area_util_ha', 2]},
                'gg_density_buildings_km2': {'$round': ['$gg_density', 2]},
                'gg_coverage_pct': {'$round': ['$gg_coverage', 4]},

                # Comparación
                'diff_count': 1,
                'diff_pct': {'$round': ['$diff_pct', 2]},
                'agreement_score': {'$round': ['$agreement_score', 4]}
            }
        },
        {
            # Ordenar por región y municipio
            '$sort': {'pdet_region': 1, 'muni_name': 1}
        }
    ]

    logger.info("Ejecutando pipeline de agregación en MongoDB...")
    logger.info(f"Stages: {len(pipeline)}")

    # MongoDB hace TODO el trabajo aquí
    results = list(buildings_coll.aggregate(pipeline, allowDiskUse=True))

    logger.info(f"MongoDB procesó {len(results)} municipios")
    logger.info("")

    # Convertir a DataFrame
    df = pd.DataFrame(results)

    # Exportar CSV
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'tables'
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / 'municipalities_stats.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    logger.info(f"CSV exportado: {csv_path}")
    logger.info(f"   Filas: {len(df)}")
    logger.info(f"   Columnas: {len(df.columns)}")
    logger.info("")

    # Resumen estadístico
    logger.info("=" * 70)
    logger.info("RESUMEN ESTADÍSTICO")
    logger.info("=" * 70)
    logger.info(f"Total municipios: {len(df)}")
    logger.info(f"Municipios con datos MS: {(df['ms_buildings_count'] > 0).sum()}")
    logger.info(f"Municipios con datos Google: {(df['gg_buildings_count'] > 0).sum()}")
    logger.info("")
    logger.info(f"Total edificaciones MS: {df['ms_buildings_count'].sum():,}")
    logger.info(f"Total edificaciones Google: {df['gg_buildings_count'].sum():,}")
    logger.info("")
    logger.info(f"Área útil total MS: {df['ms_useful_area_km2'].sum():.2f} km²")
    logger.info(f"Área útil total Google: {df['gg_useful_area_km2'].sum():.2f} km²")
    logger.info("")

    # Top 10 municipios MS
    logger.info("Top 10 Municipios - Microsoft (por edificaciones):")
    top10_ms = df.nlargest(10, 'ms_buildings_count')[['muni_name', 'dept_name', 'ms_buildings_count', 'ms_useful_area_km2']]
    for i, (_, row) in enumerate(top10_ms.iterrows(), 1):
        logger.info(f"  {i:2}. {row['muni_name']:30} ({row['dept_name']:20}): {row['ms_buildings_count']:8,} edif, {row['ms_useful_area_km2']:6.2f} km²")

    logger.info("")
    logger.info("=" * 70)
    logger.info("NOTA: Todas las métricas calculadas por MongoDB en el servidor")
    logger.info("=" * 70)

    return df


def main():
    """Función principal"""
    try:
        db = get_database()
        df = generate_statistics_mongodb(db)
        logger.info("Proceso completado exitosamente")
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
