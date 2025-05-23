"""
API endpoints for item operations.
"""
import logging
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, create_engine, func
from enum import Enum

from database.models.item import Item, EquipmentItem, Essence, ItemStat
from database.models.dps import DpsTable
from database.config import get_database_url
from .services.ev_calculator import EVCalculator

class EquipmentSlot(Enum):
    """Equipment slot definitions for the builder and filtering."""
    
    # Jewelry Slots (top-left to bottom-right)
    LEFT_EAR = "LEFT_EAR"
    RIGHT_EAR = "RIGHT_EAR"
    NECK = "NECK"
    POCKET = "POCKET"
    LEFT_WRIST = "LEFT_WRIST"
    RIGHT_WRIST = "RIGHT_WRIST"
    LEFT_FINGER = "LEFT_FINGER"
    RIGHT_FINGER = "RIGHT_FINGER"
    
    # Armor Slots (top-left to bottom-right)
    HEAD = "HEAD"
    SHOULDERS = "SHOULDERS"
    BACK = "BACK"
    CHEST = "CHEST"
    HANDS = "HANDS"
    LEGS = "LEGS"
    FEET = "FEET"
    
    # Bottom Row Slots
    MAIN_HAND = "MAIN_HAND"
    OFF_HAND = "OFF_HAND"
    RANGED = "RANGED"
    CLASS = "CLASS"

# Equipment slot groupings for intelligent filtering
JEWELRY_SLOTS = {
    EquipmentSlot.LEFT_EAR.value, EquipmentSlot.RIGHT_EAR.value,
    EquipmentSlot.NECK.value, EquipmentSlot.POCKET.value,
    EquipmentSlot.LEFT_WRIST.value, EquipmentSlot.RIGHT_WRIST.value,
    EquipmentSlot.LEFT_FINGER.value, EquipmentSlot.RIGHT_FINGER.value
}

ARMOR_SLOTS = {
    EquipmentSlot.HEAD.value, EquipmentSlot.SHOULDERS.value,
    EquipmentSlot.BACK.value, EquipmentSlot.CHEST.value,
    EquipmentSlot.HANDS.value, EquipmentSlot.LEGS.value,
    EquipmentSlot.FEET.value
}

WEAPON_SLOTS = {
    EquipmentSlot.MAIN_HAND.value, EquipmentSlot.OFF_HAND.value,
    EquipmentSlot.RANGED.value
}

CLASS_SLOTS = {
    EquipmentSlot.CLASS.value
}

# Database slot to builder slot mapping
# Maps what slot value exists in the database to which builder slots it can equip in
DATABASE_TO_BUILDER_SLOTS = {
    'EAR': [EquipmentSlot.LEFT_EAR.value, EquipmentSlot.RIGHT_EAR.value],
    'NECK': [EquipmentSlot.NECK.value],
    'WRIST': [EquipmentSlot.LEFT_WRIST.value, EquipmentSlot.RIGHT_WRIST.value],
    'FINGER': [EquipmentSlot.LEFT_FINGER.value, EquipmentSlot.RIGHT_FINGER.value],
    'POCKET': [EquipmentSlot.POCKET.value],
    'HEAD': [EquipmentSlot.HEAD.value],
    'SHOULDER': [EquipmentSlot.SHOULDERS.value],
    'BACK': [EquipmentSlot.BACK.value],
    'CHEST': [EquipmentSlot.CHEST.value],
    'HAND': [EquipmentSlot.HANDS.value],
    'LEGS': [EquipmentSlot.LEGS.value],
    'FEET': [EquipmentSlot.FEET.value],
    'EITHER_HAND': [EquipmentSlot.MAIN_HAND.value, EquipmentSlot.OFF_HAND.value],
    'MAIN_HAND': [EquipmentSlot.MAIN_HAND.value],
    'OFF_HAND': [EquipmentSlot.OFF_HAND.value],
    'RANGED_ITEM': [EquipmentSlot.RANGED.value],
    'CLASS_SLOT': [EquipmentSlot.CLASS.value]
}

# Filter bucket definitions - maps builder slot filters to database slots they should include
# This determines what database slots to query when filtering by a builder slot
FILTER_BUCKETS = {
    # General buckets (show items that can equip in either specific slot)
    'EAR': ['EAR', 'LEFT_EAR', 'RIGHT_EAR'],
    'WRIST': ['WRIST', 'LEFT_WRIST', 'RIGHT_WRIST'], 
    'FINGER': ['FINGER', 'LEFT_FINGER', 'RIGHT_FINGER'],
    
    # Specific builder slots
    EquipmentSlot.LEFT_EAR.value: ['EAR', 'LEFT_EAR'],  # Items with EAR or LEFT_EAR can go in left ear
    EquipmentSlot.RIGHT_EAR.value: ['EAR', 'RIGHT_EAR'],  # Items with EAR or RIGHT_EAR can go in right ear
    EquipmentSlot.NECK.value: ['NECK'],
    EquipmentSlot.LEFT_WRIST.value: ['WRIST', 'LEFT_WRIST'],  # Items with WRIST or LEFT_WRIST can go in left wrist
    EquipmentSlot.RIGHT_WRIST.value: ['WRIST', 'RIGHT_WRIST'],  # Items with WRIST or RIGHT_WRIST can go in right wrist
    EquipmentSlot.LEFT_FINGER.value: ['FINGER', 'LEFT_FINGER'],  # Items with FINGER or LEFT_FINGER can go in left finger
    EquipmentSlot.RIGHT_FINGER.value: ['FINGER', 'RIGHT_FINGER'],  # Items with FINGER or RIGHT_FINGER can go in right finger
    EquipmentSlot.POCKET.value: ['POCKET'],
    EquipmentSlot.HEAD.value: ['HEAD'],
    EquipmentSlot.SHOULDERS.value: ['SHOULDER'],
    EquipmentSlot.BACK.value: ['BACK'],
    EquipmentSlot.CHEST.value: ['CHEST'],
    EquipmentSlot.HANDS.value: ['HAND'],
    EquipmentSlot.LEGS.value: ['LEGS'],
    EquipmentSlot.FEET.value: ['FEET'],
    EquipmentSlot.MAIN_HAND.value: ['EITHER_HAND', 'MAIN_HAND'],  # Items with either slot can go in main hand
    EquipmentSlot.OFF_HAND.value: ['EITHER_HAND', 'OFF_HAND'],  # Items with either slot can go in off hand
    EquipmentSlot.RANGED.value: ['RANGED_ITEM'],
    EquipmentSlot.CLASS.value: ['CLASS_SLOT']
}

# Ordered filter options for the equipment panel dropdown
FILTER_OPTIONS = [
    {'key': 'EAR', 'label': 'Ear'},
    {'key': EquipmentSlot.LEFT_EAR.value, 'label': 'Left Ear'},
    {'key': EquipmentSlot.RIGHT_EAR.value, 'label': 'Right Ear'},
    {'key': EquipmentSlot.NECK.value, 'label': 'Neck'},
    {'key': 'WRIST', 'label': 'Wrist'},
    {'key': EquipmentSlot.LEFT_WRIST.value, 'label': 'Left Wrist'},
    {'key': EquipmentSlot.RIGHT_WRIST.value, 'label': 'Right Wrist'},
    {'key': 'FINGER', 'label': 'Finger'},
    {'key': EquipmentSlot.LEFT_FINGER.value, 'label': 'Left Finger'},
    {'key': EquipmentSlot.RIGHT_FINGER.value, 'label': 'Right Finger'},
    {'key': EquipmentSlot.POCKET.value, 'label': 'Pocket'},
    {'key': EquipmentSlot.HEAD.value, 'label': 'Head'},
    {'key': EquipmentSlot.SHOULDERS.value, 'label': 'Shoulders'},
    {'key': EquipmentSlot.BACK.value, 'label': 'Back'},
    {'key': EquipmentSlot.CHEST.value, 'label': 'Chest'},
    {'key': EquipmentSlot.HANDS.value, 'label': 'Hands'},
    {'key': EquipmentSlot.LEGS.value, 'label': 'Legs'},
    {'key': EquipmentSlot.FEET.value, 'label': 'Feet'},
    {'key': EquipmentSlot.MAIN_HAND.value, 'label': 'Main Hand'},
    {'key': EquipmentSlot.OFF_HAND.value, 'label': 'Off Hand'},
    {'key': EquipmentSlot.RANGED.value, 'label': 'Ranged'},
    {'key': EquipmentSlot.CLASS.value, 'label': 'Class'}
]

def get_compatible_database_slots(builder_slot: str) -> List[str]:
    """
    Get the database slot values that are compatible with a given builder slot.
    
    Args:
        builder_slot: The builder slot name (e.g., 'LEFT_EAR', 'MAIN_HAND')
        
    Returns:
        List of database slot values that can equip in the builder slot
    """
    compatible_slots = FILTER_BUCKETS.get(builder_slot, [])
    logger.debug(f"Builder slot '{builder_slot}' maps to database slots: {compatible_slots}")
    return compatible_slots

def get_builder_slots_for_item(database_slot: str) -> List[str]:
    """
    Get the builder slot values where an item with the given database slot can be equipped.
    
    Args:
        database_slot: The database slot value (e.g., 'EAR', 'EITHER_HAND')
        
    Returns:
        List of builder slot values where the item can be equipped
    """
    builder_slots = DATABASE_TO_BUILDER_SLOTS.get(database_slot, [])
    logger.debug(f"Database slot '{database_slot}' can equip in builder slots: {builder_slots}")
    return builder_slots

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
    sort: Optional[str] = Query(None, description="Sort by: name, base_ilvl, ev (default: recent/reverse key)"),
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
        # Use intelligent filtering - get database slots compatible with the requested builder slot
        compatible_slots = get_compatible_database_slots(slot)
        if compatible_slots:
            logger.debug(f"Filtering equipment for builder slot '{slot}' using database slots: {compatible_slots}")
            base_query = base_query.where(EquipmentItem.slot.in_(compatible_slots))
        else:
            # Fallback to direct slot matching if no mapping found
            logger.debug(f"No mapping found for slot '{slot}', using direct slot match")
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
    
    # Build query for items with joins
    items_query = base_query.options(joinedload(EquipmentItem.stats))
    
    # For EV sorting, we need to get ALL matching items to sort properly
    if sort == "ev":
        # Get all matching items (no pagination yet)
        all_items_result = db.execute(items_query)
        all_items = all_items_result.unique().scalars().all()
        
        # Initialize EV calculator
        ev_calculator = EVCalculator(db)
        
        # Calculate EV for all items and create processed items list
        processed_items = []
        for item in all_items:
            item_dict = item.to_dict()
            # Convert quality to uppercase for frontend
            item_dict['quality'] = item_dict['quality'].upper()
            # Convert icon to icon_urls
            item_dict['icon_urls'] = get_icon_urls(request, item_dict.get('icon'))
            # Remove the raw icon field
            item_dict.pop('icon', None)
            
            # Calculate EV for this item at its base level
            try:
                # Get concrete stat values at base level
                stat_values = []
                for stat in item.stats:
                    stat_values.append({
                        'stat_name': stat.stat_name,
                        'value': stat.get_value(item.base_ilvl)
                    })
                
                # Calculate EV including sockets
                ev_score = ev_calculator.calculate_equipment_ev(stat_values, item.socket_summary)
                item_dict['ev'] = f"{ev_score:.2f}"
                item_dict['ev_numeric'] = ev_score  # For sorting
            except Exception as e:
                logger.warning(f"Failed to calculate EV for item {item.key}: {e}")
                item_dict['ev'] = "0.00"
                item_dict['ev_numeric'] = 0.0
            
            processed_items.append(item_dict)
        
        # Sort all items by EV
        processed_items.sort(key=lambda x: x['ev_numeric'], reverse=True)
        
        # Apply pagination to the sorted results
        paginated_items = processed_items[skip:skip + limit]
        
        # Remove the temporary ev_numeric field
        for item in paginated_items:
            item.pop('ev_numeric', None)
            
        return {
            "items": paginated_items,
            "total": total_count,
            "limit": limit,
            "skip": skip
        }
    
    else:
        # For non-EV sorting, use database-level sorting and pagination as before
        # Apply database-level sorting
        if sort == "name":
            items_query = items_query.order_by(EquipmentItem.name)
        elif sort == "base_ilvl":
            items_query = items_query.order_by(EquipmentItem.base_ilvl.desc())
        else:
            # Default: recent (reverse key order)
            items_query = items_query.order_by(EquipmentItem.key.desc())
        
        items_query = items_query.offset(skip).limit(limit)
        
        # Execute items query
        result = db.execute(items_query)
        items = result.unique().scalars().all()
        
        # Initialize EV calculator
        ev_calculator = EVCalculator(db)
        
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
            
            # Calculate EV for this item at its base level
            try:
                # Get concrete stat values at base level
                stat_values = []
                for stat in item.stats:
                    stat_values.append({
                        'stat_name': stat.stat_name,
                        'value': stat.get_value(item.base_ilvl)
                    })
                
                # Calculate EV including sockets
                ev_score = ev_calculator.calculate_equipment_ev(stat_values, item.socket_summary)
                item_dict['ev'] = f"{ev_score:.2f}"
            except Exception as e:
                logger.warning(f"Failed to calculate EV for item {item.key}: {e}")
                item_dict['ev'] = "0.00"
            
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

@router.get("/equipment/filter-options")
async def get_equipment_filter_options() -> dict:
    """
    Get the ordered filter options for the equipment panel dropdown.
    Returns filter buckets with their keys and display labels.
    """
    return {
        "filter_options": FILTER_OPTIONS
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
    
    # Calculate EV for this item at the effective level
    ev_calculator = EVCalculator(db)
    try:
        ev_score = ev_calculator.calculate_equipment_ev(stat_values, item.socket_summary)
        ev_string = f"{ev_score:.2f}"
    except Exception as e:
        logger.warning(f"Failed to calculate EV for item {item.key} at ilvl {effective_ilvl}: {e}")
        ev_string = "0.00"
    
    # Format the response to match what the frontend expects
    response = {
        'key': item.key,
        'name': item.name,
        'ilvl': effective_ilvl,
        'stat_values': stat_values,
        'item_type': item.item_type,
        'sockets': item.socket_summary,  # Add socket information
        'ev': ev_string  # Add calculated EV
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

@router.get("/essences")
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
    
    # Apply filters to base query
    if ilvl is not None:
        base_query = base_query.where(Essence.base_ilvl == ilvl)
    if essence_type is not None:
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
    
    # Build query for essences with pagination and joins
    essences_query = base_query.options(joinedload(Essence.stats))
    
    # Apply sorting
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

@router.get("/essences/tiers")
async def get_essence_tiers(db: Session = Depends(get_db)) -> dict:
    """
    Get all distinct tiers from the essences table for filtering.
    Returns a list of tier values.
    """
    try:
        # Query for distinct tier values
        stmt = select(Essence.tier).distinct().order_by(Essence.tier)
        result = db.execute(stmt)
        tiers = result.scalars().all()
        
        return {
            "tiers": [tier for tier in tiers if tier is not None]
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error getting essence tiers: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/essences/types")
async def get_essence_types(db: Session = Depends(get_db)) -> dict:
    """
    Get all distinct essence types from the essences table for filtering.
    Returns a list of essence type objects with id and name.
    """
    try:
        # Query for distinct essence_type values
        stmt = select(Essence.essence_type).distinct().order_by(Essence.essence_type)
        result = db.execute(stmt)
        type_ids = result.scalars().all()
        
        # Convert to objects with readable names using the model mapping
        type_objects = []
        for type_id in type_ids:
            if type_id is not None:
                name = Essence.ESSENCE_TYPE_NAMES.get(type_id, f'Unknown ({type_id})')
                type_objects.append({
                    'id': type_id,
                    'name': name
                })
        
        return {
            "types": type_objects
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error getting essence types: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/essences/levels")
async def get_essence_levels(db: Session = Depends(get_db)) -> dict:
    """
    Get all distinct item levels from the essences table for filtering.
    Returns a list of item level values.
    """
    try:
        # Query for distinct base_ilvl values
        stmt = select(Essence.base_ilvl).distinct().order_by(Essence.base_ilvl)
        result = db.execute(stmt)
        levels = result.scalars().all()
        
        return {
            "levels": [level for level in levels if level is not None]
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error getting essence levels: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/essences/{essence_key}")
async def get_essence(
    essence_key: int,
    request: Request,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a specific essence by its key.
    Optionally specify an item level to get concrete stat values.
    """
    stmt = select(Essence).options(joinedload(Essence.stats)).where(Essence.key == essence_key)
    result = db.execute(stmt)
    essence = result.unique().scalar_one_or_none()
    
    if not essence:
        raise HTTPException(status_code=404, detail="Essence not found")
    
    essence_dict = essence.to_dict(ilvl)
    # Convert quality to uppercase for frontend
    essence_dict['quality'] = essence_dict['quality'].upper()
    # Convert icon to icon_urls
    essence_dict['icon_urls'] = get_icon_urls(request, essence_dict.get('icon'))
    # Remove the raw icon field
    essence_dict.pop('icon', None)
    
    return essence_dict

@router.get("/essences/{essence_key}/concrete")
async def get_concrete_essence(
    essence_key: int,
    ilvl: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a specific essence with concrete stat values at a given item level.
    Returns the essence with stat_values array containing actual calculated values.
    """
    stmt = select(Essence).options(joinedload(Essence.stats)).where(Essence.key == essence_key)
    result = db.execute(stmt)
    essence = result.unique().scalar_one_or_none()
    
    if not essence:
        raise HTTPException(status_code=404, detail="Essence not found")
    
    # Get the concrete stat values at the specified level
    effective_ilvl = ilvl if ilvl is not None else essence.base_ilvl
    
    # Build stat_values list preserving the original order from ItemStat.order
    stat_values = []
    for stat in essence.stats:  # This is already ordered by ItemStat.order
        stat_values.append({
            'stat_name': stat.stat_name,
            'value': stat.get_value(effective_ilvl)
        })
    
    # Format the response to match what the frontend expects
    response = {
        'key': essence.key,
        'name': essence.name,
        'ilvl': effective_ilvl,
        'stat_values': stat_values,
        'item_type': essence.item_type,
        'tier': essence.tier,
        'essence_type': essence.essence_type
    }
    
    return response 