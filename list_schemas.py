import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_schemas():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg_%%' AND nspname != 'information_schema'"))
        schemas = [row[0] for row in result]
        print(f"Schemas: {schemas}")

if __name__ == "__main__":
    list_schemas()
