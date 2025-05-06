import sqlite3
import request

from flask import Flask, render_template, request

import Ejercicio2
import Ejercicio3




app = Flask(__name__)
@app.route('/ejercicio2')
def ejercicio2():
    top_x = request.args.get('top', default=5, type=int)
    modo = request.args.get('modo', default="clientes", type=str)

    if modo == "clientes":
        datos = Ejercicio2.top_clientes_incidentes(top_x)
        titulo = "Top Clientes con Más Incidentes"
    else:
        datos = Ejercicio2.empleados_mas_tiempo(top_x)
        titulo = "Empleados que Más Tiempo Dedicaron"

    return render_template("ejercicio2.html", titulo=titulo, columnas=datos.columns, filas=datos.values.tolist())

@app.route('/ejercicio3')
def ejercicio3():
    datos = Ejercicio3.obtener_ultimas_vulnerabilidades()
    return render_template("ejercicio3.html", columnas=datos.columns, filas=datos.values.tolist())



@app.route('/top_clientes/<int:x>')
def top_clientes(x):
    conn = sqlite3.connect("mi_bd.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cliente, COUNT(*) as num_incidencias 
        FROM incidencias 
        GROUP BY cliente 
        ORDER BY num_incidencias DESC 
        LIMIT ?
    ''', (x,))
    resultados = cursor.fetchall()
    return render_template('top_clientes.html', datos=resultados)


@app.route('/top_tipos_incidencias/<int:x>')
def top_tipos_incidencias(x):
    conn = sqlite3.connect("mi_bd.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tipo, AVG(julianday(fecha_cierre) - julianday(fecha_apertura)) as tiempo_promedio 
        FROM incidencias 
        GROUP BY tipo 
        ORDER BY tiempo_promedio DESC 
        LIMIT ?
    ''', (x,))
    resultados = cursor.fetchall()
    return render_template('top_tipos.html', datos=resultados)


@app.route('/')
def index():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)