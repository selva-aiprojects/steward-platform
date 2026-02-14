import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def compare_users():
    with engine.connect() as conn:
        for schema in ['emr', 'storeai']:
            print(f"\nColumns in {schema}.users:")
            result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = '{schema}' AND table_name = 'users'
                ORDER BY column_name
            """))
            for row in result:
                print(f" - {row[0]} ({row[1]})")

if __name__ == "__main__":
    compare_users()
