"""
Database model for primitive LOTRO item definitions (from XML data).
"""
from typing import Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class ItemDefinition(Base):
    """Model for the primitive form of LOTRO items (from XML data)."""
    
    __tablename__ = "item_definitions"
    
    key: Mapped[int] = mapped_column(Integer, primary_key=True)  # XML item identifier
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    base_ilvl: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    slot: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quality: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    required_player_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    scaling: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    value_table_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    def __repr__(self) -> str:
        return f"<ItemDefinition(key={self.key}, name='{self.name}')>" 