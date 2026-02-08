import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_login():
    """Test the login endpoint with trader credentials"""
    url = f"{BASE_URL}/api/v1/auth/login"
    
    # Test with default trader credentials
    payload = {
        "email": "trader@stocksteward.ai",
        "password": "trader123"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login successful!")
            print(f"User ID: {data.get('id')}")
            print(f"Email: {data.get('email')}")
            print(f"Role: {data.get('role')}")
            print(f"Access Token: {data.get('access_token', 'Not provided')[:50]}...")
            return data.get('access_token')
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint with the token"""
    if not token:
        print("No token provided, skipping protected endpoint test")
        return
    
    # Try to access a protected endpoint (using portfolio as an example)
    url = f"{BASE_URL}/api/v1/portfolio/holdings"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\nProtected Endpoint Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully accessed protected endpoint with token")
        else:
            print(f"Failed to access protected endpoint: {response.text}")
    except Exception as e:
        print(f"Error accessing protected endpoint: {e}")

def test_invalid_credentials():
    """Test login with invalid credentials"""
    url = f"{BASE_URL}/api/v1/auth/login"
    
    # Test with invalid credentials
    payload = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nInvalid Credentials Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("Correctly rejected invalid credentials")
        else:
            print(f"Unexpected response for invalid credentials: {response.text}")
    except Exception as e:
        print(f"Error testing invalid credentials: {e}")

if __name__ == "__main__":
    print("Testing StockSteward AI Authentication System\n")
    
    print("1. Testing login with valid trader credentials...")
    token = test_login()
    
    print("\n2. Testing access to protected endpoint...")
    test_protected_endpoint(token)
    
    print("\n3. Testing login with invalid credentials...")
    test_invalid_credentials()
    
    print("\nAuthentication system test completed.")