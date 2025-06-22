"""
Web routes for template rendering.

This module contains all the main web page routes that render HTML templates,
organized separately from the main app.py for better maintainability.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Setup templates - reuse the same path structure
from ..config.config import TEMPLATES_DIR
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Create router
router = APIRouter()

@router.get("/")
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "base/home.html",
        {"request": request}
    )

@router.get("/builds")
async def builds(request: Request):
    """Render the builds page - a repository of community-created builds. Requires authentication."""
    return templates.TemplateResponse(
        "builds/builds.html",
        {"request": request}
    )

@router.get("/builder")
async def builder(request: Request):
    """Render the builder page - where users can create and edit builds. Requires authentication."""
    return templates.TemplateResponse(
        "builder/builder.html",
        {"request": request}
    )

@router.get("/database")
async def database(request: Request):
    """Render the database page. Requires authentication."""
    return templates.TemplateResponse(
        "database/database.html",
        {"request": request}
    )

@router.get("/account")
async def account(request: Request):
    """Render the account management page. Requires authentication."""
    return templates.TemplateResponse(
        "users/account.html",
        {"request": request}
    )

@router.get("/admin")
async def admin(request: Request):
    """Render the admin page. Requires admin authentication."""
    return templates.TemplateResponse(
        "users/admin.html",
        {"request": request}
    )

@router.get("/release-notes")
async def release_notes(request: Request):
    """Display release notes and roadmap. Requires authentication."""
    return templates.TemplateResponse(
        "release_notes/release_notes.html", 
        {"request": request}
    ) 