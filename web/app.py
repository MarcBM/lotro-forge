"""
Main FastAPI application for the LOTRO Forge web interface.
"""
import logging
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pathlib import Path
import traceback
from sqlalchemy.orm import Session

from .config.config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    CORS_ORIGINS, STATIC_DIR, TEMPLATES_DIR,
    DEBUG
)
from .middleware.security import add_security_middleware
from .middleware.auth import AuthenticationMiddleware
from .api.items import router as items_router
from .api.auth import router as auth_router, get_current_user, AuthenticationRequiredException

from database.models.user import User
from database.session import get_session

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Add middleware
add_security_middleware(app)

# Add authentication middleware for API routes
app.add_middleware(AuthenticationMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handler for development
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    if DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc()
            }
        )
    raise exc

# Add authentication redirect handler
@app.exception_handler(AuthenticationRequiredException)
async def auth_exception_handler(request: Request, exc: AuthenticationRequiredException):
    return RedirectResponse(url=exc.redirect_url, status_code=status.HTTP_303_SEE_OTHER)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include routers
app.include_router(items_router, prefix="/api/items", tags=["items"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# Helper function for web route authentication
async def get_current_user_for_web(request: Request, db_session: Session = Depends(get_session)) -> User:
    """
    Get current user for web routes, raising AuthenticationRequiredException if not authenticated.
    """
    try:
        return await get_current_user(request, db_session)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            if "session expired" in e.detail.lower():
                raise AuthenticationRequiredException("/?session_expired=1")
            elif "not found" in e.detail.lower():
                raise AuthenticationRequiredException("/?user_inactive=1") 
            else:
                raise AuthenticationRequiredException("/?login_required=1")
        raise e

# Routes
@app.get("/")
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "base/home.html",
        {"request": request}
    )

@app.get("/builds")
async def builds(request: Request, current_user: User = Depends(get_current_user_for_web)):
    """Render the builds page - a repository of community-created builds. Requires authentication."""
    return templates.TemplateResponse(
        "builds/builds.html",
        {"request": request, "current_user": current_user}
    )

@app.get("/builder")
async def builder(request: Request, current_user: User = Depends(get_current_user_for_web)):
    """Render the builder page - where users can create and edit builds. Requires authentication."""
    return templates.TemplateResponse(
        "builder/builder.html",
        {"request": request, "current_user": current_user}
    )

@app.get("/database")
async def database(request: Request, current_user: User = Depends(get_current_user_for_web)):
    """Render the database page. Requires authentication."""
    return templates.TemplateResponse(
        "database/database.html",
        {"request": request, "current_user": current_user}
    )

@app.get("/account")
async def account(request: Request, current_user: User = Depends(get_current_user_for_web)):
    """Render the account management page. Requires authentication."""
    return templates.TemplateResponse(
        "account/account.html",
        {"request": request, "current_user": current_user}
    )

@app.get("/admin")
async def admin(request: Request, current_user: User = Depends(get_current_user_for_web)):
    """Render the admin page. Requires admin authentication."""
    if current_user.role.value != 'admin':
        raise AuthenticationRequiredException("/?admin_required=1")
    
    return templates.TemplateResponse(
        "admin/admin.html",
        {"request": request, "current_user": current_user}
    )

@app.get("/release-notes")
async def release_notes(request: Request, current_user: User = Depends(get_current_user_for_web)):
    """Display release notes and roadmap. Requires authentication."""
    return templates.TemplateResponse(
        "release_notes/release_notes.html", 
        {"request": request, "current_user": current_user}
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )