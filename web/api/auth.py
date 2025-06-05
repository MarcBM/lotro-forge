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
from typing import Optional, Annotated, Union, List
from pydantic import BaseModel, EmailStr, Field
from fastapi.responses import RedirectResponse

from database.session import get_session
from database.models.user import User, UserSession, UserRole

# --- Pydantic models for request/response ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    display_name: Optional[str] = Field(None, max_length=100)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    display_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)

class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER

class AdminUserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    generated_password: str  # Only for admin response
    email: str  # Use regular string instead of EmailStr for temp emails

class UserListResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    display_name: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: UserRole

# --- Password hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_random_password(length: int = 8) -> str:
    """Generate a simple random password using alphanumeric characters."""
    import string
    import random
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

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

# --- Custom exception for web authentication redirects ---

class AuthenticationRequiredException(Exception):
    """Exception raised when authentication is required for web routes."""
    def __init__(self, redirect_url: str = "/?login_required=1"):
        self.redirect_url = redirect_url
        super().__init__("Authentication required")

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
        is_active=True,
        is_verified=False
    )
    
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Update the current user's profile information.
    """
    # Check if email is being changed and if it's already taken by another user
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = db_session.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already taken by another user."
            )
        current_user.email = profile_data.email
    
    # Update profile fields (only if provided)
    if profile_data.display_name is not None:
        current_user.display_name = profile_data.display_name.strip() if profile_data.display_name.strip() else None
    
    # Save changes
    db_session.commit()
    db_session.refresh(current_user)
    
    return current_user

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Change the current user's password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )
    
    # Check that new passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match."
        )
    
    # Check that new password is different from current
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password."
        )
    
    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    db_session.commit()
    
    return 

@router.post("/create_simple_user", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_simple_user(
    user_in: AdminUserCreate,
    db_session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    """
    Admin-only endpoint to create a new user with just username and generated password.
    """
    # Check if a user with the same username already exists
    if db_session.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken.")
    
    # Generate a random password
    generated_password = generate_random_password()
    hashed_password = hash_password(generated_password)
    
    # Create a temporary email using username
    temp_email = f"{user_in.username}@placeholder.email"
    
    # Create a new user
    new_user = User(
        username=user_in.username,
        email=temp_email,  # Temporary email
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=True,
        is_verified=False
    )
    
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    # Return user info with generated password
    return AdminUserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        generated_password=generated_password,
        email=temp_email
    )

@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    db_session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    """
    Admin-only endpoint to list all users.
    """
    users = db_session.query(User).order_by(User.created_at.desc()).all()
    return users

@router.put("/users/{user_id}/role", response_model=UserListResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db_session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    """
    Admin-only endpoint to update a user's role.
    """
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    user.role = role_update.role
    db_session.commit()
    db_session.refresh(user)
    
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db_session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    """
    Admin-only endpoint to delete a user.
    """
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Prevent admins from deleting themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You cannot delete your own account."
        )
    
    db_session.delete(user)
    db_session.commit()
    
    return 