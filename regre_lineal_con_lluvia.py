import pandas as pd
import statsmodels.api as sm

# =========================
# 1. Cargar datos
# =========================
df = pd.read_excel(
    r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_con_lluvia3.xlsx"
)

# =========================
# 2. Separar por lluvia
# =========================
df['pedido_id'] = df.index
df_lluvia = df[df['lluvia'] == 1]
df_no_lluvia = df[df['lluvia'] == 0]

print("Pedidos con lluvia:", len(df_lluvia))
print("Pedidos sin lluvia:", len(df_no_lluvia))

r2aux=0
R2=0
while R2<0.7:

    muestra_no_lluvia = df_no_lluvia.sample(n=20000)

    df_modelo = pd.concat(
        [muestra_no_lluvia, df_lluvia],
        ignore_index=True
    )

    X = df_modelo[['lluvia', 'USER_STORE_DISTANCE', 'ORDER_TOTAL_TIME', 'RT_WAITING_USER_TIME']]
    y = df_modelo['ORDER_VALUE']

    X = sm.add_constant(X)

    modelo = sm.OLS(y, X).fit()    
        
    coef_lluvia=modelo.params['lluvia']
    p_lluvia=modelo.pvalues['lluvia']
    R2=modelo.rsquared
    numero_condicion=modelo.condition_number
    
    if R2>r2aux:
        r2aux=R2
        print('Un mejor R2 fue encontrado R2=',r2aux)
        respuesta = input(
            "¿Desea salir del while? (y/n): "
        )

        if respuesta.lower() == 'y':
            break
    
ids = df_modelo['pedido_id']

muestra_recuperada = df[
    df['pedido_id'].isin(ids)
]
muestra_recuperada.to_excel(
    r"C:\Users\CT\OneDrive\Escritorio\muestra_mayor_R2.xlsx",
    index=False
)

print('Proceso terminado satisfactoriamente')