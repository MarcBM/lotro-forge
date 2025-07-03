"""
API endpoints for equipment database queries.
This module handles complex database queries for equipment with search, filtering, and pagination.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.session import SessionLocal
from database.models.items import EquipmentItem

# Create router
router = APIRouter()

# Database session dependency
def get_db():
    """Get a database session."""
    with SessionLocal() as session:
        yield session

@router.get("/")
async def query_equipment(
    # Pagination
    limit: int = Query(99, ge=1, le=99, description="Number of items to return"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    
    # Filtering
    slots: Optional[List[str]] = Query(None, description="Equipment slots to filter by"),
    
    # Search
    search: Optional[str] = Query(None, description="Search query for item names"),
    
    # Sorting
    sort: str = Query("recent", description="Sort by: recent, name, base_ilvl"),
    
    db: Session = Depends(get_db)
):
    """
    Query equipment items with advanced filtering, search, sorting, and pagination.
    """
    try:
        # Start with base query for equipment items
        query = db.query(EquipmentItem)
        
        # Apply slot filtering
        if slots:
            query = query.filter(EquipmentItem.slot.in_(slots))
        
        # Apply search filtering
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(EquipmentItem.name.ilike(search_term))
        
        # Apply sorting
        if sort == "name":
            query = query.order_by(EquipmentItem.name.asc())
        elif sort == "base_ilvl":
            query = query.order_by(EquipmentItem.base_ilvl.desc(), EquipmentItem.name.asc())
        else:  # recent or default
            query = query.order_by(EquipmentItem.key.desc(), EquipmentItem.name.asc())
        
        # Get total count for pagination info (before applying limit/offset)
        total_count = query.count()
        
        # Apply pagination
        equipment_items = query.offset(skip).limit(limit).all()
        
        # Use polymorphic to_list_json method - each item type provides appropriate minimal data
        equipment_data = [item.to_list_json() for item in equipment_items]
        
        return {
            "result": equipment_data,
            "total": total_count,
            "limit": limit,
            "skip": skip,
            "has_more": skip + len(equipment_data) < total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query equipment: {str(e)}")