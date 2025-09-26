# funciones de procesamiento espacial (buffers, joins)
import geopandas as gpd
from utils import load_gym_data

# Cargar gimnasios
gimnasios = load_gym_data("data/gimnasios.geojson")

# Convertir a CRS métrico (UTM zona 21S para La Plata)
gim_metrico = gimnasios.to_crs(epsg=32721)

#Crear buffers
buffer_500m = gim_metrico.buffer(500)
buffer_1000m = gim_metrico.buffer(1000)

#Guardar como GeoDataFrame en CRS original para visualización
buffer_500m_gdf = gpd.GeoDataFrame(geometry=buffer_500m, crs=32721).to_crs(epsg=4326)
buffer_1000m_gdf = gpd.GeoDataFrame(geometry=buffer_1000m, crs=32721).to_crs(epsg=4326)

# Guardar en archivos
buffer_500m_gdf.to_file("data/processed/buffer_500m.geojson", driver="GeoJSON")
buffer_1000m_gdf.to_file("data/processed/buffer_1000m.geojson", driver="GeoJSON")

print("Buffers generados y guardados.")



