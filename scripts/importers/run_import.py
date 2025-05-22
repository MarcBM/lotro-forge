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

# Only import what we need for the wrapper script
from base import Base
from progressions import ProgressionsImporter
from items import ItemImporter

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
def database_session(db_url: str, create_tables: bool = False):
    """Create and manage a database session.
    
    Args:
        db_url: Database connection URL
        create_tables: Whether to create tables if they don't exist
    
    Yields:
        Session: Database session
    """
    engine = create_engine(db_url)
    if create_tables:
        Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()

def get_importers(import_type: str, source_path: Path, session: Session) -> list:
    """Get the list of importers to run based on import type.
    
    Args:
        import_type: Type of data to import ('all', 'items', or 'progressions')
        source_path: Path to the source data directory
        session: Database session
    
    Returns:
        List of importer instances
    """
    importers = []
    if import_type in ['all', 'items']:
        importers.append(ItemImporter(source_path, session))
    if import_type in ['all', 'progressions']:
        importers.append(ProgressionsImporter(source_path, session))
    return importers

def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(description='Import LOTRO data into the database')
    parser.add_argument('--source', type=str, required=True,
                      help='Path to the lotro_companion data directory')
    parser.add_argument('--db-url', type=str, required=True,
                      help='Database URL (e.g., sqlite:///lotro_forge.db)')
    parser.add_argument('--import-type', type=str, choices=['all', 'items', 'progressions'],
                      default='all', help='Type of data to import')
    parser.add_argument('--log-dir', type=str,
                      help='Directory to store log files (default: current directory)')
    parser.add_argument('--create-tables', action='store_true',
                      help='Create database tables if they don\'t exist')
    args = parser.parse_args()
    
    # Setup logging
    log_dir = Path(args.log_dir) if args.log_dir else None
    setup_logging(log_dir)
    logger = logging.getLogger(__name__)
    
    try:
        # Setup database and run importers
        logger.info("Setting up database connection...")
        with database_session(args.db_url, args.create_tables) as session:
            # Get importers to run
            importers = get_importers(args.import_type, Path(args.source), session)
            
            if not importers:
                logger.error("No importers selected")
                return 1
            
            # Run importers
            success = True
            for importer in importers:
                logger.info(f"Starting {importer.__class__.__name__}...")
                try:
                    if not importer.run():
                        success = False
                        logger.error(f"{importer.__class__.__name__} failed")
                except Exception as e:
                    success = False
                    logger.error(f"{importer.__class__.__name__} failed with error: {str(e)}", exc_info=True)
            
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