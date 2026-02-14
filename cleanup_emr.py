import sys
import os
from sqlalchemy import create_engine, text

# Connection string for stockstewardai
DATABASE_URL = "postgresql://neondb_owner:npg_Y5IfRBbmS2FW@ep-delicate-poetry-ahi4kvos-pooler.c-3.us-east-1.aws.neon.tech/stockstewardai?sslmode=require"

def cleanup_emr():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            print("Dropping 'emr' schema from 'stockstewardai' database...")
            conn.execute(text("DROP SCHEMA IF EXISTS emr CASCADE"))
            print("Cleanup successful! 'emr' schema removed.")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_emr()
