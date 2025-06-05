"""
Authentication middleware for API routes.
"""
import logging
from datetime import datetime, UTC
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from database.session import SessionLocal
from database.models.user import User, UserSession

logger = logging.getLogger(__name__)

AUTH_SESSION_COOKIE_NAME = "auth_session_token"

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically protects all API routes (except auth endpoints).
    
    This middleware runs before any API endpoint and validates the user's session,
    returning 401 Unauthorized if the user is not authenticated.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Define which paths should be excluded from authentication
        self.excluded_paths = {
            "/api/auth/login",
            "/api/auth/logout", 
            "/api/auth/me",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Check for authentication
        auth_token = request.cookies.get(AUTH_SESSION_COOKIE_NAME)
        if not auth_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated (no session cookie)."}
            )
        
        # Validate session
        try:
            with SessionLocal() as db_session:
                user_auth_session = db_session.query(UserSession).filter(
                    UserSession.token == auth_token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(UTC)
                ).first()
                
                if not user_auth_session:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Session expired or invalid."}
                    )
                
                user = db_session.query(User).filter(
                    User.id == user_auth_session.user_id,
                    User.is_active == True
                ).first()
                
                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "User not found or inactive."}
                    )
                
                # Add user to request state for endpoints that need it
                request.state.current_user = user
                
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication error."}
            )
        
        return await call_next(request) 