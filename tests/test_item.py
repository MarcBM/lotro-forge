"""Test suite for the item models."""

import pytest
from models.item import ItemDefinition, ItemStat, Item, ConcreteStat

@pytest.fixture
def sample_item_def():
    """Create a sample item definition for testing."""
    return ItemDefinition(
        key=1879480675,
        name="Test Item",
        min_ilvl=512,
        slot="NECK",
        quality="UNCOMMON",
        stats=[
            ItemStat("VITALITY", 1879347271),
            ItemStat("CRITICAL_RATING", 1879211605)
        ],
        required_player_level=150,
        scaling="test_scaling",
        value_table_id=1879050115
    )

def test_item_definition_to_dict(sample_item_def):
    """Test converting ItemDefinition to dictionary."""
    item_dict = sample_item_def.to_dict()
    assert item_dict['key'] == 1879480675
    assert item_dict['name'] == "Test Item"
    assert item_dict['min_ilvl'] == 512
    assert item_dict['slot'] == "NECK"
    assert item_dict['quality'] == "UNCOMMON"
    assert len(item_dict['stats']) == 2
    assert item_dict['stats'][0] == {'name': 'VITALITY', 'scaling_id': 1879347271}
    assert item_dict['stats'][1] == {'name': 'CRITICAL_RATING', 'scaling_id': 1879211605}
    assert item_dict['required_player_level'] == 150
    assert item_dict['scaling'] == "test_scaling"
    assert item_dict['value_table_id'] == 1879050115

def test_item_definition_get_valid_ilvls(sample_item_def):
    """Test getting valid item levels."""
    min_ilvl, max_ilvl = sample_item_def.get_valid_ilvls()
    assert min_ilvl == 512
    assert max_ilvl == 522  # min_ilvl + 10 as per current implementation

def test_item_definition_calculate_stats(sample_item_def):
    """Test calculating stats at a specific item level."""
    stats = sample_item_def.calculate_stats_at_ilvl(514)
    assert len(stats) == 2
    assert stats[0].name == "VITALITY"
    assert stats[0].value == 300  # 100 * (514 - 512 + 1)
    assert stats[1].name == "CRITICAL_RATING"
    assert stats[1].value == 300

def test_item_creation_with_calculated_stats(sample_item_def):
    """Test creating an Item with automatically calculated stats."""
    item = Item(sample_item_def, ilvl=514)
    assert item.ilvl == 514
    assert len(item.stats) == 2
    assert item.stats[0].name == "VITALITY"
    assert item.stats[0].value == 300
    assert item.stats[1].name == "CRITICAL_RATING"
    assert item.stats[1].value == 300

def test_item_creation_with_precalculated_stats(sample_item_def):
    """Test creating an Item with pre-calculated stats."""
    precalculated_stats = [
        ConcreteStat("VITALITY", 1500),
        ConcreteStat("CRITICAL_RATING", 1200)
    ]
    item = Item(sample_item_def, ilvl=514, stats=precalculated_stats)
    assert item.ilvl == 514
    assert item.stats == precalculated_stats

def test_item_invalid_ilvl(sample_item_def):
    """Test creating an Item with invalid item level."""
    with pytest.raises(ValueError, match="Item level 500 is below minimum 512"):
        Item(sample_item_def, ilvl=500)
    
    with pytest.raises(ValueError, match="Item level 523 is above maximum 522"):
        Item(sample_item_def, ilvl=523)

def test_item_to_dict(sample_item_def):
    """Test converting Item to dictionary."""
    item = Item(sample_item_def, ilvl=514)
    item_dict = item.to_dict()
    assert item_dict['key'] == 1879480675
    assert item_dict['name'] == "Test Item"
    assert item_dict['ilvl'] == 514
    assert item_dict['slot'] == "NECK"
    assert item_dict['quality'] == "UNCOMMON"
    assert len(item_dict['stats']) == 2
    assert item_dict['stats'][0] == {'name': 'VITALITY', 'value': 300}
    assert item_dict['stats'][1] == {'name': 'CRITICAL_RATING', 'value': 300}
    assert item_dict['required_player_level'] == 150

def test_item_properties(sample_item_def):
    """Test Item property accessors."""
    item = Item(sample_item_def, ilvl=514)
    assert item.key == 1879480675
    assert item.name == "Test Item"
    assert item.slot == "NECK"
    assert item.quality == "UNCOMMON"
    assert item.required_player_level == 150 