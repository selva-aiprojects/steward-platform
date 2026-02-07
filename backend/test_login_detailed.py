"""
Test script to verify the login functionality
"""
import requests
import time

def test_login_functionality():
    """Test the login functionality"""
    base_url = "http://localhost:8000"
    
    print("=== Testing Login Functionality ===")
    
    # Test 1: Admin login
    print("\n1. Testing Admin Login...")
    admin_login_data = {
        "email": "admin@stocksteward.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=admin_login_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Admin login successful!")
            admin_result = response.json()
            print(f"   User Info: ID={admin_result.get('id')}, Role={admin_result.get('role')}")
        else:
            print("   ❌ Admin login failed!")
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
    
    # Test 2: Trader login
    print("\n2. Testing Trader Login...")
    trader_login_data = {
        "email": "trader@stocksteward.ai",
        "password": "trader123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=trader_login_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Trader login successful!")
            trader_result = response.json()
            print(f"   User Info: ID={trader_result.get('id')}, Role={trader_result.get('role')}")
        else:
            print("   ❌ Trader login failed!")
    except Exception as e:
        print(f"   ❌ Trader login error: {e}")
    
    # Test 3: Business Owner login
    print("\n3. Testing Business Owner Login...")
    owner_login_data = {
        "email": "owner@stocksteward.ai",
        "password": "owner123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=owner_login_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Business Owner login successful!")
            owner_result = response.json()
            print(f"   User Info: ID={owner_result.get('id')}, Role={owner_result.get('role')}")
        else:
            print("   ❌ Business Owner login failed!")
    except Exception as e:
        print(f"   ❌ Business Owner login error: {e}")
    
    # Test 4: Invalid credentials
    print("\n4. Testing Invalid Credentials...")
    invalid_login_data = {
        "email": "invalid@test.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=invalid_login_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid credentials!")
        else:
            print("   ⚠️  Invalid credentials were not properly rejected!")
    except Exception as e:
        print(f"   ❌ Invalid credentials test error: {e}")
    
    # Test 5: Check server health
    print("\n5. Testing Server Health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Health Status Code: {response.status_code}")
        print(f"   Health Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Server health check passed!")
        else:
            print("   ❌ Server health check failed!")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")

def main():
    print("Starting login functionality test...")
    print("Make sure the backend server is running on http://localhost:8000")
    
    # Test the login endpoints
    test_login_functionality()
    
    print("\n=== Login Functionality Test Complete ===")

if __name__ == "__main__":
    main()