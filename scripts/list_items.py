#!/usr/bin/env python3
"""
Script to list item definitions from the database.
"""
import sys
import logging
import os
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Debug: Print environment variables (except password)
logger = logging.getLogger(__name__)
logger.info("Database configuration:")
logger.info(f"DB_USER: {os.getenv('DB_USER', 'not set')}")
logger.info(f"DB_NAME: {os.getenv('DB_NAME', 'not set')}")
logger.info(f"DB_HOST: {os.getenv('DB_HOST', 'not set')}")
logger.info(f"DB_PORT: {os.getenv('DB_PORT', 'not set')}")
logger.info("DB_PASSWORD: [REDACTED]")

from database.models.item import ItemDefinition
from database.config import get_database_url

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def list_items(db_url: str) -> None:
    """List all items in the database.
    
    Args:
        db_url: Database connection URL
    """
    engine = create_engine(db_url)
    
    with Session(engine) as session:
        # Query all items
        stmt = select(ItemDefinition).order_by(ItemDefinition.key)
        items = session.execute(stmt).scalars().all()
        
        if not items:
            logger.info("No items found in database")
            return
            
        logger.info(f"Found {len(items)} items in database:")
        for item in items:
            logger.info(
                f"'{item.name}' "
                f"(key={item.key}, "
                f"slot={item.slot}, "
                f"quality={item.quality}, "
                f"base_ilvl={item.base_ilvl}, "
                f"required_level={item.required_player_level})"
            )

def main():
    """Main entry point for the script."""
    try:
        db_url = get_database_url()
        list_items(db_url)
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 