"""
Script to run the data import process.
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
    """Create and manage a database session.
    
    Args:
        create_tables: Whether to create tables if they don't exist
    
    Yields:
        Session: Database session
    """
    engine = create_engine(get_database_url())
    if create_tables:
        Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()

def get_importers(import_type: str, session: Session) -> tuple[ItemImporter, ProgressionsImporter]:
    """Get the importers to run based on import type.
    
    Args:
        import_type: Type of data to import ('all', 'items', or 'progressions')
        session: Database session
    
    Returns:
        tuple[ItemImporter, ProgressionsImporter]: The item and progression importers
    """
    # Define absolute paths for real data
    items_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-items-db/items.xml')
    progressions_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-data/lore/progressions.xml')
    
    # Create both importers
    item_importer = ItemImporter(items_path, session) if import_type in ['all', 'items'] else None
    progressions_importer = ProgressionsImporter(progressions_path, session) if import_type in ['all', 'progressions'] else None
    
    return item_importer, progressions_importer

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
    parser.add_argument('--import-type', type=str, choices=['all', 'items', 'progressions'],
                      default=None, help='Type of data to import')
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
            # If only wiping was requested (no import type specified), exit here
            if args.import_type is None:
                logger.info("Database wiped successfully. No imports requested.")
                return 0
        
        # Default to 'all' if no import type specified
        import_type = args.import_type or 'all'
        
        with database_session(args.create_tables) as session:
            # Get importers
            item_importer, progressions_importer = get_importers(import_type, session)
            
            if not item_importer and not progressions_importer:
                logger.error("No importers selected")
                return 1
            
            success = True
            
            # Step 1: If importing items, get required progression tables
            required_tables = None
            if item_importer and progressions_importer:
                logger.info("Analyzing items to determine required progression tables...")
                required_tables = item_importer.get_required_progression_tables()
                if not required_tables:
                    logger.error("No required progression tables found in items")
                    return 1
            
            # Step 2: Import required progression tables
            if progressions_importer:
                logger.info("Starting ProgressionsImporter...")
                try:
                    if not progressions_importer.run(required_tables):
                        success = False
                        logger.error("ProgressionsImporter failed")
                        session.rollback()
                    else:
                        session.commit()
                except Exception as e:
                    success = False
                    logger.error(f"ProgressionsImporter failed with error: {str(e)}", exc_info=True)
                    session.rollback()
            
            # Step 3: Import items
            if item_importer and success:
                logger.info("Starting ItemImporter...")
                try:
                    if not item_importer.run():
                        success = False
                        logger.error("ItemImporter failed")
                        session.rollback()
                    else:
                        session.commit()
                except Exception as e:
                    success = False
                    logger.error(f"ItemImporter failed with error: {str(e)}", exc_info=True)
                    session.rollback()
            
            if success:
                logger.info("All imports completed successfully")
                return 0
            else:
                logger.error("One or more imports failed")
                return 1
                
    except Exception as e:
        logger.error(f"Import failed with error: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 