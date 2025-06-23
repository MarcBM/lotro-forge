"""
Database models for LOTRO items and their stats.
These models represent both the database structure and domain logic for items.
"""
from typing import Optional, List, Dict, Tuple, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint, Enum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from enum import Enum as PythonEnum

from .base import Base
from .progressions import ProgressionTable, ProgressionType

if TYPE_CHECKING:
    from .dps import DpsTable

class ItemQuality(PythonEnum):
    """Enum for item quality levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    INCOMPARABLE = "incomparable"
    LEGENDARY = "legendary"

class ItemStat(Base):
    """Model for stats on an item, including their value table references."""
    __tablename__ = "item_stats"
    
    # Composite primary key of item and stat name
    item_key: Mapped[int] = mapped_column(ForeignKey("items.key"), primary_key=True)
    stat_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    value_table_id: Mapped[str] = mapped_column(ForeignKey("progression_tables.table_id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Preserve XML order
    
    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="stats")
    value_table: Mapped[ProgressionTable] = relationship("ProgressionTable")
    
    def __repr__(self) -> str:
        return f"<ItemStat(item_key={self.item_key}, stat_name='{self.stat_name}')>"
    
    def get_value(self, item_level: int) -> float:
        """Get the concrete value for this stat at the given item level."""
        if not self.value_table or not self.value_table.values:
            return 0.0
            
        # Find the closest value in the loaded values list
        if self.value_table.progression_type == ProgressionType.ARRAY:
            # Direct lookup
            value = next((v.value for v in self.value_table.values if v.item_level == item_level), None)
            return value if value is not None else 0.0
        else:  # LINEAR
            # Find surrounding points for interpolation
            values = sorted(self.value_table.values, key=lambda v: v.item_level)
            lower = next((v for v in reversed(values) if v.item_level <= item_level), None)
            upper = next((v for v in values if v.item_level >= item_level), None)
            
            if not lower or not upper:
                return 0.0
            if lower.item_level == upper.item_level:
                return lower.value
                
            # Linear interpolation
            ratio = (item_level - lower.item_level) / (upper.item_level - lower.item_level)
            return lower.value + (upper.value - lower.value) * ratio

class Item(Base):
    """
    Base model for all LOTRO items.
    This represents the common fields and functionality shared by all item types.
    """
    __tablename__ = "items"
    
    key: Mapped[int] = mapped_column(Integer, primary_key=True)  # XML item identifier
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    base_ilvl: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quality: Mapped[str] = mapped_column(Enum(ItemQuality), nullable=False, index=True)
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Hyphen-separated icon IDs
    
    # Relationships
    stats: Mapped[List[ItemStat]] = relationship(
        "ItemStat", 
        back_populates="item", 
        cascade="all, delete-orphan",
        order_by="ItemStat.order"  # Use the order from XML
    )
    
    # Discriminator column for inheritance
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': item_type
    }
    
    def __repr__(self) -> str:
        return f"<Item(key={self.key}, name='{self.name}')>"
    
    def get_stats_at_ilvl(self, ilvl: Optional[int] = None) -> Dict[str, float]:
        """
        Get the concrete stat values for this item at a specific item level.
        If no item level is provided, uses the base item level.
        Returns a dictionary mapping stat names to their values.
        """
        if ilvl is None:
            ilvl = self.base_ilvl
            
        return {
            stat.stat_name: stat.get_value(ilvl)
            for stat in self.stats
        }
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the item to a dictionary representation.
        If ilvl is provided, includes concrete stat values at that level.
        """
        result = {
            'key': self.key,
            'name': self.name,
            'base_ilvl': self.base_ilvl,
            'quality': self.quality.value,
            'icon': self.icon,
            'item_type': self.item_type,
            'stats': [
                {
                    'name': stat.stat_name,
                    'value_table_id': stat.value_table_id
                }
                for stat in self.stats
            ]
        }
        
        if ilvl is not None:
            result['ilvl'] = ilvl
            result['stat_values'] = self.get_stats_at_ilvl(ilvl)
        
        return result
    
    def to_json(self) -> Dict:
        """
        Convert the item to a JSON representation for API responses.
        Returns base item data suitable for frontend consumption.
        """
        # Process icon URLs
        icon_urls = []
        if self.icon:
            # Split hyphen-separated icon IDs and convert to URLs
            icon_ids = self.icon.split('-')
            icon_urls = [f"/static/icons/items/{icon_id}.png" for icon_id in icon_ids if icon_id]
        
        return {
            'key': self.key,
            'name': self.name,
            'base_ilvl': self.base_ilvl,
            'quality': self.quality.value.upper(),
            'item_type': self.item_type,
            'icon_urls': icon_urls,
            'stat_names': [stat.stat_name for stat in self.stats]
        }
    
    def to_list_json(self) -> Dict:
        """
        Convert the item to a minimal JSON representation for list views.
        Returns only essential data: key, name, icon_urls, quality.
        """
        # Process icon URLs
        icon_urls = []
        if self.icon:
            # Split hyphen-separated icon IDs and convert to URLs
            icon_ids = self.icon.split('-')
            icon_urls = [f"/static/icons/items/{icon_id}.png" for icon_id in icon_ids if icon_id]
        
        return {
            'key': self.key,
            'name': self.name,
            'quality': self.quality.value.upper(),
            'icon_urls': icon_urls
        }
    
    def get_stats_json(self, ilvl: int) -> Dict:
        """
        Get concrete stats for this item at a specific item level.
        Returns only the calculated stat values - no base item data.
        """
        stat_values = []
        for stat in self.stats:
            stat_value = stat.get_value(ilvl)
            stat_values.append({
                'stat_name': stat.stat_name,
                'value': stat_value
            })
        
        return {
            'ilvl': ilvl,
            'stat_values': stat_values
        }

class EquipmentItem(Item):
    """
    Model for equipment items (weapons, armor, etc.).
    Extends the base Item class with equipment-specific fields and functionality.
    """
    __tablename__ = "equipment_items"
    
    # Primary key is inherited from Item
    key: Mapped[int] = mapped_column(ForeignKey("items.key"), primary_key=True)
    
    # Equipment-specific fields
    slot: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    armour_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)  # e.g. "HEAVY", "MEDIUM", "LIGHT"
    scaling: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Socket counts - count of each socket type on this equipment
    sockets_basic: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_primary: Mapped[int] = mapped_column(Integer, nullable=False, default=0) 
    sockets_vital: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_cloak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_necklace: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_pvp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Socket type mapping for parsing XML strings
    SOCKET_TYPE_MAPPING = {
        'S': 'basic',
        'P': 'primary', 
        'V': 'vital',
        'C': 'cloak',
        'N': 'necklace',
        'W': 'pvp'
    }
    
    __mapper_args__ = {
        'polymorphic_identity': 'equipment',
    }
    
    def __repr__(self) -> str:
        return f"<EquipmentItem(key={self.key}, name='{self.name}')>"
    
    @classmethod
    def parse_socket_string(cls, socket_string: Optional[str]) -> Dict[str, int]:
        """
        Parse a socket string from XML into socket counts.
        
        Args:
            socket_string: String like "PVS", "PVSSS", "3", or "P2V" representing socket types
                          - Letters represent specific socket types (P=Primary, V=Vital, etc.)
                          - Numbers represent that many basic sockets
            
        Returns:
            Dict mapping socket type names to their counts
        """
        socket_counts = {
            'basic': 0,
            'primary': 0,
            'vital': 0,
            'cloak': 0,
            'necklace': 0,
            'pvp': 0
        }
        
        if not socket_string:
            return socket_counts
            
        # Count each socket type
        for socket_char in socket_string:
            if socket_char.isdigit():
                # Numbers represent basic sockets
                socket_counts['basic'] += int(socket_char)
            else:
                # Letters represent specific socket types
                socket_type = cls.SOCKET_TYPE_MAPPING.get(socket_char)
                if socket_type:
                    socket_counts[socket_type] += 1
                
        return socket_counts
    
    @property
    def total_sockets(self) -> int:
        """Get the total number of sockets on this equipment."""
        return (self.sockets_basic + self.sockets_primary + self.sockets_vital +
                self.sockets_cloak + self.sockets_necklace + self.sockets_pvp)
    
    @property
    def socket_summary(self) -> Dict[str, int]:
        """Get a summary of all sockets on this equipment."""
        return {
            'basic': self.sockets_basic,
            'primary': self.sockets_primary,
            'vital': self.sockets_vital,
            'cloak': self.sockets_cloak,
            'necklace': self.sockets_necklace,
            'pvp': self.sockets_pvp,
            'total': self.total_sockets
        }
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the equipment item to a dictionary representation.
        Extends the base to_dict with equipment-specific fields.
        """
        result = super().to_dict(ilvl)
        result.update({
            'slot': self.slot,
            'armour_type': self.armour_type,
            'scaling': self.scaling,
            'sockets': self.socket_summary
        })
        return result
    
    def to_json(self) -> Dict:
        """
        Convert the equipment item to a JSON representation for API responses.
        Extends the base to_json with equipment-specific fields.
        """
        result = super().to_json()
        result.update({
            'slot': self.slot,
            'armour_type': self.armour_type,
            'scaling': self.scaling,
            'total_sockets': self.total_sockets
        })
        
        # Add socket breakdown for equipment if there are sockets
        if self.total_sockets > 0:
            result['sockets'] = {
                'basic': self.sockets_basic,
                'primary': self.sockets_primary,
                'vital': self.sockets_vital,
                'cloak': self.sockets_cloak,
                'necklace': self.sockets_necklace,
                'pvp': self.sockets_pvp
            }
        
        return result

class Weapon(EquipmentItem):
    """
    Model for weapon items.
    Extends EquipmentItem with weapon-specific fields and functionality.
    """
    __tablename__ = "weapons"
    
    # Primary key is inherited from EquipmentItem
    key: Mapped[int] = mapped_column(ForeignKey("equipment_items.key"), primary_key=True)
    
    # Weapon-specific fields
    dps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Base DPS value
    dps_table_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("dps_tables.id"), nullable=True)
    min_damage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_damage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    damage_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. "COMMON", "WESTERNESSE"
    weapon_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # e.g. "BOW", "ONE_HANDED_SWORD"
    
    # Relationships
    dps_table: Mapped[Optional["DpsTable"]] = relationship("DpsTable")
    
    __mapper_args__ = {
        'polymorphic_identity': 'weapon',
    }
    
    def __repr__(self) -> str:
        return f"<Weapon(key={self.key}, name='{self.name}', weapon_type='{self.weapon_type}')>"
    
    def get_dps_at_ilvl(self, ilvl: Optional[int] = None) -> Optional[float]:
        """
        Get the calculated DPS for this weapon at a specific item level.
        Uses the DPS table if available, otherwise returns the base DPS.
        """
        if ilvl is None:
            ilvl = self.base_ilvl
            
        if self.dps_table:
            # Calculate DPS using the DPS table and weapon quality
            quality_enum = ItemQuality(self.quality)
            return self.dps_table.get_dps_at_level(ilvl, quality_enum)
        else:
            # Fall back to base DPS value
            return self.dps
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the weapon to a dictionary representation.
        Extends the base to_dict with weapon-specific fields.
        """
        result = super().to_dict(ilvl)
        result.update({
            'dps': self.dps,
            'dps_table_id': self.dps_table_id,
            'min_damage': self.min_damage,
            'max_damage': self.max_damage,
            'damage_type': self.damage_type,
            'weapon_type': self.weapon_type,
        })
        
        # Add calculated DPS at the specified level
        if ilvl is not None:
            result['calculated_dps'] = self.get_dps_at_ilvl(ilvl)
        
        return result
    
    def to_json(self) -> Dict:
        """
        Convert the weapon to a JSON representation for API responses.
        Extends the equipment to_json with weapon-specific fields.
        """
        result = super().to_json()
        result.update({
            'weapon_type': self.weapon_type,
            'damage_type': self.damage_type,
            'min_damage': self.min_damage,
            'max_damage': self.max_damage,
            'base_dps': self.dps
        })
        return result
    
    def get_stats_json(self, ilvl: int) -> Dict:
        """
        Get concrete stats for this weapon at a specific item level.
        Extends the base get_stats_json with weapon DPS calculation.
        """
        result = super().get_stats_json(ilvl)
        
        # Add calculated DPS for weapons
        calculated_dps = self.get_dps_at_ilvl(ilvl)
        if calculated_dps is not None:
            result['calculated_dps'] = calculated_dps
        
        return result

class Essence(Item):
    """
    Model for essence items.
    Extends the base Item class with essence-specific fields and functionality.
    """
    __tablename__ = "essences"
    
    # Primary key is inherited from Item
    key: Mapped[int] = mapped_column(ForeignKey("items.key"), primary_key=True)
    
    # Essence-specific fields
    tier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    essence_type: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # Using essence_type to avoid conflict with 'type' keyword
    
    # Essence type translation mapping
    ESSENCE_TYPE_NAMES = {
        1: 'Basic',
        18: 'PVP',
        19: 'Cloak',
        20: 'Necklace',
        22: 'Primary',
        23: 'Vital'
    }
    
    __mapper_args__ = {
        'polymorphic_identity': 'essence',
    }
    
    @property
    def essence_type_name(self) -> Optional[str]:
        """Get the readable name for this essence type."""
        if self.essence_type is None:
            return None
        return self.ESSENCE_TYPE_NAMES.get(self.essence_type, f'Unknown ({self.essence_type})')
    
    def __repr__(self) -> str:
        return f"<Essence(key={self.key}, name='{self.name}')>"
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the essence to a dictionary representation.
        Extends the base to_dict with essence-specific fields.
        """
        result = super().to_dict(ilvl)
        result.update({
            'tier': self.tier,
            'essence_type': self.essence_type,
            'essence_type_name': self.essence_type_name,
        })
        return result
    
    def to_json(self) -> Dict:
        """
        Convert the essence to a JSON representation for API responses.
        Extends the base to_json with essence-specific fields.
        """
        result = super().to_json()
        result.update({
            'tier': self.tier,
            'essence_type': self.essence_type,
            'essence_type_name': self.essence_type_name
        })
        return result
    
    def to_list_json(self) -> Dict:
        """
        Convert the essence to a minimal JSON representation for list views.
        Extends the base to_list_json with essential essence fields.
        """
        result = super().to_list_json()
        result.update({
            'essence_type': self.essence_type,
            'essence_type_name': self.essence_type_name
        })
        return result

# End of file - DPS classes moved to database/models/dps.py 