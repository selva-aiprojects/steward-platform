import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.post('/api/v1/auth/login', json={'email': 'owner@stocksteward.ai', 'password': 'owner123'})
print('STATUS CODE:', response.status_code)
print('RESPONSE:', response.text)
