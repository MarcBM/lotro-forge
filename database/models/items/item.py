"""
Base database model for all LOTRO items.
"""
from typing import Optional, List, Dict
from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .item_quality import ItemQuality
from .item_stat import ItemStat


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