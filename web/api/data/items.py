"""
API endpoints for item data.
This module handles getting base item information and calculating concrete stats.
Provides efficient endpoints that separate base item data from concrete calculations.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from database.session import SessionLocal
from database.models.items import Item

# Create router
router = APIRouter()

# Database session dependency
def get_db():
    """Get a database session."""
    with SessionLocal() as session:
        yield session

@router.get("/{item_key}")
async def get_item(
    item_key: int = Path(..., description="Item key"),
    db: Session = Depends(get_db)
):
    """
    Get base item information by key.
    Returns the item object with all base properties but no concrete stats.
    """
    try:
        # Get the item (will automatically load the correct subclass)
        item = db.query(Item).filter(Item.key == item_key).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Use polymorphic to_json method - each subclass provides appropriate data
        return {
            "result": item.to_json()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item: {str(e)}")

@router.get("/{item_key}/stats")
async def get_item_stats(
    item_key: int = Path(..., description="Item key"),
    ilvl: int = Query(..., description="Item level for concrete stats"),
    db: Session = Depends(get_db)
):
    """
    Get concrete stats for an item at a specific item level.
    Returns only the calculated stat values and DPS - no base item data.
    """
    try:
        # Get the item
        item = db.query(Item).filter(Item.key == item_key).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Use polymorphic get_stats_json method - handles type-specific stats like DPS
        return {
            "result": item.get_stats_json(ilvl)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item stats: {str(e)}")

@router.get("/{item_key}/concrete")
async def get_concrete_item(
    item_key: int = Path(..., description="Item key"),
    ilvl: Optional[int] = Query(None, description="Item level for concrete stats (defaults to base ilvl)"),
    db: Session = Depends(get_db)
):
    """
    Get a complete concrete item with both base data and calculated stats.
    
    This is a convenience endpoint for the common pattern where users select an item
    from a list view and need both the full item information and concrete stats.
    
    Returns combined item data and stats at the specified level (or base ilvl if not specified).
    """
    try:
        # Get the item
        item = db.query(Item).filter(Item.key == item_key).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Use base ilvl if no specific level requested
        target_ilvl = ilvl if ilvl is not None else item.base_ilvl
        
        # Get base item data and concrete stats
        item_data = item.to_json()
        stats_data = item.get_stats_json(target_ilvl)
        
        # Combine into a single response
        return {
            "result": {
                **item_data,  # All base item properties
                "concrete_ilvl": target_ilvl,  # The level these stats are calculated for
                "stats": stats_data  # Calculated stats at the target level
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get concrete item: {str(e)}")