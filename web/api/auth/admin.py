"""
Admin endpoints for user management (admin-only operations).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, UTC
from typing import List, Optional

from database.session import get_session
from database.models.user import User, UserSession, UserRole
from .models import (
    AdminUserCreate, UserRoleUpdate
)
from ..utils import create_api_response, create_paginated_response

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

@router.post("/users/simple", status_code=status.HTTP_201_CREATED)
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
    
    # Return standardized response
    admin_response = {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role.value,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at,
        "generated_password": generated_password,
        "email": new_user.email
    }
    
    return create_api_response(
        result=admin_response,
        metadata={
            "created_at": new_user.created_at.isoformat(),
            "is_verified": new_user.is_verified,
            "temp_email": True
        }
    )

@router.get("/users")
async def list_users(
    request: Request,
    db_session: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=100, description="Number of users to return"),
    skip: int = Query(0, ge=0, description="Number of users to skip")
):
    """
    Admin-only endpoint to list users with pagination.
    """
    # Middleware ensures current_user is set and has admin role for /api/auth/admin/* routes
    query = db_session.query(User)
    
    # Get total count for pagination info (before applying limit/offset)
    total_count = query.count()
    
    # Apply sorting and pagination
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format with role as string
    user_responses = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "display_name": user.display_name
        }
        for user in users
    ]
    
    return create_paginated_response(
        result=user_responses,
        total=total_count,
        limit=limit,
        skip=skip,
        additional_metadata={
            "retrieved_at": datetime.now(UTC).isoformat()
        }
    )

@router.put("/users/{user_id}/role")
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
    
    # Return standardized response
    user_response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "display_name": user.display_name
    }
    
    return create_api_response(
        result=user_response,
        metadata={
            "updated_at": user.updated_at.isoformat(),
            "role_changed": True
        }
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