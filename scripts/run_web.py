#!/usr/bin/env python3
"""
Script to run the LOTRO Forge web server.
This script starts the FastAPI application using Uvicorn with configurable settings.
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import configuration
from web.config.config import WEB_HOST, WEB_PORT, WEB_WORKERS, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the web server with configurable settings."""
    try:
        # Verify we're in the correct directory
        if not (project_root / "web" / "app.py").exists():
            logger.error("Could not find web/app.py. Make sure you're running this from the project root.")
            sys.exit(1)

        # Check if .env file exists
        if not (project_root / ".env").exists():
            logger.warning("No .env file found. Make sure your environment variables are set.")

        logger.info("Starting LOTRO Forge web server...")
        logger.info(f"Configuration: host={WEB_HOST}, port={WEB_PORT}, workers={WEB_WORKERS}")
        logger.info(f"Web interface will be available at: http://{WEB_HOST}:{WEB_PORT}")
        logger.info(f"API documentation will be available at: http://{WEB_HOST}:{WEB_PORT}/docs")
        
        # Run the server with configurable settings
        uvicorn.run(
            "web.app:app",
            host=WEB_HOST,
            port=WEB_PORT,
            workers=WEB_WORKERS if WEB_WORKERS > 1 else None,  # Only use workers if > 1
            reload=DEBUG,  # Auto-reload only in development
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 