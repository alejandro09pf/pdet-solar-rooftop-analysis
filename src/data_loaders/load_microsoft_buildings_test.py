"""
Script de PRUEBA para cargar Microsoft Building Footprints a MongoDB

Este script carga solo las primeras N edificaciones para verificar que todo funciona.

Autor: Equipo PDET Solar Analysis - Alejandro
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loaders.load_microsoft_buildings import MicrosoftBuildingsLoader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_sample(num_lines=1000, batch_size=100):
    """Carga solo las primeras N líneas como prueba"""

    from src.database.connection import get_database
    from datetime import datetime
    import json

    logger.info(f"MODO DE PRUEBA: Cargando solo las primeras {num_lines} edificaciones")

    db = get_database()
    collection = db['microsoft_buildings_test']

    # Drop collection de prueba
    collection.drop()
    logger.info("Colección de prueba eliminada")

    # Crear loader
    loader = MicrosoftBuildingsLoader(batch_size=batch_size)

    # Procesar solo las primeras N líneas
    batch = []
    line_num = 0

    with open(loader.data_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line_num >= num_lines:
                break

            line_num += 1
            doc = loader.transform_to_mongodb_doc(line_num, line)

            if doc:
                batch.append(doc)

            if len(batch) >= batch_size:
                collection.insert_many(batch, ordered=False)
                logger.info(f"  Insertado lote de {len(batch)} documentos")
                batch = []

        # Último lote
        if batch:
            collection.insert_many(batch, ordered=False)
            logger.info(f"  Insertado último lote de {len(batch)} documentos")

    # Crear índices
    logger.info("Creando índices...")
    collection.create_index([('geometry', '2dsphere')])
    collection.create_index('properties.area_m2')
    logger.info("Índices creados")

    # Estadísticas
    count = collection.count_documents({})
    logger.info(f"\n✓ Total documentos insertados: {count}")

    # Muestra
    sample = collection.find_one()
    logger.info(f"\nMuestra de documento:")
    logger.info(f"  Tipo geometría: {sample['geometry']['type']}")
    logger.info(f"  Área: {sample['properties']['area_m2']} m²")
    logger.info(f"  Data source: {sample['data_source']}")

    logger.info(f"\n✓ PRUEBA COMPLETADA")
    logger.info(f"Colección de prueba: microsoft_buildings_test")
    logger.info(f"Para la carga completa, ejecuta: py src/data_loaders/load_microsoft_buildings.py")


if __name__ == "__main__":
    load_sample(num_lines=1000, batch_size=100)
