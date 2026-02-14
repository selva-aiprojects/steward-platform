import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_public_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        print(f"Public tables: {tables}")

if __name__ == "__main__":
    list_public_tables()
