import requests

regiones_traducidas = {
    "Europe": "Europa",
    "Americas": "América",
    "Asia": "Asia",
    "Oceania": "Oceanía",
    "Africa": "África"
}

def obtener_paises(region,cantidad):
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        datos = response.json()
        if region:
            datos = [pais for pais in datos if pais.get("region") == region]

        datos = sorted(datos, key=lambda x: x.get("population", 0), reverse=True)

        paises = []
        for pais in datos[:cantidad]:
            paises.append({
                "nombre": pais.get("translations", {}).get("spa", {}).get("common", pais.get("name", {}).get("common", "Desconocido")),
                "capital": pais.get("capital", ["No especificada"])[0],
                "region": regiones_traducidas.get(pais.get("region"), "Desconocida"),
                "poblacion": pais.get("population", 0),
                "bandera": pais.get("flags", {}).get("png", "")
            })
        return paises
    except Exception as e:
        return {"error": str(e)}


