"""
User management endpoints for authenticated users.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, UTC

from database.session import get_session
from database.models.user import User, UserSession
from .models import UserResponse, ProfileUpdate, PasswordChange

# --- Password hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# --- Router ---

router = APIRouter(tags=["users"])

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Update the current user's profile information.
    """
    # Middleware ensures current_user is set for protected routes
    current_user = request.state.current_user
    
    # Check if email is being changed and if it's already taken by another user
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = db_session.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    # Update the user's profile
    if profile_data.display_name is not None:
        current_user.display_name = profile_data.display_name
    if profile_data.email:
        current_user.email = profile_data.email
    
    current_user.updated_at = datetime.now(UTC)
    db_session.commit()
    db_session.refresh(current_user)
    
    return current_user

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Change the current user's password.
    """
    # Middleware ensures current_user is set for protected routes
    current_user = request.state.current_user
    
    # Get the user from the current session to avoid session issues
    user = db_session.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")
    
    # Verify new password confirmation
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match.")
    
    # Update password
    new_hashed_password = hash_password(password_data.new_password)
    print(f"🔐 Password change for user: {user.username}")
    print(f"📝 Old hash: {user.hashed_password[:20]}...")
    print(f"📝 New hash: {new_hashed_password[:20]}...")
    
    user.hashed_password = new_hashed_password
    user.updated_at = datetime.now(UTC)
    
    db_session.commit()
    
    # Verify the password was actually saved
    db_session.refresh(user)
    print(f"✅ After commit - hash: {user.hashed_password[:20]}...")
    
    return 