"""
Pydantic models specific to authentication endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from database.models.user import UserRole

# --- User Response Models ---

class UserResponse(BaseModel):
    """Standard user response with all essential fields."""
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    role: str  # Return as string for frontend simplicity
    created_at: datetime

class UserListResponse(BaseModel):
    """User response for admin user list."""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    display_name: Optional[str] = None

# --- User Input Models ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    display_name: Optional[str] = Field(None, max_length=100)

class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER

class AdminUserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    generated_password: str  # Only for admin response
    email: str  # Use regular string instead of EmailStr for temp emails

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)

class UserRoleUpdate(BaseModel):
    role: UserRole 