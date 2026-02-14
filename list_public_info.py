import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_public_info():
    with engine.connect() as conn:
        print("\nExtensions in DB:")
        result = conn.execute(text("SELECT extname FROM pg_extension"))
        for row in result:
            print(f" - {row[0]}")
            
        print("\nTypes in public schema:")
        result = conn.execute(text("""
            SELECT typname 
            FROM pg_type t 
            JOIN pg_namespace n ON n.oid = t.typnamespace 
            WHERE n.nspname = 'public'
        """))
        for row in result:
            print(f" - {row[0]}")

if __name__ == "__main__":
    list_public_info()
