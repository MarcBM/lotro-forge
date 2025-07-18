"""
Example import script: imports items from example_data directory and required progressions from main data.
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logging
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.connection import create_engine
from database.config import get_database_url
from database.models.base import Base
from scripts.importers.progressions import ProgressionsImporter
from scripts.importers.items import ItemImporter  # Import the base importer
from scripts.copy_icons import copy_required_icons  # Import icon copying function
from database.session import SessionLocal, engine

# Import data path configuration
from config.data_paths import get_data_paths

# Example data paths
EXAMPLE_DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'example_data'
ITEMS_FILE = EXAMPLE_DATA_DIR / 'example_items.xml'

# Get configured main data paths
data_paths = get_data_paths()
PROGRESSIONS_FILE = data_paths.progressions_xml
DPS_TABLES_FILE = data_paths.dps_tables_xml

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('example_import.log', mode='w')
        ]
    )

@contextmanager
def database_session(create_tables: bool = False):
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
    logger = logging.getLogger(__name__)
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(engine)
    logger.info("Recreating tables...")
    Base.metadata.create_all(engine)
    logger.info("Database wiped successfully")

def main():
    parser = argparse.ArgumentParser(description='Import example LOTRO items and required progressions')
    parser.add_argument('--wipe', action='store_true',
                      help='Drop all tables and recreate them before importing')
    args = parser.parse_args()

    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Importing example items from: {ITEMS_FILE}")
    logger.info(f"Using progressions from: {PROGRESSIONS_FILE}")

    try:
        with database_session(True) as session:
            # First, analyze example items to get required progression tables
            logger.info("Analyzing example items to determine required progression tables...")
            items_importer = ItemImporter(ITEMS_FILE, session, skip_filters=True, dps_tables_path=DPS_TABLES_FILE)  # Add DPS tables path
            required_tables = items_importer.get_required_progression_tables()
            
            if not required_tables:
                logger.error("No required progression tables found in example items")
                return 1
                
            logger.info(f"Found {len(required_tables)} required progression tables")
            
            # Import only the required progression tables from main data
            logger.info(f"Importing required progressions from {PROGRESSIONS_FILE}")
            progressions_importer = ProgressionsImporter(PROGRESSIONS_FILE, session)
            if not progressions_importer.run(required_tables):
                logger.error("Progressions import failed")
                return 1
            logger.info("Progressions import complete.")
            
            # Get required DPS tables and import them
            logger.info("Analyzing required DPS tables...")
            required_dps_tables = items_importer.get_required_dps_tables()
            if required_dps_tables:
                logger.info(f"Found {len(required_dps_tables)} required DPS tables")
                success = items_importer.import_required_dps_tables(required_dps_tables)
                if not success:
                    logger.error("DPS tables import failed")
                    return 1
                logger.info("DPS tables import complete.")

            # Import example items
            logger.info(f"Importing example items from {ITEMS_FILE}")
            if not items_importer.run():
                logger.error("Items import failed")
                return 1
            logger.info("Items import complete.")

            # Copy required icons
            logger.info("Copying required icons...")
            try:
                copied, skipped, missing = copy_required_icons(session)
                logger.info(f"Icon copy complete: {copied} new, {skipped} existing, {missing} missing")
            except Exception as e:
                logger.error(f"Failed to copy icons: {str(e)}")
                return 1

        logger.info("All imports completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Import failed with error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 