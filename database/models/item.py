"""
Database models for LOTRO items and their stats.
These models represent both the database structure and domain logic for items.
"""
from typing import Optional, List, Dict, Tuple
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum as PythonEnum

from .base import Base
from .progressions import ProgressionTable, ProgressionType

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
    
    __mapper_args__ = {
        'polymorphic_identity': 'equipment',
    }
    
    def __repr__(self) -> str:
        return f"<EquipmentItem(key={self.key}, name='{self.name}')>"
    
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
        })
        return result 