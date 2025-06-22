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
from .routers import web_router, register_api_routes, not_found_handler

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
app.include_router(web_router, tags=["web"])
register_api_routes(app)



# Error handlers
app.add_exception_handler(404, not_found_handler)