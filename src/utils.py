# utils.py
# -------------------------------
# Propósito: Funciones auxiliares reutilizables en todo el proyecto.
# - Funciones para cargar GeoJSON o shapefiles.
# - Funciones para reproyecciones o transformaciones comunes.
# - Funciones de ayuda para limpieza de datos geográficos.



import geopandas as gpd
import pandas as pd

def load_gym_data(path_file: str) -> gpd.GeoDataFrame:
    """
    Carga los gimnasios desde un CSV o GeoJSON.
    Devuelve un GeoDataFrame en EPSG:4326.
    """
    # Detectar extensión del archivo
    if path_file.endswith(".csv"):
        #leemos elcsv y eliminamos filas sin lat/long
        df = pd.read_csv(path_file).dropna(subset=['lat','long'])
        # Convertimos a GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df['long'], 
            df['lat']), crs="EPSG:4326"
            )
    else:  # asumimos GeoJSON
        # Leemos el GeoJSON
        gdf = gpd.read_file(path_file)
        # Convertimos a EPSG:4326 si es necesario
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)
    return gdf

def load_barrios(path_file: str) -> gpd.GeoDataFrame:
    """
    Carga los barrios desde un GeoJSON.
    Devuelve un GeoDataFrame en EPSG:4326.
    """
    gdf = gpd.read_file(path_file)
    
    # Convertimos a EPSG:4326 si es necesario
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    
    return gdf

