import requests
import json

url = "http://localhost:8000/api/v1/ai/chat"
headers = {
    "Content-Type": "application/json",
    "X-User-Id": "1"
}
data = {
    "message": "Hello, can you see the market?"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json().get('response')}")
except Exception as e:
    print(f"Error: {e}")
