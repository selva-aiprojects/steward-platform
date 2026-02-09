#!/usr/bin/env python3
"""
Simple verification script for StockSteward AI application
"""

import requests
import sys

def check_backend():
    """Check if backend is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("[OK] Backend is running and accessible")
            return True
        else:
            print(f"[ERROR] Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Backend is not accessible at http://localhost:8000")
        return False
    except Exception as e:
        print(f"[ERROR] Error connecting to backend: {e}")
        return False

def check_api_docs():
    """Check if API documentation is accessible"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print("[OK] API documentation is accessible")
            return True
        else:
            print(f"[ERROR] API docs returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error connecting to API docs: {e}")
        return False

def check_market_data():
    """Check if market data endpoints are working"""
    try:
        response = requests.get("http://localhost:8000/api/v1/market/movers", timeout=10)
        if response.status_code == 200:
            print("[OK] Market data endpoint is accessible")
            return True
        else:
            print(f"[ERROR] Market data endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error connecting to market data endpoint: {e}")
        return False

def check_ai_prediction():
    """Check if AI prediction endpoint is working"""
    try:
        response = requests.get("http://localhost:8000/api/v1/ai/steward-prediction", timeout=10)
        if response.status_code == 200:
            print("[OK] AI steward prediction endpoint is accessible")
            return True
        else:
            print(f"[ERROR] AI prediction endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error connecting to AI prediction endpoint: {e}")
        return False

def main():
    """Main verification function"""
    print("Verifying StockSteward AI Application...")
    print("="*50)
    
    all_checks = []
    
    # Check backend services
    print("\nChecking Backend Services:")
    all_checks.append(check_backend())
    all_checks.append(check_api_docs())
    all_checks.append(check_market_data())
    all_checks.append(check_ai_prediction())
    
    print("\n" + "="*50)
    if all(all_checks):
        print("SUCCESS: All services are running properly!")
        print("\nAccess the application:")
        print("  - Backend API: http://localhost:8000/docs")
        print("  - Frontend UI: http://localhost:3000 (if running)")
        return True
    else:
        print("ERROR: Some services are not accessible.")
        failed_count = len(all_checks) - sum(all_checks)
        print(f"  {failed_count} out of {len(all_checks)} checks failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)