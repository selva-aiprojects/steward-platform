#!/usr/bin/env python3
"""
Verification script for StockSteward AI application
Checks if the backend and frontend are running properly
"""

import requests
import subprocess
import sys
import time

def check_backend():
    """Check if backend is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not accessible at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def check_api_docs():
    """Check if API documentation is accessible"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            return True
        else:
            print(f"❌ API docs returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API docs: {e}")
        return False

def check_market_data():
    """Check if market data endpoints are working"""
    try:
        response = requests.get("http://localhost:8000/api/v1/market/movers", timeout=10)
        if response.status_code == 200:
            print("✅ Market data endpoint is accessible")
            return True
        else:
            print(f"❌ Market data endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to market data endpoint: {e}")
        return False

def check_ai_prediction():
    """Check if AI prediction endpoint is working"""
    try:
        response = requests.get("http://localhost:8000/api/v1/ai/steward-prediction", timeout=10)
        if response.status_code == 200:
            print("✅ AI steward prediction endpoint is accessible")
            return True
        else:
            print(f"❌ AI prediction endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to AI prediction endpoint: {e}")
        return False

def check_frontend():
    """Check if frontend is running and accessible"""
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is running and accessible")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not accessible at http://localhost:3000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to frontend: {e}")
        return False

def main():
    """Main verification function"""
    print("[APP] Verifying StockSteward AI Application...")
    print("="*50)

    all_checks = []

    # Check backend
    print("\n[BACKEND] Checking Backend Services:")
    all_checks.append(check_backend())
    all_checks.append(check_api_docs())
    all_checks.append(check_market_data())
    all_checks.append(check_ai_prediction())

    # Check frontend
    print("\n[FRONTEND] Checking Frontend Services:")
    all_checks.append(check_frontend())

    print("\n" + "="*50)
    if all(all_checks):
        print("[SUCCESS] All services are running properly!")
        print("\n[ACCESS] Access the application:")
        print("   - Backend API: http://localhost:8000/docs")
        print("   - Frontend UI: http://localhost:3000")
        return True
    else:
        print("[ERROR] Some services are not accessible.")
        failed_count = len(all_checks) - sum(all_checks)
        print(f"   {failed_count} out of {len(all_checks)} checks failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)