"""
Script to copy required item icons from lotro_companion to our static directory.
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Set, Tuple, Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.config import DatabaseConfig
from database.connection import DatabaseConnection
from database.models.items import Item

# Import data path configuration
from config.data_paths import get_data_paths

# Get configured paths
data_paths = get_data_paths()
ICONS_SOURCE_DIR = data_paths.icons_source_dir
STATIC_ICONS_DIR = data_paths.icons_dest_dir

def get_required_icons(session: Session) -> Set[str]:
    """Get the set of unique icon IDs from the database.
    
    Args:
        session: Database session
        
    Returns:
        Set[str]: Set of icon IDs that need to be copied
    """
    # Query all items with non-null icons
    stmt = select(Item).where(Item.icon.isnot(None))
    items = session.execute(stmt).scalars().all()
    
    # Collect unique icon IDs
    required_icons = set()
    for item in items:
        if item.icon:
            required_icons.update(item.icon.split('-'))
    
    return required_icons

def copy_icons(db: Session, source_dir: str, target_dir: str) -> Tuple[int, int, int]:
    """
    Copy icon files from source directory to target directory.
    Only copies icons that are referenced by items in the database.
    
    Returns:
        Tuple[int, int, int]: (copied, skipped, missing) counts
    """
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Get all unique icon IDs from all items
    stmt = select(Item).where(Item.icon.isnot(None))
    items = db.execute(stmt).scalars().all()
    
    # Collect all icon IDs
    icon_ids = set()
    for item in items:
        if item.icon:
            icon_ids.update(item.icon.split('-'))
    
    # Copy each icon file
    copied_count = 0
    skipped_count = 0
    missing_count = 0
    
    for icon_id in icon_ids:
        source_file = os.path.join(source_dir, f"{icon_id}.png")
        target_file = os.path.join(target_dir, f"{icon_id}.png")
        
        if not os.path.exists(source_file):
            missing_count += 1
            continue
            
        if os.path.exists(target_file):
            skipped_count += 1
        else:
            shutil.copy2(source_file, target_file)
            copied_count += 1
    
    print(f"Icon copy summary: {copied_count} copied, {skipped_count} skipped, {missing_count} missing")
    return copied_count, skipped_count, missing_count

def copy_required_icons(session: Optional[Session] = None) -> Tuple[int, int, int]:
    """Copy all required icons from the database to the static directory.
    
    Args:
        session: Optional database session to use. If None, a new session will be created.
        
    Returns:
        Tuple[int, int, int]: (copied, skipped, missing) counts
    """
    try:
        # Use provided session or create a new one
        if session is None:
            config = DatabaseConfig.from_env()
            db_connection = DatabaseConnection(config)
            
            with db_connection.get_session() as session:
                # Get required icons from database
                required_icons = get_required_icons(session)
                print(f"Found {len(required_icons)} unique icon IDs in database")
                
                # Copy icons and return actual counts
                return copy_icons(session, str(ICONS_SOURCE_DIR), str(STATIC_ICONS_DIR))
        else:
            # Get required icons from database
            required_icons = get_required_icons(session)
            print(f"Found {len(required_icons)} unique icon IDs in database")
            
            # Copy icons and return actual counts
            return copy_icons(session, str(ICONS_SOURCE_DIR), str(STATIC_ICONS_DIR))
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        raise

def main():
    """Main entry point for the icon copy script."""
    try:
        copy_required_icons()
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 