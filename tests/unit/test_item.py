import unittest
from models.item import ItemDefinition, Item, ItemStat, ConcreteStat

class TestItemModels(unittest.TestCase):
    def setUp(self):
        """Set up test data that will be used across multiple tests."""
        self.test_stats = [
            ItemStat("VITALITY", 1879347271),
            ItemStat("CRITICAL_RATING", 1879211605)
        ]
        
        self.test_definition = ItemDefinition(
            key=1879480675,
            name="Test Item",
            min_ilvl=512,
            slot="NECK",
            quality="UNCOMMON",
            stats=self.test_stats,
            required_player_level=150
        )

    def test_item_definition_creation(self):
        """Test that ItemDefinition can be created with valid data."""
        self.assertEqual(self.test_definition.key, 1879480675)
        self.assertEqual(self.test_definition.name, "Test Item")
        self.assertEqual(self.test_definition.min_ilvl, 512)
        self.assertEqual(self.test_definition.slot, "NECK")
        self.assertEqual(self.test_definition.quality, "UNCOMMON")
        self.assertEqual(len(self.test_definition.stats), 2)
        self.assertEqual(self.test_definition.required_player_level, 150)

    def test_item_definition_to_dict(self):
        """Test that ItemDefinition can be converted to a dictionary."""
        item_dict = self.test_definition.to_dict()
        self.assertEqual(item_dict['key'], 1879480675)
        self.assertEqual(item_dict['name'], "Test Item")
        self.assertEqual(len(item_dict['stats']), 2)
        self.assertEqual(item_dict['stats'][0]['name'], "VITALITY")
        self.assertEqual(item_dict['stats'][0]['scaling_id'], 1879347271)

    def test_item_creation_valid_ilvl(self):
        """Test that Item can be created with a valid item level."""
        item = Item(self.test_definition, ilvl=514)
        self.assertEqual(item.ilvl, 514)
        self.assertEqual(len(item.stats), 2)
        # Stats should be calculated automatically
        self.assertTrue(all(isinstance(stat, ConcreteStat) for stat in item.stats))

    def test_item_creation_invalid_ilvl(self):
        """Test that Item creation fails with invalid item levels."""
        # Test below minimum ilvl
        with self.assertRaises(ValueError):
            Item(self.test_definition, ilvl=500)
        
        # Test above maximum ilvl (currently min_ilvl + 10)
        with self.assertRaises(ValueError):
            Item(self.test_definition, ilvl=523)

    def test_item_with_precalculated_stats(self):
        """Test that Item can be created with pre-calculated stats."""
        precalculated_stats = [
            ConcreteStat("VITALITY", 1500),
            ConcreteStat("CRITICAL_RATING", 1200)
        ]
        item = Item(self.test_definition, ilvl=514, stats=precalculated_stats)
        self.assertEqual(item.stats, precalculated_stats)

    def test_item_to_dict(self):
        """Test that Item can be converted to a dictionary."""
        item = Item(self.test_definition, ilvl=514)
        item_dict = item.to_dict()
        self.assertEqual(item_dict['key'], 1879480675)
        self.assertEqual(item_dict['ilvl'], 514)
        self.assertEqual(len(item_dict['stats']), 2)
        self.assertTrue(all('value' in stat for stat in item_dict['stats']))

if __name__ == '__main__':
    unittest.main() 