"""
Database model for essence items.
"""
from typing import Optional, Dict
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .item import Item


class Essence(Item):
    """
    Model for essence items.
    Extends the base Item class with essence-specific fields and functionality.
    """
    __tablename__ = "essences"
    
    # Primary key is inherited from Item
    key: Mapped[int] = mapped_column(ForeignKey("items.key"), primary_key=True)
    
    # Essence-specific fields
    tier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    essence_type: Mapped[Optional[str]] = mapped_column(String(8), nullable=True, index=True)  # Capitalized essence type string (max 8 chars)
    
    # Essence type translation mapping (for import only)
    ESSENCE_TYPE_VALUES = {
        1: 'BASIC',
        18: 'PVP',
        19: 'CLOAK',
        20: 'NECKLACE',
        22: 'PRIMARY',
        23: 'VITAL'
    }
    
    __mapper_args__ = {
        'polymorphic_identity': 'essence',
    }
    
    def __repr__(self) -> str:
        return f"<Essence(key={self.key}, name='{self.name}')>"
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the essence to a dictionary representation.
        Extends the base to_dict with essence-specific fields.
        """
        result = super().to_dict(ilvl)
        result.update({
            'tier': self.tier,
            'essence_type': self.essence_type,
        })
        return result
    
    def to_json(self) -> Dict:
        """
        Convert the essence to a JSON representation for API responses.
        Extends the base to_json with essence-specific fields.
        """
        result = super().to_json()
        result.update({
            'tier': self.tier,
            'essence_type': self.essence_type
        })
        return result
    
    def to_list_json(self) -> Dict:
        """
        Convert the essence to a minimal JSON representation for list views.
        Extends the base to_list_json with essential essence fields.
        """
        result = super().to_list_json()
        result.update({
            'essence_type': self.essence_type
        })
        return result 