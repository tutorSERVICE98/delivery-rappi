import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point

# ==============================
# 1. Cargar datos Excel
# ==============================
df = pd.read_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_cleaned.xlsx")
df["LAT_ORDER"] = df["LAT_ORDER"].astype(str).str.replace(",", ".").astype(float)
df["LNG_ORDER"] = df["LNG_ORDER"].astype(str).str.replace(",", ".").astype(float)
df_unique = df[["LAT_ORDER", "LNG_ORDER"]].drop_duplicates()

geometry = [Point(xy) for xy in zip(df_unique["LNG_ORDER"], df_unique["LAT_ORDER"])]

gdf_puntos = gpd.GeoDataFrame(df_unique, geometry=geometry, crs="EPSG:4326")

# ==============================
# 2. Descargar municipios (Valle de Aburrá)
# ==============================
lugares = [
    "Medellín, Colombia",
    "Bello, Colombia",
    "Itagüí, Colombia",
    "Envigado, Colombia",
    "Sabaneta, Colombia",
    "La Estrella, Colombia",
    "Caldas, Antioquia, Colombia",
    "Copacabana, Colombia",
    "Girardota, Colombia",
    "Barbosa, Antioquia, Colombia"
]

municipios_lista = []

for lugar in lugares:
    try:
        gdf = ox.features_from_place(
            lugar,
            tags={"boundary": "administrative", "admin_level": "6"}
        )
        municipios_lista.append(gdf)
    except:
        print(f"No se pudo descargar: {lugar}")

municipios = pd.concat(municipios_lista)

# Filtrar polígonos
municipios = municipios[municipios.geometry.type.isin(["Polygon", "MultiPolygon"])]

# Limpiar columnas
municipios = municipios[["name", "geometry"]]
municipios = municipios.rename(columns={"name": "municipio"})
# ==============================
# FILTRO MUNICIPIOS REALES
# ==============================

municipios = municipios[
    municipios["municipio"].isin([
        "Medellín", "Bello", "Itagüí", "Envigado",
        "Sabaneta", "La Estrella", "Caldas",
        "Copacabana", "Girardota", "Barbosa"
    ])
].copy()

municipios = municipios.dissolve(by="municipio").reset_index()
# ==============================
# DETECTAR PUNTOS FUERA DEL VALLE
# ==============================

# Spatial join SOLO con municipios
test_mpio = gpd.sjoin(gdf_puntos, municipios, how="left", predicate="within")

# Puntos fuera = municipio es NaN
fuera_valle = test_mpio[test_mpio["municipio"].isna()].copy()

# Puntos dentro
dentro_valle = test_mpio[test_mpio["municipio"].notna()].copy()

print(f"Puntos dentro del Valle: {len(dentro_valle)}")
print(f"Puntos fuera del Valle: {len(fuera_valle)}")
fuera_valle.to_excel("puntos_fuera_valle.xlsx", index=False)

# ==============================
# 3. Descargar comunas de Medellín
# ==============================
comunas = ox.features_from_place(
    "Medellín, Antioquia, Colombia",
    tags={"boundary": "administrative"}
)

# Filtrar por nivel administrativo
comunas = comunas[
    (comunas.get("admin_level") == "8") &
    (comunas.geometry.type.isin(["Polygon", "MultiPolygon"]))
].copy()

# Limpiar columnas
comunas = comunas[["name", "geometry"]]
comunas = comunas.rename(columns={"name": "comuna"})

# ==============================
# 🔥 FILTRAR COMUNAS OFICIALES (CLAVE)
# ==============================

comunas_validas = [
    "Comuna 1 - Popular",
    "Comuna 2 - Santa Cruz",
    "Comuna 3 - Manrique",
    "Comuna 4 - Aranjuez",
    "Comuna 5 - Castilla",
    "Comuna 6 - Doce de Octubre",
    "Comuna 7 - Robledo",
    "Comuna 8 - Villa Hermosa",
    "Comuna 9 - Buenos Aires",
    "Comuna 10 - La Candelaria",
    "Comuna 11 - Laureles-Estadio",
    "Comuna 12 - La América",
    "Comuna 13 - San Javier",
    "Comuna 14 - El Poblado",
    "Comuna 15 - Guayabal",
    "Comuna 16 - Belén"
]

comunas = comunas[
    comunas["comuna"].isin(comunas_validas)
].copy()

# ==============================
# FILTRAR SOLO COMUNAS DENTRO DE MEDELLÍN
# ==============================

medellin = municipios[municipios["municipio"] == "Medellín"]

comunas = gpd.sjoin(comunas, medellin, predicate="intersects")

# Limpiar columnas después del join
comunas = comunas[["comuna", "geometry"]]

import folium
from folium.plugins import MarkerCluster

# ==============================
# MAPA INTERACTIVO
# ==============================

# Centro del mapa (Medellín)
mapa = folium.Map(location=[6.25, -75.57], zoom_start=11)

# Municipios
folium.GeoJson(
    municipios,
    name="Municipios",
    style_function=lambda x: {
        "color": "black",
        "weight": 1,
        "fillOpacity": 0
    }
).add_to(mapa)

# Comunas
folium.GeoJson(
    comunas,
    name="Comunas Medellín",
    style_function=lambda x: {
        "color": "blue",
        "weight": 1,
        "fillOpacity": 0
    }
).add_to(mapa)

# Cluster de puntos (mejor rendimiento)
cluster = MarkerCluster().add_to(mapa)

# Puntos dentro (verde)
for _, row in dentro_valle.iterrows():
    folium.CircleMarker(
        location=[row["LAT_ORDER"], row["LNG_ORDER"]],
        radius=3,
        color="green",
        fill=True
    ).add_to(cluster)

# Puntos fuera (rojo)
for _, row in fuera_valle.iterrows():
    folium.CircleMarker(
        location=[row["LAT_ORDER"], row["LNG_ORDER"]],
        radius=4,
        color="red",
        fill=True
    ).add_to(cluster)

# Control de capas
folium.LayerControl().add_to(mapa)

# Guardar
mapa.save(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\Nueva carpeta\mapa_cluster_clientes.html")

import webbrowser
webbrowser.open(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\Nueva carpeta\mapa_cluster_clientes.html")

gdf_puntos = dentro_valle.copy()
# ==============================
# 4. Spatial Join con municipios
# ==============================
join_mpio = gdf_puntos.copy()
# ==============================
# 5. Spatial Join con comunas
# ==============================
join_comuna = gpd.sjoin(join_mpio, comunas, how="left", predicate="within")

# ==============================
# 6. Crear variable final "zona"
# ==============================
join_comuna["zona"] = join_comuna["comuna"].fillna(join_comuna["municipio"])

# ==============================
# 7. Clasificar tipo
# ==============================
join_comuna["tipo"] = join_comuna["comuna"].apply(
    lambda x: "comuna" if pd.notnull(x) else "municipio"
)

# ==============================
# 8. AGRUPAR Y CONTAR
# ==============================
conteo = (
    join_comuna
    .groupby(["tipo", "zona"])
    .size()
    .reset_index(name="conteo")
)

# ==============================
# 9. Guardar resultados
# ==============================
conteo.to_excel("conteo_zonas_osm.xlsx", index=False)


# ==============================
# MAPA BASE (SATELITAL)
# ==============================

mapa_final = folium.Map(
    location=[6.25, -75.57],
    zoom_start=11,
    tiles=None
)

# Capa tipo satélite (alternativa libre)
folium.TileLayer(
    tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
    name="Base",
    attr="© OpenStreetMap contributors"
).add_to(mapa_final)

# ==============================
# Preparar datos
# ==============================

zonas = pd.concat([
    comunas.assign(zona=comunas["comuna"]),
    municipios.assign(zona=municipios["municipio"])
])
zonas = zonas.dissolve(by="zona").reset_index()
zonas = zonas.merge(conteo, on="zona", how="left")
zonas["conteo"] = zonas["conteo"].fillna(0)

# ==============================
# Dibujar polígonos (SIN color por conteo)
# ==============================

def estilo(feature):
    return {
        "fillColor": "none",
        "color": "blue",
        "weight": 2
    }

def popup(feature):
    nombre = feature["properties"]["zona"]
    conteo = feature["properties"]["conteo"]
    return folium.Popup(f"<b>{nombre}</b><br>Tiendas: {int(conteo)}")

folium.GeoJson(
    zonas,
    style_function=estilo,
    popup=popup,
    tooltip=folium.GeoJsonTooltip(fields=["zona"])
).add_to(mapa_final)

# ==============================
# LEYENDA PERSONALIZADA (tabla)
# ==============================

tabla = zonas[zonas["conteo"] > 0][["zona", "conteo"]]
tabla = tabla.sort_values(by="conteo", ascending=False)

# Crear HTML de la leyenda
html_leyenda = """
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 300px;
height: 400px;
overflow-y: scroll;
background-color: white;
border:2px solid grey;
z-index:9999;
font-size:14px;
padding:10px;
">
<b>Conteo por zona</b><br>
"""

for _, row in tabla.iterrows():
    html_leyenda += f"{row['zona']}: {int(row['conteo'])}<br>"

html_leyenda += "</div>"

mapa_final.get_root().html.add_child(folium.Element(html_leyenda))

# ==============================
# Guardar y abrir
# ==============================

mapa_final.save(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\Nueva carpeta\mapa_conteo_clientes.html")

webbrowser.open(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\Nueva carpeta\mapa_conteo_clientes.html")

print("🌍 Mapa final listo")
print("✅ Proceso completado correctamente")