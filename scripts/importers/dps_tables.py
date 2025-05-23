"""
Importer for LOTRO DPS tables.

DPS tables contain the base damage-per-second values for weapons at different levels,
along with quality factors that modify the final DPS calculation.
"""
import logging
from pathlib import Path
from typing import List, Dict
from lxml import etree
from sqlalchemy.orm import Session

from database.models.dps import DpsTable, DpsValue
from .base import BaseImporter


class DpsTablesImporter(BaseImporter):
    """Importer for DPS tables from dpsTables.xml."""
    
    def __init__(self, source_path: Path, db_session: Session):
        """Initialize the DPS tables importer.
        
        Args:
            source_path: Path to the dpsTables.xml file
            db_session: Database session
        """
        super().__init__(source_path, db_session)
        self.dps_tables_file = source_path  # source_path is now the direct path to dpsTables.xml
    
    def parse_source(self) -> List[Dict]:
        """Parse dpsTables.xml into DPS table data."""
        tree = etree.parse(self.dps_tables_file)
        root = tree.getroot()
        
        dps_tables = []
        
        for table_elem in root.findall(".//valueTable"):
            table_id = table_elem.get("id")
            if not table_id:
                continue
            
            # Parse quality factors
            quality_factors = {}
            for quality_elem in table_elem.findall(".//quality"):
                quality_key = quality_elem.get("key")
                quality_factor = quality_elem.get("factor")
                if quality_key and quality_factor:
                    try:
                        quality_factors[quality_key.lower()] = float(quality_factor)
                    except ValueError:
                        logging.warning(f"Invalid quality factor for {quality_key}: {quality_factor}")
            
            # Parse base values
            base_values = []
            for value_elem in table_elem.findall(".//baseValue"):
                level = value_elem.get("level")
                value = value_elem.get("value")
                if level and value:
                    try:
                        base_values.append({
                            'level': int(level),
                            'value': float(value)
                        })
                    except ValueError:
                        logging.warning(f"Invalid base value for level {level}: {value}")
            
            dps_tables.append({
                'id': table_id,
                'quality_factors': quality_factors,
                'base_values': base_values
            })
        
        logging.info(f"Parsed {len(dps_tables)} DPS tables")
        return dps_tables
    
    def validate_source(self) -> bool:
        """Validate that dpsTables.xml exists and has the expected structure."""
        if not self.dps_tables_file.exists():
            logging.error(f"dpsTables.xml not found at {self.dps_tables_file}")
            return False
            
        try:
            tree = etree.parse(self.dps_tables_file)
            root = tree.getroot()
            # Basic validation of XML structure
            if root.tag != "valueTables":
                logging.error("Invalid root element in dpsTables.xml")
                return False
            if not root.findall(".//valueTable"):
                logging.error("No valueTable elements found in dpsTables.xml")
                return False
            return True
        except Exception as e:
            logging.error(f"Failed to validate dpsTables.xml: {str(e)}")
            return False
    
    def transform_data(self, parsed_data: List[Dict]) -> List[Dict]:
        """Transform parsed DPS table data. For DPS tables, no transformation is needed."""
        return parsed_data
    
    def import_data(self, parsed_data: List[Dict]) -> None:
        """Import DPS table data into the database."""
        logging.info("Starting DPS tables import...")
        
        imported_count = 0
        for table_data in parsed_data:
            try:
                # Check if table already exists
                existing_table = self.db.query(DpsTable).filter_by(id=table_data['id']).first()
                if existing_table:
                    logging.debug(f"DPS table {table_data['id']} already exists, skipping")
                    continue
                
                # Create DPS table
                dps_table = DpsTable(
                    id=table_data['id'],
                    quality_common=table_data['quality_factors'].get('common'),
                    quality_uncommon=table_data['quality_factors'].get('uncommon'), 
                    quality_rare=table_data['quality_factors'].get('rare'),
                    quality_incomparable=table_data['quality_factors'].get('incomparable'),
                    quality_legendary=table_data['quality_factors'].get('legendary')
                )
                
                self.db.add(dps_table)
                
                # Add base values
                for value_data in table_data['base_values']:
                    dps_value = DpsValue(
                        dps_table_id=table_data['id'],
                        level=value_data['level'],
                        value=value_data['value']
                    )
                    self.db.add(dps_value)
                
                imported_count += 1
                if imported_count % 100 == 0:
                    logging.info(f"Imported {imported_count} DPS tables so far...")
                    
            except Exception as e:
                logging.error(f"Error importing DPS table {table_data['id']}: {e}")
                raise
        
        self.db.commit()
        logging.info(f"Successfully imported {imported_count} DPS tables")
    
    def run(self) -> None:
        """Run the complete DPS tables import process."""
        logging.info("Starting DPS tables import process...")
        parsed_data = self.parse_source()
        self.import_data(parsed_data)
        logging.info("DPS tables import completed successfully!") 