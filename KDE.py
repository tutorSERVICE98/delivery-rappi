from scipy.stats import gaussian_kde
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Cargar datos
df = pd.read_excel(r"C:\Users\CT\OneDrive\Escritorio\TUTOR SERVICE\RAPPI\mde_orders_cleaned.xlsx")

data = df["ORDER_VALUE"].values

kde = gaussian_kde(data)  # bandwidth automático (DEFECTO=Scott)
#kde = gaussian_kde(data, bw_method='silverman')
x_vals = np.linspace(data.min(), data.max(), 1000)
y_vals = kde(x_vals)

plt.plot(x_vals, y_vals)
plt.fill_between(x_vals, y_vals, alpha=0.3)

plt.xlabel("ORDER_VALUE")
plt.ylabel("Densidad")
plt.title("KDE_gaussiano valor del pedido")
plt.show()