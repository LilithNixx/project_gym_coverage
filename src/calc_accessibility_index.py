# calc_accessibility_index.py
# -------------------------------
# Propósito: Calcular el índice de accesibilidad a gimnasios por barrio.
# - Usar los buffers de 500m generados previamente.
# - Contar cuántos gimnasios (buffers) intersectan cada barrio.
# - Generar índice de accesibilidad = gimnasios_cercanos / población ajustada (15-70 años).

import geopandas as gpd

# -------------------------------
# 1) Cargar datos
# -------------------------------
barrios = gpd.read_file("data/raw/barrios_con_poblacion.geojson")  # Barrios de La Plata
buffer_500 = gpd.read_file("data/raw/buffer_500m.geojson")  # Buffers ya calculados

# -------------------------------
# 2) Preparar población si no está ajustada
# -------------------------------
# Fuente: Censo Nacional 2022 y estadísticas generales: ~70% población entre 15-70 años
PORC_POB_15_70 = 0.7

if "population_15_70" not in barrios.columns:
    if "population" not in barrios.columns:
        raise ValueError("Los barrios deben tener la columna 'population'")
    barrios["population_15_70"] = (barrios["population"] * PORC_POB_15_70).round(0)

# -------------------------------
# 3) Calcular gimnasios cercanos por barrio
# -------------------------------
barrios["gimnasios_cercanos"] = 0

for idx, barrio in barrios.iterrows():
    # Contar cuántos buffers intersectan el barrio
    intersect_count = buffer_500.intersects(barrio.geometry).sum()
    barrios.at[idx, "gimnasios_cercanos"] = intersect_count

# -------------------------------
# 4) Calcular índice de accesibilidad
# -------------------------------
barrios["indice_accesibilidad"] = barrios.apply(
    lambda row: row["gimnasios_cercanos"] / row["population_15_70"]
    if row["population_15_70"] > 0 else None,
    axis=1,
)

# -------------------------------
# 5) Guardar resultados
# -------------------------------
output_file = "data/processed/barrios_con_indice.geojson"
barrios.to_file(output_file, driver="GeoJSON")
print(f"Archivo guardado con índice de accesibilidad: {output_file}")

# -------------------------------
# 6) Revisar resultados
# -------------------------------
print(barrios[["name", "population_15_70", "gimnasios_cercanos", "indice_accesibilidad"]].head(10))
