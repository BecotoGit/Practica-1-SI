import requests


def obtener_ultimas_cves(n=10):
    url = "https://cve.circl.lu/api/last"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        lista_vulnerabilidades = []

        for entry in data:
            cve_id = None
            resumen = "Sin resumen disponible"
            fecha_publicacion = "Fecha no disponible"

            if "aliases" in entry:
                for alias in entry.get("aliases", []):
                    if alias.startswith("CVE-"):
                        cve_id = alias
                        break
                resumen = entry.get("summary", resumen)
                fecha_publicacion = entry.get("published", fecha_publicacion).split("T")[0]

            elif "cveMetadata" in entry:
                cve_id = entry["cveMetadata"].get("cveId")
                if "containers" in entry and "cna" in entry["containers"]:
                    for desc in entry["containers"]["cna"].get("descriptions", []):
                        resumen = desc.get("value", resumen)
                        break
                fecha_publicacion = entry["cveMetadata"].get("datePublished", fecha_publicacion).split("T")[0]

            if cve_id:
                lista_vulnerabilidades.append({
                    "ID": cve_id,
                    "Resumen": resumen.replace("\n", " "),
                    "Fecha": fecha_publicacion
                })

            if len(lista_vulnerabilidades) >= n:
                break

        return lista_vulnerabilidades

    except requests.RequestException as e:
        return {"error": f"No se pudo obtener la lista de CVEs: {str(e)}"}