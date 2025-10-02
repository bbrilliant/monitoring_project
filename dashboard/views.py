from django.shortcuts import render
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
                down_apis.append({(api.name),(api.url)})
        except Exception:
            down_count += 1
            down_apis.append({(api.name),(api.url)})

    stats = {
        "total": total_apis,
        "up": up_count,
        "down": down_count,
    }

    return render(request, "dashboard/dashboard.html", {
        "stats": stats,
        "down_apis": down_apis,
    })
