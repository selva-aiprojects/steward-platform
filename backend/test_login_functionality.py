"""
Test script to comprehensively verify the login functionality
"""
import requests
import subprocess
import time
import sys
import os

def start_backend_server():
    """Start the backend server"""
    print("Starting backend server...")
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ], cwd=os.path.join(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give the server time to start
    time.sleep(8)
    return server_process

def test_login_endpoints():
    """Test the login functionality"""
    base_url = "http://localhost:8000"
    
    print("\n=== Testing Login Functionality ===")
    
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
    print("Starting comprehensive login functionality test...")
    
    # Start the backend server
    server_process = start_backend_server()
    
    try:
        # Test the login endpoints
        test_login_endpoints()
        
        print("\n=== Login Functionality Test Complete ===")
        
    finally:
        # Stop the server
        print("\nStopping backend server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()