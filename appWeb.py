import sqlite3


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
    resultado = Ejercicio3.obtener_ultimas_cves()

    if isinstance(resultado, dict) and "error" in resultado:
        return render_template("ejercicio3.html", error=resultado["error"])
    else:
        return render_template("ejercicio3.html", vulnerabilidades=resultado)




@app.route('/ejercicio1')
def ejercicio1():
    conn = sqlite3.connect("datos.db")

    clientes_df = Ejercicio1.top_clientes_incidencias(conn, x=5)
    incidencias_df = Ejercicio1.top_incidencias_tiempo(conn, x=5)

    conn.close()

    # Convertir los DataFrames a diccionarios para pasarlos a la plantilla
    clientes = clientes_df.to_dict(orient='records')
    incidencias = incidencias_df.to_dict(orient='records')

    return render_template("ejercicio1.html", clientes=clientes, incidencias=incidencias)


@app.route('/')
def index():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)