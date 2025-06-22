"""
Public authentication endpoints (login, logout).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
import secrets
from typing import Optional

from database.session import get_session
from database.models.user import User, UserSession, UserRole
from ...middleware.auth import AUTH_SESSION_COOKIE_NAME
from .models import UserResponse

# --- Password hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- Session token (cookie) helpers ---

AUTH_SESSION_EXPIRY_DAYS = 30

def create_auth_session_token() -> str:
    """Creates a new authentication session token for user login."""
    return secrets.token_urlsafe(32)

def get_auth_session_expiry() -> datetime:
    """Calculates when the authentication session should expire."""
    return datetime.now(UTC) + timedelta(days=AUTH_SESSION_EXPIRY_DAYS)

# --- Router ---

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=UserResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_session),
    response: Response = None
):
    """
    Authenticate a user (using OAuth2 password flow) and create an authentication session.
    """
    user = db_session.query(User).filter(
        User.username == form_data.username,
        User.is_active == True
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    
    # Update user's last login time
    user.last_login = datetime.now(UTC)
    
    # Create a new authentication session
    auth_token = create_auth_session_token()
    expires_at = get_auth_session_expiry()
    
    user_auth_session = UserSession(
        user_id=user.id,
        token=auth_token,
        expires_at=expires_at,
        is_active=True,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    db_session.add(user_auth_session)
    db_session.commit()
    
    # Set the authentication session cookie
    response.set_cookie(
        AUTH_SESSION_COOKIE_NAME,
        auth_token,
        expires=expires_at,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    db_session: Session = Depends(get_session),
    response: Response = None
):
    """
    Invalidate the current authentication session and clear the session cookie.
    """
    auth_token: Optional[str] = request.cookies.get(AUTH_SESSION_COOKIE_NAME)
    if auth_token:
         user_auth_session = db_session.query(UserSession).filter(
             UserSession.token == auth_token,
             UserSession.is_active == True
         ).first()
         if user_auth_session:
             user_auth_session.is_active = False
             db_session.commit()
    
    response.delete_cookie(
        AUTH_SESSION_COOKIE_NAME,
        secure=True,
        httponly=True,
        samesite="lax"
    )
    return

@router.get("/me", response_model=Optional[UserResponse])
async def get_current_user_info(request: Request):
    """
    Get the current user's basic information if authenticated, or return null if not.
    
    This endpoint is called by the frontend to check authentication status.
    It handles both authenticated and unauthenticated cases gracefully.
    Returns only essential user information for frontend use.
    """
    # Check if user is authenticated (middleware may have set current_user)
    current_user = getattr(request.state, 'current_user', None)
    
    if current_user:
        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            display_name=current_user.display_name,
            role=current_user.role.value,
            created_at=current_user.created_at
        )
    else:
        return None 