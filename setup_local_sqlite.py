#!/usr/bin/env python3
"""
Setup script for local StockSteward AI development environment using SQLite
This script will:
1. Configure the application to use SQLite
2. Run the seed script to create and populate the database
3. Provide instructions for running the application
"""

import subprocess
import sys
import os
from pathlib import Path

def setup_local_sqlite_environment():
    print("Setting up local StockSteward AI development environment with SQLite...")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path("./backend")
    os.chdir(backend_dir)
    
    print("\n1. Setting up SQLite environment variables...")
    # Create a .env file that uses SQLite
    env_content = """# Local Development Database Configuration (SQLite)
DATABASE_URL=sqlite:///./stocksteward_local.db

# API Keys (set to empty or dummy values for local development)
ZERODHA_API_KEY=
ZERODHA_API_SECRET=
ZERODHA_ACCESS_TOKEN=

# AI Keys (optional for local testing)
GROQ_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HUGGINGFACE_API_KEY=

# Market Data API Keys
MARKETSTACK_API_KEY=
TRUEDATA_API_KEY=b356c6c18bb8cb117d7afc79c2b3c5b5

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true

# JWT Secret (generate a random one for production)
JWT_SECRET_KEY=supersecretkeyforlocaldevelopmentchangethisforproduction
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins (comma separated)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

# Environment
APP_ENV=DEV
EXECUTION_MODE=PAPER_TRADING
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("   + Created .env file with SQLite configuration")
    
    print("\n2. Creating and seeding local database...")
    try:
        # Run the seed script which will create the SQLite database and populate it
        result = subprocess.run([sys.executable, "seed_db.py"], 
                              capture_output=True, text=True, check=True)
        print("   + Database created and seeded successfully")
        print(f"   Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"   X Failed to seed database: {e}")
        print(f"   stderr: {e.stderr}")
        return False
    
    print("\n3. Verifying database setup...")
    try:
        # Test the database connection by importing and checking
        import sys as sys_import
        sys_import.path.append('.')
        from app.core.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()
        
        print(f"   + Database connection successful")
        print(f"   + Found {user_count} users in the database")
    except Exception as e:
        print(f"   X Database verification failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("LOCAL SQLITE SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo run the application locally:")
    print("1. Run the backend server from the backend directory:")
    print("   uvicorn app.main:app --reload --port 8000")
    print("\n2. In a separate terminal, navigate to frontend directory and run:")
    print("   npm install")
    print("   npm run dev")
    print("\nLogin credentials for seeded users:")
    print("- Super Admin: admin@stocksteward.ai / admin123")
    print("- Alexander Pierce: alex@stocksteward.ai / trader123")
    print("- Sarah Connor: sarah.c@sky.net / trader123")
    print("- Tony Stark: tony@starkintl.ai / trader123")
    print("- Bruce Wayne: bruce@waynecorp.com / trader123")
    print("- Natasha Romanoff: nat@shield.gov / trader123")
    print("\nThe system is now configured for local development with SQLite database!")
    print("The seeded data includes live trading strategies and historical data for testing.")
    
    return True

if __name__ == "__main__":
    success = setup_local_sqlite_environment()
    if not success:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\nSetup completed successfully!")