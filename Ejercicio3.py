import requests

def obtener_ultimas_cves(n=10):
    url = "https://cve.circl.lu/api/last"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        cves = []

        for entry in data:
            id = None
            resumen = "Sin resumen disponible"
            fecha = "Fecha no disponible"

            if "aliases" in entry:
                id = next((alias for alias in entry.get("aliases", []) if alias.startswith("CVE-")), None)
                resumen = entry.get("summary", resumen)
                fecha = entry.get("published", fecha)

            elif "cveMetadata" in entry:
                id = entry["cveMetadata"].get("cveId")
                fecha = entry["cveMetadata"].get("datePublished", fecha)
                descripciones = entry.get("containers", {}).get("cna", {}).get("descriptions", [])
                resumen = next((d.get("value") for d in descripciones if "value" in d), resumen)

            if id:
                cves.append({
                    "ID": id,
                    "Resumen": resumen.replace("\n", " "),
                    "Fecha": fecha.split("T")[0]
                })

                if len(cves) >= n:
                    break

        return cves

    except requests.RequestException as e:
        return {"error": f"No se pudo obtener la lista de CVEs: {str(e)}"}
