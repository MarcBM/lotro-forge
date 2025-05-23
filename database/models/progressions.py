"""
Database models for progression tables.
These tables map item levels to stat values, supporting both linear interpolation and array lookup.
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped
from .base import Base
from typing import List, Optional
from sqlalchemy.orm import mapped_column

class ProgressionType(Enum):
    """Type of progression calculation."""
    LINEAR = "linear"  # Values are linearly interpolated between points
    ARRAY = "array"    # Values are looked up directly from array

class ProgressionTable(Base):
    """Model for progression tables that map item levels to stat values."""
    __tablename__ = "progression_tables"
    
    table_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    progression_type: Mapped[ProgressionType] = mapped_column(SQLEnum(ProgressionType), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # For array type, we store exact values
    # For linear type, we store control points for interpolation
    values: Mapped[List["ProgressionValue"]] = relationship("ProgressionValue", back_populates="table", cascade="all, delete-orphan")
    
    def get_value(self, item_level: int) -> float:
        """Get the value for a given item level using appropriate calculation method."""
        if self.progression_type == ProgressionType.ARRAY:
            # Direct lookup
            value = self.values.filter_by(item_level=item_level).first()
            return value.value if value else 0.0
        else:  # LINEAR
            # Find surrounding points for interpolation
            lower = self.values.filter(ProgressionValue.item_level <= item_level).order_by(ProgressionValue.item_level.desc()).first()
            upper = self.values.filter(ProgressionValue.item_level >= item_level).order_by(ProgressionValue.item_level.asc()).first()
            
            if not lower or not upper:
                return 0.0
            if lower.item_level == upper.item_level:
                return lower.value
                
            # Linear interpolation
            ratio = (item_level - lower.item_level) / (upper.item_level - lower.item_level)
            return lower.value + (upper.value - lower.value) * ratio

    def __repr__(self):
        return f"<ProgressionTable(table_id='{self.table_id}', name='{self.name}')>"

class ProgressionValue(Base):
    """Model for individual values in a progression table."""
    __tablename__ = "table_values"
    
    table_id: Mapped[str] = mapped_column(ForeignKey("progression_tables.table_id"), primary_key=True)
    item_level: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    table: Mapped[ProgressionTable] = relationship("ProgressionTable", back_populates="values")
    
    __table_args__ = (
        UniqueConstraint('table_id', 'item_level', name='uq_table_value'),
    )
    
    def __repr__(self) -> str:
        return f"<ProgressionValue(table_id='{self.table_id}', item_level={self.item_level}, value={self.value})>" 