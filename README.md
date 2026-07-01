# delivery-rappi
Compilación de códigos usados para el articulo de ingeniería inversa

Archivo distancias reales: Con este codigo se puede calcular distancias terrestres reales y acordes a la malla vial de la ciudad en cuestión, como datos de entrada le damos las coordenadas longitud y latitud del punto de partida al punto de llegada, en nuestro caso restaurantes y clientes respectivamente.

Archivo auditar distancias: Dado que el anterior codigo estaba produciendo unos errores se vio necesario auditar ese codigo mediante generación de mapas visuales para pobservar que estaba pasando con aquellas rutas restaurante cliente que estaban mostrando distancias demasiado grandes.

Archivo correlación de variables: Con este codigo se puede calcular el coeficiente de determinación Múltiple para cada variable predictora, y es un valor que indica que tan bien puede ser predicha una variable a partir de las demas variables del conjunto de datos, toma un valor entre 0 y 1 donde 1 es mejor predicha por las demas variables y 0 es no muy bien predicha por als demas variables.

Archivo estacion_mas_cercana_tienda: Con este codigo se realiza la asignación de cada restaurante con su estación pluviometrica mas cercana en fechas posteriores a la instalación de dicha estación. Este paso es importante para la creación de la variable lluvia, porque debemos saber en que conjunto de registros pluviometricos buscar la fecha y hora en la que ocurren cada uno de los pedidos para designar a ese pedido con un 0 si no hubo lluvia y con 1 si hubo registro de lluvia.

Archivo merge_lluvia_3: En este codigo se sigue con el segundo apso del anterior codigo, su algoritmo busca en la estación que fue asignada a cada restaurante la fecha y hora del pedido + tiempo de cocción y si el registro pluviometrico marca un valor mayor a 0 en alguno de los 2 sensores pues asigna 1 a la variable binaria lluvia a ese pedido en particular.

Archivo mapa medellin y conteo por comunas: Con este codigo se hace un conteo de restaurantes y clientes en zonas especificas delimitadas por comunas. También este genera un mapa interactivo donde se puede visualizar las coordenadas altitud y longitud dentro de cada poligono (comuna).

Archivo modelo_lineal_efectos_mix: Genera un modelo lineal de efectos mixtos para una variable de respuesta o efecto fijo y unas variables de efectos aleatorios.

Archivo regre_lineal_con_lluvia: una regresión lineal común para medir el coeficiente de la variable binaria 'lluvia' debido al desbalances de ceros y unos se tuvo que sacar una submuestra aleatoria de pedidos sin registro de precipitación.

Archivo regre_lineal_filtro_residuos: Con este codigo se implementa el filtro de pedidos atipicos, para aquellas predicciones de un modelo lineal que arrojan un residuo con los datos reales muy altos, así se elimina el pededido que muestra el mayor residuo en valor absoluto, de manera iterativa hasta llegar a un limite minímo de pedidos en la base de datos.

Archivo regresión lineal: Algoritmo de generación de un modelo lineal para un conjunto de datos.

Archivo KDE: Este algoritmo construye una función de densidad con funciones kernel, que su función es asignar los pesos que se le asignan a cada observación de una muestra. Apartir de ahi se construve la estimación de la función de densidad de probabilidad de la variable de interes usando la funcíon de densidad kernel. Con esto se aproxima la función de densidad real.
