import requests

def check_api_health(api_url):
    try:
        response = requests.get(api_url, timeout=5)
        data = response.json()
        print(data)

        return {
            "status": data.get("status", "UNKNOWN"),
            "disk_status": data.get("details", {}).get("diskSpace", {}).get("status", "N/A"),
            "disk_total": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("total", 0),
            "disk_free": data.get("details", {}).get("diskSpace", {}).get("details", {}).get("free", 0)
        }
    except Exception as e:
        return {
            "status": "DOWN",
            "disk_status": "N/A",
            "disk_total": 0,
            "disk_free": 0
        }
