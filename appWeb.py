import sqlite3

import joblib
import pdfkit
import requests
from flask import Flask, render_template, request, send_file, make_response, json
from datetime import datetime
import numpy as np

import Ejercicio1
import Ejercicio2
import Ejercicio3
import Ejercicio4
import io
from xhtml2pdf import pisa

app = Flask(__name__)

@app.route('/ejercicio1', methods=['GET'])
def ejercicio1():
    section = request.args.get('section', 'clientes')

    X_clientes = int(request.args.get('X_clientes', 5))
    X_incidencias = int(request.args.get('X_incidencias', 5))

    conn = sqlite3.connect("datos.db")

    if section == 'clientes':
        clientes_df = Ejercicio1.top_clientes_incidencias(conn, X_clientes)
        if 'incidencias' in request.args:
            incidencias_df = Ejercicio1.top_incidencias_tiempo(conn, X_incidencias)
        else:
            incidencias_df = Ejercicio1.top_incidencias_tiempo(conn, 5)
    else:
        incidencias_df = Ejercicio1.top_incidencias_tiempo(conn, X_incidencias)
        if 'clientes' in request.args:
            clientes_df = Ejercicio1.top_clientes_incidencias(conn, X_clientes)
        else:
            clientes_df = Ejercicio1.top_clientes_incidencias(conn, 5)
    conn.close()

    clientes = clientes_df.to_dict(orient='records')
    incidencias = incidencias_df.to_dict(orient='records')

    return render_template("ejercicio1.html", clientes=clientes, incidencias=incidencias, X_clientes=X_clientes, X_incidencias=X_incidencias, section=section)

@app.route('/ejercicio1/pdf', methods=['GET'])
def ejercicio1_pdf():
    section = request.args.get('section', 'clientes')

    X_clientes = int(request.args.get('X_clientes', 5))
    X_incidencias = int(request.args.get('X_incidencias', 5))

    conn = sqlite3.connect("datos.db")

    if section == 'clientes':
        clientes_df = Ejercicio1.top_clientes_incidencias(conn, X_clientes)
        incidencias_df = Ejercicio1.top_incidencias_tiempo(conn, X_incidencias)
    else:
        incidencias_df = Ejercicio1.top_incidencias_tiempo(conn, X_incidencias)
        clientes_df = Ejercicio1.top_clientes_incidencias(conn, X_clientes)

    conn.close()

    clientes = clientes_df.to_dict(orient='records')
    incidencias = incidencias_df.to_dict(orient='records')

    rendered_html = render_template(
        'ejercicio1_pdf.html',
        clientes=clientes,
        incidencias=incidencias,
        X_clientes=X_clientes,
        X_incidencias=X_incidencias
    )

    pdf_stream = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf_stream)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    pdf_stream.seek(0)
    return send_file(pdf_stream, as_attachment=True, download_name="ejercicio1_datos.pdf", mimetype='application/pdf')



@app.route('/ejercicio2', methods=['GET'])
def ejercicio2():
    tipo = request.args.get('tipo', 'clientes')
    cantidad = int(request.args.get('cantidad', 5))

    if tipo == 'clientes':
        df = Ejercicio2.top_clientes_incidentes(cantidad)
    else:
        df = Ejercicio2.empleados_mas_tiempo(cantidad)

    return render_template(
        'ejercicio2.html',
        titulo="Análisis de Datos de Incidentes",
        columnas=df.columns,
        filas=df.values,
        tipo=tipo,
        cantidad=cantidad
    )

@app.route('/ejercicio2/pdf', methods=['GET'])
def ejercicio2_pdf():
    tipo = request.args.get('tipo', 'clientes')
    cantidad = int(request.args.get('cantidad', 5))

    if tipo == 'clientes':
        df = Ejercicio2.top_clientes_incidentes(cantidad)
    else:
        df = Ejercicio2.empleados_mas_tiempo(cantidad)

    rendered_html = render_template(
        'ejercicio2_pdf.html',
        titulo="Análisis de ejercicio 2",
        columnas=df.columns,
        filas=df.values,
        tipo=tipo,
        cantidad=cantidad
    )
    pdf_stream = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf_stream)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    pdf_stream.seek(0)
    return send_file(pdf_stream, as_attachment=True, download_name="ejercicio2_datos.pdf", mimetype='application/pdf')


@app.route('/ejercicio3')
def ejercicio3():
    resultado = Ejercicio3.obtener_ultimas_cves()

    if isinstance(resultado, dict) and "error" in resultado:
        return render_template("ejercicio3.html", error=resultado["error"])
    else:
        return render_template("ejercicio3.html", vulnerabilidades=resultado)

@app.route('/ejercicio3/pdf', methods=['GET'])
def ejercicio3_pdf():
    resultado = Ejercicio3.obtener_ultimas_cves()

    if isinstance(resultado, dict) and "error" in resultado:
        return "No se pudo generar el PDF: " + resultado["error"], 500

    rendered_html = render_template(
        "ejercicio3_pdf.html",  # usa un template separado si es necesario
        vulnerabilidades=resultado,
        titulo="Últimas Vulnerabilidades Publicadas"
    )

    pdf_stream = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf_stream)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    pdf_stream.seek(0)
    return send_file(pdf_stream, as_attachment=True, download_name="vulnerabilidades.pdf", mimetype='application/pdf')

@app.route('/ejercicio4')
def ejercicio4():
    region = request.args.get('region', '')
    cantidad = int(request.args.get('cantidad', 5))

    resultado = Ejercicio4.obtener_paises(region,cantidad)
    if isinstance(resultado, dict) and "error" in resultado:
        return render_template("ejercicio4.html", error=resultado["error"])
    return render_template("ejercicio4.html", paises=resultado, region=region, cantidad=cantidad)

@app.route('/ejercicio4/pdf', methods=['GET'])
def ejercicio4_pdf():
    region = request.args.get('region', '')
    cantidad = int(request.args.get('cantidad', 5))

    resultado = Ejercicio4.obtener_paises(region,cantidad)
    if isinstance(resultado, dict) and "error" in resultado:
        return render_template("ejercicio4_pdf.html", error=resultado["error"])
    rendered_html= render_template("ejercicio4_pdf.html", paises=resultado, region=region, cantidad=cantidad)
    pdf_stream = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf_stream)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    pdf_stream.seek(0)
    return send_file(pdf_stream, as_attachment=True, download_name="paises.pdf", mimetype='application/pdf')


@app.route('/ejercicio5')
def formularioEj5():
    return render_template("clasificar.html")

@app.route('/ejercicio5/pdf')
def ejercicio5_pdf():
    with open("data_clasified.json", "r", encoding="utf-8") as file:
        tickets_data = json.load(file)

        # Renderizar la plantilla HTML con los datos
    html = render_template("tickets_pdf.html", tickets=tickets_data["tickets_emitidos"])

    # Crear el archivo PDF
    pdf_stream = io.BytesIO()
    pisa.CreatePDF(html, dest=pdf_stream)
    pdf_stream.seek(0)

    # Devolver el archivo PDF como respuesta
    return make_response(pdf_stream.read(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "inline; filename=tickets.pdf"
    })

@app.route('/clasificar', methods=['POST'])
def clasificarEj5():
    cliente = int(request.form['cliente'])
    mantenimiento = int(request.form['mantenimiento'])
    tipo = int(request.form['tipo'])
    metodo = request.form['metodo']

    fecha_apertura = datetime.strptime(request.form['fecha_apertura'], "%Y-%m-%d")
    fecha_cierre = datetime.strptime(request.form['fecha_cierre'], "%Y-%m-%d")
    duracion = (fecha_cierre - fecha_apertura).days

    datos = np.array([[cliente, mantenimiento, tipo, duracion]])

    if metodo == 'logistico':
        modelo = joblib.load("modelo_logistico.pkl")
    elif metodo == 'arbol':
        modelo = joblib.load("modelo_arbol.pkl")
    else:
        modelo = joblib.load("modelo_rf.pkl")

    resultado = modelo.predict(datos)[0]
    return render_template("resultado.html", resultado=resultado)

@app.route('/graficas')
def mostrar_graficas():
    return render_template("graficas.html")


@app.route('/')
def index():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)