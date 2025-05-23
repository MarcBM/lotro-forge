"""
Importer for item definitions from items.xml.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from sqlalchemy.orm import Session
from database.models.item import EquipmentItem, Weapon, Essence, ItemStat
from scripts.importers.base import BaseImporter
from scripts.importers.dps_tables import DpsTablesImporter
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
    # Socket string from XML
    sockets: Optional[str] = None  # e.g. "PVS" or "PVSSS"
    # Weapon-specific fields
    category: Optional[str] = None  # "WEAPON" vs "ARMOUR" vs "ITEM" vs "ESSENCE"
    dps: Optional[float] = None
    dps_table_id: Optional[str] = None
    min_damage: Optional[int] = None
    max_damage: Optional[int] = None
    damage_type: Optional[str] = None
    weapon_type: Optional[str] = None
    # Essence-specific fields
    tier: Optional[int] = None
    essence_type: Optional[int] = None

class ItemImporter(BaseImporter):
    """Importer for item definitions."""
    
    def __init__(self, source_path: Path, db_session: Session, skip_filters: bool = False, dps_tables_path: Optional[Path] = None):
        """Initialize the importer.
        
        Args:
            source_path: Path to the items.xml file
            db_session: Database session
            skip_filters: If True, skip filtering items by level and slot (imports all items)
            dps_tables_path: Path to the dpsTables.xml file (required for importing weapons)
        """
        super().__init__(source_path, db_session)
        self.items_file = source_path  # source_path is now the direct path to items.xml
        self.skip_filters = skip_filters
        self.required_icons = set()  # Track unique icon IDs needed
        self.dps_tables_path = dps_tables_path
        
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
                    category = item_elem.get("category", "")
                    
                    # Import all equipment items with level >= 500 that have a slot
                    # OR essences with level >= 500 (regardless of slot)
                    if level < 500:
                        continue
                    
                    # For equipment, require a slot; for essences, no slot required
                    if category == "ESSENCE":
                        # Include essence regardless of slot
                        pass
                    elif slot:
                        # Include equipment items that have a slot
                        pass
                    else:
                        # Skip items that are neither essences nor equipment with slots
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
                stats=stats,
                # Socket string from XML
                sockets=item_elem.get("slots"),  # XML attribute is "slots"
                # Weapon-specific fields
                category=item_elem.get("category"),
                dps=float(item_elem.get("dps")) if item_elem.get("dps") else None,
                dps_table_id=item_elem.get("dpsTableId"),
                min_damage=int(item_elem.get("minDamage")) if item_elem.get("minDamage") else None,
                max_damage=int(item_elem.get("maxDamage")) if item_elem.get("maxDamage") else None,
                damage_type=item_elem.get("damageType"),
                weapon_type=item_elem.get("weaponType"),
                # Essence-specific fields
                tier=int(item_elem.get("tier")) if item_elem.get("tier") else None,
                essence_type=int(item_elem.get("type")) if item_elem.get("type") else None
            )
            items.append(item)
        
        self.logger.info(f"Parsed {total_parsed} total items, filtered to {len(items)} equipment items and essences level 500+")
        return items
    
    def transform_data(self, items: List[ItemData]) -> Tuple[Tuple[List[EquipmentItem], List[Essence]], List[ItemStat]]:
        """Transform ItemData objects into database models."""
        equipment_items = []
        essences = []
        item_stats = []
        
        for item in items:
            # Determine the item type based on category
            if item.category == "ESSENCE":
                # Create essence item
                essence = Essence(
                    key=item.key,
                    name=item.name,
                    base_ilvl=item.base_ilvl,
                    quality=item.quality,
                    icon=item.icon,
                    tier=item.tier,
                    essence_type=item.essence_type
                )
                essences.append(essence)
                
                # Create item stats for essence
                for stat_name, value_table_id, order in item.stats:
                    stat = ItemStat(
                        item_key=item.key,
                        stat_name=stat_name,
                        value_table_id=value_table_id,
                        order=order
                    )
                    item_stats.append(stat)
                    
            elif item.category == "WEAPON":
                # Parse socket counts from socket string
                socket_counts = EquipmentItem.parse_socket_string(item.sockets)
                
                # Create weapon item
                equipment_item = Weapon(
                    key=item.key,
                    name=item.name,
                    base_ilvl=item.base_ilvl,
                    quality=item.quality,
                    icon=item.icon,
                    slot=item.slot,
                    armour_type=item.armour_type,
                    scaling=item.scaling,
                    # Socket counts
                    sockets_basic=socket_counts['basic'],
                    sockets_primary=socket_counts['primary'],
                    sockets_vital=socket_counts['vital'],
                    sockets_cloak=socket_counts['cloak'],
                    sockets_necklace=socket_counts['necklace'],
                    sockets_pvp=socket_counts['pvp'],
                    # Weapon-specific fields
                    dps=item.dps,
                    dps_table_id=item.dps_table_id,
                    min_damage=item.min_damage,
                    max_damage=item.max_damage,
                    damage_type=item.damage_type,
                    weapon_type=item.weapon_type
                )
                equipment_items.append(equipment_item)
                
                # Create item stats for weapon
                for stat_name, value_table_id, order in item.stats:
                    stat = ItemStat(
                        item_key=item.key,
                        stat_name=stat_name,
                        value_table_id=value_table_id,
                        order=order
                    )
                    item_stats.append(stat)
                    
            else:
                # Parse socket counts from socket string
                socket_counts = EquipmentItem.parse_socket_string(item.sockets)
                
                # Create regular equipment item
                equipment_item = EquipmentItem(
                    key=item.key,
                    name=item.name,
                    base_ilvl=item.base_ilvl,
                    quality=item.quality,
                    icon=item.icon,
                    slot=item.slot,
                    armour_type=item.armour_type,
                    scaling=item.scaling,
                    # Socket counts
                    sockets_basic=socket_counts['basic'],
                    sockets_primary=socket_counts['primary'],
                    sockets_vital=socket_counts['vital'],
                    sockets_cloak=socket_counts['cloak'],
                    sockets_necklace=socket_counts['necklace'],
                    sockets_pvp=socket_counts['pvp']
                )
                equipment_items.append(equipment_item)
                
                # Create item stats for equipment
                for stat_name, value_table_id, order in item.stats:
                    stat = ItemStat(
                        item_key=item.key,
                        stat_name=stat_name,
                        value_table_id=value_table_id,
                        order=order
                    )
                    item_stats.append(stat)
        
        return (equipment_items, essences), item_stats
    
    def import_data(self, data: Tuple[Tuple[List[EquipmentItem], List[Essence]], List[ItemStat]]) -> None:
        """Import the transformed data into the database."""
        (equipment_items, essences), item_stats = data
        
        try:
            # Import equipment items
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
            
            # Import essences
            for essence in essences:
                # Check if essence already exists
                existing = self.db.query(Essence).get(essence.key)
                if existing:
                    # Update existing essence
                    for key, value in essence.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                else:
                    # Add new essence
                    self.db.add(essence)
            
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
            
            self.logger.info(f"Successfully imported {len(equipment_items)} equipment items, {len(essences)} essences, and {len(item_stats)} stats")
            
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
        """Extract the set of icon IDs required by the items to be imported."""
        if not self.validate_source():
            return set()
            
        items = self.parse_source()
        icons = set()
        for item in items:
            if item.icon:
                # Split hyphenated icon IDs and add each one to the set
                for icon_id in item.icon.split('-'):
                    icons.add(icon_id.strip())
                
        return icons
    
    def get_required_dps_tables(self) -> Set[str]:
        """Extract the set of DPS table IDs required by weapon items."""
        if not self.validate_source():
            return set()
            
        items = self.parse_source()
        dps_tables = set()
        
        for item in items:
            if item.category == "WEAPON" and item.dps_table_id:
                dps_tables.add(item.dps_table_id)
        
        self.logger.info(f"Found {len(dps_tables)} required DPS tables from {len(items)} items")
        return dps_tables
    
    def import_required_dps_tables(self, required_tables: Set[str]) -> bool:
        """Import required DPS tables using the DPS tables importer."""
        if not required_tables:
            self.logger.info("No DPS tables required")
            return True
            
        if not self.dps_tables_path:
            self.logger.error("DPS tables path not provided but required for weapon imports")
            return False
            
        if not self.dps_tables_path.exists():
            self.logger.error(f"DPS tables file not found: {self.dps_tables_path}")
            return False
        
        try:
            self.logger.info(f"Importing {len(required_tables)} required DPS tables...")
            dps_importer = DpsTablesImporter(self.dps_tables_path, self.db)
            
            # Parse all DPS tables and filter to only import required ones
            all_dps_data = dps_importer.parse_source()
            required_dps_data = [
                dps_data for dps_data in all_dps_data 
                if dps_data['id'] in required_tables
            ]
            
            if required_dps_data:
                dps_importer.import_data(required_dps_data)
                self.logger.info(f"Successfully imported {len(required_dps_data)} DPS tables")
            else:
                self.logger.warning(f"None of the required DPS tables were found in {self.dps_tables_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import DPS tables: {e}")
            return False

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