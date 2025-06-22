"""
Main FastAPI application for the LOTRO Forge web interface.
"""
import logging
from fastapi import FastAPI, Request, HTTPException, status
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
from .api.auth import public_router, users_router, admin_router

from database.models.user import User

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



# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include routers
app.include_router(items_router, prefix="/api/items", tags=["items"])
app.include_router(public_router, prefix="/api/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/auth/users", tags=["users"])
app.include_router(admin_router, prefix="/api/auth/admin", tags=["admin"])



# Routes
@app.get("/")
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "base/home.html",
        {"request": request}
    )

@app.get("/builds")
async def builds(request: Request):
    """Render the builds page - a repository of community-created builds. Requires authentication."""
    return templates.TemplateResponse(
        "builds/builds.html",
        {"request": request}
    )

@app.get("/builder")
async def builder(request: Request):
    """Render the builder page - where users can create and edit builds. Requires authentication."""
    return templates.TemplateResponse(
        "builder/builder.html",
        {"request": request}
    )

@app.get("/database")
async def database(request: Request):
    """Render the database page. Requires authentication."""
    return templates.TemplateResponse(
        "database/database.html",
        {"request": request}
    )

@app.get("/account")
async def account(request: Request):
    """Render the account management page. Requires authentication."""
    return templates.TemplateResponse(
        "users/account.html",
        {"request": request}
    )

@app.get("/admin")
async def admin(request: Request):
    """Render the admin page. Requires admin authentication."""
    return templates.TemplateResponse(
        "users/admin.html",
        {"request": request}
    )

@app.get("/release-notes")
async def release_notes(request: Request):
    """Display release notes and roadmap. Requires authentication."""
    return templates.TemplateResponse(
        "release_notes/release_notes.html", 
        {"request": request}
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )