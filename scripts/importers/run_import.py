"""
Script to run the data import process.

This script handles importing LOTRO data with intelligent dependency management:
- 'items': Imports equipment items along with required progression tables and icons
- 'progressions': Imports only progression tables (for development/testing)

Items cannot function without their progression tables (for stat calculations) and 
icons (for display), so these dependencies are automatically included when importing items.
"""
import argparse
import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from database.models.base import Base
from database.config import get_database_url
from scripts.importers.progressions import ProgressionsImporter
from scripts.importers.items import ItemImporter
from scripts.copy_icons import copy_required_icons  # Import icon copying function
from database.session import SessionLocal, engine

def setup_logging(log_dir: Path = None):
    """Configure logging for the import script.
    
    Args:
        log_dir: Directory to store log files. If None, uses current directory.
    """
    if log_dir is None:
        log_dir = Path.cwd()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'import.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    logging.getLogger(__name__).info(f"Logging to {log_file}")

@contextmanager
def database_session(create_tables: bool = False):
    """Get a database session with optional table creation.
    
    Args:
        create_tables: If True, create tables if they don't exist
    """
    if create_tables:
        Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def wipe_database():
    """Drop all tables and recreate them.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    logger = logging.getLogger(__name__)
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(engine)
    logger.info("Recreating tables...")
    Base.metadata.create_all(engine)
    logger.info("Database wiped successfully")

def copy_icons(required_icons: set) -> None:
    """Copy required icon files to the web static directory."""
    logger = logging.getLogger(__name__)
    
    # Define source and destination paths
    source_dir = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-icons/items')
    dest_dir = Path('web/static/icons/items')
    
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    skipped = 0
    missing = 0
    
    for icon_id in required_icons:
        source_file = source_dir / f"{icon_id}.png"
        dest_file = dest_dir / f"{icon_id}.png"
        
        if not source_file.exists():
            missing += 1
            logger.warning(f"Icon not found: {source_file}")
            continue
            
        if dest_file.exists():
            skipped += 1
            continue
            
        try:
            import shutil
            shutil.copy2(source_file, dest_file)
            copied += 1
        except Exception as e:
            logger.error(f"Failed to copy {source_file} to {dest_file}: {e}")
    
    logger.info(f"Icon copy complete: {copied} new, {skipped} existing, {missing} missing")

def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(description='Import LOTRO data into the database')
    parser.add_argument('--import-type', type=str, choices=['items', 'progressions'],
                      default='items', help='Type of data to import (items includes required progressions and icons)')
    parser.add_argument('--log-dir', type=str,
                      help='Directory to store log files (default: current directory)')
    parser.add_argument('--create-tables', action='store_true',
                      help='Create database tables if they don\'t exist')
    parser.add_argument('--wipe', action='store_true',
                      help='Drop and recreate all tables before importing')
    
    args = parser.parse_args()
    
    # Set up logging
    log_dir = Path(args.log_dir) if args.log_dir else Path.cwd()
    setup_logging(log_dir / f"import_{args.import_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {args.import_type} import...")
    
    # Define absolute paths for real data
    items_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-items-db/items.xml')
    progressions_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-data/lore/progressions.xml')
    dps_tables_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-data/lore/dpsTables.xml')
    
    try:
        # Handle table creation/wiping
        if args.wipe:
            wipe_database()
        elif args.create_tables:
            Base.metadata.create_all(engine)
        
        with SessionLocal() as session:
            if args.import_type == 'items':
                # Import items with automatic dependency handling
                logger.info("Starting comprehensive items import with dependencies...")
                
                # Create item importer with DPS tables path
                item_importer = ItemImporter(items_path, session, dps_tables_path=dps_tables_path)
                
                # 1. Get required progression tables
                logger.info("Analyzing required progression tables...")
                required_progression_tables = item_importer.get_required_progression_tables()
                
                # 2. Import required progression tables
                if required_progression_tables:
                    progressions_importer = ProgressionsImporter(progressions_path, session)
                    progressions_importer.import_specific_tables(required_progression_tables)
                
                # 3. Get required DPS tables
                logger.info("Analyzing required DPS tables...")
                required_dps_tables = item_importer.get_required_dps_tables()
                
                # 4. Import required DPS tables
                if required_dps_tables:
                    success = item_importer.import_required_dps_tables(required_dps_tables)
                    if not success:
                        logger.error("Failed to import required DPS tables")
                        return
                
                # 5. Import items
                logger.info("Importing items...")
                item_importer.run()
                
                # 6. Get required icons BEFORE session closes
                logger.info("Collecting required icons...")
                required_icons = item_importer.get_required_icons()
                
                # 7. Explicit commit to ensure data is saved
                logger.info("Committing database changes...")
                session.commit()
                
            elif args.import_type == 'progressions':
                # Import only progressions
                logger.info("Starting progressions-only import...")
                progressions_importer = ProgressionsImporter(progressions_path, session)
                progressions_importer.run()
                
                # Explicit commit for progressions too
                logger.info("Committing database changes...")
                session.commit()
        
        # Copy required icons AFTER session closes (outside the session context)
        if args.import_type == 'items' and 'required_icons' in locals() and required_icons:
            logger.info("Copying required icons...")
            copy_icons(required_icons)
        
        logger.info(f"{args.import_type.title()} import completed successfully!")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise

if __name__ == '__main__':
    sys.exit(main()) 