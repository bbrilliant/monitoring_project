from django.shortcuts import render
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
    return JsonResponse(results, safe=False)
