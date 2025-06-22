"""
Authentication API module.

Organizes all authentication-related endpoints:
- public.py: Public routes (login, logout, me)
- users.py: User profile management (requires auth)
- admin.py: Admin user management (requires admin role)
"""
from .public import router as public_router
from .users import router as users_router
from .admin import router as admin_router

__all__ = ["public_router", "users_router", "admin_router"] 