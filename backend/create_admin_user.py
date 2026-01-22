"""
Script to create an admin user
Run: python -m backend.create_admin_user
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data.database import SessionLocal, init_db
from backend.services.auth_service import AuthService

def create_admin_user(username="admin", email="admin@example.com", password="admin123"):
    """Create an admin user"""
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    auth_service = AuthService(db)

    try:
        # Check if admin user already exists
        existing = auth_service.user_repo.findByUsername(username)
        if existing:
            print(f"User '{username}' already exists!")
            if existing.role == "admin":
                print("User is already an admin.")
            else:
                print("Upgrading user to admin role...")
                existing.role = "admin"
                db.commit()
                print("User upgraded to admin successfully!")
            return

        # Create admin user
        print(f"Creating admin user '{username}'...")
        success, user, error = auth_service.register_user(
            username=username,
            email=email,
            password=password
        )

        if success:
            # Set role to admin
            user.role = "admin"
            db.commit()
            print(f"\nAdmin user created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Email: {email}")
            print("\nPlease login with these credentials and change the password immediately!")
        else:
            print(f"Failed to create admin user: {error}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        email = sys.argv[2] if len(sys.argv) > 2 else f"{username}@example.com"
        password = sys.argv[3] if len(sys.argv) > 3 else "admin123"
        create_admin_user(username, email, password)
    else:
        create_admin_user()
