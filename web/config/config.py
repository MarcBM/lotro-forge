import os
from pathlib import Path
from typing import List

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment settings
ENV = os.getenv("LOTRO_FORGE_ENV", "development")
DEBUG = ENV == "development"

# Application settings
APP_NAME = "LotRO Forge"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "A tool for creating, managing, and optimizing builds for end-game characters in The Lord of the Rings Online."

# Web settings
WEB_HOST = os.getenv("LOTRO_FORGE_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("LOTRO_FORGE_PORT", "8000"))
WEB_WORKERS = int(os.getenv("LOTRO_FORGE_WORKERS", "1"))

# CORS settings
def get_cors_origins() -> List[str]:
    """Get CORS origins from environment or use defaults."""
    # Check if CORS_ORIGINS environment variable is set
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        # Parse comma-separated string into list
        return [origin.strip() for origin in cors_env.split(",")]
    
    # Default origins based on environment
    if DEBUG:
        return [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    else:
        return [
            "https://lotroforge.com",
            "https://www.lotroforge.com",
            "https://lotro-forge.fly.dev",
        ]

CORS_ORIGINS: List[str] = get_cors_origins()

# Database settings
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR}/lotro_forge.db"
)

# Static files
STATIC_DIR = BASE_DIR / "web" / "static"
TEMPLATES_DIR = BASE_DIR / "web" / "templates"

# Security settings (no secret key needed - using database session tokens) 