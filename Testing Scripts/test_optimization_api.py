import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Sample authentication token (you'll need to replace this with a real token)
# For testing purposes, you might need to first register/login to get a valid token
TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_portfolio_optimization():
    """Test the portfolio optimization endpoint"""
    url = f"{BASE_URL}/api/v1/portfolio-optimization/portfolio-optimize"
    
    # Prepare the request payload
    payload = {
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
        "start_date": (datetime.now() - timedelta(days=365)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "optimization_method": "markowitz",
        "objective_metric": "sharpe_ratio",
        "constraints": {
            "min_weight": 0.05,
            "max_weight": 0.5
        },
        "risk_free_rate": 0.02
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_optimization_results():
    """Test retrieving optimization results"""
    url = f"{BASE_URL}/api/v1/portfolio-optimization/portfolio-optimization-results"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_strategy_optimization():
    """Test the strategy optimization endpoint"""
    url = f"{BASE_URL}/api/v1/backtesting/optimize"
    
    # Prepare the request payload
    payload = {
        "symbol": "AAPL",
        "strategy_name": "sma_crossover",
        "start_date": (datetime.now() - timedelta(days=90)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "parameter_space": {
            "short_period": [10, 20, 30],
            "long_period": [50, 100, 200]
        },
        "objective_metric": "sharpe_ratio",
        "optimization_method": "grid_search"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_strategy_optimization_results():
    """Test retrieving strategy optimization results"""
    url = f"{BASE_URL}/api/v1/backtesting/optimization-results"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Portfolio Optimization API...")
    
    # Note: These tests will fail without a valid authentication token
    # You'll need to obtain a valid token by registering/logging in first
    
    print("\n1. Testing Strategy Optimization:")
    test_strategy_optimization()
    
    print("\n2. Testing Retrieval of Strategy Optimization Results:")
    test_get_strategy_optimization_results()
    
    print("\n3. Testing Portfolio Optimization:")
    test_portfolio_optimization()
    
    print("\n4. Testing Retrieval of Portfolio Optimization Results:")
    test_get_optimization_results()
    
    print("\nNote: To run these tests successfully, you need to:")
    print("- Register a user account")
    print("- Log in to get an authentication token")
    print("- Replace 'YOUR_AUTH_TOKEN_HERE' with the actual token")