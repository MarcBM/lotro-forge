"""
API endpoints for item operations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from database.models.item import ItemDefinition
from database.config import get_database_url
from sqlalchemy import create_engine, select

# Create router
router = APIRouter()

# Create a single engine instance
try:
    engine = create_engine(get_database_url())
    # Create a session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise RuntimeError(f"Failed to initialize database connection: {e}")

# Database session dependency
def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_items(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(10, ge=1, le=100, description="Limit to N items"),
    slot: Optional[str] = Query(None, description="Filter by equipment slot"),
    quality: Optional[str] = Query(None, description="Filter by item quality"),
    min_level: Optional[int] = Query(None, ge=1, description="Minimum required level"),
    max_level: Optional[int] = Query(None, ge=1, description="Maximum required level")
) -> List[dict]:
    """List items with optional filtering."""
    try:
        # Build query
        stmt = select(ItemDefinition)
        
        # Apply filters
        if slot:
            stmt = stmt.where(ItemDefinition.slot == slot)
        if quality:
            stmt = stmt.where(ItemDefinition.quality == quality)
        if min_level:
            stmt = stmt.where(ItemDefinition.required_player_level >= min_level)
        if max_level:
            stmt = stmt.where(ItemDefinition.required_player_level <= max_level)
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        # Execute query
        items = db.execute(stmt).scalars().all()
        
        # Convert to dict for JSON response
        return [
            {
                "key": item.key,
                "name": item.name,
                "base_ilvl": item.base_ilvl,
                "slot": item.slot,
                "quality": item.quality,
                "required_player_level": item.required_player_level,
                "scaling": item.scaling,
                "value_table_id": item.value_table_id
            }
            for item in items
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        )

@router.get("/{item_key}")
async def get_item(
    item_key: int,
    db: Session = Depends(get_db)
) -> dict:
    """Get a specific item by its key."""
    try:
        stmt = select(ItemDefinition).where(ItemDefinition.key == item_key)
        item = db.execute(stmt).scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {
            "key": item.key,
            "name": item.name,
            "base_ilvl": item.base_ilvl,
            "slot": item.slot,
            "quality": item.quality,
            "required_player_level": item.required_player_level,
            "scaling": item.scaling,
            "value_table_id": item.value_table_id
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        ) 