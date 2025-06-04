"""
Authentication API endpoints for session-based login, logout, and (admin-only) user creation.

Note on terminology:
- 'db_session': SQLAlchemy database session for database operations
- 'auth_session' or 'user_session': User's authentication session (login token)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
import secrets
from typing import Optional, Annotated, Union
from pydantic import BaseModel, EmailStr, Field

from database.session import get_session
from database.models.user import User, UserSession, UserRole

# --- Pydantic models for request/response ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    display_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

# --- Password hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- Session token (cookie) helpers ---

AUTH_SESSION_COOKIE_NAME = "auth_session_token"
AUTH_SESSION_EXPIRY_DAYS = 30

def create_auth_session_token() -> str:
    """Creates a new authentication session token for user login."""
    return secrets.token_urlsafe(32)

def get_auth_session_expiry() -> datetime:
    """Calculates when the authentication session should expire."""
    return datetime.now(UTC) + timedelta(days=AUTH_SESSION_EXPIRY_DAYS)

# --- Dependency (get current user) ---

async def get_current_user(request: Request, db_session: Session = Depends(get_session)) -> User:
    """Validates the authentication session token and returns the current user."""
    auth_token: Optional[str] = request.cookies.get(AUTH_SESSION_COOKIE_NAME)
    if not auth_token:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated (no session cookie).")
    
    user_auth_session = db_session.query(UserSession).filter(
        UserSession.token == auth_token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.now(UTC)
    ).first()
    
    if not user_auth_session:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")
    
    user = db_session.query(User).filter(
        User.id == user_auth_session.user_id,
        User.is_active == True
    ).first()
    
    if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
    return user

# --- Admin-only dependency ---

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user

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

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's information.
    """
    return current_user

@router.post("/create_user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db_session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    """
    Admin-only endpoint to create a new user (e.g. for beta testers).
    """
    # Check if a user with the same username or email already exists
    if db_session.query(User).filter(User.username == user_in.username).first():
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken.")
    if db_session.query(User).filter(User.email == user_in.email).first():
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken.")
    
    # Create a new user with hashed password
    hashed_password = hash_password(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        display_name=user_in.display_name,
        bio=user_in.bio,
        is_active=True,
        is_verified=False
    )
    
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user 