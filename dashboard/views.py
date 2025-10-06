""" import urllib
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import MonitoredAPI
from .services import check_api_health
import requests


def api_data(request):
    apis = MonitoredAPI.objects.all()
    results = []
    for api in apis:
        health = check_api_health(api.url)
        results.append({
            "name": api.name,
            "url": api.url,
            **health
        })
    return JsonResponse(results, safe=False)

def dashboard(request):
    apis = MonitoredAPI.objects.all()

    total_apis = apis.count()
    up_count = 0
    down_count = 0
    down_apis = []

    for api in apis:
        try:
            response = requests.get(api.url, timeout=5, verify=False)
            data = response.json()
            status = data.get("status", "DOWN")

            if status == "UP":
                up_count += 1
            else:
                down_count += 1
                # extraire stockage si dispo
                disk = data.get("details", {}).get("diskSpace", {}).get("details", {})
                free = round(disk.get("free", 0) / (1024**3), 2)  # en Go
                total = round(disk.get("total", 0) / (1024**3), 2)  # en Go
                down_apis.append({
                    "name": api.name,
                    "url": api.url,
                    "free": free,
                    "total": total,
                })
        except Exception:
            down_count += 1
            down_apis.append({
                "name": api.name,
                "url": api.url,
                "free": None,
                "total": None,
            })

    stats = {
        "total": total_apis,
        "up": up_count,
        "down": down_count,
    }

    return render(request, "dashboard/dashboard.html", {
        "stats": stats,
        "down_apis": down_apis,
    })
    
def api_detail(request, encoded_url):
    api_url = urllib.parse.unquote(encoded_url)  # décoder l’URL
    api_data = check_api_health(api_url)  # ta fonction pour vérifier l'état
    api = {
        "name": api_url,  # ou un champ Name si dispo
        "url": api_url,
        **api_data
    }
    return render(request, "dashboard/api_detail.html", {"api": api})


def api_detail_data(request, url):
    api = get_object_or_404(MonitoredAPI, url=url)

    try:
        response = requests.get(api.url, timeout=5, verify=False)
        data = response.json()
        status = data.get("status", "DOWN")

        disk = data.get("details", {}).get("diskSpace", {}).get("details", {})
        disk_free = disk.get("free", 0)
        disk_total = disk.get("total", 0)
        disk_status = data.get("details", {}).get("diskSpace", {}).get("status", "N/A")

    except Exception:
        status = "DOWN"
        disk_free = 0
        disk_total = 0
        disk_status = "N/A"

    api_data = {
        "name": api.name,
        "url": api.url,
        "status": status,
        "disk_status": disk_status,
        "disk_total": disk_total,
        "disk_free": disk_free,
    }

    return JsonResponse([api_data], safe=False)

def api_up_list(request):
    apis_up = []

    for api in MonitoredAPI.objects.all():
        try:
            response = requests.get(api.url, timeout=5, verify=False)

            if response.status_code == 200:
                # Par défaut : UP sans stockage
                api_data = {
                    "name": api.name,
                    "url": api.url,
                    "status": "UP",
                    "disk_status": "N/A",
                    "disk_total": 0,
                    "disk_free": 0,
                }

                # Si c’est du JSON, on complète avec les infos disque
                try:
                    data = response.json()
                    api_data["status"] = data.get("status", "UP")
                    api_data["disk_status"] = data.get("details", {}).get("diskSpace", {}).get("status", "N/A")
                    api_data["disk_total"] = data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total", 0)
                    api_data["disk_free"] = data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free", 0)
                except ValueError:
                    pass  # pas JSON, on garde juste "UP"

                apis_up.append(api_data)

        except requests.RequestException:
            # API inaccessible → pas ajoutée aux UP
            pass

    return render(request, "dashboard/api_up_list.html", {"apis_up": apis_up})
 """
 
import urllib
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import MonitoredAPI
from .services import check_api_health
import requests

def dashboard(request):
    """Affiche le dashboard (vide au départ, rempli en JS)"""
    return render(request, "dashboard/dashboard.html")

def api_data(request):
    """Renvoie la liste des APIs et leur statut en JSON"""
    apis = MonitoredAPI.objects.all()
    results = []

    for api in apis:
        health = check_api_health(api.url)
        results.append({
            "name": api.name,
            "url": api.url,
            "status": health["status"],
            "disk_status": health["disk_status"],
            "disk_total": health["disk_total"],
            "disk_free": health["disk_free"]
        })

    return JsonResponse(results, safe=False)

def api_detail(request, api_url):
    #Détail d’une API
    api = get_object_or_404(MonitoredAPI, url=api_url)
    health = check_api_health(api.url)
    context = {"api": api, "health": health}
    return render(request, "dashboard/api_detail.html", context)

def api_up_list(request):
    """Liste des APIs UP"""
    apis = MonitoredAPI.objects.all()
    up_apis = []
    for api in apis:
        health = check_api_health(api.url)
        if health["status"] == "UP":
            up_apis.append({"name": api.name, "url": api.url})
    return render(request, "dashboard/api_up_list.html", {"up_apis": up_apis})
