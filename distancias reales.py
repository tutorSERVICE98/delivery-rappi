import osmnx as ox
import networkx as nx
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

df = pd.read_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\datos_con_errores.xlsx")
for col in ["LNG_STORE","LAT_STORE","LNG_ORDER","LAT_ORDER"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

G = ox.graph_from_place(
    [ 
        "Medellín, Colombia",
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


df["node_origen"] = ox.distance.nearest_nodes(
    G,
    X=df["LNG_STORE"].values,
    Y=df["LAT_STORE"].values
)

df["node_destino"] = ox.distance.nearest_nodes(
    G,
    X=df["LNG_ORDER"].values,
    Y=df["LAT_ORDER"].values
)

G = ox.project_graph(G)

def calcular_distancia(row):
    try:
        return nx.shortest_path_length(
            G,
            row["node_origen"],
            row["node_destino"],
            weight="length"
        )
    except nx.NetworkXNoPath:
        return -1  # sin conexión
    except Exception as e:
        return -2  # error real

df["distancia_m"] = df.progress_apply(calcular_distancia, axis=1)

df.to_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\distancias_con_errores.xlsx", index=False)