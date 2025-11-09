"""
Script para importar Microsoft Buildings desde archivos JSON
Para que los compañeros restauren los datos
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from bson import ObjectId

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database
from tqdm import tqdm


def import_from_json(json_file):
    """
    Importa edificaciones desde archivo JSON de muestra

    Args:
        json_file: Archivo JSON con las edificaciones
    """

    print("="*80)
    print("IMPORTACION DE MICROSOFT BUILDINGS")
    print("="*80)

    db = get_database()
    collection = db['microsoft_buildings']

    # Leer archivo
    json_path = PROJECT_ROOT / json_file
    print(f"\nLeyendo: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        buildings = json.load(f)

    print(f"Edificaciones en archivo: {len(buildings):,}")

    # Convertir de vuelta a tipos MongoDB
    for building in buildings:
        if '_id' in building and isinstance(building['_id'], str):
            building['_id'] = ObjectId(building['_id'])
        if 'created_at' in building and isinstance(building['created_at'], str):
            building['created_at'] = datetime.fromisoformat(building['created_at'])

    # Eliminar coleccion existente
    print("\nEliminando coleccion existente (si existe)...")
    collection.drop()

    # Insertar
    print(f"Insertando {len(buildings):,} edificaciones...")
    result = collection.insert_many(buildings, ordered=False)

    print(f"\n{'='*80}")
    print(f"IMPORTACION COMPLETADA")
    print(f"{'='*80}")
    print(f"Insertados: {len(result.inserted_ids):,} edificaciones")

    # Verificar
    count = collection.count_documents({})
    print(f"Verificacion: {count:,} documentos en coleccion")

    return count


def import_from_batches(batch_dir):
    """
    Importa edificaciones desde multiples archivos JSON

    Args:
        batch_dir: Directorio con archivos batch_*.json
    """

    print("="*80)
    print("IMPORTACION DE LOTES")
    print("="*80)

    db = get_database()
    collection = db['microsoft_buildings']

    batch_path = PROJECT_ROOT / batch_dir

    # Leer metadata
    metadata_file = batch_path / 'export_metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            print(f"\nMetadata:")
            print(f"  Total documentos: {metadata['total_documents']:,}")
            print(f"  Total lotes: {metadata['total_batches']}")

    # Eliminar coleccion existente
    print("\nEliminando coleccion existente...")
    collection.drop()

    # Buscar archivos batch
    batch_files = sorted(batch_path.glob('microsoft_buildings_batch_*.json'))
    print(f"\nArchivos batch encontrados: {len(batch_files)}")

    total_inserted = 0

    for batch_file in tqdm(batch_files, desc="Importando lotes", unit=" file"):
        with open(batch_file, 'r', encoding='utf-8') as f:
            buildings = json.load(f)

        # Convertir tipos
        for building in buildings:
            if '_id' in building and isinstance(building['_id'], str):
                building['_id'] = ObjectId(building['_id'])
            if 'created_at' in building and isinstance(building['created_at'], str):
                building['created_at'] = datetime.fromisoformat(building['created_at'])

        # Insertar
        result = collection.insert_many(buildings, ordered=False)
        total_inserted += len(result.inserted_ids)

    print(f"\n{'='*80}")
    print(f"IMPORTACION COMPLETADA")
    print(f"{'='*80}")
    print(f"Total insertado: {total_inserted:,} edificaciones")

    # Verificar
    count = collection.count_documents({})
    print(f"Verificacion: {count:,} documentos en coleccion")

    return count


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Importar Microsoft Buildings")
    parser.add_argument('--sample', type=str, help='Importar desde archivo de muestra')
    parser.add_argument('--batches', type=str, help='Importar desde directorio de lotes')

    args = parser.parse_args()

    if args.sample:
        import_from_json(args.sample)
    elif args.batches:
        import_from_batches(args.batches)
    else:
        print("Especificar --sample o --batches")
        print("\nEjemplos:")
        print("  py src/utils/import_microsoft_buildings.py --sample backup_deliverable_3/microsoft_buildings_sample.json")
        print("  py src/utils/import_microsoft_buildings.py --batches backup_deliverable_3/full")
