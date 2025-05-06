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
