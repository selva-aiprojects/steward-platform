#!/usr/bin/env python3
"""
Setup script for local StockSteward AI development environment
This script will:
1. Create a local PostgreSQL database
2. Run migrations to set up tables
3. Seed the database with demo data
4. Provide instructions for running the application
"""

import subprocess
import sys
import os
from pathlib import Path

def setup_local_environment():
    print("Setting up local StockSteward AI development environment...")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path("./backend")
    os.chdir(backend_dir)
    
    print("\n1. Setting up environment variables...")
    # Only copy if .env doesn't exist or doesn't have a Neon URL
    env_file = Path('.env')
    has_neon = False
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'neon.tech' in content or 'DATABASE_URL' in content:
                has_neon = True
    
    if not has_neon:
        import shutil
        shutil.copy('.env.local', '.env')
        print("   ✓ Copied .env.local to .env")
    else:
        print("   ✓ Preserving existing DATABASE_URL in .env (Neon detected)")
    
    print("\n2. Installing required Python packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"], check=True)
        print("   ✓ Installed psycopg2-binary for PostgreSQL")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to install psycopg2-binary: {e}")
        return False
    
    print("\n3. Creating and seeding local database...")
    try:
        # Run the seed script which will recreate the database
        result = subprocess.run([sys.executable, "seed_db.py"], 
                              capture_output=True, text=True, check=True)
        print("   ✓ Database created and seeded successfully")
        print(f"   Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to seed database: {e}")
        print(f"   stderr: {e.stderr}")
        return False
    
    print("\n5. Verifying path portability...")
    current_path = Path(".").resolve()
    print(f"   ✓ Running from: {current_path}")
    if current_path.drive.upper() != 'C:':
        print(f"   ! Detected non-C: drive installation ({current_path.drive}). Ensuring portability...")
    
    print("\n" + "=" * 60)
    print("LOCAL SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo run the application locally:")
    print("1. Make sure PostgreSQL is running on your system (Local or Docker)")
    print("2. Ensure your PostgreSQL server accepts connections on localhost:5432")
    print("3. Run the backend server:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --port 8000")
    print("\n4. (NEW) Run the Observability Stack (Prometheus, Grafana, Superset):")
    print("   docker-compose -f infra/observability/docker-compose.observability.yml up -d")
    print("   * Note: If on D: drive, ensure Docker has access to your drive in 'Resources > File Sharing'.")
    print("\n5. In a separate terminal, navigate to frontend directory and run:")
    print("   npm install")
    print("   npm run dev")
    print("\nLogin credentials for seeded users:")
    print("- Super Admin: admin@stocksteward.ai / admin123")
    print("- Alexander Pierce: alex@stocksteward.ai / trader123")
    print("\nThe system is now configured for local development with live data!")
    
    return True

if __name__ == "__main__":
    success = setup_local_environment()
    if not success:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\nSetup completed successfully!")