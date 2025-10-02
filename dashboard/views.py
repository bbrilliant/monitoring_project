from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import MonitoredAPI
from .services import check_api_health
import requests

def api_dashboard(request):
    return render(request, "dashboard/apidashboard.html")

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
    
def api_detail(request, name):
    api = get_object_or_404(MonitoredAPI, name=name)
    return render(request, "dashboard/api_detail.html", {"api": api})

def api_detail_data(request, name):
    api = get_object_or_404(MonitoredAPI, name=name)

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