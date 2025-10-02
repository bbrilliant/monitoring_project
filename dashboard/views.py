""" from django.shortcuts import render
from django.http import JsonResponse
from .models import MonitoredAPI
from .services import check_api_health

def dashboard(request):
    return render(request, "dashboard/dashboard.html")

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
    return JsonResponse(results, safe=False) """
    
import requests
from django.http import JsonResponse

def check_api(request, api_id):
    from .models import ApiEndpoint
    api = ApiEndpoint.objects.get(id=api_id)

    try:
        response = requests.get(api.url, timeout=5, verify=False)  # ⚠️ test avec verify=False
        data = response.json()
        print("DEBUG API RESPONSE:", data)  # log console Django

        status = data.get("status", "DOWN")
        return JsonResponse({"api": api.name, "status": status})

    except Exception as e:
        print("DEBUG API ERROR:", e)
        return JsonResponse({"api": api.name, "status": "DOWN", "error": str(e)})

