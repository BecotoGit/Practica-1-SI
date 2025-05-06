import sqlite3
import json
import hashlib
import pandas as pd

# Crear conexión a la base de datos
conn = sqlite3.connect('datos.db')
c = conn.cursor()

# Borrar las tablas si ya existen
c.execute("DROP TABLE IF EXISTS tickets_emitidos")
c.execute("DROP TABLE IF EXISTS contactos_con_empleados")
c.execute("DROP TABLE IF EXISTS clientes")
c.execute("DROP TABLE IF EXISTS empleados")
c.execute("DROP TABLE IF EXISTS tipos_incidentes")

# Crear tablas
c.execute('''CREATE TABLE IF NOT EXISTS tickets_emitidos (
                id_cliente INTEGER,
                id_ticket INTEGER PRIMARY KEY,
                fecha_apertura DATE,
                fecha_cierre DATE,
                es_mantenimiento BOOLEAN,
                satisfaccion_cliente TEXT,
                tipo_incidencia INTEGER,
                es_critico BOOLEAN,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cli),
                FOREIGN KEY (tipo_incidencia) REFERENCES tipos_incidentes(id_inci)
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS contactos_con_empleados (
                id_contacto INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ticket INTEGER,
                id_empleado INTEGER,
                fecha DATE,
                tiempo FLOAT,
                FOREIGN KEY (id_ticket) REFERENCES tickets_emitidos(id_ticket),
                FOREIGN KEY (id_empleado) REFERENCES empleados(id_emp)
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                id_cli INTEGER PRIMARY KEY,
                nombre TEXT,
                telefono INTEGER,
                provincia TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS empleados (
                id_emp INTEGER PRIMARY KEY,
                nombre INTEGER,
                nivel INTEGER,
                fecha_contrato TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS tipos_incidentes (
                id_inci TEXT PRIMARY KEY,
                nombre TEXT
            )''')

# Cargar datos desde el archivo JSON
with open('datos.json') as j:
    data = json.load(j)

    # Insertar datos en la tabla de empleados
    for emp in data["empleados"]:
        c.execute("INSERT OR IGNORE INTO empleados (id_emp, nombre, nivel, fecha_contrato) VALUES (?, ?, ?, ?)",
                  (emp["id_emp"], emp["nombre"], emp["nivel"], emp["fecha_contrato"]))

    # Insertar datos en la tabla de clientes
    for cli in data["clientes"]:
        c.execute("INSERT OR IGNORE INTO clientes (id_cli, nombre, telefono, provincia) VALUES (?, ?, ?, ?)",
                  (cli["id_cli"], cli["nombre"], cli["telefono"], cli["provincia"]))

    # Insertar datos en la tabla de tipos de incidentes
    for inci in data["tipos_incidentes"]:
        c.execute("INSERT OR IGNORE INTO tipos_incidentes (id_inci, nombre) VALUES (?, ?)",
                  (inci["id_inci"], inci["nombre"]))

    # Insertar datos en la tabla de tickets emitidos
    for ticket in data["tickets_emitidos"]:
        c.execute("INSERT INTO tickets_emitidos (id_cliente, fecha_apertura, fecha_cierre, es_mantenimiento, satisfaccion_cliente, tipo_incidencia) VALUES(?, ?, ?, ?, ?, ?)",
                  (ticket["cliente"], ticket["fecha_apertura"], ticket["fecha_cierre"], ticket["es_mantenimiento"],
                   ticket["satisfaccion_cliente"], ticket["tipo_incidencia"], ticket["es_critico"]))

        id_ticket = c.lastrowid

        # Insertar contactos con empleados
        for contacto in ticket["contactos_con_empleados"]:
            c.execute("INSERT INTO contactos_con_empleados (id_ticket, id_empleado, fecha, tiempo) VALUES (?, ?, ?, ?)",
                      (id_ticket, contacto["id_emp"], contacto["fecha"], contacto["tiempo"]))

conn.commit()

# Cerrar la conexión
conn.close()


conn = sqlite3.connect('datos.db')

#2.1 Calcular número de muestras
def calcular_numero_muestras(conn):
    df_muestras = pd.read_sql_query('''SELECT COUNT(*) FROM tickets_emitidos''', conn)
    n_muestras = df_muestras.values[0][0]
    return n_muestras

#2.2 Calcular la media y desviación estándar del total de incidentes con valoracion >= 5
def calcular_media_desviacion_valoraciones(conn):
    df_valoraciones = pd.read_sql_query('''SELECT satisfaccion_cliente FROM tickets_emitidos WHERE satisfaccion_cliente >= 5''', conn)
    media_valoraciones = df_valoraciones['satisfaccion_cliente'].astype(float).mean()
    desviacion_valoraciones = df_valoraciones['satisfaccion_cliente'].astype(float).std()
    return media_valoraciones, desviacion_valoraciones


#2.3 Calcular la media y desviación estándar del total del número de incidentes por cliente
def calcular_media_desviacion_incidentes_cliente(conn):
    df_incidentes_cliente = pd.read_sql_query('''
        SELECT id_cliente, COUNT(*) as total_incidentes
        FROM tickets_emitidos
        GROUP BY id_cliente
        ''', conn)
    media_incidentes = df_incidentes_cliente['total_incidentes'].mean()
    desviacion_incidentes = df_incidentes_cliente['total_incidentes'].std()
    return media_incidentes, desviacion_incidentes


#2.4 Calcular la media y desviación estándar del número de horas totales realizadas en cada incidente
def calcular_media_desviacion_horas_incidentes(conn):
    df_horas_incidentes = pd.read_sql_query('''
        SELECT id_ticket, SUM(tiempo) as total_horas
        FROM contactos_con_empleados
        GROUP BY id_ticket
    ''', conn)
    media_horas = df_horas_incidentes['total_horas'].mean()
    desviacion_horas = df_horas_incidentes['total_horas'].std()
    return media_horas, desviacion_horas



#2.5 Calcular el valor mínimo y máximo del total de horas realizadas por los empleados
def calcular_min_max_horas_empleados(conn):
    df_horas_empleados = pd.read_sql_query('''SELECT id_empleado, SUM(tiempo) as total_horas 
                                              FROM contactos_con_empleados 
                                              GROUP BY id_empleado''', conn)
    min_horas = df_horas_empleados['total_horas'].min()
    max_horas = df_horas_empleados['total_horas'].max()
    return min_horas, max_horas

#2.6 Calcular el valor mínimo y máximo del tiempo entre apertura y cierre de incidente
def calcular_min_max_tiempo_incidentes(conn):
    df_tiempo_incidentes = pd.read_sql_query('''
        SELECT id_ticket, 
               julianday(fecha_cierre) - julianday(fecha_apertura) as tiempo_incidente
        FROM tickets_emitidos
    ''', conn)
    min_tiempo = df_tiempo_incidentes['tiempo_incidente'].min()
    max_tiempo = df_tiempo_incidentes['tiempo_incidente'].max()
    return min_tiempo, max_tiempo

#2.7 Calcular Valor minimo y maximo del numero de incidentes x empleado
def calcular_min_max_incidentes_empleados(conn):
    df_incidentes_empleados = pd.read_sql_query('''SELECT id_empleado, COUNT(*) as num_incidentes 
                                                   FROM contactos_con_empleados 
                                                   GROUP BY id_empleado''', conn)
    valor_minimo = df_incidentes_empleados['num_incidentes'].min()
    valor_maximo = df_incidentes_empleados['num_incidentes'].max()
    return valor_minimo, valor_maximo




