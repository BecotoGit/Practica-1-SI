import sqlite3
import pandas as pd
import numpy as np

# Conectar a la base de datos
conn = sqlite3.connect('datos.db')

def obtener_datos_fraude():
    query = """
    SELECT ce.id_empleado, COUNT(te.id_ticket) AS num_incidentes,
           COUNT(ce.id_contacto) AS num_actuaciones, SUM(ce.tiempo) AS total_tiempo,
           AVG(ce.tiempo) AS media_tiempo, MIN(ce.tiempo) AS min_tiempo, 
           MAX(ce.tiempo) AS max_tiempo
    FROM contactos_con_empleados ce
    JOIN tickets_emitidos te ON ce.id_ticket = te.id_ticket
    WHERE te.tipo_incidencia = 5  -- Solo fraudes
    GROUP BY ce.id_empleado;
    """
    df = pd.read_sql_query(query, conn)
    df['mediana_tiempo'] = df['total_tiempo'].median()
    df['varianza_tiempo'] = df['total_tiempo'].var()
    return df

# Obtener los datos
df_fraude = obtener_datos_fraude()

# Mostrar resultados por empleado
print("\n--- Estadísticas por empleado ---\n")
for index, row in df_fraude.iterrows():
    print(f"Empleado ID: {row['id_empleado']}")
    print(f"Número total de incidentes: {row['num_incidentes']}")
    print(f"Número total de actuaciones: {row['num_actuaciones']}")
    print(f"Tiempo total invertido: {row['total_tiempo']:.2f} horas")
    print(f"Mediana del tiempo por contacto: {row['mediana_tiempo']:.2f} horas")
    print(f"Media del tiempo por contacto: {row['media_tiempo']:.2f} horas")
    print(f"Varianza del tiempo por contacto: {row['varianza_tiempo']:.2f}")
    print(f"Tiempo mínimo en un contacto: {row['min_tiempo']:.2f} horas")
    print(f"Tiempo máximo en un contacto: {row['max_tiempo']:.2f} horas")
    print("--------------------------------------------------------")
