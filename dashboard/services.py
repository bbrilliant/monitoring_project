import requests

def check_api_health(api_url):
    try:
        response = requests.get(api_url, timeout=5, verify=False)

        # Cas 1 : réponse JSON exploitable
        try:
            data = response.json()
            return {
                "status": data.get("status", "UNKNOWN"),
                "disk_status": data.get("details", {}).get("diskSpace", {}).get("status", "N/A"),
                "disk_total": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total", 0),
                "disk_free": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free", 0)
            }
        except ValueError:
            # Cas 2 : pas du JSON → si 200 = UP (sans stockage)
            if response.status_code == 200:
                return {
                    "status": "UP",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0
                }
            else:
                # Cas 3 : autre code → DOWN
                return {
                    "status": "DOWN",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0
                }

    except requests.RequestException:
        # Cas 4 : erreur réseau → DOWN
        return {
            "status": "DOWN",
            "disk_status": "N/A",
            "disk_total": 0,
            "disk_free": 0
        }
