import sqlite3
import json
import pandas as pd

def top_clientes_incidencias(conn, x):
    query = '''
    SELECT c.id_cli, c.nombre, COUNT(t.id_ticket) as num_incidencias
    FROM clientes c
    JOIN tickets_emitidos t ON c.id_cli = t.id_cliente
    GROUP BY c.id_cli, c.nombre
    ORDER BY num_incidencias DESC
    LIMIT ?
    '''
    df = pd.read_sql_query(query, conn, params=(x,))
    print("Top clientes con más incidencias:\n", df, "\n")
    return df

def top_incidencias_tiempo(conn, x):
    query = '''
    SELECT ti.id_inci, ti.nombre, 
           AVG(julianday(t.fecha_cierre) - julianday(t.fecha_apertura)) AS tiempo_promedio,
           SUM(julianday(t.fecha_cierre) - julianday(t.fecha_apertura)) AS tiempo_total
    FROM tipos_incidentes ti
    JOIN tickets_emitidos t ON ti.id_inci = t.tipo_incidencia
    GROUP BY ti.id_inci, ti.nombre
    ORDER BY tiempo_total DESC
    LIMIT ?
    '''
    df = pd.read_sql_query(query, conn, params=(x,))
    print("Top tipos de incidencias por tiempo de resolución:\n", df, "\n")
    return df


if __name__ == "__main__":
    conn = sqlite3.connect('datos.db')
    top_clientes_incidencias(conn, x=5)
    top_incidencias_tiempo(conn, x=5)
    conn.close()