import sqlite3
import pandas as pd
import numpy as np

# Conectar a la base de datos
conn = sqlite3.connect('datos.db')


# 3.1 Análisis por empleado
def obtener_datos_fraude_empleados(conn):
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


# 3.2 Análisis por nivel de empleado
def obtener_datos_nivel_empleado(nivel, conn):
    df_num_incidentes = pd.read_sql_query(f'''
        SELECT COUNT(DISTINCT t.id_ticket) as num_incidentes
        FROM tickets_emitidos t
        JOIN contactos_con_empleados c ON t.id_ticket = c.id_ticket
        JOIN empleados e ON c.id_empleado = e.id_emp
        WHERE e.nivel = {nivel}
    ''', conn)
    num_incidentes = df_num_incidentes['num_incidentes'].values[0]

    df_num_actuaciones = pd.read_sql_query(f'''
        SELECT COUNT(*) as num_actuaciones
        FROM contactos_con_empleados c
        JOIN empleados e ON c.id_empleado = e.id_emp
        WHERE e.nivel = {nivel}
    ''', conn)
    num_actuaciones = df_num_actuaciones['num_actuaciones'].values[0]

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

    return {
        "num_incidentes": num_incidentes,
        "num_actuaciones": num_actuaciones,
        "mediana": mediana,
        "media": media,
        "varianza": varianza,
        "valor_minimo": valor_minimo,
        "valor_maximo": valor_maximo
    }


# 3.3 Análisis por cliente
def obtener_datos_fraude_cliente(conn):
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


# 3.4 Análisis por tipo de incidencia

def obtener_datos_tipo_incidencia(conn):
    tipo_incidencia_fraude = 'Fraude'

    df_num_incidentes = pd.read_sql_query('''
        SELECT COUNT(*) as num_incidentes
        FROM tickets_emitidos
        JOIN tipos_incidentes ON tickets_emitidos.tipo_incidencia = tipos_incidentes.id_inci
        WHERE tipos_incidentes.nombre = ?
    ''', conn, params=(tipo_incidencia_fraude,))
    num_incidentes = df_num_incidentes['num_incidentes'].values[0]

    df_tiempo = pd.read_sql_query('''
        SELECT julianday(fecha_cierre) - julianday(fecha_apertura) as tiempo_resolucion
        FROM tickets_emitidos
        JOIN tipos_incidentes ON tickets_emitidos.tipo_incidencia = tipos_incidentes.id_inci
        WHERE tipos_incidentes.nombre = ?
    ''', conn, params=(tipo_incidencia_fraude,))

    if df_tiempo.empty:
        return {
            'num_incidentes': num_incidentes,
            'mediana_tiempo': None,
            'media_tiempo': None,
            'varianza_tiempo': None,
            'min_tiempo': None,
            'max_tiempo': None
        }

    return {
        'num_incidentes': num_incidentes,
        'mediana_tiempo': df_tiempo['tiempo_resolucion'].median(),
        'media_tiempo': df_tiempo['tiempo_resolucion'].mean(),
        'varianza_tiempo': df_tiempo['tiempo_resolucion'].var(),
        'min_tiempo': df_tiempo['tiempo_resolucion'].min(),
        'max_tiempo': df_tiempo['tiempo_resolucion'].max()
    }



# 3.5 Análisis por día de la semana
def obtener_datos_fraude_dias_semana(conn):
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

    df["dia_semana"] = df["dia_semana"].astype(str)

    dias_semana = {
        "0": "Domingo", "1": "Lunes", "2": "Martes",
        "3": "Miércoles", "4": "Jueves", "5": "Viernes", "6": "Sábado"
    }
    df["dia_semana"] = df["dia_semana"].map(dias_semana)

    return df


