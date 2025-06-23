"""
Database model for equipment items (weapons, armor, etc.).
"""
from typing import Optional, Dict
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .item import Item


class EquipmentItem(Item):
    """
    Model for equipment items (weapons, armor, etc.).
    Extends the base Item class with equipment-specific fields and functionality.
    """
    __tablename__ = "equipment_items"
    
    # Primary key is inherited from Item
    key: Mapped[int] = mapped_column(ForeignKey("items.key"), primary_key=True)
    
    # Equipment-specific fields
    slot: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    armour_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)  # e.g. "HEAVY", "MEDIUM", "LIGHT"
    scaling: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Socket counts - count of each socket type on this equipment
    sockets_basic: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_primary: Mapped[int] = mapped_column(Integer, nullable=False, default=0) 
    sockets_vital: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_cloak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_necklace: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sockets_pvp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Socket type mapping for parsing XML strings
    SOCKET_TYPE_MAPPING = {
        'S': 'basic',
        'P': 'primary', 
        'V': 'vital',
        'C': 'cloak',
        'N': 'necklace',
        'W': 'pvp'
    }
    
    __mapper_args__ = {
        'polymorphic_identity': 'equipment',
    }
    
    def __repr__(self) -> str:
        return f"<EquipmentItem(key={self.key}, name='{self.name}', slot='{self.slot}')>"
    
    @classmethod
    def parse_socket_string(cls, socket_string: Optional[str]) -> Dict[str, int]:
        """
        Parse a socket string from XML into socket counts.
        
        Socket strings are like 'SPV' or 'PPSS' where each character represents a socket type:
        S = Basic, P = Primary, V = Vital, C = Cloak, N = Necklace, W = PVP
        
        Returns a dictionary with socket counts for each type.
        """
        if not socket_string:
            return {socket_type: 0 for socket_type in cls.SOCKET_TYPE_MAPPING.values()}
        
        # Count each socket type
        socket_counts = {socket_type: 0 for socket_type in cls.SOCKET_TYPE_MAPPING.values()}
        
        for char in socket_string:
            socket_type = cls.SOCKET_TYPE_MAPPING.get(char)
            if socket_type:
                socket_counts[socket_type] += 1
        
        return socket_counts
    
    @property
    def total_sockets(self) -> int:
        """Get the total number of sockets on this equipment."""
        return (self.sockets_basic + self.sockets_primary + self.sockets_vital + 
                self.sockets_cloak + self.sockets_necklace + self.sockets_pvp)
    
    @property 
    def socket_summary(self) -> Dict[str, int]:
        """Get a summary of all socket counts."""
        return {
            'basic': self.sockets_basic,
            'primary': self.sockets_primary,
            'vital': self.sockets_vital,
            'cloak': self.sockets_cloak,
            'necklace': self.sockets_necklace,
            'pvp': self.sockets_pvp
        }
    
    def to_dict(self, ilvl: Optional[int] = None) -> Dict:
        """
        Convert the equipment item to a dictionary representation.
        Extends the base to_dict with equipment-specific fields.
        """
        result = super().to_dict(ilvl)
        result.update({
            'slot': self.slot,
            'armour_type': self.armour_type,
            'scaling': self.scaling,
            'total_sockets': self.total_sockets,
            'sockets': self.socket_summary
        })
        return result
    
    def to_json(self) -> Dict:
        """
        Convert the equipment item to a JSON representation for API responses.
        Extends the base to_json with equipment-specific fields.
        """
        result = super().to_json()
        result.update({
            'slot': self.slot,
            'armour_type': self.armour_type,
            'scaling': self.scaling,
            'total_sockets': self.total_sockets
        })
        
        # Add socket breakdown for equipment if there are sockets
        if self.total_sockets > 0:
            result['sockets'] = {
                'basic': self.sockets_basic,
                'primary': self.sockets_primary,
                'vital': self.sockets_vital,
                'cloak': self.sockets_cloak,
                'necklace': self.sockets_necklace,
                'pvp': self.sockets_pvp
            }
        
        return result