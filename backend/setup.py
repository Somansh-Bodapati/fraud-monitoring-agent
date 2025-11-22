"""
Setup script to create initial admin user
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

def create_admin_user():
    """Create an admin user if one doesn't exist"""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        
        db.add(admin)
        db.commit()
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("\n⚠️  Please change the password after first login!")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

