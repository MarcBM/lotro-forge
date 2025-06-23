"""
Data API module for game data endpoints.

This module contains API endpoints for querying LOTRO game data including:
- Item Data
- Equipment Lists
- Essence Lists
- Future data types as the application grows
"""

from .equipment import router as equipment_router
from .items import router as items_router
from .essences import router as essences_router

__all__ = ["equipment_router", "items_router", "essences_router"] 