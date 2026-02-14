from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total users found: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Role: {u.role}, Active: {u.is_active}")
finally:
    db.close()
