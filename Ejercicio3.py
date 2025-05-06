# Ejercicio3.py
import requests
import pandas as pd

def obtener_ultimas_vulnerabilidades():
    try:
        url = "https://www.cvesearch.org/api/latest/10"
        response = requests.get(url)

        if response.status_code != 200:
            return pd.DataFrame([{"Error": "No se pudo obtener la información"}])

        data = response.json()
        lista = []

        for item in data:
            lista.append({
                "ID": item.get("id", "N/A"),
                "Resumen": item.get("summary", "N/A"),
                "Fecha": item.get("Published", "N/A")
            })

        return pd.DataFrame(lista)
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])
