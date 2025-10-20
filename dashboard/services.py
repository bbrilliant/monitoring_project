from django.core.cache import cache
import requests

def check_api_health(api_url):
    cache_key = f"api_status_{api_url}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    try:
        response = requests.get(api_url, timeout=5, verify=False)
        if response.status_code == 200:
            try:
                data = response.json()
                result = {
                    "status": "UP",
                    "disk_status": data.get("details", {}).get("diskSpace", {}).get("status", "N/A"),
                    "disk_total": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total", 0),
                    "disk_free": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free", 0),
                }
            except ValueError:
                result = {"status": "UP", "disk_status": "N/A", "disk_total": 0, "disk_free": 0}
        else:
            result = {"status": "DOWN", "disk_status": "N/A", "disk_total": 0, "disk_free": 0}

    except requests.RequestException:
        result = {"status": "DOWN", "disk_status": "N/A", "disk_total": 0, "disk_free": 0}

    cache.set(cache_key, result, timeout=300)
    return result
