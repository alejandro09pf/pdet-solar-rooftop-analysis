"""
Script para realizar join espacial entre edificaciones y municipios PDET

Este script implementa el análisis crítico del Entregable 3:
- Join espacial de edificaciones Microsoft con municipios PDET
- Cálculo de estadísticas por municipio (conteo, áreas)
- Exportación de resultados para análisis

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
Entregable: 3 - PERSONA 4
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import pandas as pd
from pymongo import MongoClient
from shapely.geometry import shape, Point
from tqdm import tqdm
import logging

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpatialJoinAnalyzer:
    """Analizador de join espacial edificaciones-municipios"""

    def __init__(self, database=None):
        """Inicializa el analizador"""
        self.db = database or get_database()
        self.results_dir = PROJECT_ROOT / 'results' / 'deliverable_3'
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def get_municipalities(self):
        """Obtiene todos los municipios PDET"""
        logger.info("Obteniendo municipios PDET...")
        munis = list(self.db.pdet_municipalities.find({}))
        logger.info(f"✅ {len(munis)} municipios PDET encontrados")
        return munis

    def count_buildings_in_municipality(self, muni_geom, dataset='microsoft'):
        """
        Cuenta edificaciones dentro de un municipio usando $geoWithin

        Args:
            muni_geom: Geometría GeoJSON del municipio
            dataset: 'microsoft' o 'google'

        Returns:
            int: Número de edificaciones
        """
        collection_name = f'{dataset}_buildings'

        # Verificar si la colección existe
        if collection_name not in self.db.list_collection_names():
            logger.warning(f"Colección {collection_name} no existe")
            return 0

        collection = self.db[collection_name]

        try:
            # Query espacial usando $geoWithin
            count = collection.count_documents({
                'geometry': {
                    '$geoWithin': {
                        '$geometry': muni_geom
                    }
                }
            })
            return count
        except Exception as e:
            logger.warning(f"Error en query espacial para {dataset}: {str(e)}")
            # Si falla $geoWithin (sin índice), usar bbox aproximado
            return self._count_by_bbox(collection, muni_geom)

    def _count_by_bbox(self, collection, muni_geom):
        """
        Método alternativo usando bounding box cuando no hay índice espacial
        """
        try:
            coords = muni_geom['coordinates'][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]

            bbox_query = {
                'geometry.coordinates.0.0.0': {
                    '$gte': min(lons),
                    '$lte': max(lons)
                },
                'geometry.coordinates.0.0.1': {
                    '$gte': min(lats),
                    '$lte': max(lats)
                }
            }

            return collection.count_documents(bbox_query)
        except Exception as e:
            logger.error(f"Error en bbox query: {str(e)}")
            return 0

    def get_buildings_in_municipality(self, muni_geom, dataset='microsoft', limit=None):
        """
        Obtiene edificaciones dentro de un municipio

        Args:
            muni_geom: Geometría GeoJSON del municipio
            dataset: 'microsoft' o 'google'
            limit: Número máximo de edificaciones a retornar

        Returns:
            list: Lista de edificaciones
        """
        collection_name = f'{dataset}_buildings'

        if collection_name not in self.db.list_collection_names():
            return []

        collection = self.db[collection_name]

        try:
            query = {
                'geometry': {
                    '$geoWithin': {
                        '$geometry': muni_geom
                    }
                }
            }

            cursor = collection.find(query)
            if limit:
                cursor = cursor.limit(limit)

            return list(cursor)
        except Exception as e:
            logger.warning(f"Error obteniendo edificaciones: {str(e)}")
            return []

    def calculate_municipality_stats(self, muni):
        """
        Calcula estadísticas completas para un municipio

        Args:
            muni: Documento de municipio PDET

        Returns:
            dict: Estadísticas del municipio
        """
        muni_code = muni.get('muni_code', muni.get('divipola_code', 'unknown'))
        muni_name = muni.get('muni_name', muni.get('municipio', 'Unknown'))
        dept_name = muni.get('dept_name', muni.get('departamento', 'Unknown'))

        stats = {
            'muni_code': muni_code,
            'muni_name': muni_name,
            'dept_name': dept_name,
            'pdet_region': muni.get('pdet_region', muni.get('region_pdet', 'Unknown')),
            'pdet_subregion': muni.get('pdet_subregion', muni.get('subregion_pdet', 'Unknown')),
            'area_km2': muni.get('area_km2', 0)
        }

        # Contar edificaciones Microsoft
        muni_geom = muni.get('geom', muni.get('geometry'))
        if muni_geom:
            stats['microsoft_buildings_count'] = self.count_buildings_in_municipality(
                muni_geom, 'microsoft'
            )
            stats['google_buildings_count'] = self.count_buildings_in_municipality(
                muni_geom, 'google'
            )
        else:
            stats['microsoft_buildings_count'] = 0
            stats['google_buildings_count'] = 0

        # Calcular área total de techos (muestra)
        if stats['microsoft_buildings_count'] > 0:
            buildings = self.get_buildings_in_municipality(muni_geom, 'microsoft', limit=1000)
            if buildings:
                areas = [b.get('properties', {}).get('area_m2', 0) for b in buildings]
                areas = [a for a in areas if a > 0]
                if areas:
                    avg_area = sum(areas) / len(areas)
                    stats['microsoft_avg_area_m2'] = round(avg_area, 2)
                    # Estimar área total
                    stats['microsoft_total_area_m2'] = round(
                        avg_area * stats['microsoft_buildings_count'], 2
                    )
                    stats['microsoft_total_area_km2'] = round(
                        stats['microsoft_total_area_m2'] / 1_000_000, 4
                    )

        return stats

    def analyze_all_municipalities(self):
        """
        Realiza análisis espacial completo de todos los municipios PDET

        Returns:
            pd.DataFrame: Resultados del análisis
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ANÁLISIS ESPACIAL EDIFICACIONES-MUNICIPIOS PDET")
        logger.info("=" * 60)

        start_time = time.time()

        # Obtener municipios
        municipalities = self.get_municipalities()

        if not municipalities:
            logger.error("❌ No se encontraron municipios PDET")
            return pd.DataFrame()

        # Procesar cada municipio
        results = []
        logger.info(f"\nProcesando {len(municipalities)} municipios...")

        for muni in tqdm(municipalities, desc="Analizando municipios"):
            try:
                stats = self.calculate_municipality_stats(muni)
                results.append(stats)
            except Exception as e:
                muni_name = muni.get('muni_name', muni.get('municipio', 'Unknown'))
                logger.error(f"Error procesando {muni_name}: {str(e)}")
                continue

        # Crear DataFrame
        df = pd.DataFrame(results)

        # Calcular tiempo
        elapsed = time.time() - start_time

        # Mostrar resumen
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DE RESULTADOS")
        logger.info("=" * 60)
        logger.info(f"Municipios procesados: {len(df)}")
        logger.info(f"Edificaciones Microsoft: {df['microsoft_buildings_count'].sum():,}")
        logger.info(f"Edificaciones Google: {df['google_buildings_count'].sum():,}")

        if 'microsoft_total_area_km2' in df.columns:
            total_area = df['microsoft_total_area_km2'].sum()
            logger.info(f"Área total techos (estimada): {total_area:.2f} km²")

        logger.info(f"\nTiempo total: {elapsed:.1f} segundos")

        # Exportar resultados
        self.export_results(df)

        return df

    def export_results(self, df):
        """Exporta resultados a CSV y JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # CSV principal
        csv_path = self.results_dir / 'buildings_by_municipality.csv'
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ CSV exportado: {csv_path}")

        # CSV con timestamp
        csv_timestamped = self.results_dir / f'buildings_by_municipality_{timestamp}.csv'
        df.to_csv(csv_timestamped, index=False)

        # Resumen JSON
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_municipalities': len(df),
            'total_microsoft_buildings': int(df['microsoft_buildings_count'].sum()),
            'total_google_buildings': int(df['google_buildings_count'].sum()),
            'municipalities_with_data': int((df['microsoft_buildings_count'] > 0).sum()),
            'top_10_municipalities': df.nlargest(10, 'microsoft_buildings_count')[
                ['muni_name', 'dept_name', 'microsoft_buildings_count']
            ].to_dict('records')
        }

        json_path = self.results_dir / 'analysis_summary.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Resumen JSON exportado: {json_path}")

        return summary

    def generate_report(self, df):
        """Genera reporte en markdown"""
        report_path = self.results_dir / 'SPATIAL_JOIN_REPORT.md'

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Reporte de Join Espacial Edificaciones-Municipios PDET\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            f.write("## Resumen General\n\n")
            f.write(f"- **Municipios analizados:** {len(df)}\n")
            f.write(f"- **Edificaciones Microsoft:** {df['microsoft_buildings_count'].sum():,}\n")
            f.write(f"- **Edificaciones Google:** {df['google_buildings_count'].sum():,}\n\n")

            f.write("## Top 10 Municipios con Más Edificaciones\n\n")
            top10 = df.nlargest(10, 'microsoft_buildings_count')
            f.write("| Municipio | Departamento | Edificaciones | Región PDET |\n")
            f.write("|-----------|--------------|---------------|-------------|\n")
            for _, row in top10.iterrows():
                f.write(f"| {row['muni_name']} | {row['dept_name']} | "
                       f"{row['microsoft_buildings_count']:,} | {row['pdet_region']} |\n")

            f.write("\n## Distribución por Región PDET\n\n")
            by_region = df.groupby('pdet_region')['microsoft_buildings_count'].sum().sort_values(ascending=False)
            f.write("| Región PDET | Edificaciones |\n")
            f.write("|-------------|---------------|\n")
            for region, count in by_region.items():
                f.write(f"| {region} | {count:,} |\n")

        logger.info(f"✅ Reporte generado: {report_path}")
        return report_path


def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("ANÁLISIS ESPACIAL: EDIFICACIONES × MUNICIPIOS PDET")
    print("=" * 60 + "\n")

    try:
        analyzer = SpatialJoinAnalyzer()
        df = analyzer.analyze_all_municipalities()

        if not df.empty:
            analyzer.generate_report(df)
            print("\n✅ Análisis completado exitosamente")
            print(f"📊 Resultados en: {analyzer.results_dir}")
        else:
            print("\n⚠️ No se generaron resultados")

    except Exception as e:
        logger.error(f"❌ Error en análisis: {str(e)}")
        raise


if __name__ == '__main__':
    main()
