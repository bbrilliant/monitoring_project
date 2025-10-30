import requests

def check_api_health(url):
    """
    Vérifie si une API répond avec un code 200.
    Retourne True si UP, False sinon.
    """
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
