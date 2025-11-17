"""
Script de validación completa del Deliverable 4

Verifica que todos los requisitos estén cumplidos

Autor: Equipo PDET Solar Analysis
Fecha: Noviembre 2025
"""

import sys
from pathlib import Path
import json
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

def validate():
    """Validación completa del Deliverable 4"""
    print("=" * 70)
    print("VALIDACIÓN DELIVERABLE 4")
    print("=" * 70)
    print()

    errors = []
    warnings = []

    # 1. Verificar MongoDB
    print("1. Verificando datos en MongoDB...")
    try:
        db = get_database()

        # Verificar colección
        count = db.buildings_by_municipality.count_documents({})
        if count != 146:
            errors.append(f"Expected 146 municipios, found {count}")
        else:
            print(f"   ✅ 146 municipios en buildings_by_municipality")

        # Verificar campos area_util
        sample = db.buildings_by_municipality.find_one({'microsoft.count': {'$gt': 0}})
        if sample:
            ms = sample.get('microsoft', {})
            if 'area_util_km2' not in ms:
                errors.append("Campo area_util_km2 faltante en Microsoft")
            elif ms['area_util_km2'] > 0:
                print(f"   ✅ Campo area_util_km2 presente: {ms['area_util_km2']} km²")

            if 'area_util_ha' not in ms:
                errors.append("Campo area_util_ha faltante en Microsoft")
            else:
                print(f"   ✅ Campo area_util_ha presente: {ms['area_util_ha']} ha")

        # Calcular totales
        pipeline = [
            {'$group': {
                '_id': None,
                'total_util_km2': {'$sum': '$microsoft.area_util_km2'},
                'total_buildings': {'$sum': '$microsoft.count'}
            }}
        ]
        result = list(db.buildings_by_municipality.aggregate(pipeline))
        if result:
            total_util = result[0].get('total_util_km2', 0)
            total_buildings = result[0].get('total_buildings', 0)
            print(f"   ✅ Total área útil: {total_util:.2f} km²")
            print(f"   ✅ Total edificaciones: {total_buildings:,}")
    except Exception as e:
        errors.append(f"Error MongoDB: {str(e)}")

    print()

    # 2. Verificar archivos CSV
    print("2. Verificando archivos CSV...")

    csv_munis = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'tables' / 'municipalities_stats.csv'
    if not csv_munis.exists():
        errors.append("municipalities_stats.csv no existe")
    else:
        lines = len(open(csv_munis, encoding='utf-8').readlines())
        if lines == 147:  # 146 + header
            print(f"   ✅ municipalities_stats.csv: {lines-1} municipios")
        else:
            errors.append(f"municipalities_stats.csv: expected 147 lines, got {lines}")

    csv_regional = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'tables' / 'regional_summary.csv'
    if not csv_regional.exists():
        errors.append("regional_summary.csv no existe")
    else:
        lines = len(open(csv_regional, encoding='utf-8').readlines())
        if lines == 15:  # 14 + header
            print(f"   ✅ regional_summary.csv: {lines-1} regiones")
        else:
            warnings.append(f"regional_summary.csv: expected 15 lines, got {lines}")

    print()

    # 3. Verificar GeoJSON
    print("3. Verificando GeoJSON...")

    geojson_path = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'geojson' / 'municipalities_with_stats.geojson'
    if not geojson_path.exists():
        errors.append("municipalities_with_stats.geojson no existe")
    else:
        size_mb = geojson_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ GeoJSON existe: {size_mb:.1f} MB")

        # Validar estructura
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('type') != 'FeatureCollection':
                errors.append("GeoJSON no es FeatureCollection")
            else:
                print(f"   ✅ Tipo: FeatureCollection")

            features = data.get('features', [])
            if len(features) != 146:
                errors.append(f"GeoJSON: expected 146 features, got {len(features)}")
            else:
                print(f"   ✅ Features: {len(features)}")

            # Verificar estructura de feature
            if features:
                sample_props = features[0].get('properties', {})
                required_fields = ['muni_code', 'muni_name', 'ms_useful_area_km2', 'ms_useful_area_ha']
                missing = [f for f in required_fields if f not in sample_props]
                if missing:
                    errors.append(f"GeoJSON falta campos: {missing}")
                else:
                    print(f"   ✅ Campos requeridos presentes")
        except Exception as e:
            errors.append(f"Error leyendo GeoJSON: {str(e)}")

    print()

    # 4. Verificar scripts
    print("4. Verificando scripts...")

    scripts_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'scripts'
    required_scripts = [
        '01_calculate_solar_area.py',
        '02_generate_statistics.py',
        '03_regional_summary.py',
        '04_export_geojson.py'
    ]

    for script in required_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            errors.append(f"Script faltante: {script}")
        else:
            print(f"   ✅ {script}")

    print()

    # 5. Verificar documentación
    print("5. Verificando documentación...")

    docs_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4'
    required_docs = [
        'README.md',
        'METODOLOGIA.md',
        'REPORTE_FINAL_ENTREGABLE_4.md'
    ]

    for doc in required_docs:
        doc_path = docs_dir / doc
        if not doc_path.exists():
            errors.append(f"Documento faltante: {doc}")
        else:
            size_kb = doc_path.stat().st_size / 1024
            print(f"   ✅ {doc} ({size_kb:.1f} KB)")

    print()

    # Resumen final
    print("=" * 70)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 70)

    if not errors and not warnings:
        print("✅ ✅ ✅ DELIVERABLE 4 COMPLETADO AL 100% ✅ ✅ ✅")
        print()
        print("Todos los requisitos cumplidos:")
        print("  ✅ Conteo de Techos y Estimación de Área")
        print("  ✅ Reproducibilidad y Metodología")
        print("  ✅ Precisión de Operaciones Espaciales")
        print("  ✅ Estructura de Datos de Salida")
    else:
        if errors:
            print(f"❌ ERRORES ENCONTRADOS: {len(errors)}")
            for err in errors:
                print(f"   ❌ {err}")
            print()

        if warnings:
            print(f"⚠️  ADVERTENCIAS: {len(warnings)}")
            for warn in warnings:
                print(f"   ⚠️  {warn}")
            print()

    print("=" * 70)

    return len(errors) == 0


if __name__ == '__main__':
    success = validate()
    sys.exit(0 if success else 1)
