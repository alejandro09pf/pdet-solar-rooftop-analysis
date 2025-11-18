"""
Script para generar visualizaciones y mapas interactivos

Genera:
- Mapas coropléticos HTML (Folium)
- Gráficos estadísticos PNG (Matplotlib)

Autor: Equipo PDET Solar Analysis
Fecha: Noviembre 2025
Deliverable: 4
"""

import sys
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar estilo de gráficos
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def create_choropleth_map():
    """Crea mapa coroplético de área útil para paneles solares"""
    logger.info("=" * 70)
    logger.info("GENERANDO MAPA COROPLÉTICO - ÁREA ÚTIL SOLAR")
    logger.info("=" * 70)

    # Leer GeoJSON
    geojson_path = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'geojson' / 'municipalities_with_stats.geojson'

    logger.info(f"Leyendo GeoJSON: {geojson_path}")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Crear mapa centrado en Colombia
    m = folium.Map(
        location=[4.5709, -74.2973],  # Centro de Colombia
        zoom_start=6,
        tiles='CartoDB positron'
    )

    # Añadir mapa coroplético
    folium.Choropleth(
        geo_data=geojson_data,
        name='Área Útil para Paneles Solares',
        data=pd.DataFrame([f['properties'] for f in geojson_data['features']]),
        columns=['muni_code', 'ms_useful_area_km2'],
        key_on='feature.properties.muni_code',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Área Útil para Paneles Solares (km²)',
        nan_fill_color='lightgray'
    ).add_to(m)

    # Añadir tooltips con información
    style_function = lambda x: {
        'fillColor': '#ffffff',
        'color': '#000000',
        'fillOpacity': 0.1,
        'weight': 0.1
    }

    highlight_function = lambda x: {
        'fillColor': '#000000',
        'color': '#000000',
        'fillOpacity': 0.50,
        'weight': 0.1
    }

    tooltip = folium.features.GeoJsonTooltip(
        fields=['muni_name', 'dept_name', 'pdet_region', 'ms_buildings_count', 'ms_useful_area_km2', 'ms_useful_area_ha'],
        aliases=['Municipio:', 'Departamento:', 'Región PDET:', 'Edificaciones:', 'Área Útil (km²):', 'Área Útil (ha):'],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=tooltip
    ).add_to(m)

    # Añadir control de capas
    folium.LayerControl().add_to(m)

    # Añadir fullscreen
    plugins.Fullscreen().add_to(m)

    # Guardar mapa
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'maps'
    output_dir.mkdir(parents=True, exist_ok=True)

    map_path = output_dir / 'area_util_choropleth.html'
    m.save(str(map_path))

    logger.info(f"Mapa coroplético guardado: {map_path}")
    logger.info(f"   Tamaño: {map_path.stat().st_size / 1024:.1f} KB")

    return map_path


def create_density_map():
    """Crea mapa coroplético de densidad de edificaciones"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("GENERANDO MAPA COROPLÉTICO - DENSIDAD DE EDIFICACIONES")
    logger.info("=" * 70)

    # Leer GeoJSON
    geojson_path = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'geojson' / 'municipalities_with_stats.geojson'

    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Crear mapa
    m = folium.Map(
        location=[4.5709, -74.2973],
        zoom_start=6,
        tiles='CartoDB positron'
    )

    # Añadir mapa coroplético
    folium.Choropleth(
        geo_data=geojson_data,
        name='Densidad de Edificaciones',
        data=pd.DataFrame([f['properties'] for f in geojson_data['features']]),
        columns=['muni_code', 'ms_buildings_count'],
        key_on='feature.properties.muni_code',
        fill_color='Blues',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Número de Edificaciones',
        nan_fill_color='lightgray'
    ).add_to(m)

    # Tooltips
    tooltip = folium.features.GeoJsonTooltip(
        fields=['muni_name', 'dept_name', 'ms_buildings_count', 'area_muni_km2'],
        aliases=['Municipio:', 'Departamento:', 'Edificaciones:', 'Área Municipal (km²):'],
        localize=True
    )

    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {'fillColor': '#ffffff', 'color': '#000000', 'fillOpacity': 0.1, 'weight': 0.1},
        control=False,
        highlight_function=lambda x: {'fillColor': '#000000', 'color': '#000000', 'fillOpacity': 0.50, 'weight': 0.1},
        tooltip=tooltip
    ).add_to(m)

    folium.LayerControl().add_to(m)
    plugins.Fullscreen().add_to(m)

    # Guardar
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'maps'
    map_path = output_dir / 'density_choropleth.html'
    m.save(str(map_path))

    logger.info(f"Mapa de densidad guardado: {map_path}")
    logger.info(f"   Tamaño: {map_path.stat().st_size / 1024:.1f} KB")

    return map_path


def create_top10_chart():
    """Crea gráfico de top 10 municipios"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("GENERANDO GRÁFICO - TOP 10 MUNICIPIOS")
    logger.info("=" * 70)

    # Leer CSV
    csv_path = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'tables' / 'municipalities_stats.csv'
    df = pd.read_csv(csv_path)

    # Top 10 por área útil
    top10 = df.nlargest(10, 'ms_useful_area_km2')[['muni_name', 'dept_name', 'ms_useful_area_km2', 'ms_buildings_count']]

    # Crear figura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Gráfico 1: Área útil
    colors1 = plt.cm.YlOrRd(range(len(top10)))
    ax1.barh(range(len(top10)), top10['ms_useful_area_km2'], color=colors1)
    ax1.set_yticks(range(len(top10)))
    ax1.set_yticklabels([f"{row['muni_name']}\n({row['dept_name']})" for _, row in top10.iterrows()])
    ax1.set_xlabel('Área Útil para Paneles Solares (km²)', fontsize=12)
    ax1.set_title('Top 10 Municipios - Área Útil Solar', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()

    # Añadir valores en las barras
    for i, v in enumerate(top10['ms_useful_area_km2']):
        ax1.text(v + 0.1, i, f'{v:.2f} km²', va='center', fontsize=10)

    # Gráfico 2: Edificaciones
    colors2 = plt.cm.Blues(range(len(top10)))
    ax2.barh(range(len(top10)), top10['ms_buildings_count'], color=colors2)
    ax2.set_yticks(range(len(top10)))
    ax2.set_yticklabels([f"{row['muni_name']}\n({row['dept_name']})" for _, row in top10.iterrows()])
    ax2.set_xlabel('Número de Edificaciones', fontsize=12)
    ax2.set_title('Top 10 Municipios - Edificaciones', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()

    # Añadir valores
    for i, v in enumerate(top10['ms_buildings_count']):
        ax2.text(v + 500, i, f'{v:,}', va='center', fontsize=10)

    plt.tight_layout()

    # Guardar
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'charts'
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_path = output_dir / 'top10_municipalities.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Gráfico Top 10 guardado: {chart_path}")
    logger.info(f"   Tamaño: {chart_path.stat().st_size / 1024:.1f} KB")

    return chart_path


def create_regional_chart():
    """Crea gráfico de distribución regional"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("GENERANDO GRÁFICO - DISTRIBUCIÓN REGIONAL")
    logger.info("=" * 70)

    # Leer CSV regional
    csv_path = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'tables' / 'regional_summary.csv'
    df = pd.read_csv(csv_path)

    # Ordenar por área útil
    df = df.sort_values('ms_total_useful_area_km2', ascending=True)

    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 8))

    colors = plt.cm.viridis(range(len(df)))
    bars = ax.barh(range(len(df)), df['ms_total_useful_area_km2'], color=colors)

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['pdet_region'], fontsize=10)
    ax.set_xlabel('Área Útil Total (km²)', fontsize=12)
    ax.set_title('Distribución Regional PDET - Área Útil para Paneles Solares', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # Añadir valores y número de municipios
    for i, (area, munis) in enumerate(zip(df['ms_total_useful_area_km2'], df['num_municipalities'])):
        ax.text(area + 0.5, i, f'{area:.2f} km² ({munis} munis)', va='center', fontsize=9)

    plt.tight_layout()

    # Guardar
    output_dir = PROJECT_ROOT / 'deliverables' / 'deliverable_4' / 'outputs' / 'charts'
    chart_path = output_dir / 'regional_distribution.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Gráfico regional guardado: {chart_path}")
    logger.info(f"   Tamaño: {chart_path.stat().st_size / 1024:.1f} KB")

    return chart_path


def main():
    """Función principal"""
    logger.info("=" * 70)
    logger.info("GENERACIÓN DE VISUALIZACIONES - DELIVERABLE 4")
    logger.info("=" * 70)
    logger.info("")

    try:
        # Crear mapas
        map1 = create_choropleth_map()
        map2 = create_density_map()

        # Crear gráficos
        chart1 = create_top10_chart()
        chart2 = create_regional_chart()

        # Resumen
        logger.info("")
        logger.info("=" * 70)
        logger.info("RESUMEN DE VISUALIZACIONES GENERADAS")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Mapas interactivos (HTML):")
        logger.info(f"  1. {map1}")
        logger.info(f"  2. {map2}")
        logger.info("")
        logger.info("Gráficos estadísticos (PNG):")
        logger.info(f"  3. {chart1}")
        logger.info(f"  4. {chart2}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("TODAS LAS VISUALIZACIONES GENERADAS EXITOSAMENTE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
