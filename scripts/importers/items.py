"""
Importer for item definitions from items.xml.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from database.models.item import ItemDefinition, ItemStat
from scripts.importers.base import BaseImporter

@dataclass
class ItemDefinitionData:
    """Represents an item definition from XML."""
    key: int
    name: str
    min_ilvl: int  # This is the level attribute from XML
    slot: str
    quality: str
    required_player_level: int
    scaling: Optional[str]
    value_table_id: Optional[int]  # Keep this for reference but don't use in ItemDefinition
    stats: List[Dict[str, str]]  # List of {name: str, scaling: str}

class ItemImporter(BaseImporter):
    """Importer for item definitions."""
    
    def __init__(self, source_path: Path, db_session: Session):
        """Initialize the importer.
        
        Args:
            source_path: Path to the items.xml file
            db_session: Database session
        """
        super().__init__(source_path, db_session)
        self.items_file = source_path  # source_path is now the direct path to items.xml
        
    def validate_source(self) -> bool:
        """Validate that items.xml exists and has the expected structure."""
        if not self.items_file.exists():
            self.logger.error(f"items.xml not found at {self.items_file}")
            return False
            
        try:
            root = self.parse_xml(self.items_file)
            # Basic validation of XML structure
            if root.tag != "items":
                self.logger.error("Invalid root element in items.xml")
                return False
            if not root.findall(".//item"):
                self.logger.error("No item elements found in items.xml")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate items.xml: {str(e)}")
            return False
    
    def parse_source(self) -> List[ItemDefinitionData]:
        """Parse items.xml into ItemDefinitionData objects."""
        root = self.parse_xml(self.items_file)
        items = []
        
        for item_elem in root.findall(".//item"):
            try:
                # Required attributes
                key = int(item_elem.get("key", "0"))
                name = item_elem.get("name", "")
                min_ilvl = int(item_elem.get("level", "0"))  # Use level attribute for base_ilvl
                slot = item_elem.get("slot", "")
                quality = item_elem.get("quality", "")
                required_player_level = int(item_elem.get("minLevel", "0"))
                
                # Skip items that don't meet our criteria
                if min_ilvl < 520 or slot != "NECK":
                    continue
                
                # Optional attributes
                scaling = item_elem.get("scaling")
                value_table_id = item_elem.get("valueTableId")
                if value_table_id is not None:
                    value_table_id = int(value_table_id)
                
                # Parse stats
                stats = []
                stats_elem = item_elem.find("stats")
                if stats_elem is not None:
                    for stat_elem in stats_elem.findall("stat"):
                        stat_name = stat_elem.get("name", "")
                        stat_scaling = stat_elem.get("scaling", "")
                        if stat_name and stat_scaling:
                            stats.append({
                                "name": stat_name,
                                "scaling": stat_scaling
                            })
                
                item = ItemDefinitionData(
                    key=key,
                    name=name,
                    min_ilvl=min_ilvl,
                    slot=slot,
                    quality=quality,
                    required_player_level=required_player_level,
                    scaling=scaling,
                    value_table_id=value_table_id,
                    stats=stats
                )
                items.append(item)
                
            except (ValueError, AttributeError) as e:
                self.logger.error(f"Failed to parse item element {item_elem.get('key', 'unknown')}: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(items)} items matching criteria (level >= 520 and slot = NECK)")
        return items
    
    def transform_data(self, items: List[ItemDefinitionData]) -> Tuple[List[ItemDefinition], List[ItemStat]]:
        """Transform ItemDefinitionData objects into database models."""
        item_defs = []
        item_stats = []
        
        for item in items:
            # Create item definition (without value_table_id)
            item_def = ItemDefinition(
                key=item.key,
                name=item.name,
                base_ilvl=item.min_ilvl,
                slot=item.slot,
                quality=item.quality,
                required_player_level=item.required_player_level,
                scaling=item.scaling
            )
            item_defs.append(item_def)
            
            # Create item stats
            for order, stat in enumerate(item.stats):
                item_stat = ItemStat(
                    item_key=item.key,
                    stat_name=stat["name"],
                    value_table_id=stat["scaling"],  # Use the scaling ID as the value table ID
                    order=order  # Preserve the order from XML
                )
                item_stats.append(item_stat)
        
        return item_defs, item_stats
    
    def import_data(self, data: Tuple[List[ItemDefinition], List[ItemStat]]) -> None:
        """Import the transformed data into the database."""
        item_defs, item_stats = data
        
        try:
            # Update or insert item definitions
            for item_def in item_defs:
                existing = self.db.query(ItemDefinition).get(item_def.key)
                if existing:
                    # Update existing item definition
                    for key, value in vars(item_def).items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                else:
                    # Insert new item definition
                    self.db.add(item_def)
            
            # Update or insert item stats
            for item_stat in item_stats:
                existing = self.db.query(ItemStat).filter_by(
                    item_key=item_stat.item_key,
                    stat_name=item_stat.stat_name
                ).first()
                
                if existing:
                    # Update existing stat
                    existing.value_table_id = item_stat.value_table_id
                    existing.order = item_stat.order
                else:
                    # Insert new stat
                    self.db.add(item_stat)
            
            self.logger.info(f"Successfully imported {len(item_defs)} items and {len(item_stats)} stats")
            
        except Exception as e:
            self.logger.error(f"Failed to import data: {str(e)}")
            raise 

    def get_required_progression_tables(self) -> set[str]:
        """Extract the set of progression table IDs required by the items.
        
        Returns:
            set[str]: Set of progression table IDs that are referenced by items
        """
        if not self.validate_source():
            return set()
            
        root = self.parse_xml(self.items_file)
        required_tables = set()
        
        for item_elem in root.findall(".//item"):
            try:
                # Skip items that don't meet our criteria
                min_ilvl = int(item_elem.get("level", "0"))
                slot = item_elem.get("slot", "")
                if min_ilvl < 520 or slot != "NECK":
                    continue
                
                # Get value table ID from item stats
                stats_elem = item_elem.find("stats")
                if stats_elem is not None:
                    for stat_elem in stats_elem.findall("stat"):
                        stat_scaling = stat_elem.get("scaling", "")
                        if stat_scaling:
                            required_tables.add(stat_scaling)
                
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Failed to parse item element {item_elem.get('key', 'unknown')}: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(required_tables)} required progression tables")
        return required_tables 