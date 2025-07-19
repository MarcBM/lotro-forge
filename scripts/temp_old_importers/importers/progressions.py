"""
Importer for progression tables from XML data.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree
from sqlalchemy.orm import Session

from database.models.progressions import ProgressionTable, ProgressionValue, ProgressionType
from scripts.importers.base import BaseImporter

class ProgressionsImporter(BaseImporter):
    """Importer for progression tables."""
    
    def __init__(self, source_path: Path, db_session: Session):
        """Initialize the importer.
        
        Args:
            source_path: Path to the progressions.xml file
            db_session: Database session
        """
        super().__init__(source_path, db_session)
        self.progressions_file = source_path  # source_path is now the direct path to progressions.xml
        
    def _validate_table(self, table_elem: ElementTree.Element, required_table_ids: set[str] = None) -> bool:
        """Validate a single progression table element.
        
        Args:
            table_elem: The table element to validate
            required_table_ids: Optional set of table IDs we care about. If None, validate all tables.
        """
        table_id = table_elem.get('identifier')
        
        # Skip validation for tables we don't care about
        if required_table_ids is not None and table_id not in required_table_ids:
            return True
            
        # Check element type
        if table_elem.tag not in ['linearInterpolationProgression', 'arrayProgression']:
            self.logger.error(f"Invalid progression type '{table_elem.tag}' for table {table_id}, must be 'linearInterpolationProgression' or 'arrayProgression'")
            return False
        
        # Check required attributes
        if not table_id:
            self.logger.error(f"Table missing required 'identifier' attribute")
            return False
        
        # Check points
        points = table_elem.findall('point')
        if not points:
            self.logger.error(f"Table {table_id} has no points")
            return False
        
        # Validate each point
        for i, point in enumerate(points):
            try:
                if table_elem.tag == 'linearInterpolationProgression':
                    x_val = point.get('x')
                    y_val = point.get('y')
                    if not x_val or not y_val:
                        self.logger.warning(f"Point {i} in table {table_id} missing x/y attributes, skipping")
                        continue
                    try:
                        int(x_val)
                        float(y_val)  # Allow both int and float values
                    except ValueError as e:
                        self.logger.warning(f"Invalid x/y values in point {i} of table {table_id}: x={x_val}, y={y_val}, error: {str(e)}")
                        continue
                else:  # arrayProgression
                    y_val = point.get('y')
                    if not y_val:
                        self.logger.warning(f"Point {i} in table {table_id} missing y attribute, skipping")
                        continue
                    try:
                        # Try float first, then int if it's a whole number
                        float_val = float(y_val)
                        if float_val.is_integer():
                            int(float_val)  # Just verify it can be converted to int
                    except ValueError as e:
                        self.logger.warning(f"Invalid y value in point {i} of table {table_id}: y={y_val}, error: {str(e)}")
                        continue
            except Exception as e:
                self.logger.warning(f"Error validating point {i} in table {table_id}: {str(e)}")
                continue
        
        # If we got here, the table is valid enough to proceed
        return True

    def validate_source(self, required_table_ids: set[str] = None) -> bool:
        """Validate that the source data exists and is in the expected format.
        
        Args:
            required_table_ids: Optional set of table IDs we care about. If None, validate all tables.
        """
        try:
            root = self.parse_xml(self.progressions_file)
            if root.tag != 'progressions':
                self.logger.error(f"Root element must be 'progressions', got '{root.tag}'")
                return False
            
            # Validate each progression table
            for table_elem in root.findall('./*'):
                if not self._validate_table(table_elem, required_table_ids):
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return False
    
    def parse_source(self, required_table_ids: set[str] = None) -> Dict[str, Dict]:
        """Parse the XML data into a dictionary of tables.
        
        Args:
            required_table_ids: Optional set of table IDs to filter by. If None, all tables are parsed.
        
        Returns:
            Dict[str, Dict]: Dictionary of table data keyed by table ID
        """
        try:
            root = self.parse_xml(self.progressions_file)
            tables = {}
            
            for table_elem in root.findall('./*'):
                table_id = table_elem.get('identifier')
                if not table_id:
                    continue
                    
                # Skip tables that aren't in the required set
                if required_table_ids is not None and table_id not in required_table_ids:
                    continue
                
                # Parse table metadata
                tables[table_id] = {
                    'type': 'linear' if table_elem.tag == 'linearInterpolationProgression' else 'array',
                    'name': table_elem.get('name', ''),
                    'description': f"{table_elem.tag} with {table_elem.get('nbPoints', '0')} points",
                    'values': []
                }
                
                # Parse points
                for point in table_elem.findall('point'):
                    try:
                        if table_elem.tag == 'linearInterpolationProgression':
                            x_val = point.get('x')
                            y_val = point.get('y')
                            if x_val and y_val:
                                try:
                                    tables[table_id]['values'].append({
                                        'level': int(x_val),
                                        'value': float(y_val)
                                    })
                                except ValueError as e:
                                    self.logger.warning(f"Skipping invalid point in table {table_id}: x={x_val}, y={y_val}, error: {str(e)}")
                        else:  # arrayProgression
                            y_val = point.get('y')
                            if y_val:
                                try:
                                    # For array progressions, use the count attribute or increment from previous point
                                    count = int(point.get('count', '1'))
                                    float_val = float(y_val)
                                    for i in range(count):
                                        tables[table_id]['values'].append({
                                            'level': len(tables[table_id]['values']) + 1,
                                            'value': float_val
                                        })
                                except ValueError as e:
                                    self.logger.warning(f"Skipping invalid point in table {table_id}: y={y_val}, error: {str(e)}")
                    except Exception as e:
                        self.logger.warning(f"Error parsing point in table {table_id}: {str(e)}")
                        continue
            
            if not tables:
                if required_table_ids:
                    self.logger.error(f"No valid tables found in progressions.xml matching required IDs: {required_table_ids}")
                else:
                    self.logger.error("No valid tables found in progressions.xml")
                return {}
                
            self.logger.info(f"Parsed {len(tables)} tables from progressions.xml")
            return tables
        except Exception as e:
            self.logger.error(f"Parsing failed: {str(e)}")
            return {}
    
    def transform_data(self, data: Dict[str, Dict]) -> Tuple[List[ProgressionTable], List[ProgressionValue]]:
        """Transform the parsed data into database models."""
        tables = []
        values = []
        
        for table_id, table_data in data.items():
            # Create table model
            table = ProgressionTable(
                table_id=table_id,
                progression_type=ProgressionType(table_data['type']),
                name=table_data.get('name'),
                description=table_data.get('description')
            )
            tables.append(table)
            
            # Create value models
            for value_data in table_data['values']:
                value = ProgressionValue(
                    table_id=table_id,
                    item_level=value_data['level'],
                    value=value_data['value']
                )
                values.append(value)
        
        return tables, values
    
    def import_data(self, data: Tuple[List[ProgressionTable], List[ProgressionValue]]) -> None:
        """Import the transformed data into the database."""
        tables, values = data
        try:
            # Update or insert tables
            for table in tables:
                existing = self.db.query(ProgressionTable).filter_by(table_id=table.table_id).first()
                if existing:
                    # Update existing table
                    existing.progression_type = table.progression_type
                    existing.name = table.name
                    existing.description = table.description
                else:
                    # Insert new table
                    self.db.add(table)
            
            # Update values
            for table in tables:
                # Remove existing values
                self.db.query(ProgressionValue).filter_by(table_id=table.table_id).delete()
            
            # Add new values
            for value in values:
                self.db.add(value)
            
            self.logger.info(f"Successfully imported {len(tables)} tables and {len(values)} values")
            
        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}")
            raise 

    def import_specific_tables(self, required_table_ids: set[str]) -> bool:
        """Import only specific progression tables that are required.
        
        Args:
            required_table_ids: Set of table IDs to import
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Importing {len(required_table_ids)} specific progression tables...")
            
            # Validate source data for only the required tables
            if not self.validate_source(required_table_ids):
                self.logger.error("Validation failed for required progression tables")
                return False
            
            # Parse only the required tables
            data = self.parse_source(required_table_ids)
            if not data:
                self.logger.error("No data found for required progression tables")
                return False
            
            # Transform and import the data
            transformed_data = self.transform_data(data)
            self.import_data(transformed_data)
            
            self.logger.info(f"Successfully imported {len(data)} specific progression tables")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import specific progression tables: {str(e)}")
            return False

    def run(self, required_table_ids: set[str] = None) -> bool:
        """Run the import process.
        
        Args:
            required_table_ids: Optional set of table IDs to import. If None, all tables are imported.
        
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            # Validate source
            if not self.validate_source(required_table_ids):
                return False
            
            # Parse source data
            data = self.parse_source(required_table_ids)
            if not data:
                return False
            
            # Transform data
            transformed_data = self.transform_data(data)
            
            # Import data
            self.import_data(transformed_data)
            
            self.logger.info("Import completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}")
            return False 