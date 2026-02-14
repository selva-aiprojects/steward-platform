from app.core.database import SessionLocal
from app.models.user import User
import json

db = SessionLocal()
try:
    users = db.query(User).all()
    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "full_name": u.full_name,
            "is_active": u.is_active
        })
    with open("user_list_debug.json", "w") as f:
        json.dump(user_list, f, indent=4)
finally:
    db.close()
