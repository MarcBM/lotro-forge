"""
Integration tests for LOTRO Forge API endpoints.

Tests the full request/response cycle for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from web.app import app
from database.models import EquipmentItem, ItemStat, ProgressionTable, ProgressionValue, ProgressionType, ItemQuality


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def api_test_data(db_session):
    """Create test data for API testing."""
    # Create progression table
    table = ProgressionTable(
        table_id="api_test_vitality",
        progression_type=ProgressionType.ARRAY
    )
    db_session.add(table)
    
    values = [
        ProgressionValue(table_id="api_test_vitality", item_level=500, value=1000.0),
        ProgressionValue(table_id="api_test_vitality", item_level=510, value=1100.0),
        ProgressionValue(table_id="api_test_vitality", item_level=520, value=1200.0),
    ]
    for value in values:
        db_session.add(value)
    
    # Create test item
    item = EquipmentItem(
        key=12345678,
        name="API Test Necklace",
        base_ilvl=510,
        quality=ItemQuality.RARE,
        slot="NECK",
        item_type="equipment"
    )
    db_session.add(item)
    
    # Add stat
    stat = ItemStat(
        item_key=item.key,
        stat_name="VITALITY",
        value_table_id="api_test_vitality",
        order=1
    )
    db_session.add(stat)
    
    db_session.commit()
    return item


@pytest.mark.integration
@pytest.mark.api
class TestItemsAPI:
    """Test suite for the Items API endpoints."""
    
    def test_get_items_endpoint(self, client):
        """Test the GET /api/items endpoint."""
        response = client.get("/api/items/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
    
    def test_get_items_with_filters(self, client):
        """Test the GET /api/items endpoint with filters."""
        # Test slot filter
        response = client.get("/api/items/?slot=NECK")
        assert response.status_code == 200
        
        # Test quality filter
        response = client.get("/api/items/?quality=rare")
        assert response.status_code == 200
        
        # Test item level filter
        response = client.get("/api/items/?min_ilvl=500&max_ilvl=520")
        assert response.status_code == 200
    
    def test_get_items_pagination(self, client):
        """Test pagination on the items endpoint."""
        response = client.get("/api/items/?page=1&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert "total" in data["pagination"]
        assert "page" in data["pagination"]
        assert "per_page" in data["pagination"]
    
    @pytest.mark.skip(reason="Requires specific item in database")
    def test_get_single_item(self, client, api_test_data):
        """Test getting a single item by key."""
        item = api_test_data
        response = client.get(f"/api/items/{item.key}")
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == item.key
        assert data["name"] == item.name
    
    def test_get_nonexistent_item(self, client):
        """Test getting a non-existent item returns 404."""
        response = client.get("/api/items/999999999")
        assert response.status_code == 404


@pytest.mark.integration
class TestWebPages:
    """Test suite for web page endpoints."""
    
    def test_home_page(self, client):
        """Test that the home page loads correctly."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_database_page(self, client):
        """Test that the database page loads correctly."""
        response = client.get("/database")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_builder_page(self, client):
        """Test that the builder page loads correctly."""
        response = client.get("/builder")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_builds_page(self, client):
        """Test that the builds page loads correctly."""
        response = client.get("/builds")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_404_page(self, client):
        """Test that 404 errors are handled properly."""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404 