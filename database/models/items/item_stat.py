"""
Database model for stats on items, including their value table references.
"""
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..value_lookup import LookupTable

if TYPE_CHECKING:
    from .item import Item


class ItemStat(Base):
    """Model for stats on an item, including their value table references."""
    __tablename__ = "item_stats"
    
    # Composite primary key of item and stat name
    item_key: Mapped[int] = mapped_column(ForeignKey("items.key"), primary_key=True)
    stat_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    value_table_id: Mapped[str] = mapped_column(ForeignKey("lookup_tables.table_id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Preserve XML order
    
    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="stats")
    value_table: Mapped[LookupTable] = relationship("LookupTable")
    
    def __repr__(self) -> str:
        return f"<ItemStat(item_key={self.item_key}, stat_name='{self.stat_name}')>"
    
    def get_value(self, item_level: int, quality: Optional[str] = None) -> Optional[float]:
        """
        Get the concrete value for this stat at the given item level.
        
        Args:
            item_level: The item level to get the value for
            quality: Optional quality string (COMMON, UNCOMMON, RARE, INCOMPARABLE, LEGENDARY)
                    Only used for stats that have quality modifiers (like DPS)
        """
        if not self.value_table:
            return None
        
        return self.value_table.get_value_at_level(item_level, quality) 