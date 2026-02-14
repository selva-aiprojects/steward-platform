import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from backend.app.core.database import engine

def list_alembic_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT schemaname, tablename FROM pg_tables WHERE tablename LIKE 'alembic%%'"))
        objects = [(row[0], row[1]) for row in result]
        print(f"Alembic objects: {objects}")

if __name__ == "__main__":
    list_alembic_tables()
