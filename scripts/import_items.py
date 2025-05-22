#!/usr/bin/env python3
"""
Script to import item definitions from XML into the database.
"""
import sys
import logging
import os
from pathlib import Path
from datetime import datetime, UTC
from sqlalchemy import create_engine
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

from parsers.item_parser import ItemParser
from domain.item import ItemDefinition as DomainItemDefinition
from database.models.item import ItemDefinition as DBItemDefinition
from database.config import get_database_url

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def convert_to_db_model(domain_item: DomainItemDefinition) -> DBItemDefinition:
    """Convert a domain ItemDefinition to a database ItemDefinition."""
    return DBItemDefinition(
        key=domain_item.key,
        name=domain_item.name,
        base_ilvl=domain_item.min_ilvl,  # Note: min_ilvl in domain is base_ilvl in DB
        slot=domain_item.slot,
        quality=domain_item.quality,
        required_player_level=domain_item.required_player_level,
        scaling=domain_item.scaling,
        value_table_id=domain_item.value_table_id
    )

def import_items(items: list[DomainItemDefinition], db_url: str) -> None:
    """Import items into the database.
    
    Args:
        items: List of domain ItemDefinition objects to import
        db_url: Database connection URL
    """
    engine = create_engine(db_url)
    
    with Session(engine) as session:
        try:
            # Convert domain models to database models
            db_items = [convert_to_db_model(item) for item in items]
            
            # Add timestamps to items
            now = datetime.now(UTC)
            for item in db_items:
                item.created_at = now
                item.updated_at = now
            
            # Add all items
            session.add_all(db_items)
            
            # Commit the transaction
            session.commit()
            logger.info(f"Successfully imported {len(items)} items into database")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error importing items: {e}")
            raise

def main():
    """Main entry point for the script."""
    # Get the XML file path from command line or use default
    if len(sys.argv) > 1:
        xml_path = Path(sys.argv[1])
    else:
        xml_path = project_root / 'example_data' / 'example_items.xml'
    
    if not xml_path.exists():
        logger.error(f"XML file not found: {xml_path}")
        sys.exit(1)
    
    try:
        # Parse items from XML using the existing parser
        logger.info(f"Parsing items from {xml_path}")
        items = ItemParser.parse_file(str(xml_path))
        logger.info(f"Successfully parsed {len(items)} items")
        
        # Get database URL and import items
        db_url = get_database_url()
        import_items(items, db_url)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 