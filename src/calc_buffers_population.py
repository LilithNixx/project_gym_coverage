# calc_accessibility.py
# -------------------------------
# Propósito: Calcular métricas de accesibilidad a gimnasios por barrio.
# - Calcular la población dentro de los buffers.
# - Contar gimnasios cercanos a cada barrio.
# - Generar índice de accesibilidad (gimnasios/población).


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

# ...PRUEBAS...
gimnasios_proj = gimnasios_proj[gimnasios_proj.is_valid & ~gimnasios_proj.is_empty]
censo_proj = censo_proj[censo_proj.is_valid & ~censo_proj.is_empty]

print("Cantidad de gimnasios:", len(gimnasios_proj))
print("Cantidad de radios censales:", len(censo_proj))

# Prueba de intersección directa
test_buffer = buffer_500.iloc[0].geometry
intersectados = censo_proj[censo_proj.intersects(test_buffer)]
print("Radios censales que intersectan el primer buffer:", len(intersectados))


# -------------------------------
# 3) Función para calcular población en buffer
# -------------------------------
def poblacion_en_buffer(buffers, censo):
    resultados = []
    for idx, buffer_row in buffers.iterrows():
        # Filtrar radios censales que intersectan el buffer
        radios_intersectados = censo[censo.intersects(buffer_row.geometry)]
        poblacion = 0
        for _, radio in radios_intersectados.iterrows():
            intersec = buffer_row.geometry.intersection(radio.geometry)
            if not intersec.is_empty:
                area_intersec = intersec.area
                area_total = radio.geometry.area
                prop_area = area_intersec / area_total if area_total > 0 else 0
                pob_est = prop_area * radio["POB_TOT_P"]
                poblacion += pob_est
        resultados.append(poblacion)
    buffers = buffers.copy()
    buffers["poblacion"] = resultados
    return buffers

# -------------------------------
# 4) Calcular
# -------------------------------
buffer_500 = poblacion_en_buffer(buffer_500, censo_proj)
buffer_1000 = poblacion_en_buffer(buffer_1000, censo_proj)


# Redondear a 2 decimales la columna "poblacion"
buffer_500["poblacion"] = buffer_500["poblacion"].round(2)
buffer_1000["poblacion"] = buffer_1000["poblacion"].round(2)

# -------------------------------
# 5) Guardar resultados
# -------------------------------

print("Área primer buffer (m2):", buffer_500.iloc[0].geometry.area)
print("Área primer radio censal (m2):", censo_proj.iloc[0].geometry.area)

# Reproyectar a EPSG:4326 antes de guardar
buffer_500 = buffer_500.to_crs(epsg=4326)
buffer_1000 = buffer_1000.to_crs(epsg=4326)

# Guardar resultados en la carpeta correcta
buffer_500.to_file("data/buffer_500m.geojson", driver="GeoJSON")
buffer_1000.to_file("data/buffer_1000m.geojson", driver="GeoJSON")

print("Buffers con población estimada guardados en /data")


print("Cantidad de buffers con población > 0:", (buffer_500["poblacion"] > 0).sum())
print("Población en cada buffer (primeros 10):")
print(buffer_500["poblacion"].head(10))

print("CRS gimnasios:", gimnasios.crs)
print("CRS censo:", censo.crs)


