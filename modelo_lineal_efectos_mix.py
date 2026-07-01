import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# =========================
# 1. Cargar datos
# =========================
df = pd.read_excel(
    r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\muestra_final_filtrada_2.xlsx"
)

# =========================
# 2. Crear ID restaurante
# =========================
# Redondear para evitar problemas decimales
df['LAT_STORE'] = df['LAT_STORE'].round(12)
df['LNG_STORE'] = df['LNG_STORE'].round(12)

# Crear identificador único
df['restaurant_id'] = (
    df['LAT_STORE'].astype(str)
    + "_"
    + df['LNG_STORE'].astype(str)
)

# =========================
# 3. Seleccionar variables
# =========================
df_modelo = df[
    [
        'ORDER_VALUE',
        'lluvia',
        'USER_STORE_DISTANCE',
        'ORDER_TOTAL_TIME',
        'restaurant_id'
    ]
].dropna()
conteos = df_modelo['restaurant_id'].value_counts()

validos = conteos[conteos >= 500].index

df_modelo = df_modelo[
    df_modelo['restaurant_id'].isin(validos)
]
# =========================
# 4. Ajustar MixedLM
# =========================
modelo = smf.mixedlm(
    "ORDER_VALUE ~ lluvia + USER_STORE_DISTANCE + ORDER_TOTAL_TIME",
    data=df_modelo,
    groups=df_modelo["restaurant_id"]
)

resultado = modelo.fit()
df_modelo['residuo'] = resultado.resid
plt.figure(figsize=(6,6))

plt.boxplot(df_modelo['residuo'])

plt.ylabel("Residuo")

plt.title("Boxplot residuos")

plt.show()
# =========================
# 5. Mostrar resultados
# =========================
intercepto_global = resultado.fe_params['Intercept']

for restaurante, efecto in resultado.random_effects.items():

    intercepto_restaurante = (
        intercepto_global
        + efecto.iloc[0]
    )

    print(
        restaurante,
        "Intercepto:",
        round(intercepto_restaurante,2)
    )
y_real = df_modelo['ORDER_VALUE']
y_pred = resultado.fittedvalues

plt.figure(figsize=(8,8))

plt.hexbin(
    y_pred,
    y_real,
    gridsize=50
)

xmin = min(y_pred.min(), y_real.min())
xmax = max(y_pred.max(), y_real.max())

plt.plot(
    [xmin, xmax],
    [xmin, xmax],
    '--'
)

plt.xlabel("Predicho")
plt.ylabel("Observado")

plt.title("Observado vs Predicho")

plt.colorbar(label="Cantidad de pedidos")

plt.show()
print(resultado.summary())