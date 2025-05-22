#!/usr/bin/env python3
"""
Script to run the LOTRO Forge web server.
This script starts the FastAPI application using Uvicorn with development settings.
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the web server with development settings."""
    try:
        # Verify we're in the correct directory
        if not (project_root / "web" / "app.py").exists():
            logger.error("Could not find web/app.py. Make sure you're running this from the project root.")
            sys.exit(1)

        # Check if .env file exists
        if not (project_root / ".env").exists():
            logger.warning("No .env file found. Make sure your environment variables are set.")

        logger.info("Starting LOTRO Forge web server...")
        logger.info("Web interface will be available at: http://localhost:8000")
        logger.info("API documentation will be available at: http://localhost:8000/docs")
        
        # Run the server
        uvicorn.run(
            "web.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 