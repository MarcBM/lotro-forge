"""
FastAPI router organization.

This module contains router definitions for better organization
of endpoints, keeping the main app.py clean and focused.

Router organization:
- web_routes.py - Main web page routes that render HTML templates
- api_routes.py - Centralized API routes registration
- error_handlers.py - Custom error handling functions
"""

from .web_routes import router as web_router
from .api_routes import register_api_routes
from .error_handlers import not_found_handler

__all__ = ["web_router", "register_api_routes", "not_found_handler"] 