#!/usr/bin/env python3
"""
Script para exportar datos de MongoDB para compartir con el equipo
"""
import sys
from pathlib import Path
import json

# Agregar el root del proyecto al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.database.connection import get_database, load_config

def export_data():
    """Exporta la colección pdet_municipalities a JSON"""
    print("=" * 60)
    print("EXPORTANDO DATOS DE MONGODB")
    print("=" * 60)

    try:
        config = load_config()
        db = get_database()
        collection = db['pdet_municipalities']

        # Obtener todos los documentos
        print("\nObteniendo documentos de MongoDB...")
        documents = list(collection.find())
        print(f"[OK] Encontrados {len(documents)} documentos")

        # Convertir ObjectId a string para JSON
        for doc in documents:
            doc['_id'] = str(doc['_id'])

        # Guardar a JSON
        output_file = Path(__file__).parent / 'pdet_municipalities_export.json'
        print(f"\nGuardando a: {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2, default=str)

        print(f"[OK] Exportados {len(documents)} documentos")
        print(f"[OK] Archivo: {output_file}")
        print(f"[OK] Tamaño: {output_file.stat().st_size / (1024*1024):.2f} MB")

        # También exportar metadatos de índices
        print("\nExportando información de índices...")
        indexes = list(collection.list_indexes())
        index_info = []
        for idx in indexes:
            index_info.append({
                'name': idx['name'],
                'key': dict(idx['key']),
                'unique': idx.get('unique', False),
                'sparse': idx.get('sparse', False)
            })

        index_file = Path(__file__).parent / 'indexes_info.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_info, f, indent=2)

        print(f"[OK] Información de índices guardada en: {index_file}")

        print("\n" + "=" * 60)
        print("EXPORTACIÓN COMPLETADA")
        print("=" * 60)
        print("\nArchivos generados:")
        print(f"  - {output_file.name} (datos)")
        print(f"  - {index_file.name} (índices)")

        return True

    except Exception as e:
        print(f"[ERROR] Error durante la exportación: {e}")
        return False

if __name__ == '__main__':
    success = export_data()
    sys.exit(0 if success else 1)
