"""
Authentication middleware for all protected routes.
"""
import logging
from datetime import datetime, UTC
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from database.session import SessionLocal
from database.models.user import User, UserSession

logger = logging.getLogger(__name__)

AUTH_SESSION_COOKIE_NAME = "auth_session_token"

def validate_user_session(auth_token: str, db_session: Session) -> Tuple[Optional[User], Optional[str]]:
    """
    Validate a user session token and update last activity.
    
    Args:
        auth_token: The session token to validate
        db_session: Database session
        
    Returns:
        Tuple of (User object, error message). If user is None, error message explains why.
    """
    if not auth_token:
        return None, "Not authenticated (no session cookie)."
    
    try:
        user_auth_session = db_session.query(UserSession).filter(
            UserSession.token == auth_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now(UTC)
        ).first()
        
        if not user_auth_session:
            return None, "Session expired or invalid."
        
        user = db_session.query(User).filter(
            User.id == user_auth_session.user_id,
            User.is_active == True
        ).first()
        
        if not user:
            return None, "User not found or inactive."
        
        # Update user's last activity time (only if more than 6 hours have passed)
        current_time = datetime.now(UTC)
        if not user.last_login or (current_time - user.last_login).total_seconds() > 21600:  # 6 hours
            user.last_login = current_time
            db_session.commit()
        
        return user, None
        
    except Exception as e:
        return None, f"Authentication error: {str(e)}"

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates authentication and protects routes.
    Sets request.state.current_user for authenticated users.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Define which web routes require authentication
        self.protected_web_routes = {
            "/account",
            "/admin", 
            "/builder",
            "/database",
            "/builds",
            "/release-notes"
        }
        
        # Define which web routes require admin access
        self.admin_web_routes = {
            "/admin"
        }
        
        # Define API route patterns that require authentication
        self.protected_api_patterns = [
            "/api/auth/users/",     # User profile management requires auth
            "/api/data/",           # All data API routes require auth
        ]
        
        # Define API route patterns that require admin access
        self.admin_api_patterns = [
            "/api/auth/admin/",     # All admin API routes require admin role
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Always try to get the current user from session if available
        auth_token = request.cookies.get(AUTH_SESSION_COOKIE_NAME)
        current_user = None
        
        if auth_token:
            try:
                with SessionLocal() as db_session:
                    user, error_message = validate_user_session(auth_token, db_session)
                    if user:
                        current_user = user
                        request.state.current_user = user
            except Exception as e:
                logger.error(f"Authentication middleware error: {e}")
                # Don't fail the request, just don't set current_user
                pass
        
        # Check if this route needs protection
        path = request.url.path
        is_api_route = path.startswith("/api/")
        
        # Check web routes
        if path in self.protected_web_routes:
            if not current_user:
                return RedirectResponse(url="/?login_required=1", status_code=status.HTTP_303_SEE_OTHER)
            
            # Check admin access for admin web routes
            if path in self.admin_web_routes and current_user.role.value != 'admin':
                return RedirectResponse(url="/?admin_required=1", status_code=status.HTTP_303_SEE_OTHER)
        
        # Check API routes
        elif is_api_route:
            # Check if API route requires authentication
            requires_auth = any(path.startswith(pattern) for pattern in self.protected_api_patterns)
            requires_admin = any(path.startswith(pattern) for pattern in self.admin_api_patterns)
            
            if requires_auth or requires_admin:
                if not current_user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Not authenticated."}
                    )
                
                # Check admin access for admin API routes
                if requires_admin and current_user.role.value != 'admin':
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Admin access required."}
                    )
        
        return await call_next(request) 