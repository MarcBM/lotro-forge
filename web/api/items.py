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
from database.models.dps import DpsTable
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
    item_type: Optional[str] = Query(None, description="Filter by item type (equipment, weapon)"),
    limit: int = Query(99, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> dict:
    """
    List all items with optional type filtering.
    Returns both items and total count.
    """
    # Build base query
    if item_type == "weapon":
        base_query = select(EquipmentItem).where(EquipmentItem.item_type == 'weapon')
        count_query = select(func.count(EquipmentItem.key)).where(EquipmentItem.item_type == 'weapon')
    elif item_type == "equipment":
        base_query = select(EquipmentItem).where(EquipmentItem.item_type != 'weapon')
        count_query = select(func.count(EquipmentItem.key)).where(EquipmentItem.item_type != 'weapon')
    else:
        # All equipment items (including weapons)
        base_query = select(EquipmentItem)
        count_query = select(func.count(EquipmentItem.key))
    
    # Get total count
    total_result = db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination and ordering
    paginated_query = base_query.order_by(EquipmentItem.name).offset(skip).limit(limit)
    result = db.execute(paginated_query)
    items = result.scalars().all()
    
    # Convert to dictionaries
    item_dicts = []
    for item in items:
        item_dict = item.to_dict()
        # Add icon URLs for frontend
        if item.icon:
            item_dict['icon_urls'] = get_icon_urls(request, item.icon)
        else:
            item_dict['icon_urls'] = []
        # Convert quality to uppercase for frontend
        item_dict['quality'] = item_dict['quality'].upper()
        item_dicts.append(item_dict)
    
    return {
        "items": item_dicts,
        "total": total
    }

@router.get("/equipment")
async def list_items(
    request: Request,
    slot: Optional[str] = None,
    quality: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    sort: Optional[str] = Query(None, description="Sort by: name, base_ilvl (default: recent/reverse key)"),
    limit: int = Query(99, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> dict:
    """
    List equipment items (including weapons) with optional filtering and pagination.
    Returns both items and total count.
    """
    # Build base query for filtering - this will include weapons polymorphically
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
    
    # Apply sorting
    if sort == "name":
        items_query = items_query.order_by(EquipmentItem.name)
    elif sort == "base_ilvl":
        items_query = items_query.order_by(EquipmentItem.base_ilvl.desc())
    else:
        # Default: recent (reverse key order)
        items_query = items_query.order_by(EquipmentItem.key.desc())
    
    items_query = items_query.offset(skip).limit(limit)
    
    # Execute items query - this will return EquipmentItem or Weapon objects based on polymorphism
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

@router.get("/equipment/slots")
async def get_equipment_slots(db: Session = Depends(get_db)) -> dict:
    """
    Get all distinct slots from the equipment table for filtering.
    Returns a list of slot values.
    """
    try:
        # Query for distinct slot values
        stmt = select(EquipmentItem.slot).distinct().order_by(EquipmentItem.slot)
        result = db.execute(stmt)
        slots = result.scalars().all()
        
        return {
            "slots": [slot for slot in slots if slot is not None]
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error getting equipment slots: {e}")
        raise HTTPException(status_code=500, detail="Database error") 

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
    Get a specific equipment item (including weapons) with concrete stat values at a given item level.
    Returns the item with stat_values array containing actual calculated values.
    For weapons, also includes calculated DPS.
    """
    # Query for EquipmentItem with eager loading - will return Weapon if it's a weapon due to polymorphism
    stmt = select(EquipmentItem).options(
        joinedload(EquipmentItem.stats)
    ).where(EquipmentItem.key == item_key)
    
    result = db.execute(stmt)
    item = result.unique().scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # If this is a weapon, we need to reload it with DPS table to get the relationship
    if hasattr(item, 'weapon_type') and item.weapon_type:
        # Import here to avoid circular imports
        from database.models.item import Weapon
        from database.models.dps import DpsTable
        weapon_stmt = select(Weapon).options(
            joinedload(Weapon.stats),
            joinedload(Weapon.dps_table)
        ).where(Weapon.key == item_key)
        weapon_result = db.execute(weapon_stmt)
        item = weapon_result.unique().scalar_one_or_none()
    
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
    response = {
        'key': item.key,
        'name': item.name,
        'ilvl': effective_ilvl,
        'stat_values': stat_values,
        'item_type': item.item_type
    }
    
    # If this is a weapon, add weapon-specific data
    if hasattr(item, 'weapon_type') and item.weapon_type:
        response.update({
            'weapon_type': item.weapon_type,
            'damage_type': item.damage_type,
            'min_damage': item.min_damage,
            'max_damage': item.max_damage,
            'dps': item.dps,
            'calculated_dps': item.get_dps_at_ilvl(effective_ilvl) if hasattr(item, 'get_dps_at_ilvl') else None
        })
    
    return response 