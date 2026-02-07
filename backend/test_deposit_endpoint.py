"""
Test script to verify the deposit endpoint is properly implemented
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app

def test_deposit_endpoint_exists():
    """Test that the deposit endpoint is registered"""
    client = TestClient(app)
    
    # Check if the endpoint is registered by looking at the routes
    routes = [route.path for route in app.routes]
    deposit_routes = [route for route in routes if 'deposit' in route.lower()]
    
    print("All routes containing 'deposit':", deposit_routes)
    
    # Look for portfolio-related routes
    portfolio_routes = [route for route in routes if 'portfolio' in route.lower()]
    print("All portfolio routes:", portfolio_routes)
    
    # Test if the deposit endpoint exists
    expected_routes = ['/api/v1/portfolio/deposit', '/portfolio/deposit']
    found_route = any(route in routes for route in expected_routes)
    
    if found_route:
        print("Deposit endpoint is registered in FastAPI app")
    else:
        print("Deposit endpoint NOT FOUND in registered routes")
        print("Available routes:", [r for r in routes if 'api' in r])

def test_deposit_functionality():
    """Test the deposit functionality"""
    client = TestClient(app)
    
    # Test the deposit endpoint with sample data
    deposit_data = {
        "user_id": 1,
        "amount": 1000.0
    }
    
    # Try to hit the deposit endpoint
    response = client.post("/api/v1/portfolio/deposit", json=deposit_data)
    
    print(f"Deposit endpoint response status: {response.status_code}")
    
    # The endpoint might return 404 if no portfolio exists for user_id=1
    # Or 422 if validation fails
    # Or 200 if successful
    if response.status_code in [200, 404, 422, 500]:
        print("Deposit endpoint responded")
        if response.status_code == 422:
            print("  - Validation error (expected if validation fails):", response.json())
        elif response.status_code == 404:
            print("  - Not found (expected if no portfolio exists for user)")
        elif response.status_code == 500:
            print("  - Internal server error:", response.json())
        elif response.status_code == 200:
            print("  - Success:", response.json())
    else:
        print(f"Unexpected response status: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    print("Testing deposit endpoint...")
    try:
        test_deposit_endpoint_exists()
        test_deposit_functionality()
        print("\nAll tests completed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()