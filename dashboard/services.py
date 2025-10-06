import requests

def check_api_health(url):
    try:
        response = requests.get(url, timeout=5)

        # 🟢 Cas 1 : statut HTTP 200 → API UP
        if response.status_code == 200:
            status = "UP"
            disk_total = 0
            disk_free = 0
            disk_status = "Non disponible"

            # Essaie d’extraire du JSON
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

        # 🔴 Cas 2 : statut HTTP 503 → API DOWN (souvent erreur serveur)
        elif response.status_code == 503:
            try:
                data = response.json()
                disk_total = data.get("disk_total", 0)
                disk_free = data.get("disk_free", 0)
                disk_status = data.get("disk_status", "Indisponible")
            except ValueError:
                disk_total = 0
                disk_free = 0
                disk_status = "Indisponible"

            return {
                "status": "DOWN",
                "disk_total": disk_total,
                "disk_free": disk_free,
                "disk_status": disk_status
            }

        # ⚪ Cas 3 : autre code HTTP → DOWN
        else:
            return {
                "status": "DOWN",
                "disk_total": 0,
                "disk_free": 0,
                "disk_status": "Indisponible"
            }

    except requests.RequestException:
        # 🔻 Cas 4 : API injoignable
        return {
            "status": "DOWN",
            "disk_total": 0,
            "disk_free": 0,
            "disk_status": "Indisponible"
        }
