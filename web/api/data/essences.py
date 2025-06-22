"""
API endpoints for essence operations.
"""
import logging
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, create_engine, func

from database.models.item import Item, Essence, ItemStat
from database.session import SessionLocal

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Database session dependency
def get_db():
    """Get a database session."""
    with SessionLocal() as session:
        yield session

def get_icon_urls(request: Request, icon_ids: Optional[str]) -> Optional[List[str]]:
    """Convert icon IDs to full URLs."""
    if not icon_ids:
        return None
        
    base_url = str(request.base_url).rstrip('/')
    return [
        f"{base_url}/static/icons/items/{icon_id}.png"
        for icon_id in icon_ids.split('-')
    ]

@router.get("/")
async def list_essences(
    request: Request,
    ilvl: Optional[int] = Query(None, description="Filter by item level"),
    essence_type: Optional[int] = Query(None, description="Filter by essence type"),
    quality: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    sort: Optional[str] = Query(None, description="Sort by: name, base_ilvl (default: recent/reverse key)"),
    limit: int = Query(99, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> dict:
    """
    List essences with optional filtering and pagination.
    Returns both essences and total count.
    """
    # Build base query for filtering
    base_query = select(Essence)
    
    # Apply filters
    if ilvl:
        base_query = base_query.where(Essence.base_ilvl == ilvl)
    if essence_type:
        base_query = base_query.where(Essence.essence_type == essence_type)
    if quality:
        base_query = base_query.where(Essence.quality == quality)
    if min_level:
        base_query = base_query.where(Essence.base_ilvl >= min_level)
    if max_level:
        base_query = base_query.where(Essence.base_ilvl <= max_level)
    
    # Get total count (without pagination)
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = db.execute(count_query)
    total_count = total_result.scalar()
    
    # Build query for essences with joins
    essences_query = base_query.options(joinedload(Essence.stats))
    
    # Apply database-level sorting
    if sort == "name":
        essences_query = essences_query.order_by(Essence.name)
    elif sort == "base_ilvl":
        essences_query = essences_query.order_by(Essence.base_ilvl.desc())
    else:
        # Default: recent (reverse key order)
        essences_query = essences_query.order_by(Essence.key.desc())
    
    essences_query = essences_query.offset(skip).limit(limit)
    
    # Execute essences query
    result = db.execute(essences_query)
    essences = result.unique().scalars().all()
    
    # Convert to dict and process for frontend
    processed_essences = []
    for essence in essences:
        essence_dict = essence.to_dict()
        # Convert quality to uppercase for frontend
        essence_dict['quality'] = essence_dict['quality'].upper()
        # Convert icon to icon_urls
        essence_dict['icon_urls'] = get_icon_urls(request, essence_dict.get('icon'))
        # Remove the raw icon field
        essence_dict.pop('icon', None)
        
        processed_essences.append(essence_dict)
    
    return {
        "essences": processed_essences,
        "total": total_count,
        "limit": limit,
        "skip": skip
    }

@router.get("/tiers")
async def get_essence_tiers(db: Session = Depends(get_db)) -> dict:
    """Get all available essence tiers from the database."""
    try:
        result = db.execute(select(Essence.tier).distinct().where(Essence.tier.isnot(None)))
        tiers = sorted([row[0] for row in result.fetchall()])
        return {"tiers": tiers}
    except Exception as e:
        logger.error(f"Error fetching essence tiers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch essence tiers")

@router.get("/types")
async def get_essence_types(db: Session = Depends(get_db)) -> dict:
    """Get all available essence types from the database."""
    try:
        result = db.execute(select(Essence.essence_type).distinct().where(Essence.essence_type.isnot(None)))
        types = sorted([row[0] for row in result.fetchall()])
        return {"types": types}
    except Exception as e:
        logger.error(f"Error fetching essence types: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch essence types")

@router.get("/levels")
async def get_essence_levels(db: Session = Depends(get_db)) -> dict:
    """Get all available essence levels from the database."""
    try:
        result = db.execute(select(Essence.base_ilvl).distinct().order_by(Essence.base_ilvl))
        levels = [row[0] for row in result.fetchall()]
        return {"levels": levels}
    except Exception as e:
        logger.error(f"Error fetching essence levels: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch essence levels")

@router.get("/{essence_key}")
async def get_essence(
    essence_key: int,
    request: Request,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Get a specific essence by key."""
    result = db.execute(
        select(Essence)
        .options(joinedload(Essence.stats))
        .where(Essence.key == essence_key)
    )
    essence = result.unique().scalar_one_or_none()
    
    if not essence:
        raise HTTPException(status_code=404, detail="Essence not found")
    
    essence_dict = essence.to_dict()
    essence_dict['quality'] = essence_dict['quality'].upper()
    essence_dict['icon_urls'] = get_icon_urls(request, essence_dict.get('icon'))
    essence_dict.pop('icon', None)
    
    return essence_dict

@router.get("/{essence_key}/concrete")
async def get_concrete_essence(
    essence_key: int,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Get a concrete essence with calculated stats at specified item level."""
    result = db.execute(
        select(Essence)
        .options(joinedload(Essence.stats))
        .where(Essence.key == essence_key)
    )
    essence = result.unique().scalar_one_or_none()
    
    if not essence:
        raise HTTPException(status_code=404, detail="Essence not found")
    
    target_ilvl = ilvl or essence.base_ilvl
    
    # Create concrete essence dict
    concrete_essence = {
        'key': essence.key,
        'name': essence.name,
        'ilvl': target_ilvl,
        'quality': essence.quality.upper(),
        'essence_type': essence.essence_type,
        'tier': essence.tier,
        'stats': []
    }
    
    # Calculate concrete stats
    for stat in essence.stats:
        concrete_essence['stats'].append({
            'stat_name': stat.stat_name,
            'value': stat.get_value(target_ilvl)
        })
    
    return concrete_essence 