import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_all_tables():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename
        """))
        for row in result:
            print(f"{row[0]}.{row[1]}")

if __name__ == "__main__":
    list_all_tables()
