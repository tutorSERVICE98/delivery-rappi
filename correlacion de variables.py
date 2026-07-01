import pandas as pd
import numpy as np

# =========================
# 1️⃣ Leer archivo de Excel
# =========================
# Cambia la ruta por la de tu archivo
ruta_archivo = r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_con_lluvia3.xlsx"

df = pd.read_excel(ruta_archivo)

# Tomar solo columnas numéricas

df_num_consolidado = df[['ORDER_VALUE', 'ORDER_TOTAL_TIME', 'COOKING_TIME', 'RT_AT_STORE_TIME',
       'RT_TO_USER_TIME', 'RT_WAITING_USER_TIME', 'RT_DISTANCE_TO_STORE',
       'RT_DISTANCE_TO_USER', 'USER_STORE_DISTANCE', 'distancia_m','lluvia']]
df_num_2019=df_num_consolidado.iloc[1:344,:]
df_num_2020=df_num_consolidado.iloc[1:117453,:]
df_num_2023=df_num_consolidado.iloc[117453:240549,:]
df_num=df_num_2023

print("Columnas numéricas utilizadas:")
print(df_num.columns)
print("\n")

# =========================
# 2️⃣ Matriz de correlación
# =========================
R = df_num.corr()

print("Matriz de correlación:")
print(R)
print("\n")

# Convertir a numpy array
R_np = R.values

# =========================
# 3️⃣ Inversa de la matriz
# =========================
# Verificar si es invertible
det = np.linalg.det(R_np)

if abs(det) > 1e-10:
    R_inv = np.linalg.inv(R_np)
    print("Se utilizó la inversa normal.")
else:
    R_inv = np.linalg.pinv(R_np)
    print("La matriz no es invertible. Se utilizó la pseudo-inversa.")

print("\nMatriz inversa:")
print(R_inv)
print("\n")

# =========================
# 4️⃣ Extraer diagonal principal
# =========================
vector_diag = np.diag(R_inv)

print("Diagonal principal de la inversa:")
print(vector_diag)
print("\n")

# =========================
# 5️⃣ Inverso multiplicativo
# =========================
vector_inv_mult = 1 / vector_diag

print("Inverso multiplicativo de la diagonal:")
print(vector_inv_mult)
print("\n")

# =========================
# 6️⃣ Multiplicar por (-1)
# =========================
vector_neg = -1 * vector_inv_mult

print("Después de multiplicar por -1:")
print(vector_neg)
print("\n")

# =========================
# 7️⃣ Sumar 1 a cada componente
# =========================
vector_final = 1 + vector_neg

resultado = pd.Series(vector_final, index=R.columns)
print("\nVector final con nombres de variables:")
print(resultado)