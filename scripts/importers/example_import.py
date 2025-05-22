"""
Example import script: imports both progressions and items from example_data directory.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logging
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from database.connection import create_engine
from database.config import get_database_url
from scripts.importers.progressions import ProgressionsImporter
from scripts.importers.items import ItemImporter

EXAMPLE_DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'example_data'
PROGRESSIONS_FILE = EXAMPLE_DATA_DIR / 'example_progressions.xml'
ITEMS_FILE = EXAMPLE_DATA_DIR / 'example_items.xml'


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
def database_session():
    engine = create_engine(get_database_url())
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

def main():
    load_dotenv()
    setup_logging()
    logging.info(f"Importing from example data directory: {EXAMPLE_DATA_DIR}")
    with database_session() as session:
        # Import progressions
        logging.info(f"Importing progressions from {PROGRESSIONS_FILE}")
        progressions_importer = ProgressionsImporter(PROGRESSIONS_FILE, session)
        progressions_importer.run()
        logging.info("Progressions import complete.")

        # Import items
        logging.info(f"Importing items from {ITEMS_FILE}")
        items_importer = ItemImporter(ITEMS_FILE, session)
        items_importer.run()
        logging.info("Items import complete.")

if __name__ == "__main__":
    main() 