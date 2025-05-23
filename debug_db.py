#!/usr/bin/env python3
"""Simple script to check what's in the database."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from database.config import get_database_url
from sqlalchemy import create_engine, text

def main():
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        # Check table existence
        tables_result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """))
        tables = [row[0] for row in tables_result]
        print(f"Tables in database: {tables}")
        
        # Check counts
        if 'items' in tables:
            result = conn.execute(text('SELECT COUNT(*) FROM items'))
            print(f'Total items: {result.scalar()}')
        
        if 'equipment_items' in tables:
            result = conn.execute(text('SELECT COUNT(*) FROM equipment_items'))
            print(f'Equipment items: {result.scalar()}')
        
        if 'weapons' in tables:
            result = conn.execute(text('SELECT COUNT(*) FROM weapons'))
            print(f'Weapons: {result.scalar()}')
        
        if 'progression_tables' in tables:
            result = conn.execute(text('SELECT COUNT(*) FROM progression_tables'))
            print(f'Progression tables: {result.scalar()}')
        
        # Sample data
        if 'items' in tables:
            result = conn.execute(text('SELECT key, name, item_type FROM items LIMIT 5'))
            print('\nSample items:')
            for row in result:
                print(f'  {row[0]}: {row[1]} ({row[2]})')

if __name__ == '__main__':
    main() 