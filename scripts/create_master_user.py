"""
Script to create the initial master user (Vuldyn) with admin privileges.
This should be run once during initial setup.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.session import SessionLocal
from database.models.user import User, UserRole
from web.api.auth import hash_password

def create_master_user():
    """Creates the master user (Vuldyn) with admin privileges."""
    with SessionLocal() as session:
        # Check if master user already exists
        existing_user = session.query(User).filter(User.username == "Vuldyn").first()
        if existing_user:
            print("Master user 'Vuldyn' already exists.")
            return
        
        # Create master user
        master_user = User(
            username="Vuldyn",
            email="vuldyn@lotroforge.com",  # Placeholder email
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN,
            display_name="Vuldyn",
            is_active=True,
            is_verified=True  # Master user is pre-verified
        )
        try:
            session.add(master_user)
            session.commit()
            print("Successfully created master user 'Vuldyn' with admin privileges.")
        except Exception as e:
            session.rollback()
            print(f"Error creating master user: {e}")
            raise

if __name__ == "__main__":
    create_master_user() 