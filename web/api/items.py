"""
API endpoints for item operations.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError

from database.models.item import ItemDefinition, ItemStat
from database.config import get_database_url
from sqlalchemy import create_engine, select

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create a single engine instance
try:
    logger.info("Initializing database connection...")
    engine = create_engine(get_database_url())
    # Create a session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database connection: {e}")
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
        logger.info("Building items query...")
        # Build query with joinedload for item stats
        stmt = select(ItemDefinition).options(joinedload(ItemDefinition.stats))
        
        # Apply filters
        if slot:
            logger.debug(f"Filtering by slot: {slot}")
            stmt = stmt.where(ItemDefinition.slot == slot)
        if quality:
            logger.debug(f"Filtering by quality: {quality}")
            stmt = stmt.where(ItemDefinition.quality == quality)
        if min_level:
            logger.debug(f"Filtering by min_level: {min_level}")
            stmt = stmt.where(ItemDefinition.required_player_level >= min_level)
        if max_level:
            logger.debug(f"Filtering by max_level: {max_level}")
            stmt = stmt.where(ItemDefinition.required_player_level <= max_level)
        
        # Apply pagination
        logger.debug(f"Applying pagination: skip={skip}, limit={limit}")
        stmt = stmt.offset(skip).limit(limit)
        
        # Execute query
        logger.info("Executing items query...")
        items = db.execute(stmt).unique().scalars().all()
        logger.info(f"Found {len(items)} items")
        
        # Convert to dict for JSON response
        logger.debug("Converting items to dict...")
        result = [
            {
                # Item definition (base data)
                "key": item.key,
                "name": item.name,
                "base_ilvl": item.base_ilvl,
                "slot": item.slot,
                "quality": item.quality,
                "required_player_level": item.required_player_level,
                "scaling": item.scaling,
                # Stats with their progression table references
                "stats": [
                    {
                        "stat_name": stat.stat_name,
                        "value_table_id": stat.value_table_id
                    }
                    for stat in item.stats  # This preserves order
                ]
            }
            for item in items
        ]
        logger.info("Successfully converted items to dict")
        return result
        
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred: {str(e)}"
        )

@router.get("/{item_key}")
async def get_item(
    item_key: int,
    db: Session = Depends(get_db)
) -> dict:
    """Get a specific item by its key."""
    try:
        stmt = select(ItemDefinition).options(joinedload(ItemDefinition.stats)).where(ItemDefinition.key == item_key)
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
            "stats": [
                {
                    "stat_name": stat.stat_name,
                    "value": stat.get_value(item.base_ilvl)
                }
                for stat in item.stats
            ]
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        )

@router.get("/{item_key}/concrete")
async def get_concrete_item(
    item_key: int,
    ilvl: int = Query(..., ge=1, description="Item level to get concrete stats for"),
    db: Session = Depends(get_db)
) -> dict:
    """Get a concrete version of an item at a specific item level."""
    try:
        # Get the item definition
        stmt = select(ItemDefinition).options(joinedload(ItemDefinition.stats)).where(ItemDefinition.key == item_key)
        item = db.execute(stmt).unique().scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # Validate the item level
        min_ilvl, max_ilvl = item.get_valid_ilvls()
        if ilvl < min_ilvl:
            raise HTTPException(
                status_code=400,
                detail=f"Item level {ilvl} is below minimum {min_ilvl}"
            )
        if max_ilvl is not None and ilvl > max_ilvl:
            raise HTTPException(
                status_code=400,
                detail=f"Item level {ilvl} is above maximum {max_ilvl}"
            )
        
        # Get concrete stats at the requested level
        return {
            "key": item.key,
            "name": item.name,
            "ilvl": ilvl,
            "slot": item.slot,
            "quality": item.quality,
            "required_player_level": item.required_player_level,
            "stat_values": [
                {
                    "stat_name": stat.stat_name,
                    "value": stat.get_value(ilvl)
                }
                for stat in item.stats  # This preserves order
            ]
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred: {str(e)}"
        ) 