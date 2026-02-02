import requests
import json

BASE_URL = "http://localhost:8999/api/v1"

def list_users():
    print(f"Fetching users from {BASE_URL}/users ...")
    resp = requests.get(f"{BASE_URL}/users/")
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        users = resp.json()
        print(f"Found {len(users)} users.")
        for u in users:
            print(f" - {u['id']}: {u['email']} ({u['full_name']})")
    else:
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    list_users()
