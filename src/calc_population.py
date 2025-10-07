import geopandas as gpd

# -------------------------------
# 1) Cargar barrios y censo
# -------------------------------
barrios = gpd.read_file("data/raw/barrios.geojson")
censo = gpd.read_file("data/raw/la_plata_censo.geojson")

# -------------------------------
# 2) Proyectar a CRS métrico (metros)
# -------------------------------
barrios_proj = barrios.to_crs(epsg=3857)
censo_proj = censo.to_crs(epsg=3857)

# -------------------------------
# 3) Join espacial y sumar población
# -------------------------------

# Antes de hacer el join espacial
if "index_right" in barrios_proj.columns:
    barrios_proj = barrios_proj.drop(columns=["index_right"])

if "index_right" in censo_proj.columns:
    censo_proj = censo_proj.drop(columns=["index_right"])

# Realizar join espacial
barrios_join = gpd.sjoin(barrios_proj, censo_proj, how="left", predicate="intersects")
pob_por_barrio = barrios_join.groupby(barrios_join.index)["POB_TOT_P"].sum()

barrios["population"] = pob_por_barrio
barrios["population"] = barrios["population"].fillna(0)

# -------------------------------
# 4) Guardar archivo
# -------------------------------
barrios.to_file("data/processed/barrios_con_poblacion.geojson", driver="GeoJSON")
print("Archivo 'barrios_con_poblacion.geojson' generado con éxito.")
