"""
Error handling routes.

This module contains custom error handlers for different HTTP status codes,
organized separately from the main app.py for better maintainability.
"""
from fastapi import Request
from fastapi.templating import Jinja2Templates

# Setup templates - reuse the same path structure
from ..config.config import TEMPLATES_DIR
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

async def not_found_handler(request: Request, exc):
    """Handle 404 Not Found errors by rendering a custom error page."""
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    ) 