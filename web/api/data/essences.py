"""
API endpoints for essence database queries.
This module handles essence queries with filtering, sorting, and pagination.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.session import SessionLocal
from database.models.items import Essence

# Create router
router = APIRouter()

# Database session dependency
def get_db():
    """Get a database session."""
    with SessionLocal() as session:
        yield session

@router.get("/")
async def query_essences(
    # Pagination
    limit: int = Query(99, ge=1, le=99, description="Number of items to return"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    
    # Filtering
    essence_type: Optional[int] = Query(None, description="Filter by essence type"),
    tier: Optional[int] = Query(None, description="Filter by tier"),
    
    # Sorting
    sort: str = Query("recent", description="Sort by: recent, name, base_ilvl"),
    
    db: Session = Depends(get_db)
):
    """
    Query essence items with filtering, sorting, and pagination.
    """
    try:
        # Start with base query for essence items
        query = db.query(Essence)
        
        # Apply essence type filtering
        if essence_type is not None:
            query = query.filter(Essence.essence_type == essence_type)
        
        # Apply tier filtering
        if tier is not None:
            query = query.filter(Essence.tier == tier)
        
        # Apply sorting
        if sort == "name":
            query = query.order_by(Essence.name.asc())
        elif sort == "base_ilvl":
            query = query.order_by(Essence.base_ilvl.desc())
        else:  # recent or default
            query = query.order_by(Essence.key.desc())
        
        # Get total count for pagination info (before applying limit/offset)
        total_count = query.count()
        
        # Apply pagination
        essence_items = query.offset(skip).limit(limit).all()
        
        # Use polymorphic to_list_json method - each item type provides appropriate minimal data
        essence_data = [essence.to_list_json() for essence in essence_items]
        
        return {
            "essences": essence_data,
            "total": total_count,
            "limit": limit,
            "skip": skip,
            "has_more": skip + len(essence_data) < total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query essences: {str(e)}") 