#!/usr/bin/env python3
"""
Script para importar datos de MongoDB desde el backup compartido
Para uso del equipo
"""
import sys
from pathlib import Path
import json

# Agregar el root del proyecto al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.database.connection import get_database, load_config, create_spatial_indexes

def import_data():
    """Importa la colección pdet_municipalities desde JSON"""
    print("=" * 60)
    print("IMPORTANDO DATOS A MONGODB")
    print("=" * 60)

    try:
        # Verificar archivos
        data_file = Path(__file__).parent / 'pdet_municipalities_export.json'
        index_file = Path(__file__).parent / 'indexes_info.json'

        if not data_file.exists():
            print(f"[ERROR] Archivo no encontrado: {data_file}")
            print("Asegurate de haber descargado el backup completo")
            return False

        print(f"\nArchivo de datos: {data_file}")
        print(f"Tamaño: {data_file.stat().st_size / (1024*1024):.2f} MB")

        # Cargar datos
        print("\nCargando documentos desde JSON...")
        with open(data_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        print(f"[OK] Cargados {len(documents)} documentos")

        # Remover _id para que MongoDB genere nuevos
        for doc in documents:
            if '_id' in doc:
                del doc['_id']

        # Conectar a MongoDB
        config = load_config()
        db = get_database()
        collection = db['pdet_municipalities']

        # Verificar si ya hay datos
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"\n[!] La coleccion ya contiene {existing_count} documentos")
            response = input("Deseas eliminar los datos existentes y recargar? (s/n): ")
            if response.lower() != 's':
                print("Operacion cancelada")
                return False
            collection.delete_many({})
            print("[OK] Datos existentes eliminados")

        # Insertar documentos
        print(f"\nInsertando {len(documents)} documentos...")
        try:
            result = collection.insert_many(documents, ordered=False)
            print(f"[OK] Insertados {len(result.inserted_ids)} documentos")
        except Exception as e:
            print(f"[ERROR] Error durante la insercion: {e}")
            return False

        # Crear índices
        print("\nCreando indices...")

        # Índice espacial
        print("  - Indice espacial 2dsphere en 'geom'...")
        create_spatial_indexes('pdet_municipalities', 'geom', config=config, verbose=False)
        print("    [OK] Creado")

        # Índice único en muni_code
        print("  - Indice unico en 'muni_code'...")
        collection.create_index('muni_code', unique=True)
        print("    [OK] Creado")

        # Índices adicionales
        print("  - Indice en 'dept_code'...")
        collection.create_index('dept_code')
        print("    [OK] Creado")

        print("  - Indice en 'pdet_region'...")
        collection.create_index('pdet_region')
        print("    [OK] Creado")

        print("  - Indice en 'pdet_subregion'...")
        collection.create_index('pdet_subregion')
        print("    [OK] Creado")

        print("\n[OK] Todos los indices creados correctamente")

        # Verificación final
        final_count = collection.count_documents({})
        print("\n" + "=" * 60)
        print("IMPORTACION COMPLETADA")
        print("=" * 60)
        print(f"\nTotal de documentos en MongoDB: {final_count}")
        print(f"Indices creados: 6")
        print(f"\n[OK] Base de datos lista para usar!")

        return True

    except Exception as e:
        print(f"[ERROR] Error durante la importacion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = import_data()
    sys.exit(0 if success else 1)
