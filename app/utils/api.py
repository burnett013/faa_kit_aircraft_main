import os, requests

API = os.getenv("API_BASE", "http://api_service:8000")

def get_json(path: str, **params):
    r = requests.get(f"{API}{path}", params=params or None, timeout=30)
    r.raise_for_status()
    return r.json()