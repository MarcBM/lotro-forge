"""
API endpoints for item operations.
"""
import logging
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, create_engine, func

from database.models.item import Item, EquipmentItem, ItemStat
from database.config import get_database_url

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create database engine and session factory
try:
    logger.info("Initializing database connection...")
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    logger.info("Database connection initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database connection: {e}")
    raise RuntimeError(f"Failed to initialize database connection: {e}")

# Database session dependency
def get_db():
    """Get a database session."""
    with SessionLocal() as session:
        yield session

def get_icon_urls(request: Request, icon_ids: Optional[str]) -> Optional[List[str]]:
    """Convert icon IDs to full URLs.
    
    Args:
        request: FastAPI request object for getting base URL
        icon_ids: Comma-separated icon IDs or None
        
    Returns:
        List of icon URLs or None if no icons
    """
    if not icon_ids:
        return None
        
    base_url = str(request.base_url).rstrip('/')
    return [
        f"{base_url}/static/icons/items/{icon_id}.png"
        for icon_id in icon_ids.split('-')
    ]

@router.get("/")
async def list_all_items(
    request: Request,
    item_type: Optional[str] = Query(None, description="Filter by item type (e.g., 'equipment')"),
    slot: Optional[str] = None,
    quality: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    limit: int = Query(99, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    List all items with optional filtering by type and other parameters.
    Use item_type='equipment' to get only equipment items.
    """
    # Choose the model based on item_type filter
    if item_type == "equipment":
        model = EquipmentItem
        stmt = select(EquipmentItem).options(joinedload(EquipmentItem.stats))
        
        # Apply equipment-specific filters
        if slot:
            stmt = stmt.where(EquipmentItem.slot == slot)
    else:
        # Default to base Item model for now, but in future can handle other types
        model = Item
        stmt = select(Item)
        
        # Apply item_type filter if specified
        if item_type:
            stmt = stmt.where(Item.item_type == item_type)
    
    # Apply common filters
    if quality:
        stmt = stmt.where(model.quality == quality)
    if min_level:
        stmt = stmt.where(model.base_ilvl >= min_level)
    if max_level:
        stmt = stmt.where(model.base_ilvl <= max_level)
    
    # Order by key descending (newest first)
    stmt = stmt.order_by(model.key.desc())
    
    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)
    
    # Execute query
    result = db.execute(stmt)
    items = result.unique().scalars().all()
    
    # Convert to dict and process for frontend
    processed_items = []
    for item in items:
        item_dict = item.to_dict()
        # Convert quality to uppercase for frontend
        item_dict['quality'] = item_dict['quality'].upper()
        # Convert icon to icon_urls
        item_dict['icon_urls'] = get_icon_urls(request, item_dict.get('icon'))
        # Remove the raw icon field
        item_dict.pop('icon', None)
        processed_items.append(item_dict)
    
    return processed_items

@router.get("/equipment")
async def list_items(
    request: Request,
    slot: Optional[str] = None,
    quality: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    limit: int = Query(99, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> dict:
    """
    List equipment items with optional filtering and pagination.
    Returns both items and total count.
    """
    # Build base query for filtering
    base_query = select(EquipmentItem)
    
    # Apply filters to base query
    if slot:
        base_query = base_query.where(EquipmentItem.slot == slot)
    if quality:
        base_query = base_query.where(EquipmentItem.quality == quality)
    if min_level:
        base_query = base_query.where(EquipmentItem.base_ilvl >= min_level)
    if max_level:
        base_query = base_query.where(EquipmentItem.base_ilvl <= max_level)
    
    # Get total count (without pagination)
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = db.execute(count_query)
    total_count = total_result.scalar()
    
    # Build query for items with pagination and joins
    items_query = base_query.options(joinedload(EquipmentItem.stats))
    items_query = items_query.order_by(EquipmentItem.key.desc())
    items_query = items_query.offset(skip).limit(limit)
    
    # Execute items query
    result = db.execute(items_query)
    items = result.unique().scalars().all()
    
    # Convert to dict and process for frontend
    processed_items = []
    for item in items:
        item_dict = item.to_dict()
        # Convert quality to uppercase for frontend
        item_dict['quality'] = item_dict['quality'].upper()
        # Convert icon to icon_urls
        item_dict['icon_urls'] = get_icon_urls(request, item_dict.get('icon'))
        # Remove the raw icon field
        item_dict.pop('icon', None)
        processed_items.append(item_dict)
    
    return {
        "items": processed_items,
        "total": total_count,
        "limit": limit,
        "skip": skip
    }

@router.get("/equipment/{item_key}")
async def get_item(
    item_key: int,
    request: Request,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a specific equipment item by its key.
    Optionally specify an item level to get concrete stat values.
    """
    stmt = select(EquipmentItem).options(joinedload(EquipmentItem.stats)).where(EquipmentItem.key == item_key)
    result = db.execute(stmt)
    item = result.unique().scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_dict = item.to_dict(ilvl)
    # Convert quality to uppercase for frontend
    item_dict['quality'] = item_dict['quality'].upper()
    # Convert icon to icon_urls
    item_dict['icon_urls'] = get_icon_urls(request, item_dict.get('icon'))
    # Remove the raw icon field
    item_dict.pop('icon', None)
    
    return item_dict

@router.get("/equipment/{item_key}/stats")
async def get_item_stats(
    item_key: int,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get the stats for a specific equipment item at a given item level.
    If no item level is provided, uses the base item level.
    """
    stmt = select(EquipmentItem).options(joinedload(EquipmentItem.stats)).where(EquipmentItem.key == item_key)
    result = db.execute(stmt)
    item = result.unique().scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {
        'key': item.key,
        'name': item.name,
        'ilvl': ilvl if ilvl is not None else item.base_ilvl,
        'stats': item.get_stats_at_ilvl(ilvl)
    }

@router.get("/equipment/{item_key}/concrete")
async def get_concrete_item(
    item_key: int,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a specific equipment item with concrete stat values at a given item level.
    Returns the item with stat_values array containing actual calculated values.
    """
    stmt = select(EquipmentItem).options(joinedload(EquipmentItem.stats)).where(EquipmentItem.key == item_key)
    result = db.execute(stmt)
    item = result.unique().scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get the concrete stat values at the specified level
    effective_ilvl = ilvl if ilvl is not None else item.base_ilvl
    
    # Build stat_values list preserving the original order from ItemStat.order
    stat_values = []
    for stat in item.stats:  # This is already ordered by ItemStat.order
        stat_values.append({
            'stat_name': stat.stat_name,
            'value': stat.get_value(effective_ilvl)
        })
    
    # Format the response to match what the frontend expects
    return {
        'key': item.key,
        'name': item.name,
        'ilvl': effective_ilvl,
        'stat_values': stat_values
    } 