import requests

def obtener_ultimas_cves(n=10):
    url = "https://cve.circl.lu/api/last"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        lista = []
        for item in data:
            documento = item.get("document", {})
            tracking = documento.get("tracking", {})
            notes = documento.get("notes", [])

            cve_id = tracking.get("id")
            fecha = tracking.get("current_release_date")
            resumen = next((n["text"] for n in notes if n["category"] == "summary"), None)

            if cve_id and resumen and fecha:
                lista.append({
                    "ID": cve_id,
                    "Resumen": resumen.replace("\n", " "),
                    "Fecha": fecha.split("T")[0]
                })

            if len(lista) >= n:
                break

        return lista

    except requests.RequestException as e:
        return {"error": str(e)}
