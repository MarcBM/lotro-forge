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
from scripts.importers.items import ItemImporter, ItemDefinitionData

class ExampleItemImporter(ItemImporter):
    """Custom importer for example items that doesn't apply filtering."""
    
    def parse_source(self) -> list[ItemDefinitionData]:
        """Parse items.xml into ItemDefinitionData objects without filtering."""
        root = self.parse_xml(self.items_file)
        items = []
        
        for item_elem in root.findall(".//item"):
            try:
                # Required attributes
                key = int(item_elem.get("key", "0"))
                name = item_elem.get("name", "")
                min_ilvl = int(item_elem.get("level", "0"))  # Use level attribute for base_ilvl
                slot = item_elem.get("slot", "")
                quality = item_elem.get("quality", "")
                required_player_level = int(item_elem.get("minLevel", "0"))
                
                # Optional attributes
                scaling = item_elem.get("scaling")
                value_table_id = item_elem.get("valueTableId")
                if value_table_id is not None:
                    value_table_id = int(value_table_id)
                armour_type = item_elem.get("armourType")  # Get armour type if present
                
                # Parse stats
                stats = []
                stats_elem = item_elem.find("stats")
                if stats_elem is not None:
                    for stat_elem in stats_elem.findall("stat"):
                        stat_name = stat_elem.get("name", "")
                        stat_scaling = stat_elem.get("scaling", "")
                        if stat_name and stat_scaling:
                            stats.append({
                                "name": stat_name,
                                "scaling": stat_scaling
                            })
                
                item = ItemDefinitionData(
                    key=key,
                    name=name,
                    min_ilvl=min_ilvl,
                    slot=slot,
                    quality=quality,
                    required_player_level=required_player_level,
                    scaling=scaling,
                    value_table_id=value_table_id,
                    armour_type=armour_type,  # Include armour type
                    stats=stats
                )
                items.append(item)
                
            except (ValueError, AttributeError) as e:
                self.logger.error(f"Failed to parse item element {item_elem.get('key', 'unknown')}: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(items)} items in example data")
        return items

    def get_required_progression_tables(self) -> set[str]:
        """Extract the set of progression table IDs required by the items without filtering."""
        if not self.validate_source():
            return set()
            
        root = self.parse_xml(self.items_file)
        required_tables = set()
        
        for item_elem in root.findall(".//item"):
            try:
                # Get value table ID from item stats
                stats_elem = item_elem.find("stats")
                if stats_elem is not None:
                    for stat_elem in stats_elem.findall("stat"):
                        stat_scaling = stat_elem.get("scaling", "")
                        if stat_scaling:
                            required_tables.add(stat_scaling)
                
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Failed to parse item element {item_elem.get('key', 'unknown')}: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(required_tables)} required progression tables")
        return required_tables

# Example data paths
EXAMPLE_DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'example_data'
ITEMS_FILE = EXAMPLE_DATA_DIR / 'example_items.xml'

# Main data paths
MAIN_DATA_DIR = Path('/home/marcb/workspace/lotro/lotro_companion')
PROGRESSIONS_FILE = MAIN_DATA_DIR / 'lotro-data/lore/progressions.xml'


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
        # Setup database
        engine = create_engine(get_database_url())
        
        # Wipe database if requested
        if args.wipe:
            wipe_database(engine)
        
        with database_session(True) as session:
            # First, analyze example items to get required progression tables
            logger.info("Analyzing example items to determine required progression tables...")
            items_importer = ExampleItemImporter(ITEMS_FILE, session)  # Use custom importer
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

            # Import example items
            logger.info(f"Importing example items from {ITEMS_FILE}")
            if not items_importer.run():
                logger.error("Items import failed")
                return 1
            logger.info("Items import complete.")

        logger.info("All imports completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Import failed with error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 