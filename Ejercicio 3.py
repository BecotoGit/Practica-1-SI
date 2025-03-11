import sqlite3
import pandas as pd
import numpy as np

# Conectar a la base de datos
conn = sqlite3.connect('datos.db')

# 3.1 Por empleado
def fraude_empleados():
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
df_fraude = fraude_empleados()

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


# 3.2 Análisis por nivel de empleado (1-3)
niveles = [1, 2, 3]

print("\n--- Estadísticas por nivel de empleado ---\n")

for nivel in niveles:
    print(f"Análisis para el nivel de empleado {nivel}:")

    # Número de incidentes
    df_num_incidentes = pd.read_sql_query(f'''
        SELECT COUNT(DISTINCT t.id_ticket) as num_incidentes
        FROM tickets_emitidos t
        JOIN contactos_con_empleados c ON t.id_ticket = c.id_ticket
        JOIN empleados e ON c.id_empleado = e.id_emp
        WHERE e.nivel = {nivel}
    ''', conn)
    num_incidentes = df_num_incidentes['num_incidentes'].values[0]
    print(f"Número de incidentes: {num_incidentes}")

    # Número de actuaciones realizadas por los empleados (contactos)
    df_num_actuaciones = pd.read_sql_query(f'''
        SELECT COUNT(*) as num_actuaciones
        FROM contactos_con_empleados c
        JOIN empleados e ON c.id_empleado = e.id_emp
        WHERE e.nivel = {nivel}
    ''', conn)
    num_actuaciones = df_num_actuaciones['num_actuaciones'].values[0]
    print(f"Número de actuaciones realizadas por los empleados: {num_actuaciones}")

    # Análisis estadístico básico (mediana, media, varianza y valores máximo y mínimo)
    df_tiempos = pd.read_sql_query(f'''
        SELECT julianday(t.fecha_cierre) - julianday(t.fecha_apertura) as tiempo_incidente
        FROM tickets_emitidos t
        JOIN contactos_con_empleados c ON t.id_ticket = c.id_ticket
        JOIN empleados e ON c.id_empleado = e.id_emp
        WHERE e.nivel = {nivel}
    ''', conn)

    tiempos = df_tiempos['tiempo_incidente'].astype(float)
    mediana = tiempos.median()
    media = tiempos.mean()
    varianza = tiempos.var()
    valor_minimo = tiempos.min()
    valor_maximo = tiempos.max()

    print(f"Mediana del tiempo de incidentes: {mediana:.2f} días")
    print(f"Media del tiempo de incidentes: {media:.2f} días")
    print(f"Varianza del tiempo de incidentes: {varianza:.2f}")
    print(f"Valor mínimo del tiempo de incidentes: {valor_minimo:.2f} días")
    print(f"Valor máximo del tiempo de incidentes: {valor_maximo:.2f} días")
    print("------------------------")


# 3.3 Análisis por cliente
def obtener_datos_fraude_cliente():
    query = """
    SELECT te.id_cliente, COUNT(te.id_ticket) AS num_incidentes,
           COUNT(ce.id_contacto) AS num_actuaciones, SUM(ce.tiempo) AS total_tiempo,
           AVG(ce.tiempo) AS media_tiempo, MIN(ce.tiempo) AS min_tiempo, 
           MAX(ce.tiempo) AS max_tiempo
    FROM contactos_con_empleados ce
    JOIN tickets_emitidos te ON ce.id_ticket = te.id_ticket
    WHERE te.tipo_incidencia = 5  -- Solo fraudes
    GROUP BY te.id_cliente;
    """
    df = pd.read_sql_query(query, conn)
    df['mediana_tiempo'] = df['total_tiempo'].median()
    df['varianza_tiempo'] = df['total_tiempo'].var()
    return df


# Obtener los datos
df_fraude_cliente = obtener_datos_fraude_cliente()

# Mostrar resultados por cliente
print("\n--- Estadísticas por cliente ---\n")
for index, row in df_fraude_cliente.iterrows():
    print(f"Cliente ID: {row['id_cliente']}")
    print(f"Número total de incidentes: {row['num_incidentes']}")
    print(f"Número total de actuaciones: {row['num_actuaciones']}")
    print(f"Tiempo total invertido: {row['total_tiempo']:.2f} horas")
    print(f"Mediana del tiempo por contacto: {row['mediana_tiempo']:.2f} horas")
    print(f"Media del tiempo por contacto: {row['media_tiempo']:.2f} horas")
    print(f"Varianza del tiempo por contacto: {row['varianza_tiempo']:.2f}")
    print(f"Tiempo mínimo en un contacto: {row['min_tiempo']:.2f} horas")
    print(f"Tiempo máximo en un contacto: {row['max_tiempo']:.2f} horas")
    print("--------------------------------------------------------")

# 3.4 Análisis por tipo de incidente
tipo_incidencia_fraude = 'Fraude'

# Número de incidentes de tipo "Fraude"
df_num_incidentes_fraude = pd.read_sql_query('''
    SELECT COUNT(*) as num_incidentes
    FROM tickets_emitidos
    JOIN tipos_incidentes ON tickets_emitidos.tipo_incidencia = tipos_incidentes.id_inci
    WHERE tipos_incidentes.nombre = ?
''', conn, params=(tipo_incidencia_fraude,))
num_incidentes_fraude = df_num_incidentes_fraude['num_incidentes'].values[0]
print("Número de incidentes de tipo 'Fraude': %d" % num_incidentes_fraude)
print("------------------------")

# Número de actuaciones realizadas por los empleados (contactos) en incidentes de tipo "Fraude"
df_num_actuaciones_fraude = pd.read_sql_query('''
    SELECT COUNT(*) as num_actuaciones
    FROM contactos_con_empleados
    JOIN tickets_emitidos ON contactos_con_empleados.id_ticket = tickets_emitidos.id_ticket
    JOIN tipos_incidentes ON tickets_emitidos.tipo_incidencia = tipos_incidentes.id_inci
    WHERE tipos_incidentes.nombre = ?
''', conn, params=(tipo_incidencia_fraude,))
num_actuaciones_fraude = df_num_actuaciones_fraude['num_actuaciones'].values[0]
print("Número de actuaciones en incidentes de tipo 'Fraude': %d" % num_actuaciones_fraude)
print("------------------------")

# Análisis estadístico básico para el tiempo de resolución de incidentes de tipo "Fraude"
df_tiempo_fraude = pd.read_sql_query('''
    SELECT julianday(fecha_cierre) - julianday(fecha_apertura) as tiempo_resolucion
    FROM tickets_emitidos
    JOIN tipos_incidentes ON tickets_emitidos.tipo_incidencia = tipos_incidentes.id_inci
    WHERE tipos_incidentes.nombre = ?
''', conn, params=(tipo_incidencia_fraude,))

mediana_tiempo_fraude = df_tiempo_fraude['tiempo_resolucion'].median()
media_tiempo_fraude = df_tiempo_fraude['tiempo_resolucion'].mean()
varianza_tiempo_fraude = df_tiempo_fraude['tiempo_resolucion'].var()
min_tiempo_fraude = df_tiempo_fraude['tiempo_resolucion'].min()
max_tiempo_fraude = df_tiempo_fraude['tiempo_resolucion'].max()

print("Análisis estadístico del tiempo de resolución de incidentes de tipo 'Fraude':")
print("Mediana: %.2f días" % mediana_tiempo_fraude)
print("Media: %.2f días" % media_tiempo_fraude)
print("Varianza: %.2f" % varianza_tiempo_fraude)
print("Valor mínimo: %.2f días" % min_tiempo_fraude)
print("Valor máximo: %.2f días" % max_tiempo_fraude)
print("------------------------")

#3.5 Por Dia de la Semana
def fraude_dias_semana():
    query = """
    SELECT strftime('%w', te.fecha_apertura) AS dia_semana, COUNT(te.id_ticket) AS num_incidentes,
           COUNT(ce.id_contacto) AS num_actuaciones, SUM(ce.tiempo) AS total_tiempo,
           AVG(ce.tiempo) AS media_tiempo, MIN(ce.tiempo) AS min_tiempo, 
           MAX(ce.tiempo) AS max_tiempo
    FROM contactos_con_empleados ce
    JOIN tickets_emitidos te ON ce.id_ticket = te.id_ticket
    WHERE te.tipo_incidencia = 5  -- Solo fraudes
    GROUP BY dia_semana;
    """
    df = pd.read_sql_query(query, conn)
    df['mediana_tiempo'] = df['total_tiempo'].median()
    df['varianza_tiempo'] = df['total_tiempo'].var()
    return df

# Obtener los datos
df_fraude = fraude_dias_semana()

# Mapeo de días de la semana con todos los días asegurados
dias_semana = {
    "1": "Lunes", "2": "Martes", "3": "Miércoles",
    "4": "Jueves", "5": "Viernes", "6": "Sábado", "0": "Domingo"
}

df_fraude['dia_semana'] = df_fraude['dia_semana'].map(dias_semana)

df_fraude = df_fraude.set_index('dia_semana').reindex(dias_semana.values(), fill_value=0).reset_index()

# Mostrar resultados por día de la semana
print("\n--- Estadísticas por día de la semana ---\n")
for index, row in df_fraude.iterrows():
    print(f"Día de la semana: {row['dia_semana']}")
    print(f"Número total de incidentes: {row['num_incidentes']}")
    print(f"Número total de actuaciones: {row['num_actuaciones']}")
    print(f"Tiempo total invertido: {row['total_tiempo']:.2f} horas")
    print(f"Mediana del tiempo por contacto: {row['mediana_tiempo']:.2f} horas")
    print(f"Media del tiempo por contacto: {row['media_tiempo']:.2f} horas")
    print(f"Varianza del tiempo por contacto: {row['varianza_tiempo']:.2f}")
    print(f"Tiempo mínimo en un contacto: {row['min_tiempo']:.2f} horas")
    print(f"Tiempo máximo en un contacto: {row['max_tiempo']:.2f} horas")
    print("--------------------------------------------------------")