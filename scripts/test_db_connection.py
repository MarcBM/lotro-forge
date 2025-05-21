"""
Test script to verify database connection.
"""
import os
import sys
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from database import DatabaseConfig, DatabaseConnection

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Create database configuration
    config = DatabaseConfig.from_env()
    
    # Print configuration (without password)
    print("\nDatabase Configuration:")
    print(f"Host: {config.host}")
    print(f"Port: {config.port}")
    print(f"Database: {config.database}")
    print(f"User: {config.user}")
    print("Password: [HIDDEN]")
    
    # Validate configuration
    if error := config.validate():
        print(f"\n❌ Configuration error: {error}")
        return
    
    # Create database connection
    print("\nTesting database connection...")
    try:
        db = DatabaseConnection(config)
        if db.test_connection():
            print("✅ Successfully connected to the database!")
            
            # Try a simple query to verify we can execute SQL
            with db.get_session() as session:
                result = session.execute(text("SELECT version();")).scalar()
                print(f"PostgreSQL version: {result}")
    except OperationalError as e:
        print(f"\n❌ Database connection error: {str(e)}")
        print("\nThis is likely a credentials or connection issue. Please verify:")
        print("1. The password in your .env file matches your PostgreSQL password")
        print("2. PostgreSQL is running: sudo service postgresql status")
        print("3. You can connect manually with: psql -d lotro_forge -U marcb")
        print("\nConnection URL (with password hidden):")
        print(f"postgresql://{config.user}:****@{config.host}:{config.port}/{config.database}")
    except SQLAlchemyError as e:
        print(f"\n❌ Unexpected database error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify PostgreSQL is running: sudo service postgresql status")
        print("2. Check your .env file credentials match your PostgreSQL setup")
        print("3. Ensure the database exists: psql -l")
        print("4. Verify user permissions: psql -d lotro_forge -U marcb")

if __name__ == "__main__":
    main() 