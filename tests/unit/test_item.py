"""
Unit tests for LOTRO Forge item models.

Tests the core functionality of Item, EquipmentItem, and ItemStat models.
"""
import pytest
from database.models import Item, EquipmentItem, Weapon, Essence, ItemStat, ItemQuality
from database.models import ProgressionTable, ProgressionValue, ProgressionType


@pytest.mark.unit
class TestItemModels:
    """Test suite for Item model and its subclasses."""
    
    def test_item_creation(self, db_session):
        """Test that a basic Item can be created with valid data."""
        item = Item(
            key=12345,
            name="Test Item",
            base_ilvl=500,
            quality=ItemQuality.UNCOMMON,
            item_type="item"
        )
        db_session.add(item)
        db_session.commit()
        
        assert item.key == 12345
        assert item.name == "Test Item"
        assert item.base_ilvl == 500
        assert item.quality == ItemQuality.UNCOMMON
        assert item.item_type == "item"
    
    def test_equipment_item_creation(self, db_session):
        """Test that an EquipmentItem can be created with equipment-specific fields."""
        item = EquipmentItem(
            key=67890,
            name="Test Necklace",
            base_ilvl=510,
            quality=ItemQuality.RARE,
            slot="NECK",
            armour_type=None,
            item_type="equipment"
        )
        db_session.add(item)
        db_session.commit()
        
        assert item.key == 67890
        assert item.slot == "NECK"
        assert item.quality == ItemQuality.RARE
        assert item.armour_type is None
    
    def test_weapon_creation(self, db_session):
        """Test that a Weapon can be created with weapon-specific fields."""
        weapon = Weapon(
            key=99999,
            name="Test Sword",
            base_ilvl=515,
            quality=ItemQuality.INCOMPARABLE,
            slot="MAIN_HAND",
            weapon_type="ONE_HANDED_SWORD",
            dps=150.5,
            min_damage=100,
            max_damage=200,
            damage_type="COMMON",
            item_type="weapon"
        )
        db_session.add(weapon)
        db_session.commit()
        
        assert weapon.weapon_type == "ONE_HANDED_SWORD"
        assert weapon.dps == 150.5
        assert weapon.min_damage == 100
        assert weapon.max_damage == 200
    
    def test_essence_creation(self, db_session):
        """Test that an Essence can be created with essence-specific fields."""
        essence = Essence(
            key=88888,
            name="Test Essence",
            base_ilvl=505,
            quality=ItemQuality.RARE,
            tier=7,
            essence_type=22,  # Primary
            item_type="essence"
        )
        db_session.add(essence)
        db_session.commit()
        
        assert essence.tier == 7
        assert essence.essence_type == 22
        assert essence.essence_type_name == "Primary"


@pytest.mark.unit
class TestItemStats:
    """Test suite for ItemStat functionality."""
    
    def test_item_stat_creation(self, db_session, sample_item):
        """Test that ItemStat can be created and linked to an item."""
        # sample_item fixture already creates an item with a stat
        item = sample_item
        
        assert len(item.stats) == 1
        stat = item.stats[0]
        assert stat.stat_name == "VITALITY"
        assert stat.value_table_id == sample_item.stats[0].value_table_id
        assert stat.order == 1
    
    def test_stat_value_calculation(self, db_session, sample_item):
        """Test that ItemStat can calculate values from progression tables."""
        item = sample_item
        stat = item.stats[0]
        
        # Test exact level match
        value_510 = stat.get_value(510)
        assert value_510 == 1100.0
        
        # Test missing level (should return 0)
        value_999 = stat.get_value(999)
        assert value_999 == 0.0
    
    def test_item_stats_at_ilvl(self, db_session, sample_item):
        """Test that Item can get all stat values at a specific level."""
        item = sample_item
        
        stats = item.get_stats_at_ilvl(510)
        assert "VITALITY" in stats
        assert stats["VITALITY"] == 1100.0
        
        # Test with base ilvl (default)
        stats_base = item.get_stats_at_ilvl()
        assert stats_base["VITALITY"] == 1100.0  # base_ilvl is 510


@pytest.mark.unit
class TestSocketParsing:
    """Test suite for socket parsing functionality in EquipmentItem."""
    
    def test_socket_string_parsing(self):
        """Test that socket strings are parsed correctly."""
        # Test letter-based socket string
        result = EquipmentItem.parse_socket_string("PVS")
        expected = {
            'basic': 1,      # S
            'primary': 1,    # P
            'vital': 1,      # V
            'cloak': 0,
            'necklace': 0,
            'pvp': 0
        }
        assert result == expected
        
        # Test multiple of same type
        result2 = EquipmentItem.parse_socket_string("PVSSS")
        expected2 = {
            'basic': 3,      # SSS
            'primary': 1,    # P
            'vital': 1,      # V
            'cloak': 0,
            'necklace': 0,
            'pvp': 0
        }
        assert result2 == expected2
        
        # Test empty/None
        result3 = EquipmentItem.parse_socket_string(None)
        expected3 = {
            'basic': 0,
            'primary': 0,
            'vital': 0,
            'cloak': 0,
            'necklace': 0,
            'pvp': 0
        }
        assert result3 == expected3
    
    def test_equipment_socket_properties(self, db_session):
        """Test socket-related properties on EquipmentItem."""
        item = EquipmentItem(
            key=77777,
            name="Test Armor",
            base_ilvl=505,
            quality=ItemQuality.RARE,
            slot="CHEST",
            sockets_basic=2,
            sockets_primary=1,
            sockets_vital=0,
            item_type="equipment"
        )
        db_session.add(item)
        db_session.commit()
        
        assert item.total_sockets == 3
        summary = item.socket_summary
        assert summary['basic'] == 2
        assert summary['primary'] == 1
        assert summary['vital'] == 0


@pytest.mark.unit
class TestItemDictSerialization:
    """Test suite for item dictionary serialization."""
    
    def test_item_to_dict_basic(self, db_session, sample_item):
        """Test basic item dictionary serialization."""
        item = sample_item
        item_dict = item.to_dict()
        
        assert item_dict['key'] == item.key
        assert item_dict['name'] == "Test Necklace"
        assert item_dict['base_ilvl'] == 510
        assert item_dict['quality'] == "uncommon"
        assert item_dict['item_type'] == "equipment"
        assert len(item_dict['stats']) == 1
        assert item_dict['stats'][0]['name'] == "VITALITY"
    
    def test_item_to_dict_with_ilvl(self, db_session, sample_item):
        """Test item dictionary serialization with specific item level."""
        item = sample_item
        item_dict = item.to_dict(ilvl=520)
        
        assert item_dict['ilvl'] == 520
        assert 'stat_values' in item_dict
        assert item_dict['stat_values']['VITALITY'] == 1200.0
    
    def test_weapon_to_dict(self, db_session):
        """Test weapon-specific dictionary serialization."""
        weapon = Weapon(
            key=11111,
            name="Test Bow",
            base_ilvl=512,
            quality=ItemQuality.LEGENDARY,
            slot="RANGED",
            weapon_type="BOW",
            dps=175.0,
            item_type="weapon"
        )
        db_session.add(weapon)
        db_session.commit()
        
        weapon_dict = weapon.to_dict()
        assert weapon_dict['weapon_type'] == "BOW"
        assert weapon_dict['dps'] == 175.0 