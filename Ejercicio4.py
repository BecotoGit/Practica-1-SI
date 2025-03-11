import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Conectar a la base de datos
conn = sqlite3.connect('datos.db')

# Calcular la media de tiempo (apertura-cierre) de los incidentes agrupando entre los que son de mantenimiento y los que no
df_tiempo_mantenimiento = pd.read_sql_query('''
    SELECT es_mantenimiento, 
           AVG(julianday(fecha_cierre) - julianday(fecha_apertura)) as tiempo_promedio
    FROM tickets_emitidos
    GROUP BY es_mantenimiento
''', conn)

# Graficar los resultados
df_tiempo_mantenimiento['es_mantenimiento'] = df_tiempo_mantenimiento['es_mantenimiento'].map({1: 'Mantenimiento', 0: 'No Mantenimiento'})
df_tiempo_mantenimiento.set_index('es_mantenimiento', inplace=True)

df_tiempo_mantenimiento.plot(kind='bar', legend=False)
plt.title('Media de tiempo (apertura-cierre) de los incidentes')
plt.xlabel('Tipo de Incidente')
plt.ylabel('Tiempo Promedio (días)')
plt.xticks(rotation=0)
plt.show()
