#!/usr/bin/env python3
"""
StockSteward AI Startup Script
Starts the backend server with yfinance integration
"""

import os
import sys
import subprocess
import signal
import time

def main():
    print("Starting StockSteward AI with yfinance integration...")
    print("Loading application...")
    
    # Import and start the application
    import uvicorn
    from app.main import app
    
    print("Starting server on http://0.0.0.0:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()