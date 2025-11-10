"""
Script para descargar Google Open Buildings - Colombia

Este script descarga los datos de Google Open Buildings v3 para Colombia
desde Google Cloud Storage de forma directa.

Autor: Equipo PDET Solar Analysis
Fecha: 10 Noviembre 2025
"""

import os
import urllib.request
from pathlib import Path
from tqdm import tqdm

def download_with_progress(url, output_path):
    """Descarga archivo con barra de progreso"""

    class DownloadProgressBar(tqdm):
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=output_path.name) as t:
        urllib.request.urlretrieve(url, filename=output_path,
                                   reporthook=t.update_to)

def main():
    """Función principal"""
    print("=" * 70)
    print("DESCARGA DE GOOGLE OPEN BUILDINGS - COLOMBIA")
    print("=" * 70)
    print()

    # URLs de Google Cloud Storage (públicas)
    # Nota: Esta es una URL de ejemplo. Google Open Buildings requiere
    # descarga mediante el notebook de Colab o construcción manual de URL

    print("⚠️ INSTRUCCIONES:")
    print()
    print("Google Open Buildings requiere descarga mediante:")
    print()
    print("1. Google Colab Notebook (RECOMENDADO):")
    print("   URL: https://colab.research.google.com/github/google-research/")
    print("        google-research/blob/master/building_detection/")
    print("        open_buildings_download_region_polygons.ipynb")
    print()
    print("2. Pasos en Colab:")
    print("   - Region Border Source: Natural Earth (Low Res 110m)")
    print("   - Region: COL (Colombia)")
    print("   - Data Type: polygons")
    print("   - Download method: Download directly")
    print()
    print("3. Guardar archivo descargado en:")
    print("   data/raw/google/open_buildings_v3_polygons_ne_110m_COL.csv.gz")
    print()
    print("=" * 70)
    print()

    # Preguntar si el usuario ya descargó
    response = input("¿Ya descargaste el archivo? (s/n): ").lower()

    if response == 's':
        # Buscar el archivo
        possible_locations = [
            Path.home() / "Downloads" / "open_buildings_v3_polygons_ne_110m_COL.csv.gz",
            Path.home() / "Desktop" / "open_buildings_v3_polygons_ne_110m_COL.csv.gz",
            Path("data/raw/google/open_buildings_v3_polygons_ne_110m_COL.csv.gz")
        ]

        found = False
        for location in possible_locations:
            if location.exists():
                print(f"\n✅ Archivo encontrado: {location}")
                print(f"   Tamaño: {location.stat().st_size / (1024**3):.2f} GB")

                # Mover a la ubicación correcta
                target = Path("data/raw/google/open_buildings_v3_polygons_ne_110m_COL.csv.gz")
                target.parent.mkdir(parents=True, exist_ok=True)

                if location != target:
                    import shutil
                    print(f"\n📦 Moviendo archivo a: {target}")
                    shutil.copy2(location, target)
                    print("✅ Archivo copiado correctamente")

                found = True
                break

        if not found:
            print("\n❌ Archivo no encontrado en ubicaciones comunes")
            print("Por favor, coloca el archivo en:")
            print("   data/raw/google/open_buildings_v3_polygons_ne_110m_COL.csv.gz")
    else:
        print("\n📝 Por favor, descarga el archivo usando el Google Colab Notebook")
        print("   y vuelve a ejecutar este script.")

    print("\n" + "=" * 70)
    print("Para cargar los datos a MongoDB, ejecuta:")
    print("   py src/data_loaders/load_google_buildings.py")
    print("=" * 70)

if __name__ == '__main__':
    main()
