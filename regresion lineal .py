import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm

# =========================================
# 1️⃣ Cargar datos
# =========================================
ruta_archivo = r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_variables_numericas_1.xlsx"

df = pd.read_excel(ruta_archivo)

# solo variables numéricas
df_num = df.select_dtypes(include=[np.number])

# =========================================
# 2️⃣ Separar por años (ajusta índices si hace falta)
# =========================================
data_dict = {
    "Consolidado": df_num,
    "2019": df_num.iloc[1:361, :],
    "2020": df_num.iloc[361:120390, :],
    "2023": df_num.iloc[120390:243748, :]
}

# =========================================
# 3️⃣ Función de regresión
# =========================================
def regresion_y_grafico(df, titulo):

    # limpiar datos
    df = df[["ORDER_TOTAL_TIME", "ORDER_VALUE"]].dropna()

    # ordenar (importante para la recta)
    df = df.sort_values("ORDER_TOTAL_TIME")

    X = df[["ORDER_TOTAL_TIME"]]   # 2D
    Y = df["ORDER_VALUE"]  # 1D

    # ======================
    # modelo sklearn
    # ======================
    modelo = LinearRegression()
    modelo.fit(X, Y)

    beta_0 = modelo.intercept_
    beta_1 = modelo.coef_[0]

    Y_pred = modelo.predict(X)

    # ======================
    # R²
    # ======================
    R2 = r2_score(Y, Y_pred)

    # ======================
    # statsmodels (p-valor)
    # ======================
    X_sm = sm.add_constant(X)
    modelo_sm = sm.OLS(Y, X_sm).fit()

    p_valor = modelo_sm.pvalues["ORDER_TOTAL_TIME"]

    # ======================
    # gráfico
    # ======================
    plt.figure()

    plt.scatter(df["ORDER_TOTAL_TIME"], Y)
    plt.plot(df["ORDER_TOTAL_TIME"], Y_pred)

    plt.xlabel("ORDER_TOTAL_TIME")
    plt.ylabel("ORDER_VALUE")

    texto = f"$R^2$ = {R2:.4f}\np-valor = {p_valor:.6e}"

    plt.text(
        0.05, 0.95, texto,
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict()
    )

    plt.title(f"Regresión lineal - {titulo}")
    plt.show()

    # ======================
    # resultados
    # ======================
    print(f"\n===== {titulo} =====")
    print(f"ORDER_VALUE = {beta_0:.4f} + {beta_1:.4f} * ORDER_TOTAL_TIME")
    print(f"R² = {R2:.4f}")
    print(f"p-valor = {p_valor:.6f}")


# =========================================
# 4️⃣ Ejecutar para todos
# =========================================
for nombre, data in data_dict.items():
    regresion_y_grafico(data, nombre)