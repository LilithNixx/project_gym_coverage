import geopandas as gpd
from utils import load_barrios

# Cargar barrios con población
barrios = load_barrios("data/barrios.geojson")

# Para prueba, si no tenemos población real:
if 'population' not in barrios.columns:
    import numpy as np
    barrios['population'] = np.random.randint(1000, 20000, size=len(barrios))

# Cargar buffers de 500 m
buffer_500 = gpd.read_file("data/processed/buffer_500m.geojson")

# Asegurarnos de que todos los CRS coincidan
buffer_500 = buffer_500.to_crs(barrios.crs)

# Inicializamos columna de accesibilidad
barrios['gimnasios_cercanos'] = 0

# Contamos cuántos buffers intersectan cada barrio
for idx, barrio in barrios.iterrows():
    intersect_count = buffer_500.intersects(barrio.geometry).sum()
    barrios.at[idx, 'gimnasios_cercanos'] = intersect_count

# Calculamos índice de accesibilidad
barrios['indice_accesibilidad'] = barrios['gimnasios_cercanos'] / barrios['population']

print(barrios[['nombre', 'population', 'gimnasios_cercanos', 'indice_accesibilidad']])
