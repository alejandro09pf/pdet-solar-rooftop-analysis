"""
Script para calcular área útil para paneles solares

Aplica factor de eficiencia de 0.476 a las áreas totales de techos
para estimar área realmente utilizable para instalación de paneles.

Factor de eficiencia = orientación (0.7) × pendiente (0.8) × obstrucciones (0.85)

Autor: Equipo PDET Solar Analysis
Fecha: Noviembre 2025
Deliverable: 4
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Factor de eficiencia para área útil
EFFICIENCY_FACTOR = 0.476  # 47.6% del área total

def calculate_solar_area(db):
    """
    Calcula área útil para paneles solares basado en área total de techos

    Args:
        db: Conexión a MongoDB
    """
    logger.info("=" * 70)
    logger.info("CÁLCULO DE ÁREA ÚTIL PARA PANELES SOLARES")
    logger.info("=" * 70)
    logger.info(f"Factor de eficiencia: {EFFICIENCY_FACTOR} ({EFFICIENCY_FACTOR*100:.1f}%)")
    logger.info("")

    # Colección de entrada
    buildings_coll = db.buildings_by_municipality

    # Contar documentos
    total_docs = buildings_coll.count_documents({})
    logger.info(f"Total municipios a procesar: {total_docs}")

    # Procesamiento
    updated = 0
    errors = 0

    for doc in buildings_coll.find({}):
        try:
            muni_code = doc.get('muni_code', 'unknown')
            muni_name = doc.get('muni_name', 'Unknown')

            # Procesar Microsoft
            ms_data = doc.get('microsoft', {})
            if 'total_area_m2' in ms_data and ms_data['total_area_m2'] > 0:
                area_total = ms_data['total_area_m2']
                area_util = area_total * EFFICIENCY_FACTOR

                ms_data['area_util_m2'] = round(area_util, 2)
                ms_data['area_util_km2'] = round(area_util / 1_000_000, 4)
                ms_data['area_util_ha'] = round(area_util / 10_000, 2)

            # Procesar Google
            gg_data = doc.get('google', {})
            if 'total_area_m2' in gg_data and gg_data['total_area_m2'] > 0:
                area_total = gg_data['total_area_m2']
                area_util = area_total * EFFICIENCY_FACTOR

                gg_data['area_util_m2'] = round(area_util, 2)
                gg_data['area_util_km2'] = round(area_util / 1_000_000, 4)
                gg_data['area_util_ha'] = round(area_util / 10_000, 2)

            # Actualizar documento
            buildings_coll.update_one(
                {'_id': doc['_id']},
                {
                    '$set': {
                        'microsoft': ms_data,
                        'google': gg_data,
                        'updated_at': datetime.utcnow()
                    }
                }
            )

            updated += 1

            if updated % 20 == 0:
                logger.info(f"Procesados: {updated}/{total_docs}")

        except Exception as e:
            logger.error(f"Error en {muni_name}: {str(e)}")
            errors += 1
            continue

    # Resumen
    logger.info("")
    logger.info("=" * 70)
    logger.info("RESUMEN")
    logger.info("=" * 70)
    logger.info(f"Municipios actualizados: {updated}")
    logger.info(f"Errores: {errors}")

    # Calcular totales
    pipeline = [
        {
            '$group': {
                '_id': None,
                'total_ms_area_util_km2': {'$sum': '$microsoft.area_util_km2'},
                'total_gg_area_util_km2': {'$sum': '$google.area_util_km2'},
                'total_ms_buildings': {'$sum': '$microsoft.count'},
                'total_gg_buildings': {'$sum': '$google.count'}
            }
        }
    ]

    result = list(buildings_coll.aggregate(pipeline))

    if result:
        totals = result[0]
        logger.info("")
        logger.info("Totales calculados:")
        logger.info(f"  Microsoft:")
        logger.info(f"    - Edificaciones: {totals.get('total_ms_buildings', 0):,}")
        logger.info(f"    - Área útil: {totals.get('total_ms_area_util_km2', 0):.2f} km²")
        logger.info(f"  Google:")
        logger.info(f"    - Edificaciones: {totals.get('total_gg_buildings', 0):,}")
        logger.info(f"    - Área útil: {totals.get('total_gg_area_util_km2', 0):.2f} km²")

    logger.info("")
    logger.info("Cálculo completado exitosamente")
    logger.info("=" * 70)


def main():
    """Función principal"""
    try:
        db = get_database()
        calculate_solar_area(db)
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
