"""
Base classes and utilities for the import framework.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import logging
import xml.etree.ElementTree as ET
from sqlalchemy.ext.declarative import declarative_base

# Create base class for import models
Base = declarative_base()

class BaseImporter(ABC):
    """Base class for all data importers."""
    
    def __init__(self, source_path: Path, db_session):
        """
        Initialize the importer.
        
        Args:
            source_path: Path to the lotro_companion data directory
            db_session: SQLAlchemy database session
        """
        self.source_path = source_path
        self.db = db_session
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def validate_source(self) -> bool:
        """Validate that the source data exists and is in the expected format."""
        pass
    
    @abstractmethod
    def parse_source(self) -> Any:
        """Parse the source data into an intermediate format."""
        pass
    
    @abstractmethod
    def transform_data(self, data: Any) -> Any:
        """Transform the parsed data into the format needed for import."""
        pass
    
    @abstractmethod
    def import_data(self, data: Any) -> None:
        """Import the transformed data into the database."""
        pass
    
    def run(self) -> bool:
        """
        Run the complete import process.
        
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            if not self.validate_source():
                self.logger.error("Source validation failed")
                return False
                
            parsed_data = self.parse_source()
            transformed_data = self.transform_data(parsed_data)
            self.import_data(transformed_data)
            
            self.logger.info("Import completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}", exc_info=True)
            return False
    
    def parse_xml(self, file_path: Path) -> ET.Element:
        """
        Parse an XML file and return its root element.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            ET.Element: Root element of the parsed XML
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ET.ParseError: If the XML is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except ET.ParseError as e:
            raise ET.ParseError(f"Failed to parse XML file {file_path}: {str(e)}") 