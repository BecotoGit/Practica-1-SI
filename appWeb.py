import sqlite3

from flask import Flask, render_template
import Ejercicio2
import Ejercicio3
import Ejercicio4



app = Flask(__name__)
@app.route('/ejercicio2')
def ejercicio2():
    conn = sqlite3.connect('datos.db')
    num_muestras = Ejercicio2.calcular_numero_muestras(conn) # Replace with the actual function call from Ejercicio2
    media_valoraciones, desviacion_valoraciones = Ejercicio2.calcular_media_desviacion_valoraciones(conn)
    media_incidentes, desviacion_incidentes = Ejercicio2.calcular_media_desviacion_incidentes_cliente(conn)
    media_horas, desviacion_horas = Ejercicio2.calcular_media_desviacion_horas_incidentes(conn)
    min_horas, max_horas = Ejercicio2.calcular_min_max_horas_empleados(conn)
    min_tiempo, max_tiempo = Ejercicio2.calcular_min_max_tiempo_incidentes(conn)
    valor_minimo, valor_maximo = Ejercicio2.calcular_min_max_incidentes_empleados(conn)

    return render_template('ejercicio2.html',
                           num_muestras=num_muestras,
                           media_valoraciones=media_valoraciones,
                           desviacion_valoraciones=desviacion_valoraciones,
                           media_incidentes=media_incidentes,
                           desviacion_incidentes=desviacion_incidentes,
                           media_horas=media_horas,
                           desviacion_horas=desviacion_horas,
                           min_horas=min_horas,
                           max_horas=max_horas,
                           min_tiempo=min_tiempo,
                           max_tiempo=max_tiempo,
                           valor_minimo=valor_minimo,
                           valor_maximo=valor_maximo)


@app.route('/ejercicio3/empleado')
def ejercicio3_empleado():
    with sqlite3.connect('datos.db') as conn:
        empleados = Ejercicio3.obtener_datos_fraude_empleados(conn).to_dict(orient='records')
    return render_template('ejercicio3_empleado.html', empleados=empleados)


@app.route('/ejercicio3/nivel')
def ejercicio3_nivel():
    niveles = [1, 2, 3]  # Niveles de empleado a analizar
    datos_niveles = {}

    with sqlite3.connect('datos.db') as conn:
        for nivel in niveles:
            datos_niveles[nivel] = Ejercicio3.obtener_datos_nivel_empleado(nivel, conn)

    return render_template('ejercicio3_nivel.html', datos_niveles=datos_niveles)


@app.route('/ejercicio3/cliente')
def ejercicio3_cliente():
    with sqlite3.connect('datos.db') as conn:
        clientes = Ejercicio3.obtener_datos_fraude_cliente(conn).to_dict(orient='records')
    return render_template('ejercicio3_cliente.html', clientes=clientes)


@app.route('/ejercicio3/incidente')
def ejercicio3_incidente():
    tipos_incidentes = ['Fraude']  # Lista de tipos de incidentes (puedes agregar más si es necesario)
    datos_incidentes = {}

    with sqlite3.connect('datos.db') as conn:
        for tipo in tipos_incidentes:
            datos_incidentes[tipo] = Ejercicio3.obtener_datos_tipo_incidencia(conn)

    return render_template('ejercicio3_incidente.html', datos_incidentes=datos_incidentes)


@app.route('/ejercicio3/dia')
def ejercicio3_dia():

    with sqlite3.connect('datos.db') as conn:
        dias = Ejercicio3.obtener_datos_fraude_dias_semana(conn).to_dict(orient='records')
    return render_template('ejercicio3_dia.html', dias=dias)


@app.route('/ejercicio4')
def ejercicio4():
    conn = sqlite3.connect('datos.db')

    tiempo_mantenimiento = Ejercicio4.calcular_media_tiempo_mantenimiento(conn)
    graficas_bigotes = Ejercicio4.mostrar_grafica_bigotes(conn)
    clientes_criticos = Ejercicio4.obtener_clientes_criticos(conn)
    actuaciones_empleados = Ejercicio4.mostrar_actuaciones_empleados(conn)
    actuaciones_dia_semana = Ejercicio4.actuaciones_por_dia_semana(conn)

    return render_template('ejercicio4.html',
                           tiempo_mantenimiento=tiempo_mantenimiento,
                           graficas_bigotes=graficas_bigotes,
                           clientes_criticos=clientes_criticos,
                           actuaciones_empleados=actuaciones_empleados,
                           actuaciones_dia_semana=actuaciones_dia_semana)


@app.route('/')
def index():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)