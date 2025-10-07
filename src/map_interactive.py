# map_interactive.py
# -------------------------------
# Funciones para generar el mapa interactivo de gimnasios en La Plata.

import folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
from shapely.geometry import Point
from folium import FeatureGroup
from utils import load_gym_data, load_barrios


def preparar_datos():
    """Carga y prepara los datos: gimnasios, buffers, barrios y censo."""
    gimnasios = load_gym_data("data/raw/gimnasios.geojson")
    buffer_500 = gpd.read_file("data/processed/buffer_500m.geojson")
    buffer_1000 = gpd.read_file("data/processed/buffer_1000m.geojson")
    barrios = load_barrios("data/raw/barrios.geojson")
    censo = gpd.read_file("data/raw/la_plata_censo.geojson")

    # Agregar población a barrios
    barrios = barrios.reset_index(drop=True)
    censo = censo.reset_index(drop=True)

    if "index_right" in barrios.columns:
        barrios = barrios.drop(columns=["index_right"])
    if "index_right" in censo.columns:
        censo = censo.drop(columns=["index_right"])

    barrios_proj = barrios.to_crs(epsg=3857)
    censo_proj = censo.to_crs(epsg=3857)

    barrios_join = gpd.sjoin(barrios_proj, censo_proj, how="left", predicate="intersects")
    pob_por_barrio = barrios_join.groupby(barrios_join.index)["POB_TOT_P"].sum()
    barrios["population"] = pob_por_barrio.fillna(0)

    # Reparar gimnasios inválidos
    gimnasios_invalidos = gimnasios[~gimnasios.geometry.type.eq("Point") | gimnasios.geometry.isna()]
    if not gimnasios_invalidos.empty:
        gimnasios_invalidos["geometry"] = gimnasios_invalidos.apply(
            lambda row: Point(row["long"], row["lat"]), axis=1
        )

    gimnasios_validos = gimnasios[gimnasios.geometry.type.eq("Point") & gimnasios.geometry.notna()]
    gimnasios = gpd.GeoDataFrame(
        pd.concat([gimnasios_validos, gimnasios_invalidos], ignore_index=True),
        geometry="geometry",
        crs="EPSG:4326"
    )

    return gimnasios, buffer_500, buffer_1000, barrios


def calcular_indice_accesibilidad(barrios, buffer_500):
    """Calcula el índice de accesibilidad 2SFCA."""
    buffer_500["Rj"] = 1 / buffer_500["poblacion"]
    buffer_500["Rj"] = buffer_500["Rj"].replace([float("inf")], 0).fillna(0)

    barrios["indice_accesibilidad"] = 0.0
    for i, barrio in barrios.iterrows():
        gimnasios_cercanos = buffer_500[buffer_500.intersects(barrio.geometry)]
        barrios.at[i, "indice_accesibilidad"] = gimnasios_cercanos["Rj"].sum() if len(gimnasios_cercanos) > 0 else 0.0

    barrios["gimnasios_cercanos"] = barrios.apply(
        lambda row: buffer_500.intersects(row.geometry).sum(), axis=1
    )
    return barrios


def generar_mapa(gimnasios, buffer_500, buffer_1000, barrios, output_file="docs/index.html"):
    """Genera y guarda el mapa interactivo."""
    m = folium.Map(location=[-34.9214, -57.9544], zoom_start=13)

    # Grupos de capas
    gimnasios_group = FeatureGroup(name="Gimnasios")
    buffer500_group = FeatureGroup(name="Cobertura 500m")
    buffer1000_group = FeatureGroup(name="Cobertura 1000m")
    barrios_group = FeatureGroup(name="Índice de accesibilidad (barrios)")

    # Colormap
    valores = barrios["indice_accesibilidad"].dropna()
    min_val, max_val = (valores.min(), valores.max()) if not valores.empty else (0, 1)
    colormap = cm.linear.Blues_09.scale(min_val, max_val)
    colormap.caption = "Índice de accesibilidad (gimnasios / población)"

    # Agregar barrios
    for idx, row in barrios.iterrows():
        color = colormap(row["indice_accesibilidad"]) if pd.notnull(row["indice_accesibilidad"]) else "#cccccc"
        folium.GeoJson(
            barrios.iloc[[idx]],
            style_function=lambda x, color=color: {
                "color": "black",
                "weight": 1,
                "fillColor": color,
                "fillOpacity": 0.6,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["population", "gimnasios_cercanos", "indice_accesibilidad"],
                aliases=["Población:", "Gimnasios cercanos:", "Índice de accesibilidad:"],
                localize=True,
            ),
        ).add_to(barrios_group)

    # Gimnasios
    for idx, row in gimnasios.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"Gimnasio: {row['name']}",
            icon=folium.Icon(color="red", icon="dumbbell", prefix="fa"),
        ).add_to(gimnasios_group)

    # Buffers
    for idx, row in buffer_500.iterrows():
        folium.GeoJson(
            row.geometry,
            style_function=lambda x: {"color": "blue", "weight": 2, "fillOpacity": 0.1},
            tooltip=f"Buffer 500m - población cubierta: {row['poblacion']}",
        ).add_to(buffer500_group)

    for idx, row in buffer_1000.iterrows():
        folium.GeoJson(
            row.geometry,
            style_function=lambda x: {"color": "green", "weight": 2, "fillOpacity": 0.1},
            tooltip=f"Buffer 1000m - población cubierta: {row['poblacion']}",
        ).add_to(buffer1000_group)

    # Añadir al mapa
    barrios_group.add_to(m)
    gimnasios_group.add_to(m)
    buffer500_group.add_to(m)
    buffer1000_group.add_to(m)
    colormap.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    m.save(output_file)
    print(f"Mapa guardado en {output_file}")
