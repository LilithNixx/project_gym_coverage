# src/get_data.py
import osmnx as ox

ciudad = "La Plata, Argentina"

# -------------------------------
# 1) Descargar polígonos de barrios
# -------------------------------
barrios = ox.geocode_to_gdf(ciudad)
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
