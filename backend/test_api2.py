import requests

try:
    print("Testing API...")
    payload = {"objective": "Sanctioning of funds for modernizing district courts in the Vidarbha region.", "language": "Marathi"}
    response = requests.post("http://127.0.0.1:8000/api/draft/initiate", json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Request failed:", e)
