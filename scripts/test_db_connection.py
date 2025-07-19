"""
Test script to verify SQLite database connection and file status.
"""
import sys
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import SessionLocal

def main():
    """Test SQLite database connection and file status."""
    print("\nSQLite Database Connection Test")
    print("=" * 40)
    
    # Check if database file exists
    db_file = Path("lotro_forge.db")
    if db_file.exists():
        print(f"✅ Database file found: {db_file.absolute()}")
        print(f"📁 File size: {db_file.stat().st_size} bytes")
    else:
        print(f"❌ Database file not found: {db_file.absolute()}")
        print("💡 Run database migrations to create the database")
        return
    
    # Test database connection
    print("\n🔗 Testing database connection...")
    try:
        with SessionLocal() as session:
            # Try a simple query to verify we can execute SQL
            result = session.execute(text("SELECT sqlite_version();")).scalar()
            print(f"✅ Successfully connected to SQLite database!")
            print(f"📊 SQLite version: {result}")
            
            # Check if tables exist
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
            tables = [row[0] for row in result]
            print(f"📋 Found {len(tables)} tables: {', '.join(tables) if tables else 'None'}")
            
    except OperationalError as e:
        print(f"\n❌ Database connection error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if the database file is corrupted")
        print("2. Ensure you have write permissions to the database directory")
        print("3. Try deleting the database file and running migrations again")
    except SQLAlchemyError as e:
        print(f"\n❌ Unexpected database error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check database file permissions")
        print("2. Verify the database schema is correct")
        print("3. Try running database migrations")

if __name__ == "__main__":
    main() 