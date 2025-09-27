# test_buffers.py
# -------------------------------
# Propósito: Probar la creación y validez de los buffers alrededor de los gimnasios.
# - Verificar que los buffers tengan la distancia correcta (500 m, 1000 m, etc.).
# - Confirmar que los buffers están correctamente proyectados y superpuestos con los barrios.
# - Facilitar la detección de errores antes de calcular métricas de accesibilidad.


import geopandas as gpd
from utils import load_gym_data, load_barrios
import matplotlib.pyplot as plt

# -------------------------------
# Cargar datos
# -------------------------------
gimnasios = load_gym_data("data/gimnasios.geojson")

buffer_500 = gpd.read_file("data/processed/buffer_500m.geojson")
buffer_1000 = gpd.read_file("data/processed/buffer_1000m.geojson")
barrios = load_barrios("data/barrios.geojson")

# -------------------------------
# Inspección rápida
# -------------------------------
print("Gimnasios:")
print(gimnasios.head())
print(gimnasios.info())
print(gimnasios.geom_type.value_counts())
print("Gimnasios sin geometría válida:")
print(gimnasios[gimnasios.geometry.isna()])
print("Cantidad de gimnasios:" )
print(len(gimnasios))

print("\nBuffer 500m:")
print(buffer_500.head())
print(buffer_500.crs)
print(buffer_500.geom_type.value_counts())

# -------------------------------
# Visualización rápida
# -------------------------------
ax = buffer_500.plot(facecolor="blue", alpha=0.3, edgecolor="black")
gimnasios.plot(ax=ax, color="red", markersize=10)
plt.show()
