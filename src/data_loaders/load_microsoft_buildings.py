"""
Script para cargar Microsoft Building Footprints a MongoDB

Este script carga las 6+ millones de edificaciones de Microsoft para Colombia
en MongoDB utilizando procesamiento por lotes para máxima eficiencia.

Autor: Equipo PDET Solar Analysis - Alejandro
Fecha: Noviembre 2025
Entregable: 3
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from shapely.geometry import shape
from shapely.ops import transform
import pyproj
from tqdm import tqdm
import logging

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database, load_config, create_spatial_indexes

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'microsoft_buildings_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MicrosoftBuildingsLoader:
    """Cargador optimizado de Microsoft Building Footprints a MongoDB"""

    def __init__(self, batch_size=10000):
        """
        Inicializa el cargador

        Args:
            batch_size (int): Número de documentos a insertar por lote
        """
        self.batch_size = batch_size
        self.data_file = PROJECT_ROOT / 'data' / 'raw' / 'microsoft' / 'Colombia.geojsonl'

        # Verificar que el archivo existe
        if not self.data_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.data_file}")

        # Configurar proyección para cálculo de áreas
        # WGS84 (EPSG:4326) -> Colombia MAGNA-SIRGAS (EPSG:3116)
        self.wgs84 = pyproj.CRS('EPSG:4326')
        self.colombia_proj = pyproj.CRS('EPSG:3116')
        self.project_to_meters = pyproj.Transformer.from_crs(
            self.wgs84, self.colombia_proj, always_xy=True
        ).transform

        # Estadísticas
        self.stats = {
            'total_processed': 0,
            'total_inserted': 0,
            'total_errors': 0,
            'start_time': None,
            'end_time': None,
            'batches_processed': 0
        }

    def calculate_area_m2(self, geom_coords):
        """
        Calcula el área de un polígono en metros cuadrados

        Args:
            geom_coords (list): Coordenadas del polígono en WGS84

        Returns:
            float: Área en metros cuadrados
        """
        try:
            # Crear geometría Shapely
            geom = {
                "type": "Polygon",
                "coordinates": geom_coords
            }
            polygon = shape(geom)

            # Proyectar a sistema de coordenadas métrico
            polygon_projected = transform(self.project_to_meters, polygon)

            # Calcular área
            area_m2 = polygon_projected.area

            return round(area_m2, 2)

        except Exception as e:
            logger.warning(f"Error calculando área: {e}")
            return 0.0

    def transform_to_mongodb_doc(self, line_num, geojson_line):
        """
        Transforma una línea GeoJSON a documento MongoDB

        Args:
            line_num (int): Número de línea (para ID único)
            geojson_line (str): Línea JSON del archivo

        Returns:
            dict: Documento listo para MongoDB
        """
        try:
            # Parsear JSON
            geom_data = json.loads(geojson_line.strip())

            # El formato del archivo es solo geometría:
            # {"type": "Polygon", "coordinates": [[[lon, lat], ...]]}

            coords = geom_data['coordinates']
            geom_type = geom_data['type']

            # Calcular área
            area_m2 = self.calculate_area_m2(coords)

            # Crear documento MongoDB con formato GeoJSON
            doc = {
                'geometry': {
                    'type': geom_type,
                    'coordinates': coords
                },
                'properties': {
                    'area_m2': area_m2,
                    'source_line': line_num  # Para debugging
                },
                'data_source': 'Microsoft',
                'dataset': 'MS Building Footprints 2020-2021',
                'created_at': datetime.utcnow()
            }

            return doc

        except Exception as e:
            logger.error(f"Error transformando línea {line_num}: {e}")
            self.stats['total_errors'] += 1
            return None

    def load_to_mongodb(self, collection_name='microsoft_buildings', drop_existing=False):
        """
        Carga las edificaciones a MongoDB en lotes

        Args:
            collection_name (str): Nombre de la colección
            drop_existing (bool): Si es True, elimina la colección existente

        Returns:
            dict: Estadísticas de la carga
        """
        logger.info("="*80)
        logger.info("CARGA DE MICROSOFT BUILDING FOOTPRINTS A MONGODB")
        logger.info("="*80)

        self.stats['start_time'] = datetime.now()

        # Conectar a MongoDB
        logger.info("Conectando a MongoDB...")
        db = get_database()
        collection = db[collection_name]

        # Drop collection si se solicita
        if drop_existing:
            logger.info(f"Eliminando colección existente: {collection_name}")
            collection.drop()
            collection = db[collection_name]

        # Contar líneas totales para progress bar
        logger.info("Contando edificaciones totales...")
        with open(self.data_file, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)

        logger.info(f"Total de edificaciones a cargar: {total_lines:,}")
        logger.info(f"Tamaño de lote: {self.batch_size:,}")
        logger.info(f"Lotes estimados: {total_lines // self.batch_size + 1:,}")

        # Procesar archivo en lotes
        batch = []
        line_num = 0

        with open(self.data_file, 'r', encoding='utf-8') as f:
            with tqdm(total=total_lines, desc="Cargando edificaciones", unit=" docs") as pbar:
                for line in f:
                    line_num += 1

                    # Transformar a documento MongoDB
                    doc = self.transform_to_mongodb_doc(line_num, line)

                    if doc:
                        batch.append(doc)
                        self.stats['total_processed'] += 1

                    # Insertar lote cuando alcanza el tamaño
                    if len(batch) >= self.batch_size:
                        try:
                            result = collection.insert_many(batch, ordered=False)
                            self.stats['total_inserted'] += len(result.inserted_ids)
                            self.stats['batches_processed'] += 1
                            batch = []

                        except Exception as e:
                            logger.error(f"Error insertando lote {self.stats['batches_processed']}: {e}")
                            self.stats['total_errors'] += len(batch)
                            batch = []

                    pbar.update(1)

                # Insertar último lote si queda algo
                if batch:
                    try:
                        result = collection.insert_many(batch, ordered=False)
                        self.stats['total_inserted'] += len(result.inserted_ids)
                        self.stats['batches_processed'] += 1

                    except Exception as e:
                        logger.error(f"Error insertando último lote: {e}")
                        self.stats['total_errors'] += len(batch)

        self.stats['end_time'] = datetime.now()

        # Crear índices espaciales
        logger.info("\nCreando índices espaciales...")
        try:
            create_spatial_indexes(collection_name, 'geometry', verbose=True)

            # Índice adicional en área
            collection.create_index('properties.area_m2')
            logger.info("✓ Creado índice en properties.area_m2")

            # Índice en data_source
            collection.create_index('data_source')
            logger.info("✓ Creado índice en data_source")

        except Exception as e:
            logger.error(f"Error creando índices: {e}")

        # Mostrar estadísticas finales
        self._print_stats(collection)

        return self.stats

    def _print_stats(self, collection):
        """Imprime estadísticas de la carga"""

        duration = self.stats['end_time'] - self.stats['start_time']
        duration_seconds = duration.total_seconds()

        logger.info("\n" + "="*80)
        logger.info("ESTADÍSTICAS DE CARGA")
        logger.info("="*80)
        logger.info(f"Edificaciones procesadas: {self.stats['total_processed']:,}")
        logger.info(f"Edificaciones insertadas: {self.stats['total_inserted']:,}")
        logger.info(f"Errores: {self.stats['total_errors']:,}")
        logger.info(f"Lotes procesados: {self.stats['batches_processed']:,}")
        logger.info(f"Tamaño de lote: {self.batch_size:,}")
        logger.info(f"\nDuración: {duration}")
        logger.info(f"Velocidad: {self.stats['total_inserted'] / duration_seconds:.0f} docs/segundo")

        # Verificar conteo en MongoDB
        count_in_db = collection.count_documents({})
        logger.info(f"\nDocumentos en MongoDB: {count_in_db:,}")

        # Estadísticas de áreas
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'avg_area': {'$avg': '$properties.area_m2'},
                    'min_area': {'$min': '$properties.area_m2'},
                    'max_area': {'$max': '$properties.area_m2'},
                    'total_area': {'$sum': '$properties.area_m2'}
                }
            }
        ]

        area_stats = list(collection.aggregate(pipeline))
        if area_stats:
            stats = area_stats[0]
            logger.info(f"\nEstadísticas de áreas:")
            logger.info(f"  Área promedio: {stats['avg_area']:.2f} m²")
            logger.info(f"  Área mínima: {stats['min_area']:.2f} m²")
            logger.info(f"  Área máxima: {stats['max_area']:.2f} m²")
            logger.info(f"  Área total: {stats['total_area']/1_000_000:.2f} km²")

        # Muestra
        logger.info(f"\nMuestra de documentos:")
        samples = collection.find().limit(2)
        for i, doc in enumerate(samples, 1):
            logger.info(f"\nDocumento {i}:")
            logger.info(f"  _id: {doc['_id']}")
            logger.info(f"  Tipo geometría: {doc['geometry']['type']}")
            logger.info(f"  Área: {doc['properties']['area_m2']} m²")
            logger.info(f"  Coordenadas (primeras 3): {doc['geometry']['coordinates'][0][:3]}")

        logger.info("\n" + "="*80)
        logger.info("✓ CARGA COMPLETADA EXITOSAMENTE")
        logger.info("="*80 + "\n")


def main():
    """Función principal"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Carga Microsoft Building Footprints a MongoDB"
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10000,
        help='Número de documentos por lote (default: 10000)'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default='microsoft_buildings',
        help='Nombre de la colección MongoDB (default: microsoft_buildings)'
    )
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Eliminar colección existente antes de cargar'
    )

    args = parser.parse_args()

    # Crear directorio de logs si no existe
    logs_dir = PROJECT_ROOT / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Crear y ejecutar cargador
    try:
        loader = MicrosoftBuildingsLoader(batch_size=args.batch_size)
        stats = loader.load_to_mongodb(
            collection_name=args.collection,
            drop_existing=args.drop
        )

        # Guardar estadísticas en archivo JSON
        stats_file = PROJECT_ROOT / 'logs' / 'microsoft_load_stats.json'
        with open(stats_file, 'w') as f:
            stats_copy = stats.copy()
            stats_copy['start_time'] = stats['start_time'].isoformat()
            stats_copy['end_time'] = stats['end_time'].isoformat()
            json.dump(stats_copy, f, indent=2)

        logger.info(f"Estadísticas guardadas en: {stats_file}")

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
