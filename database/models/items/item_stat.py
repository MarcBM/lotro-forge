"""
Database model for stats on items, including their value table references.
"""
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..progressions import ProgressionTable, ProgressionType

if TYPE_CHECKING:
    from .item import Item


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