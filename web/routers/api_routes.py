"""
API routes organization and registration.

This module centralizes all API router imports and provides a single function
to register all API routes with the main FastAPI application.
"""
from fastapi import FastAPI

from ..api.data import equipment_router, essences_router
from ..api.auth import public_router, users_router, admin_router

def register_api_routes(app: FastAPI) -> None:
    """
    Register all API routes with the FastAPI application.
    
    This function includes all API routers with their appropriate prefixes and tags.
    Add new API routers here as they are created to keep the main app.py clean.
    
    Args:
        app: The FastAPI application instance
    """
    # Data API
    app.include_router(equipment_router, prefix="/api/data/equipment", tags=["equipment"])
    app.include_router(essences_router, prefix="/api/data/essences", tags=["essences"])
    
    # Authentication API
    app.include_router(public_router, prefix="/api/auth", tags=["auth"])
    app.include_router(users_router, prefix="/api/auth/users", tags=["users"])
    app.include_router(admin_router, prefix="/api/auth/admin", tags=["admin"])
    
    # TODO: Add new API routers here as they are created:
    # app.include_router(builds_router, prefix="/api/builds", tags=["builds"])
    # app.include_router(character_router, prefix="/api/characters", tags=["characters"])
    # app.include_router(progressions_router, prefix="/api/data/progressions", tags=["progressions"])
    # app.include_router(traits_router, prefix="/api/data/traits", tags=["traits"]) 