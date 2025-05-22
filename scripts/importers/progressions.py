"""
Importer for progression tables from XML data.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree
from sqlalchemy.orm import Session

from database.models.progressions import ProgressionTable, TableValue, ProgressionType
from scripts.importers.base import BaseImporter

class ProgressionsImporter(BaseImporter):
    """Importer for progression tables."""
    
    def validate_source(self) -> bool:
        """Validate that the source data exists and is in the expected format."""
        try:
            root = self.parse_xml(self.source_path)
            if root.tag != 'progressions':
                self.logger.error(f"Root element must be 'progressions', got '{root.tag}'")
                return False
            
            # Validate each progression table
            for table_elem in root.findall('./*'):
                if not self._validate_table(table_elem):
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return False
    
    def _validate_table(self, table_elem: ElementTree.Element) -> bool:
        """Validate a single progression table element."""
        # Check element type
        if table_elem.tag not in ['linearInterpolationProgression', 'arrayProgression']:
            self.logger.error(f"Invalid progression type '{table_elem.tag}', must be 'linearInterpolationProgression' or 'arrayProgression'")
            return False
        
        # Check required attributes
        if not table_elem.get('identifier'):
            self.logger.error(f"Table missing required 'identifier' attribute")
            return False
        
        # Check points
        points = table_elem.findall('point')
        if not points:
            self.logger.error(f"Table {table_elem.get('identifier')} has no points")
            return False
        
        # Validate each point
        for point in points:
            if table_elem.tag == 'linearInterpolationProgression':
                if not point.get('x') or not point.get('y'):
                    self.logger.error(f"Point in table {table_elem.get('identifier')} missing required x/y attributes")
                    return False
                try:
                    int(point.get('x'))
                    float(point.get('y'))
                except ValueError:
                    self.logger.error(f"Invalid x/y values in table {table_elem.get('identifier')}")
                    return False
            else:  # arrayProgression
                if not point.get('y'):
                    self.logger.error(f"Point in table {table_elem.get('identifier')} missing required y attribute")
                    return False
                try:
                    int(point.get('y'))
                except ValueError:
                    self.logger.error(f"Invalid y value in table {table_elem.get('identifier')}")
                    return False
        
        return True
    
    def parse_source(self) -> Dict[str, Dict]:
        """Parse the XML data into a dictionary of tables."""
        try:
            root = self.parse_xml(self.source_path)
            tables = {}
            
            for table_elem in root.findall('./*'):
                table_id = table_elem.get('identifier')
                if not table_id:
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
                    if table_elem.tag == 'linearInterpolationProgression':
                        tables[table_id]['values'].append({
                            'level': int(point.get('x')),
                            'value': float(point.get('y'))
                        })
                    else:  # arrayProgression
                        # For array progressions, use the count attribute or increment from previous point
                        count = int(point.get('count', '1'))
                        for i in range(count):
                            tables[table_id]['values'].append({
                                'level': len(tables[table_id]['values']) + 1,
                                'value': float(point.get('y'))
                            })
            
            return tables
        except Exception as e:
            self.logger.error(f"Parsing failed: {str(e)}")
            return {}
    
    def transform_data(self, data: Dict[str, Dict]) -> Tuple[List[ProgressionTable], List[TableValue]]:
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
                value = TableValue(
                    table_id=table_id,
                    item_level=value_data['level'],
                    value=value_data['value']
                )
                values.append(value)
        
        return tables, values
    
    def import_data(self, data: Tuple[List[ProgressionTable], List[TableValue]]) -> None:
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
                self.db.query(TableValue).filter_by(table_id=table.table_id).delete()
            
            # Add new values
            for value in values:
                self.db.add(value)
            
            self.logger.info(f"Successfully imported {len(tables)} tables and {len(values)} values")
            
        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}")
            raise 