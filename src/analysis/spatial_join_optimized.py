"""
Script OPTIMIZADO para join espacial edificaciones-municipios PDET

Este script usa un enfoque optimizado con bbox pre-filtering para acelerar
el análisis cuando no hay índices espaciales disponibles.

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
Entregable: 3 - PERSONA 4 (Optimizado)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
from shapely.geometry import shape, Point, box
from shapely import wkt
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


class FastSpatialJoin:
    """Join espacial optimizado usando muestra y bbox"""

    def __init__(self, database=None, sample_size=10000):
        """
        Args:
            database: Conexión MongoDB
            sample_size: Tamaño de muestra para análisis rápido
        """
        self.db = database or get_database()
        self.sample_size = sample_size
        self.results_dir = PROJECT_ROOT / 'results' / 'deliverable_3'
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def get_bbox(self, geom):
        """Obtiene bounding box de una geometría GeoJSON"""
        if geom['type'] == 'Polygon':
            coords = geom['coordinates'][0]
        elif geom['type'] == 'MultiPolygon':
            coords = []
            for poly in geom['coordinates']:
                coords.extend(poly[0])
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

    def count_buildings_fast(self, muni, dataset='microsoft'):
        """
        Cuenta edificaciones usando bbox y sampling

        Este método es más rápido que $geoWithin sin índices
        """
        collection_name = f'{dataset}_buildings'

        if collection_name not in self.db.list_collection_names():
            return 0, 0

        collection = self.db[collection_name]

        # Obtener geometría del municipio
        muni_geom = muni.get('geom', muni.get('geometry'))
        if not muni_geom:
            return 0, 0

        # Obtener bbox
        bbox = self.get_bbox(muni_geom)
        if not bbox:
            return 0, 0

        # Query optimizado usando bbox en coordenadas
        # Para acelerar, usamos una aproximación: contamos edificaciones
        # cuyo primer punto del polígono está en el bbox
        try:
            # Pipeline de agregación más rápido
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
                    '$count': 'total'
                }
            ]

            result = list(collection.aggregate(pipeline))
            bbox_count = result[0]['total'] if result else 0

            # Si hay edificaciones en bbox, tomar muestra para estadísticas
            avg_area = 0
            if bbox_count > 0:
                sample = list(collection.find(
                    {
                        'geometry.coordinates.0.0.0': {
                            '$gte': bbox['min_lon'],
                            '$lte': bbox['max_lon']
                        },
                        'geometry.coordinates.0.0.1': {
                            '$gte': bbox['min_lat'],
                            '$lte': bbox['max_lat']
                        }
                    },
                    {'properties.area_m2': 1}
                ).limit(min(1000, bbox_count)))

                areas = [
                    b.get('properties', {}).get('area_m2', 0)
                    for b in sample if b.get('properties', {}).get('area_m2', 0) > 0
                ]

                if areas:
                    avg_area = sum(areas) / len(areas)

            return bbox_count, avg_area

        except Exception as e:
            logger.warning(f"Error en query optimizado: {str(e)}")
            return 0, 0

    def analyze_all_fast(self):
        """Análisis rápido de todos los municipios"""
        logger.info("=" * 70)
        logger.info("ANÁLISIS ESPACIAL OPTIMIZADO: EDIFICACIONES × MUNICIPIOS PDET")
        logger.info("=" * 70)

        start_time = time.time()

        # Obtener municipios
        municipalities = list(self.db.pdet_municipalities.find({}))
        logger.info(f"✅ {len(municipalities)} municipios PDET encontrados")

        # Procesar
        results = []
        logger.info(f"\nProcesando con método optimizado (bbox + sampling)...")

        for muni in tqdm(municipalities, desc="Analizando"):
            try:
                muni_code = muni.get('muni_code', muni.get('divipola_code', 'unknown'))
                muni_name = muni.get('muni_name', muni.get('municipio', 'Unknown'))
                dept_name = muni.get('dept_name', muni.get('departamento', 'Unknown'))

                # Contar edificaciones
                ms_count, ms_avg_area = self.count_buildings_fast(muni, 'microsoft')
                gg_count, gg_avg_area = self.count_buildings_fast(muni, 'google')

                stats = {
                    'muni_code': muni_code,
                    'muni_name': muni_name,
                    'dept_name': dept_name,
                    'pdet_region': muni.get('pdet_region', muni.get('region_pdet', 'Unknown')),
                    'pdet_subregion': muni.get('pdet_subregion', muni.get('subregion_pdet', 'Unknown')),
                    'area_km2': muni.get('area_km2', 0),
                    'microsoft_buildings_count': ms_count,
                    'microsoft_avg_area_m2': round(ms_avg_area, 2) if ms_avg_area > 0 else 0,
                    'google_buildings_count': gg_count,
                    'google_avg_area_m2': round(gg_avg_area, 2) if gg_avg_area > 0 else 0
                }

                # Calcular totales estimados
                if ms_count > 0 and ms_avg_area > 0:
                    stats['microsoft_total_area_m2'] = round(ms_avg_area * ms_count, 2)
                    stats['microsoft_total_area_km2'] = round(stats['microsoft_total_area_m2'] / 1_000_000, 4)

                if gg_count > 0 and gg_avg_area > 0:
                    stats['google_total_area_m2'] = round(gg_avg_area * gg_count, 2)
                    stats['google_total_area_km2'] = round(stats['google_total_area_m2'] / 1_000_000, 4)

                results.append(stats)

            except Exception as e:
                logger.error(f"Error procesando {muni_name}: {str(e)}")
                continue

        # Crear DataFrame
        df = pd.DataFrame(results)

        # Tiempo
        elapsed = time.time() - start_time

        # Resumen
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE RESULTADOS")
        logger.info("=" * 70)
        logger.info(f"Municipios procesados: {len(df)}")
        logger.info(f"Edificaciones Microsoft: {df['microsoft_buildings_count'].sum():,}")
        logger.info(f"Edificaciones Google: {df['google_buildings_count'].sum():,}")

        if 'microsoft_total_area_km2' in df.columns:
            total_ms = df['microsoft_total_area_km2'].dropna().sum()
            logger.info(f"Área total techos Microsoft (estimada): {total_ms:.2f} km²")

        if 'google_total_area_km2' in df.columns:
            total_gg = df['google_total_area_km2'].dropna().sum()
            logger.info(f"Área total techos Google (estimada): {total_gg:.2f} km²")

        logger.info(f"\nTiempo total: {elapsed:.1f} segundos ({elapsed/60:.1f} minutos)")
        logger.info(f"Velocidad: {len(df)/elapsed:.2f} municipios/seg")

        # Exportar
        self.export_results(df)
        self.generate_report(df)

        return df

    def export_results(self, df):
        """Exporta resultados"""
        # CSV principal
        csv_path = self.results_dir / 'buildings_by_municipality.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"✅ CSV exportado: {csv_path}")

        # Resumen JSON
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_municipalities': len(df),
            'total_microsoft_buildings': int(df['microsoft_buildings_count'].sum()),
            'total_google_buildings': int(df['google_buildings_count'].sum()),
            'municipalities_with_microsoft_data': int((df['microsoft_buildings_count'] > 0).sum()),
            'municipalities_with_google_data': int((df['google_buildings_count'] > 0).sum()),
            'top_10_municipalities_microsoft': df.nlargest(10, 'microsoft_buildings_count')[
                ['muni_name', 'dept_name', 'microsoft_buildings_count']
            ].to_dict('records'),
            'by_region': df.groupby('pdet_region')['microsoft_buildings_count'].sum().to_dict()
        }

        json_path = self.results_dir / 'analysis_summary.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Resumen JSON: {json_path}")

    def generate_report(self, df):
        """Genera reporte markdown"""
        report_path = self.results_dir / 'SPATIAL_JOIN_REPORT.md'

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Reporte de Join Espacial Edificaciones-Municipios PDET\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Método:** Optimizado (bbox + sampling)\n\n")
            f.write("---\n\n")

            # Resumen
            f.write("## Resumen General\n\n")
            f.write(f"- **Municipios analizados:** {len(df)}\n")
            f.write(f"- **Edificaciones Microsoft:** {df['microsoft_buildings_count'].sum():,}\n")
            f.write(f"- **Edificaciones Google:** {df['google_buildings_count'].sum():,}\n")
            f.write(f"- **Municipios con datos MS:** {(df['microsoft_buildings_count'] > 0).sum()}\n")
            f.write(f"- **Municipios con datos Google:** {(df['google_buildings_count'] > 0).sum()}\n\n")

            # Top 10
            f.write("## Top 10 Municipios - Microsoft Buildings\n\n")
            top10 = df.nlargest(10, 'microsoft_buildings_count')
            f.write("| # | Municipio | Departamento | Edificaciones | Área Total (km²) |\n")
            f.write("|---|-----------|--------------|---------------|------------------|\n")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                area = row.get('microsoft_total_area_km2', 0)
                f.write(f"| {i} | {row['muni_name']} | {row['dept_name']} | "
                       f"{row['microsoft_buildings_count']:,} | {area:.2f} |\n")

            # Por región
            f.write("\n## Distribución por Región PDET\n\n")
            by_region = df.groupby('pdet_region').agg({
                'microsoft_buildings_count': 'sum',
                'muni_name': 'count'
            }).sort_values('microsoft_buildings_count', ascending=False)
            by_region.columns = ['Edificaciones', 'Municipios']

            f.write("| Región PDET | Municipios | Edificaciones |\n")
            f.write("|-------------|------------|---------------|\n")
            for region, row in by_region.iterrows():
                f.write(f"| {region} | {int(row['Municipios'])} | {int(row['Edificaciones']):,} |\n")

            # Notas
            f.write("\n## Notas Metodológicas\n\n")
            f.write("- **Método:** Bbox filtering + sampling para velocidad\n")
            f.write("- **Limitación:** Sin índices espaciales, se usa aproximación por bbox\n")
            f.write("- **Área:** Calculada por promedio de muestra × conteo total\n")
            f.write("- **Google Buildings:** No disponible en esta base de datos\n")

        logger.info(f"✅ Reporte: {report_path}")


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("ANÁLISIS ESPACIAL OPTIMIZADO")
    print("=" * 70 + "\n")

    try:
        analyzer = FastSpatialJoin()
        df = analyzer.analyze_all_fast()

        if not df.empty:
            print("\n✅ Análisis completado exitosamente")
            print(f"📊 Resultados en: {analyzer.results_dir}")
        else:
            print("\n⚠️ No se generaron resultados")

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
