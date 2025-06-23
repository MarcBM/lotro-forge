"""
Enum for LOTRO item quality levels.
"""
from enum import Enum as PythonEnum


class ItemQuality(PythonEnum):
    """Enum for item quality levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    INCOMPARABLE = "incomparable"
    LEGENDARY = "legendary" 