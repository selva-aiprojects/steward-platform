import sys
import os
from sqlalchemy import create_engine, text, inspect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connection string for destination emr
DEST_URL = "postgresql://neondb_owner:npg_Y5IfRBbmS2FW@ep-delicate-poetry-ahi4kvos-pooler.c-3.us-east-1.aws.neon.tech/emr?sslmode=require"

def verify_migration():
    try:
        dest_engine = create_engine(DEST_URL)
        inspector = inspect(dest_engine)
        
        # Check 'emr' schema tables
        tables = inspector.get_table_names(schema='emr')
        print(f"\nTables found in 'emr' database (schema 'emr'): {len(tables)}")
        
        with dest_engine.connect() as conn:
            for table in tables:
                res = conn.execute(text(f"SELECT count(*) FROM emr.{table}"))
                count = res.scalar()
                print(f" - {table}: {count} rows")

        if len(tables) == 16:
            print("\nVERIFICATION SUCCESS: All 16 tables migrated.")
        else:
            print(f"\nVERIFICATION WARNING: Only {len(tables)}/16 tables migrated.")
            
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify_migration()
