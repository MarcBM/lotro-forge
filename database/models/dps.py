"""
Database models for LOTRO DPS (damage per second) tables.
"""
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .items.item_quality import ItemQuality


class DpsTable(Base):
    """Model for DPS (damage per second) tables used by weapons."""
    __tablename__ = "dps_tables"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # DPS table ID from XML
    
    # Quality factors
    quality_common: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_uncommon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_rare: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_incomparable: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_legendary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    values: Mapped[List["DpsValue"]] = relationship(
        "DpsValue", 
        back_populates="dps_table", 
        cascade="all, delete-orphan",
        order_by="DpsValue.level"
    )
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<DpsTable(id='{self.id}')>"
    
    def get_quality_factor(self, quality) -> float:
        """Get the quality factor for this DPS table."""
        
        quality_map = {
            ItemQuality.COMMON: self.quality_common or 1.0,
            ItemQuality.UNCOMMON: self.quality_uncommon or 1.0,
            ItemQuality.RARE: self.quality_rare or 1.0,
            ItemQuality.INCOMPARABLE: self.quality_incomparable or 1.0,
            ItemQuality.LEGENDARY: self.quality_legendary or 1.0,
        }
        return quality_map.get(quality, 1.0)
    
    def get_base_dps_at_level(self, level: int) -> float:
        """Get the base DPS value at a specific level."""
        if not self.values:
            return 0.0
        
        # Find exact level match
        exact_match = next((v.value for v in self.values if v.level == level), None)
        if exact_match is not None:
            return exact_match
        
        # Find surrounding values for interpolation
        values = sorted(self.values, key=lambda v: v.level)
        lower = next((v for v in reversed(values) if v.level <= level), None)
        upper = next((v for v in values if v.level >= level), None)
        
        if not lower or not upper:
            return 0.0
        if lower.level == upper.level:
            return lower.value
            
        # Linear interpolation
        ratio = (level - lower.level) / (upper.level - lower.level)
        return lower.value + (upper.value - lower.value) * ratio
    
    def get_dps_at_level(self, level: int, quality) -> float:
        """Get the final DPS value at a specific level with quality factor applied."""
        base_dps = self.get_base_dps_at_level(level)
        quality_factor = self.get_quality_factor(quality)
        return base_dps * quality_factor


class DpsValue(Base):
    """Model for individual DPS values at specific levels."""
    __tablename__ = "dps_values"
    
    dps_table_id: Mapped[str] = mapped_column(String(50), ForeignKey("dps_tables.id"), primary_key=True)
    level: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    dps_table: Mapped["DpsTable"] = relationship("DpsTable", back_populates="values")
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<DpsValue(table_id='{self.dps_table_id}', level={self.level}, value={self.value})>" 