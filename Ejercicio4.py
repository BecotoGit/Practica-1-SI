import io
import base64
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Función para convertir una imagen a base64
def plot_to_base64(fig):
    img_io = io.BytesIO()
    fig.savefig(img_io, format='png')
    img_io.seek(0)
    img_b64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return img_b64

def calcular_media_tiempo_mantenimiento(conn):
    df_tiempo_mantenimiento = pd.read_sql_query('''
        SELECT es_mantenimiento, 
               AVG(julianday(fecha_cierre) - julianday(fecha_apertura)) as tiempo_promedio
        FROM tickets_emitidos
        GROUP BY es_mantenimiento
    ''', conn)

    df_tiempo_mantenimiento['es_mantenimiento'] = df_tiempo_mantenimiento['es_mantenimiento'].map({1: 'Mantenimiento', 0: 'No Mantenimiento'})
    df_tiempo_mantenimiento.set_index('es_mantenimiento', inplace=True)

    fig, ax = plt.subplots()
    df_tiempo_mantenimiento.plot(kind='bar', legend=False, ax=ax)
    ax.set_title('Media de tiempo (apertura-cierre) de los incidentes')
    ax.set_xlabel('Tipo de Incidente')
    ax.set_ylabel('Tiempo Promedio (días)')
    plt.xticks(rotation=0)

    return plot_to_base64(fig)

def mostrar_grafica_bigotes(conn):
    def obtener_tiempos_resolucion():
        query = """
        SELECT te.tipo_incidencia, 
               julianday(te.fecha_cierre) - julianday(te.fecha_apertura) AS tiempo_resolucion
        FROM tickets_emitidos te
        WHERE te.fecha_cierre IS NOT NULL;
        """
        df = pd.read_sql_query(query, conn)
        return df

    df_resolucion = obtener_tiempos_resolucion()
    tipos_incidentes = df_resolucion['tipo_incidencia'].unique()

    fig, ax = plt.subplots(figsize=(8, 5))

    for tipo in tipos_incidentes:
        df_filtrado = df_resolucion[df_resolucion['tipo_incidencia'] == tipo]

        ax.boxplot(df_filtrado['tiempo_resolucion'], vert=True, patch_artist=True, showfliers=False)

        percentiles = df_filtrado['tiempo_resolucion'].quantile([0.05, 0.90])
        ax.scatter(1, percentiles[0.05], color='red', label='Percentil 5%')
        ax.scatter(1, percentiles[0.90], color='green', label='Percentil 90%')

    ax.set_ylabel("Tiempo de Resolución (días)")
    ax.set_title(f"Distribución del Tiempo de Resolución por Tipo de Incidente")
    ax.legend()
    ax.grid()

    return plot_to_base64(fig)

def obtener_clientes_criticos(conn):
    df_clientes_criticos = pd.read_sql_query('''
        SELECT id_cliente, COUNT(*) as num_incidentes
        FROM tickets_emitidos
        WHERE es_mantenimiento = 1 AND tipo_incidencia != 1
        GROUP BY id_cliente
        ORDER BY num_incidentes DESC
        LIMIT 5
    ''', conn)

    df_clientes_criticos.set_index('id_cliente', inplace=True)

    fig, ax = plt.subplots()
    df_clientes_criticos.plot(kind='bar', legend=False, ax=ax)
    ax.set_title('Top 5 Clientes Más Críticos')
    ax.set_xlabel('ID del Cliente')
    ax.set_ylabel('Número de Incidentes')
    plt.xticks(rotation=0)

    return plot_to_base64(fig)

def mostrar_actuaciones_empleados(conn):
    df_actuaciones_empleados = pd.read_sql_query('''SELECT e.nombre, COUNT(*) as num_actuaciones 
                                                    FROM contactos_con_empleados cce
                                                    JOIN empleados e ON cce.id_empleado = e.id_emp
                                                    GROUP BY e.nombre''', conn)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_actuaciones_empleados['nombre'], df_actuaciones_empleados['num_actuaciones'], color='skyblue')
    ax.set_xlabel('Empleados')
    ax.set_ylabel('Número de Actuaciones')
    ax.set_title('Número Total de Actuaciones Realizadas por los Empleados')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return plot_to_base64(fig)


def actuaciones_por_dia_semana(conn):
    df_actuaciones_dia = pd.read_sql_query('''
        SELECT strftime('%w', cce.fecha) AS dia_semana, COUNT(*) as total_actuaciones
        FROM contactos_con_empleados cce
        GROUP BY dia_semana
        ORDER BY dia_semana
    ''', conn)

    dias_semana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    df_actuaciones_dia['dia_semana'] = df_actuaciones_dia['dia_semana'].astype(int).map(lambda x: dias_semana[x])

    fig, ax = plt.subplots()
    ax.bar(df_actuaciones_dia['dia_semana'], df_actuaciones_dia['total_actuaciones'], color='coral')
    ax.set_title('Total de Actuaciones por Día de la Semana')
    ax.set_xlabel('Día de la Semana')
    ax.set_ylabel('Número de Actuaciones')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    return plot_to_base64(fig)