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
                   ticket["satisfaccion_cliente"], ticket["tipo_incidencia"]))

        # Obtener el ID del ticket recién insertado
        id_ticket = c.lastrowid

        # Insertar contactos con empleados
        for contacto in ticket["contactos_con_empleados"]:
            c.execute("INSERT INTO contactos_con_empleados (id_ticket, id_empleado, fecha, tiempo) VALUES (?, ?, ?, ?)",
                      (id_ticket, contacto["id_emp"], contacto["fecha"], contacto["tiempo"]))

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("Datos insertados correctamente en la base de datos.")

conn = sqlite3.connect('datos.db')

#2.1 Calcular número de muestras
df_muestras = pd.read_sql_query('''SELECT COUNT(*) FROM tickets_emitidos''', conn)
n_muestras = df_muestras.values[0][0]
print("Número de muestras: %d" % n_muestras)
print("------------------------")

#2.2 Calcular la media y desviación estándar del total de incidentes
df_valoraciones = pd.read_sql_query('''SELECT satisfaccion_cliente FROM tickets_emitidos WHERE satisfaccion_cliente >= 5''', conn)

media_valoraciones = df_valoraciones['satisfaccion_cliente'].astype(float).mean()
desviacion_valoraciones = df_valoraciones['satisfaccion_cliente'].astype(float).std()

print("Media de valoraciones >= 5: %.2f" % media_valoraciones)
print("Desviación estándar de valoraciones >= 5: %.2f" % desviacion_valoraciones)
print("------------------------")

#2.4 Calcular la media y desviación estándar del número de horas totales realizadas en cada incidente
df_horas_incidentes = pd.read_sql_query('''
    SELECT id_ticket, SUM(tiempo) as total_horas
    FROM contactos_con_empleados
    GROUP BY id_ticket
''', conn)
media_horas = df_horas_incidentes['total_horas'].mean()
desviacion_horas = df_horas_incidentes['total_horas'].std()

print("Media de horas por incidente: %.2f" % media_horas)
print("Desviación estándar de horas por incidente: %.2f" % desviacion_horas)
print("------------------------")

#2.6 Calcular el valor mínimo y máximo del tiempo entre apertura y cierre de incidente
df_tiempo_incidentes = pd.read_sql_query('''
    SELECT id_ticket, 
           julianday(fecha_cierre) - julianday(fecha_apertura) as tiempo_incidente
    FROM tickets_emitidos
''', conn)

min_tiempo = df_tiempo_incidentes['tiempo_incidente'].min()
max_tiempo = df_tiempo_incidentes['tiempo_incidente'].max()

print("Tiempo mínimo entre apertura y cierre de incidente: %.2f días" % min_tiempo)
print("Tiempo máximo entre apertura y cierre de incidente: %.2f días" % max_tiempo)
print("------------------------")

#2.7 Calcular Valor minimo y maximo del numero de incidentes x empleado
df_incidentes_empleados = pd.read_sql_query('''SELECT id_empleado, COUNT(*) as num_incidentes 
                                               FROM contactos_con_empleados 
                                               GROUP BY id_empleado''', conn)

valor_minimo = df_incidentes_empleados['num_incidentes'].min()
valor_maximo = df_incidentes_empleados['num_incidentes'].max()

print("Valor mínimo de incidentes por empleado: %d" % valor_minimo)
print("Valor máximo de incidentes por empleado: %d" % valor_maximo)
print("------------------------")