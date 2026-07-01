import pandas as pd
import statsmodels.api as sm
import time

# =====================================
# 1. Cargar datos
# =====================================
df = pd.read_excel(
    r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_con_lluvia3.xlsx"
)

# =====================================
# 2. Crear ID único
# =====================================
df['pedido_id'] = df.index

# =====================================
# 3. Separar por lluvia
# =====================================
df_lluvia = df[df['lluvia'] == 1]
df_no_lluvia = df[df['lluvia'] == 0]

print("Pedidos con lluvia:", len(df_lluvia))
print("Pedidos sin lluvia:", len(df_no_lluvia))

# =====================================
# 4. Variables auxiliares
# =====================================

# Este es el R2 de la MEJOR MUESTRA
# ANTES del filtro residual
mejor_R2_muestra = 0

# Guardar mejor resultado final
mejor_R2_filtrado = 0
mejor_muestra_filtrada = None
mejor_eliminados = None
mejor_modelo = None

# Tiempo máximo de búsqueda
TIEMPO_MAXIMO = 15 * 60  # 30 minutos

# =====================================
# 5. WHILE PRINCIPAL
# =====================================
while True:

    # =================================
    # INICIO TEMPORIZADOR
    # =================================
    inicio_busqueda = time.time()

    nueva_muestra_encontrada = False

    # =================================
    # BUSCAR NUEVA MUESTRA
    # =================================
    while True:

        # -----------------------------
        # Verificar tiempo
        # -----------------------------
        tiempo_actual = time.time()

        if tiempo_actual - inicio_busqueda > TIEMPO_MAXIMO:

            break

        # -----------------------------
        # Tomar muestra aleatoria
        # -----------------------------
        muestra_no_lluvia = df_no_lluvia.sample(n=20000)

        df_modelo = pd.concat(
            [muestra_no_lluvia, df_lluvia]
        )

        # -----------------------------
        # Variables modelo
        # -----------------------------
        X = df_modelo[
            [
                'lluvia',
                'USER_STORE_DISTANCE',
                'ORDER_TOTAL_TIME',
                'RT_WAITING_USER_TIME', 
                'RT_DISTANCE_TO_STORE'
            ]
        ]

        y = df_modelo['ORDER_VALUE']

        X = sm.add_constant(X)

        modelo = sm.OLS(y, X).fit()

        R2_muestra = modelo.rsquared

        # -----------------------------
        # ¿Nueva mejor muestra?
        # -----------------------------
        if R2_muestra > mejor_R2_muestra:

            mejor_R2_muestra = R2_muestra

            nueva_muestra_encontrada = True

            print(
                "\n1) Una muestra con mejor R2 fue hallada con R2 =",
                round(R2_muestra, 6)
            )

            break

    # =================================
    # Si no se encontró mejor muestra
    # =================================
    if not nueva_muestra_encontrada:

        break

    # =================================
    # 6. FILTRO DE RESIDUOS
    # =================================
    eliminados = []

    while True:

        # -----------------------------
        # Variables modelo
        # -----------------------------
        X = df_modelo[
            [
                'lluvia',
                'USER_STORE_DISTANCE',
                'ORDER_TOTAL_TIME',
                'RT_WAITING_USER_TIME', 
                'RT_DISTANCE_TO_STORE'
            ]
        ]

        y = df_modelo['ORDER_VALUE']

        X = sm.add_constant(X)

        modelo = sm.OLS(y, X).fit()

        R2_filtrado = modelo.rsquared

        # -----------------------------
        # CONDICIÓN 1
        # -----------------------------
        if R2_filtrado >= 0.6:

            print(
                "\n2) La muestra anterior obtuvo un R2' =",
                round(R2_filtrado, 6),
                "después del filtro de residuales."
            )

            break

        # -----------------------------
        # CONDICIÓN 2
        # -----------------------------
        if len(df_modelo) <= 18000:

            print(
                "\n2) La muestra anterior llegó al límite mínimo "
                "de 18000 pedidos con un R2' =",
                round(R2_filtrado, 6)
            )

            break

        # -----------------------------
        # Calcular residuos
        # -----------------------------
        residuos = modelo.resid

        # -----------------------------
        # Encontrar mayor residuo
        # -----------------------------
        idx_max = residuos.abs().idxmax()

        # -----------------------------
        # Guardar eliminado
        # -----------------------------
        fila_eliminada = df_modelo.loc[[idx_max]].copy()

        fila_eliminada['residuo'] = residuos.loc[idx_max]

        eliminados.append(fila_eliminada)

        # -----------------------------
        # Eliminar fila
        # -----------------------------
        df_modelo = df_modelo.drop(index=idx_max)

    # =================================
    # 7. Guardar mejor resultado final
    # =================================
    if R2_filtrado > mejor_R2_filtrado:

        mejor_R2_filtrado = R2_filtrado

        mejor_muestra_filtrada = df_modelo.copy()

        mejor_modelo = modelo

        if len(eliminados) > 0:

            mejor_eliminados = pd.concat(
                eliminados,
                ignore_index=False
            )

        else:

            mejor_eliminados = pd.DataFrame()

    # =================================
    # 8. Preguntar continuar
    # =================================
    respuesta = input(
        "\n3) ¿Buscamos una nueva muestra o salimos del while? "
        "(yes/no): "
    )

    if respuesta.lower() == "no":

        break

# =====================================
# 9. Guardar resultados finales
# =====================================

# -------------------------------------
# Guardar muestra final filtrada
# -------------------------------------
if mejor_muestra_filtrada is not None:

    mejor_muestra_filtrada.to_excel(
        r"C:\Users\CT\OneDrive\Escritorio\muestra_final_filtrada4.xlsx",
        index=False
    )

# -------------------------------------
# Guardar eliminados
# -------------------------------------
if mejor_eliminados is not None:

    mejor_eliminados.to_excel(
        r"C:\Users\CT\OneDrive\Escritorio\elementos_eliminados4.xlsx",
        index=False
    )


# =====================================
# 10. Resumen final
# =====================================
print("\n====================================")
print("Proceso finalizado satisfactoriamente")
print("====================================")

print(
    "\nMejor R2 de muestra inicial:",
    round(mejor_R2_muestra, 6)
)

print(
    "Mejor R2 filtrado:",
    round(mejor_R2_filtrado, 6)
)

if mejor_modelo is not None:

    print("\nResumen del modelo final:\n")

    print(mejor_modelo.summary())