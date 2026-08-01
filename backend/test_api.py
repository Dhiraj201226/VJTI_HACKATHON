import requests

try:
    response = requests.post("http://127.0.0.1:8000/api/draft/initiate", json={"objective": "Sanctioning of funds", "language": "Marathi"})
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Request failed:", e)
