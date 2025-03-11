import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar a la base de datos
conn = sqlite3.connect('datos.db')

#4.1 Calcular la media de tiempo (apertura-cierre) de los incidentes agrupando entre los que son de mantenimiento y los que no
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

#4.2 Mostrar de incidente una gráfica de “bigotes”.
def obtener_tiempos_resolucion():
    query = """
    SELECT te.tipo_incidencia, 
           julianday(te.fecha_cierre) - julianday(te.fecha_apertura) AS tiempo_resolucion
    FROM tickets_emitidos te
    WHERE te.fecha_cierre IS NOT NULL;
    """
    df = pd.read_sql_query(query, conn)
    return df


# Obtener los datos
df_resolucion = obtener_tiempos_resolucion()


tipos_incidentes = df_resolucion['tipo_incidencia'].unique()

for tipo in tipos_incidentes:
    df_filtrado = df_resolucion[df_resolucion['tipo_incidencia'] == tipo]

    plt.figure(figsize=(8, 5))
    sns.boxplot(y=df_filtrado['tiempo_resolucion'], showfliers=False)

    percentiles = df_filtrado['tiempo_resolucion'].quantile([0.05, 0.90])
    plt.scatter(0, percentiles[0.05], color='red', label='Percentil 5%')
    plt.scatter(0, percentiles[0.90], color='green', label='Percentil 90%')

    plt.ylabel("Tiempo de Resolución (días)")
    plt.title(f"Distribución del Tiempo de Resolución - Tipo {tipo}")
    plt.legend()
    plt.grid()

    # Mostrar gráfico
    plt.show()
