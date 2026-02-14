import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_miscellaneous_tables():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'emr', 'storeai')
        """))
        objects = [(row[0], row[1]) for row in result]
        print(f"Miscellaneous objects: {objects}")

if __name__ == "__main__":
    list_miscellaneous_tables()
