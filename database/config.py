"""
Database configuration module.
Handles loading and validating database connection settings from environment variables.
"""
import os
from typing import Optional
from dataclasses import dataclass

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
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def validate(self) -> Optional[str]:
        """Validate the configuration.
        
        Returns:
            Optional[str]: Error message if validation fails, None if valid
        """
        if not self.user:
            return "Database user not set"
        if not self.password:
            return "Database password not set"
        if not self.database:
            return "Database name not set"
        return None 