"""Test suite for the ItemParser class."""

import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
from parsers.item_parser import ItemParser
from models.item import ItemDefinition, ItemStat

@pytest.mark.parser
class TestItemParser:
    """Test suite for the ItemParser class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        # Valid item XML
        self.valid_item_xml = '''
        <item key="1879480675" name="Chipped Bright Umbari Necklace" level="512" 
              slot="NECK" quality="UNCOMMON" minLevel="150" 
              scaling="ze_skirmish_level#141-:1879471052;2:0.3" 
              valueTableId="1879050115">
            <stats>
                <stat name="VITALITY" scaling="1879347271"/>
                <stat name="CRITICAL_RATING" scaling="1879211605"/>
                <stat name="FINESSE" scaling="1879211717"/>
            </stats>
        </item>
        '''
        
        # Valid item with minimal attributes
        self.minimal_item_xml = '''
        <item key="1879480676" name="Minimal Item" level="1" 
              slot="NECK" quality="COMMON" minLevel="1">
            <stats>
                <stat name="VITALITY" scaling="1879347271"/>
            </stats>
        </item>
        '''
        
        # Invalid item XML (missing required attributes)
        self.invalid_item_xml = '''
        <item key="1879480677" name="Invalid Item">
            <stats>
                <stat name="VITALITY" scaling="1879347271"/>
            </stats>
        </item>
        '''
        
        # Invalid stat XML (missing scaling)
        self.invalid_stat_xml = '''
        <item key="1879480678" name="Invalid Stat Item" level="1" 
              slot="NECK" quality="COMMON" minLevel="1">
            <stats>
                <stat name="VITALITY"/>
            </stats>
        </item>
        '''

    @pytest.mark.parser
    def test_parse_valid_item(self):
        """Test parsing a valid item with all attributes."""
        item_elem = ET.fromstring(self.valid_item_xml)
        item_def = ItemParser.parse_item_element(item_elem)
        
        # Check basic attributes
        assert item_def.key == 1879480675
        assert item_def.name == "Chipped Bright Umbari Necklace"
        assert item_def.min_ilvl == 512
        assert item_def.slot == "NECK"
        assert item_def.quality == "UNCOMMON"
        assert item_def.required_player_level == 150
        assert item_def.scaling == "ze_skirmish_level#141-:1879471052;2:0.3"
        assert item_def.value_table_id == 1879050115
        
        # Check stats
        assert len(item_def.stats) == 3
        assert item_def.stats[0] == ItemStat("VITALITY", 1879347271)
        assert item_def.stats[1] == ItemStat("CRITICAL_RATING", 1879211605)
        assert item_def.stats[2] == ItemStat("FINESSE", 1879211717)

    @pytest.mark.parser
    def test_parse_minimal_item(self):
        """Test parsing an item with only required attributes."""
        item_elem = ET.fromstring(self.minimal_item_xml)
        item_def = ItemParser.parse_item_element(item_elem)
        
        # Check basic attributes
        assert item_def.key == 1879480676
        assert item_def.name == "Minimal Item"
        assert item_def.min_ilvl == 1
        assert item_def.slot == "NECK"
        assert item_def.quality == "COMMON"
        assert item_def.required_player_level == 1
        assert item_def.scaling is None
        assert item_def.value_table_id is None
        
        # Check stats
        assert len(item_def.stats) == 1
        assert item_def.stats[0] == ItemStat("VITALITY", 1879347271)

    @pytest.mark.parser
    def test_parse_invalid_item(self):
        """Test parsing an item with missing required attributes."""
        item_elem = ET.fromstring(self.invalid_item_xml)
        with pytest.raises(ValueError) as exc_info:
            ItemParser.parse_item_element(item_elem)
        assert "Invalid or missing required attribute" in str(exc_info.value)

    @pytest.mark.parser
    def test_parse_invalid_stat(self):
        """Test parsing an item with invalid stat data."""
        item_elem = ET.fromstring(self.invalid_stat_xml)
        with pytest.raises(ValueError) as exc_info:
            ItemParser.parse_item_element(item_elem)
        assert "Invalid stat" in str(exc_info.value)

    @pytest.mark.parser
    def test_parse_file_valid(self):
        """Test parsing a valid XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><items>')
            f.write(self.valid_item_xml)
            f.write(self.minimal_item_xml)
            f.write('</items>')
            temp_path = f.name

        try:
            items = ItemParser.parse_file(temp_path)
            assert len(items) == 2
            assert items[0].key == 1879480675
            assert items[1].key == 1879480676
        finally:
            Path(temp_path).unlink()

    @pytest.mark.parser
    def test_parse_file_invalid_xml(self):
        """Test parsing an invalid XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><items>')
            f.write('<invalid>')
            f.write('</items>')
            temp_path = f.name

        try:
            with pytest.raises(ET.ParseError):
                ItemParser.parse_file(temp_path)
        finally:
            Path(temp_path).unlink()

    @pytest.mark.parser
    def test_parse_file_mixed_valid_invalid(self):
        """Test parsing a file with both valid and invalid items."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><items>')
            f.write(self.valid_item_xml)
            f.write(self.invalid_item_xml)
            f.write(self.minimal_item_xml)
            f.write('</items>')
            temp_path = f.name

        try:
            items = ItemParser.parse_file(temp_path)
            # Should get 2 valid items, skipping the invalid one
            assert len(items) == 2
            assert items[0].key == 1879480675
            assert items[1].key == 1879480676
        finally:
            Path(temp_path).unlink()

    @pytest.mark.parser
    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            ItemParser.parse_file("nonexistent.xml")

    @pytest.mark.parser
    def test_parse_file_error_handling(self):
        """Test error handling in parse_file."""
        # Test with a file containing an invalid item
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><items>')
            f.write(self.invalid_item_xml)
            f.write('</items>')
            temp_path = f.name

        try:
            # Should not raise an exception, but should log the error
            items = ItemParser.parse_file(temp_path)
            assert len(items) == 0  # No valid items should be parsed
        finally:
            Path(temp_path).unlink()

    @pytest.mark.parser
    def test_parse_file_multiple_errors(self):
        """Test error handling in parse_file with multiple invalid items."""
        # Create a file with multiple invalid items
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><items>')
            f.write(self.invalid_item_xml)  # Missing required attributes
            f.write(self.invalid_stat_xml)  # Invalid stat
            f.write(self.valid_item_xml)    # One valid item
            f.write(self.invalid_item_xml)  # Another invalid item
            f.write('</items>')
            temp_path = f.name

        try:
            # Should parse the valid item and skip the invalid ones
            items = ItemParser.parse_file(temp_path)
            assert len(items) == 1  # Only the valid item should be parsed
            assert items[0].key == 1879480675  # Key of the valid item
        finally:
            Path(temp_path).unlink() 