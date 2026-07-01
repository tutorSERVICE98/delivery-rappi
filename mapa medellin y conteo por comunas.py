import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point

# ==============================
# 1. Cargar datos Excel
# ==============================
df = pd.read_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_cleaned.xlsx")
df["LAT_STORE"] = df["LAT_STORE"].astype(str).str.replace(",", ".").astype(float)
df["LNG_STORE"] = df["LNG_STORE"].astype(str).str.replace(",", ".").astype(float)
df_unique = df[["LAT_STORE", "LNG_STORE"]].drop_duplicates()

geometry = [Point(xy) for xy in zip(df_unique["LNG_STORE"], df_unique["LAT_STORE"])]

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
        location=[row["LAT_STORE"], row["LNG_STORE"]],
        radius=3,
        color="green",
        fill=True
    ).add_to(cluster)

# Puntos fuera (rojo)
for _, row in fuera_valle.iterrows():
    folium.CircleMarker(
        location=[row["LAT_STORE"], row["LNG_STORE"]],
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

# =====================================================
# CONTEO DE TIENDAS POR COMUNA
# =====================================================

import matplotlib.pyplot as plt

# Solo puntos que quedaron dentro de una comuna
tiendas_comunas = join_comuna[
    join_comuna["comuna"].notna()
].copy()

# Conteo
conteo_comunas = (
    tiendas_comunas
    .groupby("comuna")
    .size()
    .reset_index(name="tiendas")
)

# Orden descendente
conteo_comunas = conteo_comunas.sort_values(
    by="tiendas",
    ascending=False
)

print(conteo_comunas)

# =====================================================
# UNIR CONTEOS AL SHAPE DE COMUNAS
# =====================================================

comunas_plot = comunas.merge(
    conteo_comunas,
    on="comuna",
    how="left"
)

comunas_plot["tiendas"] = (
    comunas_plot["tiendas"]
    .fillna(0)
    .astype(int)
)

# =====================================================
# MAPA PLANO DE COMUNAS
# =====================================================

fig, ax = plt.subplots(
    figsize=(12, 10)
)

comunas_plot.plot(
    column="tiendas",
    cmap="YlOrRd",
    edgecolor="black",
    linewidth=1,
    legend=True,
    ax=ax,
    legend_kwds={
        "label": "Número de tiendas"
    }
)

# Etiquetas sobre cada comuna
for _, row in comunas_plot.iterrows():

    centro = row.geometry.centroid

    nombre = (
        row["comuna"]
        .replace("Comuna ", "")
        .replace(" - ", "\n")
    )

    ax.annotate(
        text=nombre,
        xy=(centro.x, centro.y),
        ha="center",
        fontsize=7
    )

ax.set_title(
    "Distribución de Tiendas por Comuna - Medellín",
    fontsize=16,
    fontweight="bold"
)

ax.axis("off")

plt.tight_layout()

plt.savefig(
    "mapa_comunas_medellin.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# =====================================================
# PREPARAR NOMBRES CORTOS PARA BARRAS
# =====================================================

conteo_comunas["nombre"] = (
    conteo_comunas["comuna"]
    .str.replace(r"Comuna \d+ - ", "", regex=True)
)

# =====================================================
# GRÁFICO DE BARRAS
# =====================================================

fig, ax = plt.subplots(
    figsize=(14, 6)
)

bars = ax.bar(
    conteo_comunas["nombre"],
    conteo_comunas["tiendas"]
)

# Mostrar valor encima de cada barra
for bar in bars:

    altura = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width()/2,
        altura,
        f"{int(altura)}",
        ha="center",
        va="bottom",
        fontsize=8
    )

ax.set_title(
    "Cantidad de Tiendas por Comuna",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Comuna")
ax.set_ylabel("Número de tiendas")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "barras_comunas_medellin.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# =====================================================
# EXPORTAR TABLA
# =====================================================

conteo_comunas.to_excel(
    "conteo_tiendas_comunas_medellin.xlsx",
    index=False
)

print("\nProceso terminado")
print("✓ mapa_comunas_medellin.png")
print("✓ barras_comunas_medellin.png")
print("✓ conteo_tiendas_comunas_medellin.xlsx")