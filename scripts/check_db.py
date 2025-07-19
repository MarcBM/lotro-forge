"""
Script to check database schema and tables.
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import inspect
from database.session import engine

def check_database():
    """Check database schema and display table information."""
    inspector = inspect(engine)
    
    print("\nDatabase Tables:")
    print("-" * 50)
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        print("Columns:")
        for column in inspector.get_columns(table_name):
            print(f"  - {column['name']}: {column['type']}")
        
        print("\nForeign Keys:")
        for fk in inspector.get_foreign_keys(table_name):
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        print("\nIndexes:")
        for index in inspector.get_indexes(table_name):
            print(f"  - {index['name']}: {index['column_names']}")

if __name__ == "__main__":
    check_database() 