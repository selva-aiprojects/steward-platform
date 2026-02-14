import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_public_objects():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.relname, c.relkind 
            FROM pg_class c 
            JOIN pg_namespace n ON n.oid = c.relnamespace 
            WHERE n.nspname = 'public'
        """))
        objects = [(row[0], row[1]) for row in result]
        print(f"Public objects: {objects}")
        # relkind: r = table, v = view, S = sequence, m = materialized view, f = foreign table, p = partitioned table, I = index

if __name__ == "__main__":
    list_public_objects()
