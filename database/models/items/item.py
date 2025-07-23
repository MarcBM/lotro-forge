"""
Base database model for all LOTRO items.
"""
from typing import Optional, List, Dict
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .item_stat import ItemStat
from ..icon import EntityIcon


class Item(Base):
    """
    Base model for all LOTRO items.
    This represents the common fields and functionality shared by all item types.
    """
    __tablename__ = "items"
    
    key: Mapped[int] = mapped_column(Integer, primary_key=True)  # XML item identifier
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    base_ilvl: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quality: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # Uppercase quality string
    # Icon URLs are now stored in the normalized ItemIcon table
    
    # Relationships
    stats: Mapped[List[ItemStat]] = relationship(
        "ItemStat", 
        back_populates="item", 
        cascade="all, delete-orphan",
        order_by="ItemStat.order"  # Use the order from XML
    )
    # Icons are now stored in the generic EntityIcon table
    icons: Mapped[List[EntityIcon]] = relationship(
        EntityIcon,
        primaryjoin="Item.key == EntityIcon.entity_key",
        cascade="all, delete-orphan",
        order_by="EntityIcon.order"
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
            stat.stat_name: stat.get_value(ilvl, self.quality)
            for stat in self.stats
        }
    

    
    def to_json(self) -> Dict:
        """
        Convert the item to a JSON representation for API responses.
        Returns complete item data suitable for full object views.
        """
        return {
            'key': self.key,
            'name': self.name,
            'base_ilvl': self.base_ilvl,
            'quality': self.quality,
            'item_type': self.item_type,
            'icon_ids': self._get_icon_ids(),
            'stat_names': [stat.stat_name for stat in self.stats]
        }
    
    def to_list_json(self) -> Dict:
        """
        Convert the item to a minimal JSON representation for list views.
        Returns only essential data for performance in list displays.
        """
        return {
            'key': self.key,
            'name': self.name,
            'quality': self.quality,
            'icon_ids': self._get_icon_ids()
        }
    
    def get_stats_json(self, ilvl: int) -> Dict:
        """
        Get concrete stats for this item at a specific item level.
        Returns only the calculated stat values - no base item data.
        """
        stat_values = []
        for stat in self.stats:
            stat_value = stat.get_value(ilvl, self.quality)
            stat_values.append({
                'stat_name': stat.stat_name,
                'value': stat_value
            })
        
        return {
            'ilvl': ilvl,
            'stat_values': stat_values
        }
    
    def _get_icon_ids(self) -> Optional[List[str]]:
        """
        Get icon IDs for this item.
        Returns None if no icons, otherwise list of icon IDs.
        """
        if not self.icons:
            return None
        return [icon.icon_id for icon in self.icons]
    
 