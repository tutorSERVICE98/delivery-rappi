import pandas as pd

# =========================
# 1. Cargar pedidos
# =========================
orders = pd.read_excel(
    r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_con_estaciones.xlsx"
)

# Convertir fecha_hora
orders['fecha_hora'] = pd.to_datetime(
    orders['fecha_hora']
)

# ==========================================
# 2. Crear fecha corregida por duración
# ==========================================
# ORDER_TOTAL_TIME está en segundos

orders['fecha_fin'] = (
    orders['fecha_hora'] +
    pd.to_timedelta(orders['ORDER_TOTAL_TIME'], unit='s')
)

# Redondear ambas fechas al minuto
orders['fecha_inicio_min'] = orders['fecha_hora'].dt.floor('min')
orders['fecha_fin_min'] = orders['fecha_fin'].dt.floor('min')


# =========================
# 3. Definir rangos
# =========================
rangos = [
    (10, 1, 47),
    (36, 48, 118627),
    (40, 118628, 131188),
    (44, 131189, 131198),
    (51, 131199, 140350),
    (62, 140351, 140470),
    (67, 140471, 163129),
    (104, 163130, 172802),
    (127, 172803, 174866),
    (132, 174867, 212260),
    (133, 212261, 240549)
]

resultados = []


# =========================
# 4. Procesar cada estación
# =========================
for id_estacion, inicio, fin in rangos:

    print(f"Procesando estación {id_estacion}")

    # ==================================
    # Pedidos de esta estación
    # ==================================
    df_pedidos = orders.iloc[inicio:fin+1].copy()

    # ==================================
    # Cargar archivo pluviométrico
    # ==================================
    archivo = rf"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\análisis_pluviometria\estacion_pluviometrica_{id_estacion}.xlsx"

    df_est = pd.read_excel(archivo)

    # Procesar fechas
    df_est['fecha_hora'] = pd.to_datetime(df_est['fecha_hora'])

    # Redondear a minuto
    df_est['fecha_min'] = df_est['fecha_hora'].dt.floor('min')

    # Reducir columnas
    df_est = df_est[['fecha_min', 'p_max']]

    # Evitar duplicados
    df_est = df_est.drop_duplicates(subset=['fecha_min'])

    # ==================================
    # Crear diccionario:
    # minuto -> p_max
    # ==================================
    lluvia_dict = dict(
        zip(df_est['fecha_min'], df_est['p_max'])
    )

    # ==================================
    # Evaluar lluvia dentro del intervalo
    # ==================================
    lluvia_resultado = []

    for _, row in df_pedidos.iterrows():

        inicio_tiempo = row['fecha_inicio_min']
        fin_tiempo = row['fecha_fin_min']

        # Crear rango minuto a minuto
        rango_minutos = pd.date_range(
            start=inicio_tiempo,
            end=fin_tiempo,
            freq='min'
        )

        # Verificar si en algún minuto hubo lluvia
        hubo_lluvia = 0

        for minuto in rango_minutos:

            p = lluvia_dict.get(minuto, 0)

            if pd.notna(p) and p > 0:
                hubo_lluvia = 1
                break

        lluvia_resultado.append(hubo_lluvia)

    # Agregar variable lluvia
    df_pedidos['lluvia'] = lluvia_resultado

    # Guardar resultado parcial
    resultados.append(df_pedidos)


# =========================
# 5. Unir resultados
# =========================
resultado_final = pd.concat(
    resultados,
    ignore_index=True
)

# =========================
# 6. Guardar archivo final
# =========================
resultado_final.to_excel(
    r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_con_lluvia3.xlsx",
    index=False
)

print("archivo creado")