"""
Database models for unified value lookup tables.
This replaces the separate DpsTable and ProgressionTable models with a consistent approach.
"""
from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LookupTable(Base):
    """
    Unified model for value lookup tables.
    Replaces DpsTable and ProgressionTable with a consistent approach.
    """
    __tablename__ = "lookup_tables"
    
    table_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Quality modifiers - 5 separate float columns for better performance
    # Nullable since most progression tables won't use quality modifiers
    quality_common: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_uncommon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_rare: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_incomparable: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_legendary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    values: Mapped[List["LookupValue"]] = relationship(
        "LookupValue", 
        back_populates="table", 
        cascade="all, delete-orphan",
        order_by="LookupValue.level"
    )
    
    def __repr__(self) -> str:
        return f"<LookupTable(table_id='{self.table_id}', name='{self.name}')>"
    
    def get_quality_modifier(self, quality: str) -> float:
        """
        Get the quality modifier for a given quality string.
        
        Args:
            quality: Quality string (COMMON, UNCOMMON, RARE, INCOMPARABLE, LEGENDARY)
        """
        # Direct mapping to individual columns for better performance
        quality_map = {
            'COMMON': self.quality_common,
            'UNCOMMON': self.quality_uncommon,
            'RARE': self.quality_rare,
            'INCOMPARABLE': self.quality_incomparable,
            'LEGENDARY': self.quality_legendary
        }
        
        return quality_map.get(quality, 1.0) or 1.0
    
    @property
    def has_quality_modifiers(self) -> bool:
        """Check if this table has any quality modifiers set."""
        return any([
            self.quality_common is not None,
            self.quality_uncommon is not None,
            self.quality_rare is not None,
            self.quality_incomparable is not None,
            self.quality_legendary is not None
        ])
    
    def get_value_at_level(self, level: int, quality: Optional[str] = None) -> Optional[float]:
        """
        Get the exact value at a specific level, optionally applying quality modifier.
        
        Args:
            level: The item level to look up
            quality: Optional quality string (COMMON, UNCOMMON, RARE, INCOMPARABLE, LEGENDARY)
        """
        if not self.values:
            return None
        
        # Find exact level match
        exact_match = next((v.value for v in self.values if v.level == level), None)
        if exact_match is None:
            return None
        
        base_value = exact_match
        
        # Apply quality modifier if specified
        if quality is not None:
            if not self.has_quality_modifiers:
                print(f"Warning: Quality '{quality}' specified but no quality modifiers exist for table '{self.table_id}'")
                return base_value
            
            quality_modifier = self.get_quality_modifier(quality)
            return base_value * quality_modifier
        
        return base_value


class LookupValue(Base):
    """
    Model for individual values in a lookup table.
    Replaces DpsValue and ProgressionValue with a consistent approach.
    """
    __tablename__ = "lookup_values"
    
    table_id: Mapped[str] = mapped_column(String(50), ForeignKey("lookup_tables.table_id"), primary_key=True)
    level: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    table: Mapped[LookupTable] = relationship("LookupTable", back_populates="values")
    
    def __repr__(self) -> str:
        return f"<LookupValue(table_id='{self.table_id}', level={self.level}, value={self.value})>" 