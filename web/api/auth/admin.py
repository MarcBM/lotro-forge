"""
Admin endpoints for user management (admin-only operations).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, UTC
from typing import List

from database.session import get_session
from database.models.user import User, UserSession, UserRole
from .models import (
    UserCreate, UserResponse, AdminUserCreate, AdminUserResponse,
    UserListResponse, UserRoleUpdate
)

# --- Password hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_random_password(length: int = 8) -> str:
    """Generate a simple random password using alphanumeric characters."""
    import string
    import random
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# --- Router ---

router = APIRouter(tags=["admin"])

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Admin-only endpoint to create a new user (e.g. for beta testers).
    """
    # Middleware ensures current_user is set and has admin role for /api/auth/admin/* routes
    
    # Check if a user with the same username or email already exists
    if db_session.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered.")
    if db_session.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    # Create the new user
    hashed_password = hash_password(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        display_name=user_in.display_name,
        is_active=True,
        is_verified=True,  # Admin-created users are auto-verified
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    return new_user

@router.post("/users/simple", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_simple_user(
    user_in: AdminUserCreate,
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Admin-only endpoint to create a new user with just username and generated password.
    """
    # Middleware ensures current_user is set and has admin role for /api/auth/admin/* routes
    
    # Check if a user with the same username already exists
    if db_session.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered.")
    
    # Generate password and create temporary email
    generated_password = generate_random_password()
    temp_email = f"{user_in.username}@temp.lotroforge.com"
    
    # Create the new user
    hashed_password = hash_password(generated_password)
    new_user = User(
        username=user_in.username,
        email=temp_email,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=True,
        is_verified=False,  # User needs to verify email
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    return AdminUserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role.value,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        generated_password=generated_password,
        email=new_user.email
    )

@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Admin-only endpoint to list all users.
    """
    # Middleware ensures current_user is set and has admin role for /api/auth/admin/* routes
    users = db_session.query(User).order_by(User.created_at.desc()).all()
    
    # Convert to response format with role as string
    return [
        UserListResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            display_name=user.display_name
        )
        for user in users
    ]

@router.put("/users/{user_id}/role", response_model=UserListResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Admin-only endpoint to update a user's role.
    """
    # Middleware ensures current_user is set and has admin role for /api/auth/admin/* routes
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    user.role = role_update.role
    user.updated_at = datetime.now(UTC)
    db_session.commit()
    db_session.refresh(user)
    
    return UserListResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
        display_name=user.display_name
    )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    request: Request,
    db_session: Session = Depends(get_session)
):
    """
    Admin-only endpoint to delete a user.
    """
    # Middleware ensures current_user is set and has admin role for /api/auth/admin/* routes
    current_user = request.state.current_user
    
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account.")
    
    # Delete all user sessions first
    db_session.query(UserSession).filter(UserSession.user_id == user_id).delete()
    
    # Delete the user
    db_session.delete(user)
    db_session.commit()
    
    return 