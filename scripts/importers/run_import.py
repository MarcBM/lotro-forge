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

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from database.models.base import Base
from database.config import get_database_url
from scripts.importers.progressions import ProgressionsImporter
from scripts.importers.items import ItemImporter
from scripts.copy_icons import copy_required_icons  # Import icon copying function

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
    engine = create_engine(get_database_url())
    if create_tables:
        Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()

def wipe_database(engine):
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
                      help='Drop all tables and recreate them before importing')
    args = parser.parse_args()
    
    # Setup logging
    log_dir = Path(args.log_dir) if args.log_dir else None
    setup_logging(log_dir)
    logger = logging.getLogger(__name__)
    
    try:
        # Setup database and run importers
        logger.info("Setting up database connection...")
        engine = create_engine(get_database_url())
        
        # Wipe database if requested
        if args.wipe:
            wipe_database(engine)
        
        import_type = args.import_type
        
        with database_session(args.create_tables) as session:
            success = True
            
            if import_type == 'items':
                # When importing items, automatically include required progressions and icons
                logger.info("Importing items (includes required progressions and icons)...")
                
                # Step 1: Create item importer to analyze required progression tables
                items_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-items-db/items.xml')
                item_importer = ItemImporter(items_path, session)
                
                logger.info("Analyzing items to determine required progression tables...")
                required_tables = item_importer.get_required_progression_tables()
                if not required_tables:
                    logger.error("No required progression tables found in items")
                    return 1
                
                # Step 2: Import required progression tables first
                progressions_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-data/lore/progressions.xml')
                progressions_importer = ProgressionsImporter(progressions_path, session)
                
                logger.info("Importing required progression tables...")
                try:
                    if not progressions_importer.run(required_tables):
                        success = False
                        logger.error("ProgressionsImporter failed")
                        session.rollback()
                    else:
                        session.commit()
                        logger.info("Progression tables imported successfully")
                except Exception as e:
                    success = False
                    logger.error(f"ProgressionsImporter failed with error: {str(e)}", exc_info=True)
                    session.rollback()
                
                # Step 3: Import items
                if success:
                    logger.info("Importing items...")
                    try:
                        if not item_importer.run():
                            success = False
                            logger.error("ItemImporter failed")
                            session.rollback()
                        else:
                            session.commit()
                            logger.info("Items imported successfully")
                    except Exception as e:
                        success = False
                        logger.error(f"ItemImporter failed with error: {str(e)}", exc_info=True)
                        session.rollback()
                
                # Step 4: Copy required icons
                if success:
                    logger.info("Copying required icons...")
                    try:
                        copied, skipped, missing = copy_required_icons(session)
                        logger.info(f"Icon copy complete: {copied} new, {skipped} existing, {missing} missing")
                    except Exception as e:
                        logger.error(f"Failed to copy icons: {str(e)}")
                        success = False
                        
            elif import_type == 'progressions':
                # Import only progressions (for development/testing)
                progressions_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-data/lore/progressions.xml')
                progressions_importer = ProgressionsImporter(progressions_path, session)
                
                logger.info("Importing all progression tables...")
                try:
                    if not progressions_importer.run():
                        success = False
                        logger.error("ProgressionsImporter failed")
                        session.rollback()
                    else:
                        session.commit()
                except Exception as e:
                    success = False
                    logger.error(f"ProgressionsImporter failed with error: {str(e)}", exc_info=True)
                    session.rollback()
            
            if success:
                logger.info("Import completed successfully")
                return 0
            else:
                logger.error("Import failed")
                return 1
                
    except Exception as e:
        logger.error(f"Import failed with error: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 