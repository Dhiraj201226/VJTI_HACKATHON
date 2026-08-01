import requests

try:
    print("Fetching History...")
    response = requests.get("http://127.0.0.1:8000/api/draft/history")
    print("Status:", response.status_code)
    print("Response:", response.content[:1000])
except Exception as e:
    print("Request failed:", e)
