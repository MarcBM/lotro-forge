"""
Database model for essence items.
"""
from typing import Optional, Dict
from sqlalchemy import Integer, ForeignKey
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
    essence_type: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # Using essence_type to avoid conflict with 'type' keyword
    
    # Essence type translation mapping
    ESSENCE_TYPE_NAMES = {
        1: 'Basic',
        18: 'PVP',
        19: 'Cloak',
        20: 'Necklace',
        22: 'Primary',
        23: 'Vital'
    }
    
    __mapper_args__ = {
        'polymorphic_identity': 'essence',
    }
    
    @property
    def essence_type_name(self) -> Optional[str]:
        """Get the readable name for this essence type."""
        if self.essence_type is None:
            return None
        return self.ESSENCE_TYPE_NAMES.get(self.essence_type, f'Unknown ({self.essence_type})')
    
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
            'essence_type_name': self.essence_type_name,
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
            'essence_type': self.essence_type,
            'essence_type_name': self.essence_type_name
        })
        return result
    
    def to_list_json(self) -> Dict:
        """
        Convert the essence to a minimal JSON representation for list views.
        Extends the base to_list_json with essential essence fields.
        """
        result = super().to_list_json()
        result.update({
            'essence_type': self.essence_type,
            'essence_type_name': self.essence_type_name
        })
        return result 