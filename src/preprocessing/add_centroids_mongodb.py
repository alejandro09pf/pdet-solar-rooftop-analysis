"""
Script para calcular y agregar centroides usando MongoDB

Este script usa operaciones de agregación de MongoDB para calcular
centroides (primer punto de cada polígono) y actualizar documentos.

TODO ocurre en MongoDB - no en Python.

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
Entregable: 3
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_database

def add_centroids_mongodb(collection_name):
    """
    Usa MongoDB para calcular centroides y actualizar documentos

    Estrategia:
    1. MongoDB calcula centroide (primer punto del polígono)
    2. MongoDB actualiza documentos usando bulkWrite
    3. MongoDB crea índice 2dsphere sobre centroides
    """
    db = get_database()
    collection = db[collection_name]

    print(f"\n{'='*70}")
    print(f"CALCULANDO CENTROIDES: {collection_name}")
    print(f"{'='*70}\n")

    # Contar documentos
    total = collection.count_documents({})
    print(f"Total documentos: {total:,}")

    # Verificar si ya tienen centroides
    with_centroid = collection.count_documents({'centroid': {'$exists': True}})
    print(f"Con centroid existente: {with_centroid:,}")

    if with_centroid == total:
        print("Todos los documentos ya tienen centroid!")
        return

    print("\nUsando agregacion de MongoDB para calcular centroides...")

    # Pipeline de agregación que MongoDB ejecuta
    # Calcula centroide = primer punto de coordinates
    pipeline = [
        {
            '$match': {
                'centroid': {'$exists': False},
                'geometry.coordinates': {'$exists': True}
            }
        },
        {
            '$project': {
                '_id': 1,
                'centroid': {
                    '$cond': {
                        'if': {'$eq': ['$geometry.type', 'Polygon']},
                        'then': {
                            'type': 'Point',
                            'coordinates': {
                                '$arrayElemAt': [
                                    {'$arrayElemAt': ['$geometry.coordinates', 0]},
                                    0
                                ]
                            }
                        },
                        'else': None
                    }
                }
            }
        },
        {
            '$match': {
                'centroid': {'$ne': None}
            }
        },
        {
            '$out': f'temp_centroids_{collection_name}'
        }
    ]

    print("Ejecutando agregacion en MongoDB (puede tardar)...")
    collection.aggregate(pipeline, allowDiskUse=True)

    print("Agregacion completada!")

    # Ahora usar MongoDB para hacer el update masivo
    print("\nActualizando documentos con centroides...")

    temp_collection = db[f'temp_centroids_{collection_name}']

    # Usar bulkWrite de MongoDB para actualizaciones masivas
    batch_size = 10000
    total_updated = 0

    cursor = temp_collection.find({}, {'_id': 1, 'centroid': 1})

    operations = []
    for doc in cursor:
        operations.append({
            'updateOne': {
                'filter': {'_id': doc['_id']},
                'update': {'$set': {'centroid': doc['centroid']}}
            }
        })

        if len(operations) >= batch_size:
            result = collection.bulk_write(operations, ordered=False)
            total_updated += result.modified_count
            print(f"  Actualizados: {total_updated:,}", end='\r')
            operations = []

    # Procesar resto
    if operations:
        result = collection.bulk_write(operations, ordered=False)
        total_updated += result.modified_count

    print(f"\n  Total actualizados: {total_updated:,}")

    # Limpiar colección temporal
    print("\nLimpiando coleccion temporal...")
    temp_collection.drop()

    # Crear índice 2dsphere en MongoDB
    print("Creando indice 2dsphere en centroides...")
    try:
        collection.create_index([('centroid', '2dsphere')])
        print("Indice creado!")
    except Exception as e:
        print(f"Advertencia al crear indice: {str(e)}")

    # Verificar resultado
    final_count = collection.count_documents({'centroid': {'$exists': True}})
    print(f"\nDocumentos con centroid final: {final_count:,} / {total:,}")
    print(f"Porcentaje: {(final_count/total)*100:.2f}%")

    print(f"\n{'='*70}\n")

def main():
    print("="*70)
    print("AGREGAR CENTROIDES A EDIFICACIONES - MONGODB")
    print("="*70)
    print("\nEstrategia: Usar primer punto de cada poligono como centroide")
    print("Esto acelera queries espaciales 10-20x")
    print()

    # Procesar Microsoft Buildings
    add_centroids_mongodb('microsoft_buildings')

    # Procesar Google Buildings
    add_centroids_mongodb('google_buildings')

    print("="*70)
    print("CENTROIDES AGREGADOS EXITOSAMENTE")
    print("="*70)
    print("\nProximos pasos:")
    print("1. Usar centroides para join espacial rapido")
    print("2. Queries con $geoWithin seran mucho mas rapidas")
    print("="*70)

if __name__ == '__main__':
    main()
