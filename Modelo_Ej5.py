import json
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

def cargar_datos_json(ruta):
    with open(ruta, 'r') as f:
        data = json.load(f)

    registros = []
    for ticket in data["tickets_emitidos"]:
        cliente = int(ticket["cliente"])
        mantenimiento = int(ticket["es_mantenimiento"])
        tipo = int(ticket["tipo_incidencia"])
        critico = int(ticket["es_critico"])

        # Calcular duración en días
        fecha_apertura = datetime.strptime(ticket["fecha_apertura"], "%Y-%m-%d")
        fecha_cierre = datetime.strptime(ticket["fecha_cierre"], "%Y-%m-%d")
        duracion = (fecha_cierre - fecha_apertura).days

        registros.append({
            "cliente": cliente,
            "mantenimiento": mantenimiento,
            "tipo": tipo,
            "duracion": duracion,
            "critico": critico
        })

    return pd.DataFrame(registros)

def entrenar_modelos():
    df = cargar_datos_json("data_clasified.json")

    X = df[["cliente", "mantenimiento", "tipo", "duracion"]]
    y = df["critico"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Modelo de Regresión Logística
    modelo_logistico = LogisticRegression()
    modelo_logistico.fit(X_train, y_train)
    joblib.dump(modelo_logistico, "modelo_logistico.pkl")

    # Modelo de Árbol de Decisión
    modelo_arbol = DecisionTreeClassifier()
    modelo_arbol.fit(X_train, y_train)
    joblib.dump(modelo_arbol, "modelo_arbol.pkl")

    # Modelo de Random Forest
    modelo_rf = RandomForestClassifier()
    modelo_rf.fit(X_train, y_train)
    joblib.dump(modelo_rf, "modelo_rf.pkl")

if __name__ == "__main__":
    entrenar_modelos()
