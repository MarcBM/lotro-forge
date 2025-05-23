"""
Importer for item definitions from items.xml.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from database.models.item import EquipmentItem, ItemStat
from scripts.importers.base import BaseImporter
from lxml import etree

@dataclass
class ItemData:
    """Data class for raw item data from XML."""
    key: int
    name: str
    base_ilvl: int
    slot: str
    quality: str
    icon: Optional[str]
    armour_type: Optional[str]
    scaling: Optional[str]
    stats: List[Tuple[str, str, int]]  # (stat_name, value_table_id, order)

class ItemImporter(BaseImporter):
    """Importer for item definitions."""
    
    def __init__(self, source_path: Path, db_session: Session, skip_filters: bool = False):
        """Initialize the importer.
        
        Args:
            source_path: Path to the items.xml file
            db_session: Database session
            skip_filters: If True, skip filtering items by level and slot (imports all items)
        """
        super().__init__(source_path, db_session)
        self.items_file = source_path  # source_path is now the direct path to items.xml
        self.skip_filters = skip_filters
        self.required_icons = set()  # Track unique icon IDs needed
        
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
    
    def parse_source(self) -> List[ItemData]:
        """Parse items.xml into ItemData objects."""
        tree = etree.parse(self.items_file)
        root = tree.getroot()
        
        items = []
        total_parsed = 0
        
        for item_elem in root.findall(".//item"):
            total_parsed += 1
            
            # Apply filtering during parsing (unless skip_filters is True)
            if not self.skip_filters:
                try:
                    level = int(item_elem.get("level", "1"))
                    slot = item_elem.get("slot", "")
                    
                    # Import all equipment items with level >= 500 that have a slot
                    # Skip items that don't meet our criteria
                    if level < 500 or not slot:
                        continue
                except (ValueError, TypeError):
                    # Skip items with invalid level data
                    continue
            
            # Parse stats first
            stats = []
            for order, stat_elem in enumerate(item_elem.findall(".//stat")):
                stat_name = stat_elem.get("name")
                scaling = stat_elem.get("scaling")  # Changed from value_table_id to scaling
                if stat_name and scaling:
                    stats.append((stat_name, scaling, order))
            
            # Parse item data
            item = ItemData(
                key=int(item_elem.get("key")),
                name=item_elem.get("name", ""),
                base_ilvl=int(item_elem.get("level", "1")),  # Changed from base_ilvl to level
                slot=item_elem.get("slot", ""),
                quality=item_elem.get("quality", "common"),
                icon=item_elem.get("icon"),
                armour_type=item_elem.get("armourType"),  # Note: might be armourType in XML
                scaling=item_elem.get("scaling"),
                stats=stats
            )
            items.append(item)
        
        self.logger.info(f"Parsed {total_parsed} total items, filtered to {len(items)} equipment items level 500+")
        return items
    
    def transform_data(self, items: List[ItemData]) -> Tuple[List[EquipmentItem], List[ItemStat]]:
        """Transform ItemData objects into database models."""
        equipment_items = []
        item_stats = []
        
        for item in items:
            # Create equipment item (all imported items are equipment)
            equipment_item = EquipmentItem(
                key=item.key,
                name=item.name,
                base_ilvl=item.base_ilvl,
                quality=item.quality,
                icon=item.icon,
                slot=item.slot,
                armour_type=item.armour_type,
                scaling=item.scaling
            )
            equipment_items.append(equipment_item)
            
            # Create item stats
            for stat_name, value_table_id, order in item.stats:
                stat = ItemStat(
                    item_key=item.key,
                    stat_name=stat_name,
                    value_table_id=value_table_id,
                    order=order
                )
                item_stats.append(stat)
        
        return equipment_items, item_stats
    
    def import_data(self, data: Tuple[List[EquipmentItem], List[ItemStat]]) -> None:
        """Import the transformed data into the database."""
        equipment_items, item_stats = data
        
        try:
            # Import items
            for equipment_item in equipment_items:
                # Check if item already exists
                existing = self.db.query(EquipmentItem).get(equipment_item.key)
                if existing:
                    # Update existing item
                    for key, value in equipment_item.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                else:
                    # Add new item
                    self.db.add(equipment_item)
            
            # Import stats
            for stat in item_stats:
                # Check if stat already exists
                existing = self.db.query(ItemStat).filter_by(
                    item_key=stat.item_key,
                    stat_name=stat.stat_name
                ).first()
                if existing:
                    # Update existing stat
                    existing.value_table_id = stat.value_table_id
                    existing.order = stat.order
                else:
                    # Add new stat
                    self.db.add(stat)
            
            self.logger.info(f"Successfully imported {len(equipment_items)} equipment items and {len(item_stats)} stats")
            
        except Exception as e:
            self.logger.error(f"Failed to import data: {str(e)}")
            raise

    def get_required_progression_tables(self) -> set[str]:
        """Extract the set of progression table IDs required by the items."""
        if not self.validate_source():
            return set()
            
        # Parse items using our new logic (already filtered)
        items = self.parse_source()
        required_tables = set()
        
        items_with_scaling = 0
        items_with_stats = 0
        
        for item in items:
            try:
                # Get scaling from item level
                if item.scaling:
                    required_tables.add(item.scaling)
                    items_with_scaling += 1
                
                # Get value_table_ids from item stats
                for stat_name, value_table_id, order in item.stats:
                    if value_table_id:
                        required_tables.add(value_table_id)
                
                if item.stats:
                    items_with_stats += 1
                
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Failed to parse item {item.key}: {str(e)}")
                continue
        
        self.logger.info(f"Processed {len(items)} filtered items:")
        self.logger.info(f"  Items with scaling: {items_with_scaling}")
        self.logger.info(f"  Items with stats: {items_with_stats}")
        self.logger.info(f"Found {len(required_tables)} required progression tables")
        return required_tables

    def get_required_icons(self) -> set[str]:
        """Get the set of unique icon IDs required by the imported items.
        
        Returns:
            set[str]: Set of icon IDs that need to be copied
        """
        return self.required_icons 

    def run(self, required_tables: Optional[set[str]] = None) -> bool:
        """Override the base run method to use filtered parsing."""
        try:
            self.logger.info("Starting import process...")
            
            if not self.validate_source():
                self.logger.error("Source validation failed")
                return False
            
            # Parse filtered items based on project requirements
            raw_data = self.parse_source()
            if not raw_data:
                self.logger.error("No data to import")
                return False
            
            self.logger.info("Transforming data...")
            transformed_data = self.transform_data(raw_data)
            
            self.logger.info("Importing data...")
            self.import_data(transformed_data)
            
            self.logger.info("Import completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}")
            return False 