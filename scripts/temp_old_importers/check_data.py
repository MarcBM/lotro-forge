"""
Script to check data in the database tables.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from database.models.items import EquipmentItem, ItemStat
from database.models.progressions import ProgressionTable, TableValue
from database.config import get_database_url
from database.session import SessionLocal

def check_data(db: Session) -> None:
    """Check the database for data integrity issues."""
    # Check items
    stmt = select(EquipmentItem)
    items = db.execute(stmt).scalars().all()
    
    if not items:
        print("No items found in database")
        return
    
    print(f"Found {len(items)} items")
    
    # Check a sample item
    sample_item = db.execute(stmt).first()
    if sample_item:
        print("\nSample item:")
        print(f"Key: {sample_item.key}")
        print(f"Name: {sample_item.name}")
        print(f"Base ILVL: {sample_item.base_ilvl}")
        print(f"Quality: {sample_item.quality}")
        print(f"Slot: {sample_item.slot}")
        print(f"Armour Type: {sample_item.armour_type}")
        print(f"Scaling: {sample_item.scaling}")
        print(f"Icon: {sample_item.icon}")
        
        # Print stats
        print("\nStats:")
        for stat in sample_item.stats:
            print(f"- {stat.stat_name}: {stat.value_table_id} (order: {stat.order})")

def main():
    # Create database connection
    try:
        with SessionLocal() as db:
            check_data(db)
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 