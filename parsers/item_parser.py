from dataclasses import dataclass
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from domain.item import ItemDefinition, ItemStat

class ItemParser:
    """Parser for converting XML item data into ItemDefinition objects."""

    @staticmethod
    def parse_item_element(item_elem: ET.Element) -> ItemDefinition:
        """
        Parse an XML item element into an ItemDefinition.
        
        Args:
            item_elem: XML element representing an item
            
        Returns:
            ItemDefinition object containing the parsed item data
            
        Raises:
            ValueError: If required attributes are missing or invalid, or if stats are missing
            
        Notes:
            - All items must have a <stats> element with at least one stat
            - All items must have the required attributes: key, name, level, slot, quality, minLevel
            - Optional attributes (scaling, valueTableId) may be None
            - Each stat in the <stats> element must have both name and scaling attributes
        """
        # Required attributes
        try:
            key = int(item_elem.get('key'))
            name = item_elem.get('name')
            min_ilvl = int(item_elem.get('level'))  # This is the baseline ilvl
            slot = item_elem.get('slot')
            quality = item_elem.get('quality')
            required_player_level = int(item_elem.get('minLevel'))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid or missing required attribute in item {item_elem.get('key')}: {e}")

        # Optional attributes
        scaling = item_elem.get('scaling')
        value_table_id = item_elem.get('valueTableId')
        if value_table_id is not None:
            value_table_id = int(value_table_id)

        # Parse stats - required for all items
        stats = []
        stats_elem = item_elem.find('stats')
        if stats_elem is None:
            raise ValueError(f"Item {key} ({name}) is missing required <stats> element")
            
        for stat_elem in stats_elem.findall('stat'):
            stat_name = stat_elem.get('name')
            scaling_id = stat_elem.get('scaling')
            if stat_name is None or scaling_id is None:
                raise ValueError(f"Invalid stat in item {key}: missing name or scaling")
            try:
                scaling_id = int(scaling_id)
            except ValueError:
                raise ValueError(f"Invalid scaling ID in item {key} for stat {stat_name}")
            stats.append(ItemStat(name=stat_name, scaling_id=scaling_id))
            
        if not stats:
            raise ValueError(f"Item {key} ({name}) has no stats defined in <stats> element")

        return ItemDefinition(
            key=key,
            name=name,
            min_ilvl=min_ilvl,
            slot=slot,
            quality=quality,
            stats=stats,
            required_player_level=required_player_level,
            scaling=scaling,
            value_table_id=value_table_id
        )

    @classmethod
    def parse_file(cls, file_path: str) -> List[ItemDefinition]:
        """
        Parse an XML file containing item definitions.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            List of ItemDefinition objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ET.ParseError: If the XML is invalid
            ValueError: If any item data is invalid
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            items = []
            for item_elem in root.findall('item'):
                try:
                    item_def = cls.parse_item_element(item_elem)
                    items.append(item_def)
                except ValueError as e:
                    # Log the error but continue parsing other items
                    print(f"Error parsing item: {e}")
                    continue
                    
            return items
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Item definition file not found: {file_path}")
        except ET.ParseError as e:
            raise ET.ParseError(f"Invalid XML in file {file_path}: {e}")

# Example usage:
"""
# Parse a single item from XML string
xml_str = '''
<item key="1879480675" name="Chipped Bright Umbari Necklace" level="512" 
      slot="NECK" quality="UNCOMMON" minLevel="150" 
      scaling="ze_skirmish_level#141-:1879471052;2:0.3" 
      valueTableId="1879050115">
    <stats>
        <stat name="VITALITY" scaling="1879347271"/>
        <stat name="CRITICAL_RATING" scaling="1879211605"/>
        <stat name="FINESSE" scaling="1879211717"/>
    </stats>
</item>
'''
item_elem = ET.fromstring(xml_str)
item_def = ItemParser.parse_item_element(item_elem)

# Parse all items from a file
items = ItemParser.parse_file('path/to/items.xml')
""" 