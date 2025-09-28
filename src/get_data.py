# get_data.py
# -------------------------------
# Propósito: Descargar y cargar los datos iniciales.
# 1) Obtener los polígonos de barrios de La Plata desde OSM.
# 2) Obtener la ubicación de los gimnasios desde OSM.
# 3) Cargar el censo de La Plata desde un shapefile comprimido.
# Todos los datos se guardan en la carpeta "data/" para su uso posterior.

import osmnx as ox
import geopandas as gpd

ciudad = "La Plata, Argentina"

# -------------------------------
# 1) Descargar polígonos de barrios
# -------------------------------
barrios = ox.geocode_to_gdf(ciudad)
barrios = barrios.to_crs(epsg=4326)
barrios.to_file("data/barrios.geojson", driver="GeoJSON")
print("Barrios guardados en data/barrios.geojson")

# -------------------------------
# 2) Descargar gimnasios
# -------------------------------
tags = {"leisure": "fitness_centre"}
gimnasios = ox.features_from_place(ciudad, tags)

# Convertir geometrías que no sean Point a su centroide
gimnasios["geometry"] = gimnasios.geometry.apply(
    lambda geom: geom.centroid if geom.type != "Point" else geom
)

# Ahora todos los gimnasios tienen Point como geometría
gimnasios.to_file("data/gimnasios.geojson", driver="GeoJSON")
print("Gimnasios guardados en data/gimnasios.geojson")

print("Datos descargados y guardados correctamente en la carpeta data/")

# -------------------------------
# 3) Cargar censo de La Plata
# -------------------------------

#  Cargar censo de todos los departamentos de BA
archivo = "data/RADIOS_2022_V2025-1.zip"
gdf = gpd.read_file(f"zip://{archivo}")
gdf = gdf[gdf["PROV"] == "06"]  # solo provincia BA
gdf = gdf.to_crs(epsg=4326)

#  Filtrar radios que intersectan con barrios
la_plata_censo = gpd.sjoin(gdf, barrios, how="inner", predicate="intersects")

#  Guardar
la_plata_censo.to_file("data/la_plata_censo.geojson", driver="GeoJSON")
print("Censo de La Plata guardado en data/la_plata_censo.geojson")