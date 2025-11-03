import sys
import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping
from shapely.validation import make_valid
from datetime import datetime
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.database.connection import get_database, load_config, test_connection, create_spatial_indexes


def step1_verify_connection():
    """Verificar conexión a MongoDB"""
    print("="*60)
    print("Verificando conexión a MongoDB")
    print("="*60)

    success = test_connection()

    if success:
        print("\n✓ Conexión exitosa! Puedes continuar con el siguiente paso.")
    else:
        print("\n✗ Error de conexión. Verifica que MongoDB esté ejecutándose.")
        print("\nPara iniciar MongoDB:")
        print("  Windows: Busca 'MongoDB' en servicios o ejecuta 'mongod'")
        print("  Linux/Mac: sudo systemctl start mongod")

    return success


def step2_process_shapefile(shapefile_path):
    """Procesar shapefile y filtrar municipios PDET"""
    print("="*60)
    print("Procesando shapefile y filtrando municipios PDET")
    print("="*60)

    pdet_list_path = PROJECT_ROOT / 'data' / 'processed' / 'pdet_municipalities_list.csv'
    print(f"\nCargando lista de municipios PDET...")
    pdet_df = pd.read_csv(pdet_list_path)
    pdet_codes = set(pdet_df['divipola_code'].astype(str))
    print(f"✓ {len(pdet_codes)} municipios PDET en la lista")

    print(f"\nCargando shapefile: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    print(f"✓ Cargados {len(gdf)} municipios totales")
    print(f"  Columnas: {gdf.columns.tolist()}")
    print(f"  CRS: {gdf.crs}")

    possible_code_cols = ['MPIO_CDPMP', 'COD_MPIO', 'DIVIPOLA', 'MPIO_CODIGO', 'CODIGO', 'MPIO_CCNCT', 'mpio_cdpmp']
    code_col = None

    for col in possible_code_cols:
        if col in gdf.columns:
            code_col = col
            break

    if code_col is None:
        print("\n✗ No se encontró columna de código DIVIPOLA")
        print(f"Columnas disponibles: {gdf.columns.tolist()}")
        return None

    print(f"\n✓ Usando columna de código: {code_col}")

    gdf[code_col] = gdf[code_col].astype(str).str.zfill(5)

    print(f"\nFiltrando municipios PDET...")
    gdf_pdet = gdf[gdf[code_col].isin(pdet_codes)].copy()
    print(f"✓ Encontrados {len(gdf_pdet)} municipios PDET en el shapefile")

    if len(gdf_pdet) < len(pdet_codes):
        missing = len(pdet_codes) - len(gdf_pdet)
        print(f"⚠ Advertencia: Faltan {missing} municipios")

    print(f"\nValidando geometrías...")
    invalid = ~gdf_pdet.geometry.is_valid
    if invalid.sum() > 0:
        print(f"  Reparando {invalid.sum()} geometrías inválidas...")
        gdf_pdet.loc[invalid, 'geometry'] = gdf_pdet.loc[invalid, 'geometry'].apply(make_valid)
    print("✓ Todas las geometrías son válidas")

    if gdf_pdet.crs != 'EPSG:4326':
        print(f"\nConvirtiendo de {gdf_pdet.crs} a EPSG:4326...")
        gdf_pdet = gdf_pdet.to_crs('EPSG:4326')
        print("✓ Convertido a WGS84 (EPSG:4326)")

    print(f"\nCalculando áreas...")
    gdf_projected = gdf_pdet.to_crs('EPSG:3116')
    gdf_pdet['area_km2'] = gdf_projected.geometry.area / 1_000_000
    print(f"✓ Áreas calculadas")
    print(f"  Área total: {gdf_pdet['area_km2'].sum():.2f} km²")
    print(f"  Área promedio: {gdf_pdet['area_km2'].mean():.2f} km²")

    print(f"\nPreparando documentos para MongoDB...")
    documents = []

    for idx, row in gdf_pdet.iterrows():
        muni_code = row[code_col]

        pdet_info = pdet_df[pdet_df['divipola_code'].astype(str) == muni_code]

        if len(pdet_info) > 0:
            pdet_info = pdet_info.iloc[0]
            dept_name = pdet_info['departamento']
            muni_name = pdet_info['municipio']
            pdet_region = pdet_info['region_pdet']
            pdet_subregion = pdet_info['subregion_pdet']
        else:
            dept_name = row.get('DPTO_CNMBR', row.get('DEPARTAMENTO', 'Desconocido'))
            muni_name = row.get('MPIO_CNMBR', row.get('MUNICIPIO', 'Desconocido'))
            pdet_region = 'Desconocido'
            pdet_subregion = 'Desconocido'

        dept_code = muni_code[:2]

        geom_json = mapping(row.geometry)

        doc = {
            'dept_code': dept_code,
            'muni_code': muni_code,
            'dept_name': dept_name,
            'muni_name': muni_name,
            'pdet_region': pdet_region,
            'pdet_subregion': pdet_subregion,
            'geom': geom_json,
            'area_km2': float(row['area_km2']),
            'data_source': 'DANE MGN',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        documents.append(doc)

    print(f"✓ Preparados {len(documents)} documentos")

    output_path = PROJECT_ROOT / 'data' / 'processed' / 'pdet_municipalities_ready.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n✓ Documentos guardados en: {output_path}")

    return documents


def step3_load_to_mongodb():
    """Cargar documentos a MongoDB"""
    print("="*60)
    print("Cargando documentos a MongoDB")
    print("="*60)

    input_path = PROJECT_ROOT / 'data' / 'processed' / 'pdet_municipalities_ready.json'

    if not input_path.exists():
        print(f"\n✗ Error: Archivo no encontrado: {input_path}")
        print("Primero ejecuta el paso 2 para procesar los datos")
        return False

    print(f"\nCargando documentos desde: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    print(f"✓ Cargados {len(documents)} documentos")

    config = load_config()
    env = os.getenv('ENVIRONMENT', 'development')
    db = get_database()
    collection_name = config[env]['collections']['municipalities']
    collection = db[collection_name]

    existing_count = collection.count_documents({})
    if existing_count > 0:
        print(f"\n⚠ La colección '{collection_name}' ya contiene {existing_count} documentos")
        response = input("¿Deseas eliminar los datos existentes y recargar? (s/n): ")
        if response.lower() == 's':
            collection.delete_many({})
            print("✓ Datos existentes eliminados")
        else:
            print("Operación cancelada")
            return False

    print(f"\nInsertando documentos en colección '{collection_name}'...")
    try:
        result = collection.insert_many(documents, ordered=False)
        print(f"✓ Insertados {len(result.inserted_ids)} documentos")
    except Exception as e:
        print(f"✗ Error durante la inserción: {e}")
        return False

    print(f"\nCreando índices...")

    print("  - Índice espacial 2dsphere en campo 'geom'...")
    create_spatial_indexes(collection_name, 'geom', config=config, verbose=False)
    print("    ✓ Creado")

    print("  - Índice único en 'muni_code'...")
    collection.create_index('muni_code', unique=True)
    print("    ✓ Creado")

    print("  - Índice en 'dept_code'...")
    collection.create_index('dept_code')
    print("    ✓ Creado")

    print("  - Índice en 'pdet_region'...")
    collection.create_index('pdet_region')
    print("    ✓ Creado")

    print("  - Índice en 'pdet_subregion'...")
    collection.create_index('pdet_subregion')
    print("    ✓ Creado")

    print("\n✓ Todos los índices creados correctamente")

    print(f"\n✓ Carga completada exitosamente!")

    return True


def step4_validate():
    """Validar datos cargados"""
    print("="*60)
    print("Validando datos cargados")
    print("="*60)

    config = load_config()
    env = os.getenv('ENVIRONMENT', 'development')
    db = get_database()
    collection_name = config[env]['collections']['municipalities']
    collection = db[collection_name]

    total_count = collection.count_documents({})
    print(f"\nTotal de documentos: {total_count}")
    print(f"Esperado: 170 municipios PDET")

    if total_count == 170:
        print("✓ Conteo correcto!")
    else:
        print(f"⚠ Advertencia: Se esperaban 170, se encontraron {total_count}")

    print(f"\nÍndices en la colección:")
    indexes = collection.list_indexes()
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['key']}")

    print(f"\nMunicipios por región PDET:")
    pipeline = [
        {'$group': {
            '_id': '$pdet_region',
            'count': {'$sum': 1},
            'total_area_km2': {'$sum': '$area_km2'}
        }},
        {'$sort': {'count': -1}}
    ]

    for doc in collection.aggregate(pipeline):
        print(f"  - {doc['_id']}: {doc['count']} municipios, {doc['total_area_km2']:.2f} km²")

    print(f"\nEstadísticas de área:")
    stats = collection.aggregate([
        {'$group': {
            '_id': None,
            'total_area': {'$sum': '$area_km2'},
            'avg_area': {'$avg': '$area_km2'},
            'min_area': {'$min': '$area_km2'},
            'max_area': {'$max': '$area_km2'}
        }}
    ])

    for doc in stats:
        print(f"  Área total: {doc['total_area']:.2f} km²")
        print(f"  Área promedio: {doc['avg_area']:.2f} km²")
        print(f"  Área mínima: {doc['min_area']:.2f} km²")
        print(f"  Área máxima: {doc['max_area']:.2f} km²")

    print(f"\nMuestra de 3 documentos:")
    for i, doc in enumerate(collection.find().limit(3), 1):
        print(f"\n  Documento {i}:")
        print(f"    Código: {doc['muni_code']}")
        print(f"    Municipio: {doc['muni_name']}, {doc['dept_name']}")
        print(f"    Región PDET: {doc['pdet_region']}")
        print(f"    Subregión: {doc['pdet_subregion']}")
        print(f"    Área: {doc['area_km2']:.2f} km²")
        print(f"    Tipo geometría: {doc['geom']['type']}")

    print(f"\nPrueba de consulta espacial (primer municipio):")
    sample = collection.find_one({})
    if sample and sample.get('geom', {}).get('type') == 'Point':
        try:
            nearby = collection.find({
                'geom': {
                    '$near': {
                        '$geometry': sample['geom'],
                        '$maxDistance': 100000 
                    }
                }
            }).limit(5)
            print(f"  Municipios cercanos a {sample['muni_name']}:")
            for doc in nearby:
                print(f"    - {doc['muni_name']}, {doc['dept_name']}")
        except Exception as e:
            print(f"  (No se pudo ejecutar consulta espacial: {e})")
    else:
        print("  (Consulta espacial omitida: geometría no es tipo Point)")

    print("\n" + "="*60)
    print("✓ Validación completada!")
    print("="*60)
    print("\nLos datos están listos para usar.")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Cargar municipios PDET a MongoDB - Paso a Paso'
    )
    parser.add_argument(
        '--step',
        type=int,
        required=True,
        choices=[1, 2, 3, 4],
        help='Paso a ejecutar (1: verificar, 2: procesar, 3: cargar, 4: validar)'
    )
    parser.add_argument(
        '--shapefile',
        type=str,
        help='Ruta al shapefile de municipios DANE (requerido para paso 2)'
    )

    args = parser.parse_args()

    if args.step == 1:
        step1_verify_connection()

    elif args.step == 2:
        if not args.shapefile:
            print("Error: --shapefile es requerido para el paso 2")
            print("\nEjemplo:")
            print("  python src/data_loaders/load_pdet_simple.py --step 2 --shapefile data/raw/dane/MGN_MPIO.shp")
            return

        shapefile_path = Path(args.shapefile)
        if not shapefile_path.exists():
            print(f"Error: Archivo no encontrado: {shapefile_path}")
            return

        step2_process_shapefile(shapefile_path)

    elif args.step == 3:
        step3_load_to_mongodb()

    elif args.step == 4:
        step4_validate()


if __name__ == '__main__':
    main()
