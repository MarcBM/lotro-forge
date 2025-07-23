"""
Pydantic models specific to authentication endpoints.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from database.models.user import UserRole

# --- User Input Models ---

class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)

class UserRoleUpdate(BaseModel):
    role: UserRole 