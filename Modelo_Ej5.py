import json
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import matplotlib.pyplot as plt
import os

def cargar_datos_json(ruta):
    with open(ruta, 'r') as f:
        data = json.load(f)

    registros = []
    for ticket in data["tickets_emitidos"]:
        cliente = int(ticket["cliente"])
        mantenimiento = int(ticket["es_mantenimiento"])
        tipo = int(ticket["tipo_incidencia"])
        critico = int(ticket["es_critico"])

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

    os.makedirs("static/graficas", exist_ok=True)  # Crea carpeta si no existe

    # Regresión Logística
    modelo_logistico = LogisticRegression()
    modelo_logistico.fit(X_train, y_train)
    joblib.dump(modelo_logistico, "modelo_logistico.pkl")

    # Gráfica para Regresión Logística
    plt.figure()
    plt.scatter(X_train["duracion"], y_train, color="blue", label="Datos reales")
    plt.plot(X_train["duracion"], modelo_logistico.predict(X_train), color="red", label="Predicción")
    plt.xlabel("Duración (días)")
    plt.ylabel("¿Crítico?")
    plt.title("Regresión Logística")
    plt.legend()
    plt.savefig("graficas/regresion_logistica.png")

    # Árbol de Decisión
    modelo_arbol = DecisionTreeClassifier()
    modelo_arbol.fit(X_train, y_train)
    joblib.dump(modelo_arbol, "modelo_arbol.pkl")

    # Gráfica para Árbol de Decisión
    plt.figure(figsize=(20, 10))
    plot_tree(modelo_arbol, filled=True, feature_names=X.columns, class_names=["No Crítico", "Crítico"])
    plt.title("Árbol de Decisión")
    plt.savefig("graficas/arbol_decision.png")

    # Random Forest
    modelo_rf = RandomForestClassifier()
    modelo_rf.fit(X_train, y_train)
    joblib.dump(modelo_rf, "modelo_rf.pkl")

    # Gráfica de importancia de variables para Random Forest
    importancias = modelo_rf.feature_importances_
    features = X.columns
    plt.figure()
    plt.barh(features, importancias)
    plt.xlabel("Importancia")
    plt.title("Importancia de variables en Random Forest")
    plt.savefig("graficas/importancia_random_forest.png")

if __name__ == "__main__":
    entrenar_modelos()
