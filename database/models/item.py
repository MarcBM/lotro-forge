"""
Database models for LOTRO items and their stats.
These models represent both the database structure and domain logic for items.
"""
from typing import Optional, List, Dict, Tuple
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base
from .progressions import ProgressionTable, ProgressionType

class ItemStat(Base):
    """Model for stats on an item, including their value table references."""
    __tablename__ = "item_stats"
    
    # Composite primary key of item and stat name
    item_key: Mapped[int] = mapped_column(ForeignKey("item_definitions.key"), primary_key=True)
    stat_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    value_table_id: Mapped[str] = mapped_column(ForeignKey("progression_tables.table_id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Preserve XML order
    
    # Relationships
    item: Mapped["ItemDefinition"] = relationship("ItemDefinition", back_populates="stats")
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

class ItemDefinition(Base):
    """
    Model for LOTRO items, including both database structure and domain logic.
    This represents both the primitive form (from XML) and the concrete form (with item level).
    """
    __tablename__ = "item_definitions"
    
    key: Mapped[int] = mapped_column(Integer, primary_key=True)  # XML item identifier
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    base_ilvl: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    slot: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quality: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    required_player_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    scaling: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    armour_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)  # e.g. "HEAVY", "MEDIUM", "LIGHT"
    
    # Relationships
    stats: Mapped[List[ItemStat]] = relationship(
        "ItemStat", 
        back_populates="item", 
        cascade="all, delete-orphan",
        order_by="ItemStat.order"  # Use the order from XML
    )
    
    def __repr__(self) -> str:
        return f"<ItemDefinition(key={self.key}, name='{self.name}')>" 
    
    @validates('required_player_level')
    def validate_player_level(self, key: str, value: int) -> int:
        """Validate that the required player level is within valid range."""
        if value < 1 or value > 150:
            raise ValueError("Required player level must be between 1 and 150")
        return value
    
    def get_valid_ilvls(self) -> Tuple[int, Optional[int]]:
        """
        Returns a tuple of (min_ilvl, max_ilvl) for this item.
        The max_ilvl may be None if there is no upper bound.
        """
        # TODO: Implement proper scaling parsing
        # For now, return a simple range based on the base_ilvl
        return (self.base_ilvl, self.base_ilvl + 10)  # Example range
    
    def get_stats_at_ilvl(self, ilvl: int) -> Dict[str, float]:
        """
        Get the concrete stat values for this item at a specific item level.
        Returns a dictionary mapping stat names to their values.
        """
        min_ilvl, max_ilvl = self.get_valid_ilvls()
        if ilvl < min_ilvl:
            raise ValueError(f"Item level {ilvl} is below minimum {min_ilvl}")
        if max_ilvl is not None and ilvl > max_ilvl:
            raise ValueError(f"Item level {ilvl} is above maximum {max_ilvl}")
        
        return {
            stat.stat_name: stat.get_value(ilvl)
            for stat in self.stats
        }
    
    @hybrid_property
    def is_legendary(self) -> bool:
        """Check if this item is legendary quality."""
        return self.quality.lower() == 'legendary'
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the item to a dictionary representation.
        If ilvl is provided, includes concrete stat values at that level.
        """
        result = {
            'key': self.key,
            'name': self.name,
            'base_ilvl': self.base_ilvl,
            'slot': self.slot,
            'quality': self.quality,
            'required_player_level': self.required_player_level,
            'scaling': self.scaling,
            'armour_type': self.armour_type,  # Include armour type in output
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