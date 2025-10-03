import requests


import requests

def check_api_health(api_url):
    try:
        response = requests.get(api_url, timeout=5, verify=False)

        # --- Étape 1 : Vérification du code HTTP ---
        if response.status_code == 200:
            status = "UP"
        else:
            return {
                "status": "DOWN",
                "disk_status": "N/A",
                "disk_total": None,
                "disk_free": None
            }

        # --- Étape 2 : Tenter d’analyser la réponse JSON ---
        try:
            data = response.json()
            return {
                "status": status,  # toujours UP car HTTP 200
                "disk_status": data.get("details", {}).get("diskSpace", {}).get("status", "N/A"),
                "disk_total": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total"),
                "disk_free": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free")
            }
        except ValueError:
            # Réponse non JSON → stockage indisponible
            return {
                "status": status,
                "disk_status": "N/A",
                "disk_total": None,
                "disk_free": None
            }

    except requests.RequestException:
        # En cas d’erreur réseau ou timeout
        return {
            "status": "DOWN",
            "disk_status": "N/A",
            "disk_total": None,
            "disk_free": None
        }
