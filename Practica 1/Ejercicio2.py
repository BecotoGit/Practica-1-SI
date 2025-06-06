import sqlite3
import json
import hashlib
import pandas as pd

# Crear conexión a la base de datos
conn = sqlite3.connect('../datos.db')
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
with open('../datos.json') as j:
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
        c.execute("INSERT INTO tickets_emitidos (id_cliente, fecha_apertura, fecha_cierre, es_mantenimiento, satisfaccion_cliente, tipo_incidencia) VALUES(?, ?, ?, ?, ?)",
                  (ticket["cliente"], ticket["fecha_apertura"], ticket["fecha_cierre"], ticket["es_mantenimiento"],
                   ticket["satisfaccion_cliente"], ticket["tipo_incidencia"]))

        id_ticket = c.lastrowid

        # Insertar contactos con empleados
        for contacto in ticket["contactos_con_empleados"]:
            c.execute("INSERT INTO contactos_con_empleados (id_ticket, id_empleado, fecha, tiempo) VALUES (?, ?, ?, ?)",
                      (id_ticket, contacto["id_emp"], contacto["fecha"], contacto["tiempo"]))

conn.commit()

# Cerrar la conexión
conn.close()


conn = sqlite3.connect('/datos.db')



