from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Icon(Base):
    """
    Generic model for storing unique icons with metadata for sprite optimization.
    Used by Items, Traits, Effects, and other entities that have icons.
    """
    __tablename__ = "icons"
    
    icon_id: Mapped[str] = mapped_column(String(16), primary_key=True)  # e.g., "123", "456"
    width: Mapped[int] = mapped_column(Integer, nullable=False)  # Required for sprite sheets
    height: Mapped[int] = mapped_column(Integer, nullable=False)  # Required for sprite sheets
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bytes
    
    # Sprite sheet optimization fields
    sprite_sheet_name: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("sprite_sheets.name"), nullable=True)  # e.g., "sprites1.png"
    x_coord: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Position in sprite sheet
    y_coord: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Position in sprite sheet
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Relationships
    entity_icons: Mapped[List["EntityIcon"]] = relationship(
        "EntityIcon", 
        back_populates="icon",
        cascade="all, delete-orphan"  
    )
    sprite_sheet_ref: Mapped[Optional["SpriteSheet"]] = relationship(
        "SpriteSheet",
        back_populates="icons"
    )
    
    @property
    def sprite_sheet_version(self) -> Optional[str]:
        """Get the version for this icon's sprite sheet."""
        if not self.sprite_sheet_ref:
            return None
        
        return self.sprite_sheet_ref.version
    
    def __repr__(self) -> str:
        return f"<Icon(icon_id='{self.icon_id}', usage_count={self.usage_count})>"
    
    @property
    def is_in_sprite_sheet(self) -> bool:
        """Check if this icon is included in a sprite sheet."""
        return self.sprite_sheet_ref is not None
    
    @property
    def css_class(self) -> str:
        """Generate CSS class name for this icon."""
        return f"icon-{self.icon_id}"
    
    def generate_css_rule(self) -> str:
        """Generate complete CSS rule for this icon."""
        if not self.is_in_sprite_sheet:
            return ""
        
        sprite_url = self.get_sprite_sheet_url()
        if not sprite_url:
            return ""
        
        return f"""
.{self.css_class} {{
    background-image: url('{sprite_url}');
    background-position: {self.css_background_position};
    width: {self.width}px;
    height: {self.height}px;
    display: inline-block;
}}"""
    
    @property
    def css_background_position(self) -> str:
        """Generate CSS background position for sprite sheet."""
        if not self.is_in_sprite_sheet:
            return "0 0"
        return f"-{self.x_coord}px -{self.y_coord}px"
    
    def validate_for_sprite_sheet(self) -> bool:
        """Validate that this icon is ready for sprite sheet inclusion."""
        return (
            self.width is not None and 
            self.height is not None and 
            self.width > 0 and 
            self.height > 0
        )
    
    def get_sprite_sheet_url(self) -> Optional[str]:
        """Get the full sprite sheet URL with version for cache busting."""
        if not self.is_in_sprite_sheet:
            return None
        
        base_url = f"/static/sprites/{self.sprite_sheet_ref.name}"
        if self.sprite_sheet_version:
            return f"{base_url}?v={self.sprite_sheet_version}"
        return base_url
    
    @classmethod
    def update_sprite_sheet_versions(cls, db_session, sprite_sheet_name: str, version: str):
        """Update version for a specific sprite sheet."""
        # Upsert the sprite sheet record
        sprite_sheet = db_session.query(SpriteSheet).filter_by(
            name=sprite_sheet_name
        ).first()
        
        if sprite_sheet:
            sprite_sheet.version = version
        else:
            sprite_sheet = SpriteSheet(
                name=sprite_sheet_name,
                version=version
            )
            db_session.add(sprite_sheet)
        
        db_session.commit()


class EntityIcon(Base):
    """
    Generic model for storing entity-icon relationships.
    Can be used by Items, Traits, Effects, and other entities that have icons.
    """
    __tablename__ = "entity_icons"
    
    # Generic entity reference - all entities have unique keys
    entity_key: Mapped[int] = mapped_column(Integer, primary_key=True)  # The entity's primary key
    icon_id: Mapped[str] = mapped_column(String(16), ForeignKey("icons.icon_id"), primary_key=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # For multi-icon entities
    
    # Relationships
    icon: Mapped[Icon] = relationship("Icon", back_populates="entity_icons")
    
    def __repr__(self) -> str:
        return f"<EntityIcon(entity_key={self.entity_key}, icon_id='{self.icon_id}', order={self.order})>"


class SpriteSheet(Base):
    """
    Model for storing sprite sheets with versioning.
    """
    __tablename__ = "sprite_sheets"
    
    name: Mapped[str] = mapped_column(String(255), primary_key=True)  # e.g., "sprites1.png"
    version: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "1.0.0", "20241219_143022"
    
    # Relationships
    icons: Mapped[List[Icon]] = relationship(
        "Icon",
        back_populates="sprite_sheet_ref",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<SpriteSheet(name='{self.name}', version='{self.version}')>" 