"""
Script to check database schema and tables.
"""
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import inspect
from database.models.base import Base
from database.connection import create_engine
from database.config import get_database_url

def check_database():
    # Load environment variables
    load_dotenv()
    
    # Get database URL and create engine
    engine = create_engine(get_database_url())
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