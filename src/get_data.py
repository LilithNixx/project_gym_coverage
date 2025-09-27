# src/get_data.py
import osmnx as ox
import geopandas as gpd

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

# -------------------------------
# 3) Cargar censo de La Plata
# -------------------------------

archivo = "data/RADIOS_2022_V2025-1.zip"

# Cargar el shapefile comprimido
gdf = gpd.read_file(f"zip://{archivo}")

# Filtrar La Plata (provincia Buenos Aires = '06', departamento = '134')
la_plata_censo = gdf[(gdf["PROV"] == "06") & (gdf["DEPTO"] == "134")]

# Reproyectar a WGS84 para que encaje con los gimnasios (EPSG:4326)
la_plata_censo = la_plata_censo.to_crs(epsg=4326)

# Guardar para usar después
la_plata_censo.to_file("data/la_plata_censo.geojson", driver="GeoJSON")
print("Censo de La Plata guardado en data/la_plata_censo.geojson")

