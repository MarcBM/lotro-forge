"""
API endpoints for equipment operations.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from database.session import SessionLocal
from database.models.item import EquipmentItem

# Create router
router = APIRouter()

# Database session dependency
def get_db():
    """Get a database session."""
    with SessionLocal() as session:
        yield session

# Slot grouping configuration
SLOT_GROUPS = {
    "Ear": ["EAR", "LEFT_EAR", "RIGHT_EAR"],
    "Neck": ["NECK"],
    "Pocket": ["POCKET"],
    "Wrist": ["WRIST", "LEFT_WRIST", "RIGHT_WRIST"],
    "Finger": ["FINGER", "LEFT_FINGER", "RIGHT_FINGER"],
    "Head": ["HEAD"],
    "Shoulder": ["SHOULDER"],
    "Back": ["BACK"],
    "Chest": ["CHEST"],
    "Hands": ["HANDS"],
    "Legs": ["LEGS"],
    "Feet": ["FEET"],
    "Main Hand": ["MAIN_HAND", "EITHER_HAND"],
    "Off Hand": ["OFF_HAND", "EITHER_HAND"],
    "Ranged Item": ["RANGED_ITEM"],
    "Class Slot": ["CLASS_SLOT"]
}

# Ordered list for consistent display
SLOT_GROUP_ORDER = [
    "Ear", "Neck", "Pocket", "Wrist", "Finger", 
    "Head", "Shoulder", "Back", "Chest", "Hands", "Legs", "Feet",
    "Main Hand", "Off Hand", "Ranged Item", "Class Slot"
]

@router.get("/slots")
async def get_equipment_slots(db: Session = Depends(get_db)):
    """
    Get organized equipment slot groups for filtering.
    Returns grouped slots in a specific order for the database panel.
    """
    try:
        # Query for all unique slot values from the database
        unique_slots_result = db.query(distinct(EquipmentItem.slot)).all()
        unique_slots = {slot[0] for slot in unique_slots_result if slot[0]}
        
        # Build filter options based on groups that have items in the database
        filter_options = []
        
        for group_name in SLOT_GROUP_ORDER:
            group_slots = SLOT_GROUPS[group_name]
            # Check if any slots in this group exist in the database
            matching_slots = [slot for slot in group_slots if slot in unique_slots]
            if matching_slots:
                filter_options.append({
                    "key": group_name.upper().replace(" ", "_"),  # e.g., "MAIN_HAND"
                    "label": group_name,  # e.g., "Main Hand"
                    "slots": group_slots  # The actual database slots this group represents
                })
        
        return {"slots": filter_options}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch equipment slots")

@router.get("/")
async def get_equipment(
    limit: int = Query(99, ge=1, le=99, description="Number of items to return"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    slot_group: Optional[str] = Query(None, description="Slot group filter (e.g., 'EAR', 'MAIN_HAND')"),
    sort: str = Query("recent", description="Sort by: recent, name, base_ilvl"),
    db: Session = Depends(get_db)
):
    """
    Get equipment items with filtering, sorting, and pagination.
    """
    try:
        # Start with base query for equipment items
        query = db.query(EquipmentItem)
        
        # Apply slot group filtering if specified
        if slot_group:
            # Find the corresponding slot group configuration
            group_name = None
            for name, config in SLOT_GROUPS.items():
                if name.upper().replace(" ", "_") == slot_group.upper():
                    group_name = name
                    break
            
            if group_name and group_name in SLOT_GROUPS:
                allowed_slots = SLOT_GROUPS[group_name]
                query = query.filter(EquipmentItem.slot.in_(allowed_slots))
            else:
                pass
        
        # Apply sorting
        if sort == "name":
            query = query.order_by(EquipmentItem.name.asc())
        elif sort == "base_ilvl":
            query = query.order_by(EquipmentItem.base_ilvl.desc())
        else:  # recent or default
            query = query.order_by(EquipmentItem.key.desc())
        
        # Get total count for pagination info
        total_count = query.count()
        
        # Apply pagination
        equipment_items = query.offset(skip).limit(limit).all()
        
        # Convert to dictionary format with proper icon processing
        equipment_data = []
        for item in equipment_items:
            # Process icon URLs
            icon_urls = []
            if item.icon:
                # Split hyphen-separated icon IDs and convert to URLs
                icon_ids = item.icon.split('-')
                icon_urls = [f"/static/icons/items/{icon_id}.png" for icon_id in icon_ids if icon_id]
            
            item_dict = {
                "key": item.key,
                "name": item.name,
                "base_ilvl": item.base_ilvl,
                "quality": item.quality.value.upper(),  # Convert to uppercase for template compatibility
                "slot": item.slot,
                "armour_type": item.armour_type,
                "icon_urls": icon_urls
            }
            
            # Add weapon-specific data if it's a weapon
            if hasattr(item, 'weapon_type') and item.weapon_type:
                item_dict["weapon_type"] = item.weapon_type
                item_dict["dps"] = item.dps
            
            # Add socket information
            total_sockets = (item.sockets_basic + item.sockets_primary + item.sockets_vital + 
                           item.sockets_cloak + item.sockets_necklace + item.sockets_pvp)
            if total_sockets > 0:
                item_dict["sockets"] = {
                    "total": total_sockets,
                    "basic": item.sockets_basic,
                    "primary": item.sockets_primary,
                    "vital": item.sockets_vital,
                    "cloak": item.sockets_cloak,
                    "necklace": item.sockets_necklace,
                    "pvp": item.sockets_pvp
                }
            
            equipment_data.append(item_dict)
        
        return {
            "equipment": equipment_data,
            "total": total_count,
            "limit": limit,
            "skip": skip,
            "has_more": skip + len(equipment_data) < total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch equipment")

@router.get("/{equipment_key}/concrete")
async def get_concrete_equipment(
    equipment_key: int,
    ilvl: int = Query(..., description="Item level for concrete stats"),
    db: Session = Depends(get_db)
):
    """
    Get concrete equipment details with stats calculated at a specific item level.
    """
    try:
        # Get the equipment item
        equipment = db.query(EquipmentItem).filter(EquipmentItem.key == equipment_key).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        # Calculate concrete stats at the specified item level
        stat_values = []
        for stat in equipment.stats:
            stat_value = stat.get_value(ilvl)
            stat_values.append({
                'stat_name': stat.stat_name,
                'value': stat_value
            })
        
        # Prepare socket summary
        socket_summary = {
            'basic': equipment.sockets_basic,
            'primary': equipment.sockets_primary,
            'vital': equipment.sockets_vital,
            'cloak': equipment.sockets_cloak,
            'necklace': equipment.sockets_necklace,
            'pvp': equipment.sockets_pvp
        }
        
        # Calculate DPS for weapons
        calculated_dps = None
        if hasattr(equipment, 'weapon_type') and equipment.weapon_type:
            if hasattr(equipment, 'get_dps_at_ilvl'):
                calculated_dps = equipment.get_dps_at_ilvl(ilvl)
            elif equipment.dps:
                # Fallback to base DPS if no scaling available
                calculated_dps = equipment.dps
        
        # Build response
        concrete_data = {
            'key': equipment.key,
            'name': equipment.name,
            'ilvl': ilvl,
            'base_ilvl': equipment.base_ilvl,
            'quality': equipment.quality.value.upper(),
            'slot': equipment.slot,
            'armour_type': equipment.armour_type,
            'stat_values': stat_values,
            'sockets': socket_summary if sum(socket_summary.values()) > 0 else None,
            'calculated_dps': calculated_dps
        }
        
        # Add weapon-specific data
        if hasattr(equipment, 'weapon_type') and equipment.weapon_type:
            concrete_data['weapon_type'] = equipment.weapon_type
            concrete_data['damage_type'] = equipment.damage_type
            concrete_data['min_damage'] = equipment.min_damage
            concrete_data['max_damage'] = equipment.max_damage
        
        return concrete_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch concrete equipment")

# TODO: Add more equipment endpoints here 