"""
Script to check data in the database tables.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models.item import ItemDefinition, ItemStat
from database.models.progressions import ProgressionTable, TableValue
from database.config import get_database_url

load_dotenv()

def check_data():
    db_url = get_database_url()
    print(f"\nDatabase URL: {db_url}\n")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Table row counts
    print("Table Row Counts:")
    print("-" * 50)
    with engine.connect() as conn:
        for table_name in ["alembic_version", "item_stats", "progression_tables", "table_values", "item_definitions"]:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"{table_name}: {result} rows")
    print()
    print("Sample Data:")
    print("-" * 50)
    # Sample Item
    print("\nSample Item:")
    sample_item = session.query(ItemDefinition).first()
    if sample_item:
        print(f"  Key: {sample_item.key}")
        print(f"  Name: {sample_item.name}")
        print(f"  Base iLvl: {sample_item.base_ilvl}")
        print(f"  Slot: {sample_item.slot}")
        print(f"  Quality: {sample_item.quality}")
        print(f"  Required Player Level: {sample_item.required_player_level}")
        print(f"  Scaling: {sample_item.scaling}")
        # Print stats for this item
        stats = session.query(ItemStat).filter_by(item_key=sample_item.key).all()
        print(f"  Stats ({len(stats)}):")
        for stat in stats:
            print(f"    - {stat.stat_name} (value_table_id: {stat.value_table_id})")
    else:
        print("  No items found.")
    # Sample Progression Table
    print("\nSample Progression Table:")
    sample_table = session.query(ProgressionTable).first()
    if sample_table:
        print(f"  Table ID: {sample_table.table_id}")
        print(f"  Name: {sample_table.name}")
        print(f"  Type: {sample_table.progression_type}")
        # Print a few values
        values = session.query(TableValue).filter_by(table_id=sample_table.table_id).order_by(TableValue.item_level).limit(5).all()
        print(f"  First 5 values:")
        for v in values:
            print(f"    Level {v.item_level}: {v.value}")
    else:
        print("  No progression tables found.")

if __name__ == "__main__":
    check_data() 