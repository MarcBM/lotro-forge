"""
Database configuration module.
Handles loading and validating database connection settings from environment variables.
"""
import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create a DatabaseConfig instance from environment variables."""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'lotro_forge'),
            user=os.getenv('DB_USER', ''),
            password=os.getenv('DB_PASSWORD', '')
        )

    def get_connection_url(self) -> str:
        """Get the SQLAlchemy connection URL."""
        # For peer authentication, we can omit the password
        if not self.password:
            return f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}"
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def validate(self) -> Optional[str]:
        """Validate the configuration.
        
        Returns:
            Optional[str]: Error message if validation fails, None if valid
        """
        if not self.user:
            return "Database user not set"
        if not self.database:
            return "Database name not set"
        return None

def get_database_url() -> str:
    """Get the database URL for Alembic migrations.
    
    Returns:
        str: The database URL in SQLAlchemy format
    """
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        raise ValueError(f".env file not found at {env_path}")

    config = DatabaseConfig.from_env()
    error = config.validate()
    if error:
        raise ValueError(f"Invalid database configuration: {error}")
    return config.get_connection_url() 