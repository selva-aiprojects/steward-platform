import sys
import os
from sqlalchemy import create_engine, text

# Get the URL from the environment or use the one from .env
database_url = "postgresql://neondb_owner:npg_Y5IfRBbmS2FW@ep-delicate-poetry-ahi4kvos-pooler.c-3.us-east-1.aws.neon.tech/stockstewardai?sslmode=require&channel_binding=require"

# To create a database, we connect to a default database (like postgres or our current one)
# but we must ensure we are not in a transaction.
engine = create_engine(database_url)

def check_and_create_db():
    try:
        # Check if database exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'emr'"))
            if result.scalar():
                print("Database 'emr' already exists.")
                return True
        
        # Create database
        # We need a connection with autocommit
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            print("Attempting to create database 'emr'...")
            conn.execute(text("CREATE DATABASE emr"))
            print("Database 'emr' created successfully!")
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_and_create_db()
