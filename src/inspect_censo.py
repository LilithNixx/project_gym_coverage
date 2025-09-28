# inspect_censo.py
# -------------------------------
# Propósito: Inspeccionar y explorar los datos del censo.
# - Revisar columnas y geometrías.
# - Filtrar La Plata.
# - Guardar el censo en formato GeoJSON para su uso en otros scripts.


import geopandas as gpd

archivo = "data\RADIOS_2022_V2025-1.zip"

gdf = gpd.read_file(archivo)

#print("Columnas disponibles:", gdf.columns)
#print("Primeras filas:")
#print(gdf.head())
#print("CRS:", gdf.crs)


# Filtrar por provincia de Buenos Aires (06)
ba = gdf[gdf["PROV"] == "06"]

# Ver todos los deptos disponibles
print(ba["DEPTO"].unique())

