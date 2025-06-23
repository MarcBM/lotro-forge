"""
Simple unit tests for LOTRO Forge models without database dependencies.

Tests basic functionality that doesn't require database connections.
"""
import pytest

@pytest.mark.unit
def test_item_quality_enum():
    """Test that we can import and use the ItemQuality enum."""
    from database.models.items import ItemQuality
    
    # Test enum values
    assert ItemQuality.COMMON.value == "common"
    assert ItemQuality.UNCOMMON.value == "uncommon"
    assert ItemQuality.RARE.value == "rare"
    assert ItemQuality.INCOMPARABLE.value == "incomparable"
    assert ItemQuality.LEGENDARY.value == "legendary"
    
    # Test enum comparison
    assert ItemQuality.LEGENDARY != ItemQuality.COMMON

@pytest.mark.unit
def test_socket_string_parsing():
    """Test socket string parsing without database."""
    from database.models.items import EquipmentItem
    
    # Test static method without creating instances
    result = EquipmentItem.parse_socket_string("PVS")
    expected = {
        'basic': 1,
        'primary': 1,
        'vital': 1,
        'cloak': 0,
        'necklace': 0,
        'pvp': 0
    }
    assert result == expected
    
    # Test empty string
    result_empty = EquipmentItem.parse_socket_string(None)
    assert all(count == 0 for count in result_empty.values())

@pytest.mark.unit
def test_essence_type_names():
    """Test essence type name mapping."""
    from database.models.items import Essence
    
    # Test static mapping
    assert Essence.ESSENCE_TYPE_NAMES[1] == 'Basic'
    assert Essence.ESSENCE_TYPE_NAMES[22] == 'Primary'
    assert Essence.ESSENCE_TYPE_NAMES[23] == 'Vital'

# These tests are duplicates but with different names for variety
@pytest.mark.unit
def test_models_can_import():
    """Test that our models can be imported successfully."""
    test_item_quality_enum()

@pytest.mark.unit  
def test_socket_parsing_works():
    """Test that socket parsing functionality works."""
    test_socket_string_parsing()

@pytest.mark.unit
def test_essence_mappings_work():
    """Test that essence type mappings work."""
    test_essence_type_names() 