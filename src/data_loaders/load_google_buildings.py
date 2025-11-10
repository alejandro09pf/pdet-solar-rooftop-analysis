"""
Script para cargar Google Open Buildings a MongoDB

Este script carga las edificaciones de Google Open Buildings para Colombia
en MongoDB utilizando procesamiento por lotes para máxima eficiencia.

Autor: Equipo PDET Solar Analysis
Fecha: Noviembre 2025
Entregable: 3
"""

import os
import sys
import gzip
import csv
import json
import time
from pathlib import Path
from datetime import datetime
from shapely import wkt
from shapely.geometry import shape
from shapely.ops import transform
import pyproj
from tqdm import tqdm
import logging

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database, load_config, create_spatial_indexes

# Crear directorio de logs si no existe
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'google_buildings_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GoogleBuildingsLoader:
    """Cargador optimizado de Google Open Buildings a MongoDB"""

    def __init__(self, batch_size=10000):
        """
        Inicializa el cargador

        Args:
            batch_size (int): Número de documentos a insertar por lote
        """
        self.batch_size = batch_size
        self.data_file = PROJECT_ROOT / 'data' / 'raw' / 'google' / 'google_buildings' / 'open_buildings_v3_polygons_ne_110m_COL.csv.gz'

        # Verificar que el archivo existe
        if not self.data_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.data_file}")

        # Configurar proyección para cálculo de áreas (opcional, Google ya da área)
        # WGS84 (EPSG:4326) -> Colombia MAGNA-SIRGAS (EPSG:3116)
        self.wgs84 = pyproj.CRS('EPSG:4326')
        self.colombia_proj = pyproj.CRS('EPSG:3116')

        # Estadísticas
        self.stats = {
            'total_processed': 0,
            'total_inserted': 0,
            'total_errors': 0,
            'total_skipped_low_confidence': 0,
            'start_time': None,
            'end_time': None,
            'batches_processed': 0,
            'confidence_distribution': {
                '0.65-0.70': 0,
                '0.70-0.80': 0,
                '0.80-0.90': 0,
                '0.90-1.00': 0
            }
        }

    def wkt_to_geojson(self, wkt_string):
        """
        Convierte geometría WKT a formato GeoJSON

        Args:
            wkt_string (str): Geometría en formato WKT

        Returns:
            dict: Geometría en formato GeoJSON
        """
        try:
            # Parsear WKT con Shapely
            geom = wkt.loads(wkt_string)
            
            # Convertir a GeoJSON (diccionario)
            geojson = {
                'type': geom.geom_type,
                'coordinates': list(geom.coords) if geom.geom_type == 'Point' else self._extract_coords(geom)
            }
            
            return geojson

        except Exception as e:
            logger.warning(f"Error convirtiendo WKT a GeoJSON: {e}")
            return None

    def _extract_coords(self, geom):
        """Extrae coordenadas de geometría Shapely"""
        if geom.geom_type == 'Polygon':
            exterior = list(geom.exterior.coords)
            interiors = [list(interior.coords) for interior in geom.interiors]
            return [exterior] + interiors if interiors else [exterior]
        elif geom.geom_type == 'MultiPolygon':
            return [self._extract_coords(poly) for poly in geom.geoms]
        return list(geom.coords)

    def transform_to_mongodb_doc(self, row_num, row):
        """
        Transforma una fila CSV a documento MongoDB

        Args:
            row_num (int): Número de fila (para ID único)
            row (dict): Fila del CSV como diccionario

        Returns:
            dict: Documento listo para MongoDB
        """
        try:
            # Extraer campos del CSV
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            area_in_meters = float(row['area_in_meters'])
            confidence = float(row['confidence'])
            geometry_wkt = row['geometry']
            full_plus_code = row['full_plus_code']

            # Convertir WKT a GeoJSON
            geometry_geojson = self.wkt_to_geojson(geometry_wkt)

            if not geometry_geojson:
                self.stats['total_errors'] += 1
                return None

            # Actualizar distribución de confianza
            if confidence < 0.70:
                self.stats['confidence_distribution']['0.65-0.70'] += 1
            elif confidence < 0.80:
                self.stats['confidence_distribution']['0.70-0.80'] += 1
            elif confidence < 0.90:
                self.stats['confidence_distribution']['0.80-0.90'] += 1
            else:
                self.stats['confidence_distribution']['0.90-1.00'] += 1

            # Crear documento MongoDB con formato GeoJSON
            doc = {
                'geometry': geometry_geojson,
                'properties': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'area_in_meters': area_in_meters,
                    'confidence': confidence,
                    'full_plus_code': full_plus_code,
                    'source_row': row_num  # Para debugging
                },
                'data_source': 'Google',
                'dataset': 'Google Open Buildings v3',
                'created_at': datetime.utcnow()
            }

            return doc

        except Exception as e:
            logger.error(f"Error transformando fila {row_num}: {e}")
            self.stats['total_errors'] += 1
            return None

    def count_rows_in_gzip_csv(self):
        """Cuenta el número de filas en el archivo CSV.gz"""
        try:
            logger.info("Contando edificaciones totales (esto puede tardar unos minutos)...")
            count = 0
            with gzip.open(self.data_file, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for _ in reader:
                    count += 1
            return count
        except Exception as e:
            logger.warning(f"No se pudo contar filas: {e}. Usando estimación.")
            # Estimación basada en tamaño del archivo (1.6 GB ≈ 2-3M buildings)
            return 2500000  # Estimación conservadora

    def load_to_mongodb(self, collection_name='google_buildings', drop_existing=False, min_confidence=0.65):
        """
        Carga las edificaciones a MongoDB en lotes

        Args:
            collection_name (str): Nombre de la colección
            drop_existing (bool): Si es True, elimina la colección existente
            min_confidence (float): Confianza mínima para incluir edificación (0.65-1.0)

        Returns:
            dict: Estadísticas de la carga
        """
        logger.info("="*80)
        logger.info("CARGA DE GOOGLE OPEN BUILDINGS A MONGODB")
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

        # Contar filas totales
        total_rows = self.count_rows_in_gzip_csv()

        logger.info(f"Edificaciones estimadas: {total_rows:,}")
        logger.info(f"Confianza mínima: {min_confidence}")
        logger.info(f"Tamaño de lote: {self.batch_size:,}")
        logger.info(f"Lotes estimados: {total_rows // self.batch_size + 1:,}")

        # Procesar archivo en lotes
        batch = []
        row_num = 0

        with gzip.open(self.data_file, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with tqdm(total=total_rows, desc="Cargando edificaciones", unit=" docs") as pbar:
                for row in reader:
                    row_num += 1

                    # Filtrar por confianza
                    confidence = float(row['confidence'])
                    if confidence < min_confidence:
                        self.stats['total_skipped_low_confidence'] += 1
                        pbar.update(1)
                        continue

                    # Transformar a documento MongoDB
                    doc = self.transform_to_mongodb_doc(row_num, row)

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

            # Índices adicionales específicos de Google
            collection.create_index('properties.confidence')
            logger.info("✓ Creado índice en properties.confidence")

            collection.create_index('properties.area_in_meters')
            logger.info("✓ Creado índice en properties.area_in_meters")

            collection.create_index('properties.full_plus_code')
            logger.info("✓ Creado índice en properties.full_plus_code")

            collection.create_index('data_source')
            logger.info("✓ Creado índice en data_source")

            # Índice compuesto para queries comunes
            collection.create_index([
                ('properties.confidence', -1),
                ('properties.area_in_meters', -1)
            ])
            logger.info("✓ Creado índice compuesto en confidence + area")

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
        logger.info(f"Omitidas (baja confianza): {self.stats['total_skipped_low_confidence']:,}")
        logger.info(f"Errores: {self.stats['total_errors']:,}")
        logger.info(f"Lotes procesados: {self.stats['batches_processed']:,}")
        logger.info(f"Tamaño de lote: {self.batch_size:,}")
        
        logger.info(f"\nDistribución de confianza:")
        for range_name, count in self.stats['confidence_distribution'].items():
            percentage = (count / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
            logger.info(f"  {range_name}: {count:,} ({percentage:.1f}%)")

        logger.info(f"\nDuración: {duration}")
        if duration_seconds > 0:
            logger.info(f"Velocidad: {self.stats['total_inserted'] / duration_seconds:.0f} docs/segundo")

        # Verificar conteo en MongoDB
        count_in_db = collection.count_documents({})
        logger.info(f"\nDocumentos en MongoDB: {count_in_db:,}")

        # Estadísticas de áreas y confianza
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'avg_area': {'$avg': '$properties.area_in_meters'},
                    'min_area': {'$min': '$properties.area_in_meters'},
                    'max_area': {'$max': '$properties.area_in_meters'},
                    'total_area': {'$sum': '$properties.area_in_meters'},
                    'avg_confidence': {'$avg': '$properties.confidence'},
                    'min_confidence': {'$min': '$properties.confidence'},
                    'max_confidence': {'$max': '$properties.confidence'}
                }
            }
        ]

        stats = list(collection.aggregate(pipeline))
        if stats:
            s = stats[0]
            logger.info(f"\nEstadísticas de áreas:")
            logger.info(f"  Área promedio: {s['avg_area']:.2f} m²")
            logger.info(f"  Área mínima: {s['min_area']:.2f} m²")
            logger.info(f"  Área máxima: {s['max_area']:.2f} m²")
            logger.info(f"  Área total: {s['total_area']/1_000_000:.2f} km²")
            
            logger.info(f"\nEstadísticas de confianza:")
            logger.info(f"  Confianza promedio: {s['avg_confidence']:.3f}")
            logger.info(f"  Confianza mínima: {s['min_confidence']:.3f}")
            logger.info(f"  Confianza máxima: {s['max_confidence']:.3f}")

        # Muestra
        logger.info(f"\nMuestra de documentos:")
        samples = collection.find().limit(2)
        for i, doc in enumerate(samples, 1):
            logger.info(f"\nDocumento {i}:")
            logger.info(f"  _id: {doc['_id']}")
            logger.info(f"  Tipo geometría: {doc['geometry']['type']}")
            logger.info(f"  Área: {doc['properties']['area_in_meters']:.2f} m²")
            logger.info(f"  Confianza: {doc['properties']['confidence']:.3f}")
            logger.info(f"  Plus Code: {doc['properties']['full_plus_code']}")
            logger.info(f"  Ubicación: ({doc['properties']['latitude']:.6f}, {doc['properties']['longitude']:.6f})")

        logger.info("\n" + "="*80)
        logger.info("✓ CARGA COMPLETADA EXITOSAMENTE")
        logger.info("="*80 + "\n")


def main():
    """Función principal"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Carga Google Open Buildings a MongoDB"
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
        default='google_buildings',
        help='Nombre de la colección MongoDB (default: google_buildings)'
    )
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Eliminar colección existente antes de cargar'
    )
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0.65,
        help='Confianza mínima para incluir edificación (default: 0.65)'
    )

    args = parser.parse_args()

    # Validar confianza
    if not 0.65 <= args.min_confidence <= 1.0:
        logger.error("La confianza mínima debe estar entre 0.65 y 1.0")
        sys.exit(1)

    # Crear directorio de logs si no existe
    logs_dir = PROJECT_ROOT / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Crear y ejecutar cargador
    try:
        loader = GoogleBuildingsLoader(batch_size=args.batch_size)
        stats = loader.load_to_mongodb(
            collection_name=args.collection,
            drop_existing=args.drop,
            min_confidence=args.min_confidence
        )

        # Guardar estadísticas en archivo JSON
        stats_file = PROJECT_ROOT / 'logs' / 'google_load_stats.json'
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