"""
Pytest configuration and shared fixtures for LOTRO Forge tests.
"""
import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.base import Base
from database.models import Item, EquipmentItem, ItemStat, ProgressionTable, ProgressionValue, ProgressionType, ItemQuality


@pytest.fixture(scope="session")
def test_engine():
    """Create a temporary in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    yield session
    
    # Clean up
    session.close()


@pytest.fixture
def sample_progression_table(db_session):
    """Create a sample progression table for testing."""
    # Use unique table ID to prevent conflicts
    table_id = f"test_vitality_table_{uuid.uuid4().hex[:8]}"
    
    table = ProgressionTable(
        table_id=table_id,
        progression_type=ProgressionType.ARRAY
    )
    db_session.add(table)
    
    # Add some sample values
    values = [
        ProgressionValue(table_id=table_id, item_level=500, value=1000.0),
        ProgressionValue(table_id=table_id, item_level=510, value=1100.0),
        ProgressionValue(table_id=table_id, item_level=520, value=1200.0),
    ]
    for value in values:
        db_session.add(value)
    
    db_session.commit()
    return table


@pytest.fixture
def sample_item(db_session, sample_progression_table):
    """Create a sample item for testing."""
    item_key = 1879480000 + hash(uuid.uuid4().hex) % 100000  # Unique key
    
    item = EquipmentItem(
        key=item_key,
        name="Test Necklace",
        base_ilvl=510,
        quality=ItemQuality.UNCOMMON,  # Use enum instead of string
        slot="NECK",
        item_type="equipment"
    )
    db_session.add(item)
    
    # Add a stat
    stat = ItemStat(
        item_key=item.key,
        stat_name="VITALITY",
        value_table_id=sample_progression_table.table_id,
        order=1
    )
    db_session.add(stat)
    
    db_session.commit()
    return item 