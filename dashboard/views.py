# dashboard/views.py
import concurrent.futures
import requests
from django.shortcuts import render, get_object_or_404
from .models import MonitoredAPI

# --- Fonction utilitaire ---
def check_api_health(api_url):
    try:
        response = requests.get(api_url, timeout=5, verify=False)

        # Si code 200 → API UP
        if response.status_code == 200:
            try:
                data = response.json()
                return {
                    "status": "UP",
                    "disk_status": data.get("details", {}).get("diskSpace", {}).get("status", "N/A"),
                    "disk_total": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total", 0),
                    "disk_free": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free", 0)
                }
            except ValueError:
                # Pas de JSON → API UP mais pas de stockage
                return {
                    "status": "UP",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0
                }

        # Sinon API DOWN
        return {
            "status": "DOWN",
            "disk_status": "N/A",
            "disk_total": 0,
            "disk_free": 0
        }

    except requests.RequestException:
        # Erreur réseau ou timeout
        return {
            "status": "DOWN",
            "disk_status": "N/A",
            "disk_total": 0,
            "disk_free": 0
        }

# --- Vue principale : dashboard ---
def dashboard(request):
    apis = MonitoredAPI.objects.all()
    api_data = []

    # On utilise ThreadPoolExecutor pour rendre la page plus rapide
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_api = {executor.submit(check_api_health, api.url): api for api in apis}
        for future in concurrent.futures.as_completed(future_to_api):
            api = future_to_api[future]
            try:
                result = future.result()
                api_data.append({
                    "name": api.name,
                    "url": api.url,
                    **result
                })
            except Exception:
                api_data.append({
                    "name": api.name,
                    "url": api.url,
                    "status": "DOWN",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0
                })

    # Séparation des UP et DOWN
    up_apis = [a for a in api_data if a["status"] == "UP"]
    down_apis = [a for a in api_data if a["status"] != "UP"]

    stats = {
        "total": len(api_data),
        "up": len(up_apis),
        "down": len(down_apis)
    }

    return render(request, "dashboard/dashboard.html", {
        "stats": stats,
        "down_apis": down_apis
    })

# --- Vue des détails d'une API ---
# Exemple dans views.py

def api_detail(request, api_id):
    api = get_object_or_404(MonitoredAPI, id=api_id)
    api_info = check_api_health(api.url)

    # Conversion en Go et ajout de l'espace utilisé
    disk_total = api_info.get("disk_total", 0)
    disk_free = api_info.get("disk_free", 0)
    disk_used = disk_total - disk_free

    api_info["disk_total_gb"] = round(disk_total / (1024 ** 3), 2)
    api_info["disk_free_gb"] = round(disk_free / (1024 ** 3), 2)
    api_info["disk_used_gb"] = round(disk_used / (1024 ** 3), 2)

    context = {
        "api": api,
        "api_info": api_info
    }
    return render(request, "dashboard/api_detail.html", context)



# --- Vue des APIs UP ---
def api_up_list(request):
    apis = MonitoredAPI.objects.all()
    api_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_api = {executor.submit(check_api_health, api.url): api for api in apis}
        for future in concurrent.futures.as_completed(future_to_api):
            api = future_to_api[future]
            try:
                result = future.result()
                if result["status"] == "UP":
                    api_data.append({
                        "id": api.id,  # ✅ ajouté
                        "name": api.name,
                        "url": api.url,
                        "disk_total": round(result["disk_total"] / (1024 ** 3), 2),
                        "disk_free": round(result["disk_free"] / (1024 ** 3), 2),
                        "disk_used": round(((result["disk_total"] - result["disk_free"])) / (1024 ** 3), 2),
                        **result
                    })
            except Exception:
                continue

    return render(request, "dashboard/api_up_list.html", {"up_apis": api_data})
