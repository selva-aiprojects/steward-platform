#!/usr/bin/env python3
"""
Fix Demo Users Script
This script ensures the correct demo users exist in the database with proper credentials.
"""

import sys
import os
import hashlib

# Add the project root and backend folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

def fix_demo_users():
    print("Fixing Demo Users...")
    
    db = SessionLocal()
    try:
        # Define the correct demo users
        demo_users = [
            {
                "id": 999,
                "full_name": "Super Admin",
                "email": "admin@stocksteward.ai",
                "password": "admin123",
                "role": "SUPERADMIN",
                "risk_tolerance": "LOW"
            },
            {
                "id": 777,
                "full_name": "Business Owner",
                "email": "owner@stocksteward.ai",  # Fixed: was "owner@stocksteward.ai" in seed script
                "password": "owner123",
                "role": "BUSINESS_OWNER",
                "risk_tolerance": "MODERATE"
            },
            {
                "id": 888,
                "full_name": "Auditor User",
                "email": "auditor@stocksteward.ai",  # Fixed: was "audit@stocksteward.ai" in seed script
                "password": "audit123",
                "role": "AUDITOR",
                "risk_tolerance": "LOW"
            },
            {
                "id": 100,
                "full_name": "Trader User",
                "email": "trader@stocksteward.ai",
                "password": "trader123",
                "role": "TRADER",
                "risk_tolerance": "MODERATE"
            }
        ]
        
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                print(f"User {user_data['email']} already exists, updating password...")
                existing_user.hashed_password = get_password_hash(user_data["password"])
                existing_user.full_name = user_data["full_name"]
                existing_user.role = user_data["role"]
                existing_user.risk_tolerance = user_data["risk_tolerance"]
                # Don't update ID if user already exists to avoid foreign key constraint violations
                db.add(existing_user)
            else:
                print(f"Creating user {user_data['email']}...")
                new_user = User(
                    id=user_data.get("id"),
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    risk_tolerance=user_data["risk_tolerance"],
                    is_active=True,
                    is_superuser=(user_data["role"] == "SUPERADMIN")
                )
                db.add(new_user)
        
        db.commit()
        print("Demo users fixed successfully!")
        
        # Verify users were created
        print("\nVerifying users:")
        for user_data in demo_users:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if user:
                print(f"[OK] {user_data['email']} - ID: {user.id}, Role: {user.role}")
            else:
                print(f"[MISSING] {user_data['email']} - NOT FOUND")
                
    except Exception as e:
        print(f"Error fixing demo users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_demo_users()