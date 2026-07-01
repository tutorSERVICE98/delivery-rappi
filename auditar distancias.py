import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import contextily as ctx

# ================================
# 1️⃣ DATOS
# ================================
lon_o = float("-75,6061577".replace(",", "."))
lat_o = float("6,1585028".replace(",", "."))

lon_d = float("-75,561309".replace(",", "."))
lat_d = float("6,18471".replace(",", "."))

distancia_previa = 32483.9705

# ================================
# 2️⃣ RED Y PROYECCIÓN
# ================================
G = ox.graph_from_place(
    [ "Medellín, Colombia",
    "Bello, Colombia",
    "Itagüí, Colombia",
    "Envigado, Colombia",
    "Sabaneta, Colombia",
    "La Estrella, Colombia",
    "Copacabana, Colombia",
    "Girardota, Colombia",
    "Barbosa, Colombia",
    "Caldas, Colombia"
    ],
    network_type="drive"
)

# 🔥 IMPORTANTE: proyectar para usar mapa base
G = ox.project_graph(G)

# ================================
# 3️⃣ NODOS (OJO: usar coordenadas proyectadas)
# ================================
# convertir puntos a sistema del grafo
import pyproj
project = pyproj.Transformer.from_crs("EPSG:4326", G.graph["crs"], always_xy=True)

x_o, y_o = project.transform(lon_o, lat_o)
x_d, y_d = project.transform(lon_d, lat_d)

node_origen = ox.distance.nearest_nodes(G, X=x_o, Y=y_o)
node_destino = ox.distance.nearest_nodes(G, X=x_d, Y=y_d)

# ================================
# 4️⃣ RUTA
# ================================
ruta = nx.shortest_path(G, node_origen, node_destino, weight="length")

distancia_actual = nx.shortest_path_length(G, node_origen, node_destino, weight="length")

# ================================
# 5️⃣ GRAFICAR
# ================================
fig, ax = ox.plot_graph_route(
    G,
    ruta,
    route_color="red",
    route_linewidth=3,
    node_size=0,
    show=False,
    close=False
)

# ================================
# 6️⃣ PUNTOS
# ================================
ax.scatter(x_o, y_o, c="blue", s=100, label="Origen real")
ax.scatter(x_d, y_d, c="green", s=100, label="Destino real")

# nodos
xn_o = G.nodes[node_origen]["x"]
yn_o = G.nodes[node_origen]["y"]

xn_d = G.nodes[node_destino]["x"]
yn_d = G.nodes[node_destino]["y"]

ax.scatter(xn_o, yn_o, c="cyan", s=80, label="Nodo origen")
ax.scatter(xn_d, yn_d, c="yellow", s=80, label="Nodo destino")

# ================================
# 7️⃣ MAPA BASE 🔥
# ================================
ctx.add_basemap(
    ax,
    source=ctx.providers.OpenStreetMap.Mapnik
)

# ================================
# 8️⃣ TEXTO
# ================================
texto = (
    f"Previa: {distancia_previa:.1f} m\n"
    f"Actual: {distancia_actual:.1f} m"
)

ax.text(
    0.02, 0.98, texto,
    transform=ax.transAxes,
    fontsize=10,
    verticalalignment='top',
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
)

plt.legend()
plt.title("Ruta sobre mapa base")
plt.show()