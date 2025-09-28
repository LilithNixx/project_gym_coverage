# map_interactive.py
# -------------------------------
# Propósito: Visualizar los datos y métricas en un mapa interactivo.
# - Mostrar barrios de La Plata y su población.
# - Superponer buffers de gimnasios.
# - Colorear barrios según el índice de accesibilidad.
# - Permitir interacción con el mapa (hover, click, leyendas).

import folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm

from shapely.geometry import Point
from utils import load_gym_data, load_barrios
from folium import FeatureGroup


# -------------------------------
# 1) Cargar datos reales
# -------------------------------
gimnasios = load_gym_data("data/gimnasios.geojson")
buffer_500 = gpd.read_file("data/buffer_500m.geojson")
buffer_1000 = gpd.read_file("data/buffer_1000m.geojson")
barrios = load_barrios("data/barrios.geojson")
censo = gpd.read_file("data/la_plata_censo.geojson")

# -------------------------------
# 1a) Agregar población estimada a cada barrio
# -------------------------------
barrios = barrios.reset_index(drop=True)
censo = censo.reset_index(drop=True)

if "index_right" in barrios.columns:
    barrios = barrios.drop(columns=["index_right"])
if "index_right" in censo.columns:
    censo = censo.drop(columns=["index_right"])

# Proyección a CRS métrico
barrios_proj = barrios.to_crs(epsg=3857)
censo_proj = censo.to_crs(epsg=3857)

# Join espacial
barrios_join = gpd.sjoin(barrios_proj, censo_proj, how="left", predicate="intersects")
pob_por_barrio = barrios_join.groupby(barrios_join.index)["POB_TOT_P"].sum()

# Asignar población
barrios["population"] = pob_por_barrio
barrios["population"] = barrios["population"].fillna(0)
print(barrios[["name", "population"]].head(10))

# -------------------------------
# 2) Reparar gimnasios inválidos
# -------------------------------
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

gimnasios["name"] = gimnasios["name"].fillna("Sin nombre")
gimnasios = gimnasios[["geometry", "name", "leisure"]]

# -------------------------------
# 3) Índice de accesibilidad
# -------------------------------
barrios["gimnasios_cercanos"] = 0

for idx, barrio in barrios.iterrows():
    intersect_count = buffer_500.intersects(barrio.geometry).sum()
    barrios.at[idx, "gimnasios_cercanos"] = intersect_count

barrios["indice_accesibilidad"] = barrios.apply(
    lambda row: row["gimnasios_cercanos"] / row["population"] if row["population"] > 0 else None,
    axis=1,
)

# -------------------------------
# 4) Generar mapa
# -------------------------------
def generar_mapa(gimnasios, buffer_500, buffer_1000, barrios, output_file="mapa.html"):
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

    # Barrios
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

    # Guardar
    output_file = "src/outputs/mapa_interactivo.html"
    m.save(output_file)
    print(f"Mapa guardado en {output_file}")


if __name__ == "__main__":
    generar_mapa(
        gimnasios,
        buffer_500,
        buffer_1000,
        barrios,
        output_file="outputs/mapa_interactivo.html",
    )

