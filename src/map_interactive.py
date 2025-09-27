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
from shapely.geometry import Point
from utils import load_gym_data, load_barrios

# -------------------------------
# 1) Cargar datos reales
# -------------------------------
gimnasios = load_gym_data("data/gimnasios.geojson")
buffer_500 = gpd.read_file("data/processed/buffer_500m.geojson")
buffer_1000 = gpd.read_file("data/processed/buffer_1000m.geojson")
barrios = load_barrios("data/barrios.geojson")
censo = gpd.read_file("data/la_plata_censo.geojson")

# -------------------------------
# 2) Reparar gimnasios con geometría faltante
# -------------------------------
# Seleccionar gimnasios con geometría vacía o no Point
gimnasios_invalidos = gimnasios[~gimnasios.geometry.type.eq("Point") | gimnasios.geometry.isna()]

if not gimnasios_invalidos.empty:
    # Crear Point desde lat/long
    gimnasios_invalidos["geometry"] = gimnasios_invalidos.apply(
        lambda row: Point(row["long"], row["lat"]), axis=1
    )

# Seleccionar gimnasios que ya tenían geometría correcta
gimnasios_validos = gimnasios[gimnasios.geometry.type.eq("Point") & gimnasios.geometry.notna()]

# Unir ambos
gimnasios = gpd.GeoDataFrame(
    pd.concat([gimnasios_validos, gimnasios_invalidos], ignore_index=True),
    geometry="geometry",
    crs="EPSG:4326"
)

# Reemplazar nombres faltantes
gimnasios["name"] = gimnasios["name"].fillna("Sin nombre")

# Filtrar solo columnas necesarias
gimnasios = gimnasios[['geometry', 'name', 'leisure']]

# -------------------------------
# 3) Crear mapa base
# -------------------------------
centro = [-34.9214, -57.9545]
m = folium.Map(location=centro, zoom_start=13, tiles="OpenStreetMap")

# -------------------------------
# 4) Agregar barrios
# -------------------------------
folium.GeoJson(
    barrios,
    name="Barrios",
    style_function=lambda x: {"fillColor": "none", "color": "black", "weight": 2}
).add_to(m)

# -------------------------------
# 5) Agregar buffers 500 m con popups
# -------------------------------
for idx, buffer in buffer_500.iterrows():
    count_gym = gimnasios[gimnasios.geometry.within(buffer.geometry)].shape[0]
    popup_text = f"Este buffer cubre {count_gym} gimnasio(s)"
    
    folium.GeoJson(
        buffer.geometry,
        style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.3},
        popup=folium.Popup(popup_text, max_width=200)
    ).add_to(m)

# -------------------------------
# 6) Agregar buffers 1000 m con popups
# -------------------------------
for idx, buffer in buffer_1000.iterrows():
    count_gym = gimnasios[gimnasios.geometry.within(buffer.geometry)].shape[0]
    popup_text = f"Este buffer cubre {count_gym} gimnasio(s)"
    
    folium.GeoJson(
        buffer.geometry,
        style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.2},
        popup=folium.Popup(popup_text, max_width=200)
    ).add_to(m)

# -------------------------------
# 7) Agregar gimnasios con popups enriquecidos
# -------------------------------
for idx, row in gimnasios.iterrows():
    # Construir popup
    popup_text = f"<b>{row['name']}</b><br>Tipo: {row.get('leisure', 'No disponible')}"
    
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color="red",
        fill=True,
        fill_color="red",
        popup=folium.Popup(popup_text, max_width=250)
    ).add_to(m)

# -------------------------------
# 8) Control de capas
# -------------------------------
folium.LayerControl().add_to(m)

# -------------------------------
# 9) Guardar mapa interactivo
# -------------------------------
m.save("data/mapa_interactivo.html")
print("Mapa interactivo guardado en data/mapa_interactivo.html")

def poblacion_en_buffer(buffer_gdf, censo_gdf, columna_poblacion="POB_TOTAL"):
    
    poblaciones = []
    for idx, buffer in buffer_gdf.iterrows():
        #Seleccionar radios censales que intersectan con el buffer
        dentro = censo_gdf[censo_gdf.geometry.intersects(buffer.geometry)]
        #Sumar la población
        poblacion_total = dentro[columna_poblacion].sum()
        poblaciones.append(poblacion_total)
        
    buffer_gdf = buffer_gdf.copy()
    buffer_gdf["poblacion"] = poblaciones
    
    return buffer_gdf


buffer_500 = poblacion_en_buffer(buffer_500, censo)
buffer_1000 = poblacion_en_buffer(buffer_1000, censo)
