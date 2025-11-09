"""
Script para exportar Microsoft Buildings a archivo JSON
Para compartir con compañeros del equipo
"""
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database
from tqdm import tqdm


def export_to_json_batches(output_dir, batch_size=100000):
    """
    Exporta microsoft_buildings en lotes a archivos JSON

    Args:
        output_dir: Directorio de salida
        batch_size: Documentos por archivo
    """

    print("="*80)
    print("EXPORTACION DE MICROSOFT BUILDINGS")
    print("="*80)

    db = get_database()
    collection = db['microsoft_buildings']

    # Contar total
    total = collection.count_documents({})
    print(f"\nTotal a exportar: {total:,} edificaciones")
    print(f"Tamano de lote: {batch_size:,}")
    print(f"Archivos estimados: {total // batch_size + 1}")

    # Crear directorio
    output_path = PROJECT_ROOT / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Exportar en lotes
    batch_num = 0
    skip = 0

    with tqdm(total=total, desc="Exportando", unit=" docs") as pbar:
        while skip < total:
            # Leer lote
            batch = list(collection.find().skip(skip).limit(batch_size))

            if not batch:
                break

            # Guardar lote
            batch_file = output_path / f"microsoft_buildings_batch_{batch_num:04d}.json"

            with open(batch_file, 'w', encoding='utf-8') as f:
                # Convertir ObjectId a string
                for doc in batch:
                    doc['_id'] = str(doc['_id'])
                    doc['created_at'] = doc['created_at'].isoformat()

                json.dump(batch, f, ensure_ascii=False)

            print(f"\n  Guardado: {batch_file.name} ({len(batch):,} docs)")

            batch_num += 1
            skip += batch_size
            pbar.update(len(batch))

    # Crear archivo de metadata
    metadata = {
        'total_documents': total,
        'batch_size': batch_size,
        'total_batches': batch_num,
        'collection': 'microsoft_buildings',
        'database': 'pdet_solar_analysis',
        'exported_at': datetime.now().isoformat(),
        'data_source': 'Microsoft Building Footprints 2020-2021'
    }

    metadata_file = output_path / 'export_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*80}")
    print(f"EXPORTACION COMPLETADA")
    print(f"{'='*80}")
    print(f"Directorio: {output_path}")
    print(f"Archivos: {batch_num} lotes + 1 metadata")
    print(f"Total exportado: {total:,} edificaciones")

    # Estimar tamaño
    import os
    total_size = sum(f.stat().st_size for f in output_path.glob('*.json'))
    print(f"Tamano total: {total_size / (1024**3):.2f} GB")

    return output_path


def create_sample_export(output_file, sample_size=10000):
    """Exporta solo una muestra para testing"""

    print("="*80)
    print("EXPORTACION DE MUESTRA")
    print("="*80)

    db = get_database()
    collection = db['microsoft_buildings']

    print(f"\nCreando muestra de {sample_size:,} edificaciones...")

    # Obtener muestra aleatoria
    sample = list(collection.aggregate([
        {'$sample': {'size': sample_size}}
    ]))

    # Convertir a JSON serializable
    for doc in sample:
        doc['_id'] = str(doc['_id'])
        doc['created_at'] = doc['created_at'].isoformat()

    # Guardar
    output_path = PROJECT_ROOT / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    # Tamaño
    size_mb = output_path.stat().st_size / (1024**2)

    print(f"\n{'='*80}")
    print(f"MUESTRA CREADA")
    print(f"{'='*80}")
    print(f"Archivo: {output_path}")
    print(f"Documentos: {len(sample):,}")
    print(f"Tamano: {size_mb:.2f} MB")
    print(f"\nCompartir este archivo con compañeros para testing rapido")

    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Exportar Microsoft Buildings")
    parser.add_argument('--sample', action='store_true', help='Exportar solo muestra de 10,000')
    parser.add_argument('--full', action='store_true', help='Exportar coleccion completa')
    parser.add_argument('--batch-size', type=int, default=100000, help='Tamano de lote')

    args = parser.parse_args()

    if args.sample:
        create_sample_export('backup_deliverable_3/microsoft_buildings_sample.json')
    elif args.full:
        export_to_json_batches('backup_deliverable_3/full', batch_size=args.batch_size)
    else:
        print("Usar --sample para muestra o --full para exportacion completa")
        print("\nEjemplos:")
        print("  py src/utils/export_microsoft_buildings.py --sample")
        print("  py src/utils/export_microsoft_buildings.py --full --batch-size 100000")
