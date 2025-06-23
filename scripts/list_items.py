#!/usr/bin/env python3
"""
Script to list item definitions from the database.
"""
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
import argparse
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.models.items import EquipmentItem
from database.config import get_database_url
from database.session import SessionLocal

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def list_items(
    db: Session,
    slot: Optional[str] = None,
    quality: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None
) -> None:
    """List items with optional filtering."""
    # Build query
    stmt = select(EquipmentItem).order_by(EquipmentItem.key)
    
    # Apply filters
    if slot:
        stmt = stmt.where(EquipmentItem.slot == slot)
    if quality:
        stmt = stmt.where(EquipmentItem.quality == quality)
    if min_level:
        stmt = stmt.where(EquipmentItem.base_ilvl >= min_level)
    if max_level:
        stmt = stmt.where(EquipmentItem.base_ilvl <= max_level)
    
    # Execute query
    items = db.execute(stmt).scalars().all()
    
    # Print items
    for item in items:
        print(f"{item.key}: {item.name} (ilvl {item.base_ilvl}, {item.quality}, {item.slot})")

def main():
    parser = argparse.ArgumentParser(description="List items from the database")
    parser.add_argument("--slot", help="Filter by equipment slot")
    parser.add_argument("--quality", help="Filter by item quality")
    parser.add_argument("--min-level", type=int, help="Minimum item level")
    parser.add_argument("--max-level", type=int, help="Maximum item level")
    args = parser.parse_args()
    
    # Create database connection
    try:
        with SessionLocal() as db:
            list_items(
                db,
                slot=args.slot,
                quality=args.quality,
                min_level=args.min_level,
                max_level=args.max_level
            )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 