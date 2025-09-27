# calc_accessibility.py
# -------------------------------
# Propósito: Calcular métricas de accesibilidad a gimnasios por barrio.
# - Calcular la población dentro de los buffers.
# - Contar gimnasios cercanos a cada barrio.
# - Generar índice de accesibilidad (gimnasios/populación).


import geopandas as gpd

# -------------------------------
# 1) Cargar datos procesados
# -------------------------------
gimnasios = gpd.read_file("data/gimnasios.geojson")
censo = gpd.read_file("data/la_plata_censo.geojson")

# -------------------------------
# 2) Crear buffers
# -------------------------------
# EPSG:4326 (grados) no sirve para buffers, hay que proyectar a metros
gimnasios_proj = gimnasios.to_crs(epsg=3857)  # Web Mercator (metros)
censo_proj = censo.to_crs(epsg=3857)

buffer_500 = gimnasios_proj.copy()
buffer_500["geometry"] = buffer_500.buffer(500)

buffer_1000 = gimnasios_proj.copy()
buffer_1000["geometry"] = buffer_1000.buffer(1000)

# -------------------------------
# 3) Función para calcular población en buffer
# -------------------------------
def poblacion_en_buffer(buffers, censo):
    resultados = []
    for index_row, buffer_pol in buffers.iterrows():
        interseccion = gpd.overlay(censo, gpd.GeoDataFrame(geometry=[buffer_pol.geometry], crs=censo.crs), how="intersection")
        
        #Si el buffer no toca ningún polígono censal, interseccion queda vacío.
        if not interseccion.empty:
            # Calcular proporción de área
            interseccion["area_intersec"] = interseccion.geometry.area
            interseccion["area_total"] = interseccion.to_crs(epsg=3857).geometry.area
            interseccion["prop_area"] = interseccion["area_intersec"] / interseccion["area_total"]
            
            # Población ponderada
            interseccion["pob_est"] = interseccion["prop_area"] * interseccion["POB_TOT_P"]
            poblacion = interseccion["pob_est"].sum()
        else:
            poblacion = 0
        resultados.append(poblacion)
    buffers["poblacion"] = resultados
    return buffers

# -------------------------------
# 4) Calcular
# -------------------------------
buffer_500 = poblacion_en_buffer(buffer_500, censo_proj)
buffer_1000 = poblacion_en_buffer(buffer_1000, censo_proj)

# -------------------------------
# 5) Guardar resultados
# -------------------------------
buffer_500.to_file("data/buffer_500.geojson", driver="GeoJSON")
buffer_1000.to_file("data/buffer_1000.geojson", driver="GeoJSON")

print("Buffers con población estimada guardados en data/")
