"""
Database connection utilities.
Manages SQLAlchemy engine and session creation.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from .config import DatabaseConfig

class DatabaseConnection:
    """Manages database connections and sessions."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize the database connection.
        
        Args:
            config: Database configuration settings
        """
        self.config = config
        try:
            self.engine = create_engine(
                config.get_connection_url(),
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True  # Enable connection health checks
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        except SQLAlchemyError as e:
            raise OperationalError(
                f"Failed to create database engine: {str(e)}",
                None,
                None
            ) from e

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.
        
        Yields:
            Session: A SQLAlchemy database session
            
        Example:
            with db.get_session() as session:
                result = session.execute("SELECT 1")
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def test_connection(self) -> bool:
        """Test the database connection.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Raises:
            OperationalError: If there's a connection error
        """
        try:
            with self.get_session() as session:
                # Use text() to properly handle the SQL query
                result = session.execute(text("SELECT 1")).scalar()
                return result == 1
        except OperationalError as e:
            # Re-raise the error with more context
            raise OperationalError(
                f"Failed to connect to database: {str(e)}",
                None,
                None
            ) from e
        except SQLAlchemyError as e:
            # Convert other SQLAlchemy errors to OperationalError
            raise OperationalError(
                f"Database error during connection test: {str(e)}",
                None,
                None
            ) from e 