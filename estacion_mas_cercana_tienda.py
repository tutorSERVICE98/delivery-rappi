import pandas as pd

# Cargar archivos
estaciones = pd.read_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\estaciones.xlsx")
tiendas = pd.read_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_cleaned.xlsx")

tiendas_unicas = tiendas[['LAT_STORE', 'LNG_STORE']].drop_duplicates().reset_index(drop=True)
import numpy as np

from sklearn.neighbors import BallTree

# Convertir a radianes
coords_estaciones = np.radians(estaciones[['Latitud', 'Longitud']].to_numpy())
coords_tiendas = np.radians(tiendas_unicas[['LAT_STORE', 'LNG_STORE']].to_numpy())

# Crear árbol con Haversine
tree = BallTree(coords_estaciones, metric='haversine')

# Buscar estación más cercana
distancias, indices = tree.query(coords_tiendas, k=1)

# Convertir a km
radio_tierra_km = 6371
distancias_km = distancias * radio_tierra_km

# Guardar resultados
tiendas_unicas['dist_min_km'] = distancias_km.flatten()
tiendas_unicas['estacion_cercana'] = indices.flatten()

resultado_final = tiendas.merge(
    tiendas_unicas,
    on=['LAT_STORE', 'LNG_STORE'],
    how='left'
)

resultado_final.to_excel(
    r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_con_estaciones_2.xlsx",
    index=False
)