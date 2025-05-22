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

from database.config import get_database_url
from database.models.item import ItemDefinition

# Paths
LOTRO_COMPANION_ROOT = Path('/home/marcb/workspace/lotro/lotro_companion')
ICONS_SOURCE_DIR = LOTRO_COMPANION_ROOT / 'lotro-icons' / 'items'
STATIC_ICONS_DIR = project_root / 'web' / 'static' / 'icons' / 'items'

def get_required_icons(session: Session) -> Set[str]:
    """Get the set of unique icon IDs from the database.
    
    Args:
        session: Database session
        
    Returns:
        Set[str]: Set of icon IDs that need to be copied
    """
    # Query all items with non-null icons
    stmt = select(ItemDefinition).where(ItemDefinition.icon.isnot(None))
    items = session.execute(stmt).scalars().all()
    
    # Collect unique icon IDs
    required_icons = set()
    for item in items:
        if item.icon:
            required_icons.update(item.icon.split('-'))
    
    return required_icons

def copy_icons(required_icons: Set[str], source_dir: Path, target_dir: Path) -> Tuple[int, int, int]:
    """Copy required icons from source to target directory.
    
    Args:
        required_icons: Set of icon IDs to copy
        source_dir: Source directory containing icon files
        target_dir: Target directory to copy icons to
        
    Returns:
        Tuple[int, int, int]: (copied, skipped, missing) counts
    """
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy each icon file
    copied = 0
    skipped = 0
    missing = 0
    for icon_id in required_icons:
        source_file = source_dir / f"{icon_id}.png"
        target_file = target_dir / f"{icon_id}.png"
        
        # Skip if target already exists
        if target_file.exists():
            skipped += 1
            continue
            
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            copied += 1
        else:
            print(f"Warning: Icon file not found: {source_file}")
            missing += 1
    
    return copied, skipped, missing

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
            engine = create_engine(get_database_url())
            session = Session(engine)
            should_close = True
        else:
            should_close = False
            
        try:
            # Get required icons from database
            required_icons = get_required_icons(session)
            print(f"Found {len(required_icons)} unique icon IDs in database")
            
            # Copy icons
            copied, skipped, missing = copy_icons(required_icons, ICONS_SOURCE_DIR, STATIC_ICONS_DIR)
            
            # Print summary
            print(f"\nIcon copy complete:")
            print(f"- Copied {copied} new icons")
            print(f"- Skipped {skipped} existing icons")
            if missing > 0:
                print(f"- {missing} icons were missing")
            
            return copied, skipped, missing
            
        finally:
            if should_close:
                session.close()
            
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