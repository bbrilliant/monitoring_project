import requests

def check_api_health(url):
    try:
        response = requests.get(url, timeout=5)

        # Vérifie le statut HTTP
        if response.status_code == 200:
            status = "UP"
            disk_total = 0
            disk_free = 0
            disk_status = "Non disponible"

            # Tente d’extraire du JSON
            try:
                data = response.json()
                if "disk_total" in data and "disk_free" in data:
                    disk_total = data.get("disk_total", 0)
                    disk_free = data.get("disk_free", 0)
                    disk_status = "OK"
            except ValueError:
                # Pas de JSON → on ignore le stockage
                pass

            return {
                "status": status,
                "disk_total": disk_total,
                "disk_free": disk_free,
                "disk_status": disk_status
            }

        else:
            # Code HTTP non 200 → DOWN
            return {
                "status": "DOWN",
                "disk_total": 0,
                "disk_free": 0,
                "disk_status": "Indisponible"
            }

    except requests.RequestException:
        # Impossible de joindre le serveur → DOWN
        return {
            "status": "DOWN",
            "disk_total": 0,
            "disk_free": 0,
            "disk_status": "Indisponible"
        }
