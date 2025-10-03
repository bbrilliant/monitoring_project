import requests

def check_api_health(api_url):
    try:
        response = requests.get(api_url, timeout=5, verify=False)

        # Si la réponse est JSON, on essaie de l'exploiter
        try:
            data = response.json()
            return {
                "status": data.get("status", "UNKNOWN"),
                "disk_status": data.get("details", {}).get("diskSpace", {}).get("status", "N/A"),
                "disk_total": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total", 0),
                "disk_free": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free", 0)
            }
        except ValueError:
            # Si ce n'est pas du JSON → on regarde juste le code HTTP
            if response.status_code == 200:
                return {
                    "status": "UP",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0
                }
            else:
                return {
                    "status": "DOWN",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0
                }

    except requests.RequestException:
        # En cas d'erreur de connexion
        return {
            "status": "DOWN",
            "disk_status": "N/A",
            "disk_total": 0,
            "disk_free": 0
        }
