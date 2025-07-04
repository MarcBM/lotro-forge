"""
Database model for weapon items.
"""
from typing import Optional, Dict, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .equipment_item import EquipmentItem
from .item_quality import ItemQuality

if TYPE_CHECKING:
    from ..dps import DpsTable


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
    
    def to_list_json(self) -> Dict:
        """
        Convert the weapon to a minimal JSON representation for list views.
        Extends the equipment to_list_json with essential weapon fields.
        """
        result = super().to_list_json()
        result.update({
            'slot': self.slot,
            'armour_type': self.armour_type,
            'weapon_type': self.weapon_type,
            'base_dps': self.dps,
            'total_sockets': self.total_sockets
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
            result['stat_values'].append({
                'stat_name': 'DPS',
                'value': calculated_dps
            })
        
        return result 