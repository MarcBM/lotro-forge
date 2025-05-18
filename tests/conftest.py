"""Pytest configuration file for LOTRO Forge tests."""

import pytest
from pathlib import Path

# Add the project root to the Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def pytest_configure(config):
    """Configure pytest with coverage settings."""
    config.addinivalue_line(
        "markers",
        "parser: mark test as a parser test"
    )

@pytest.fixture(autouse=True)
def setup_coverage():
    """Setup coverage reporting for all tests."""
    # This fixture ensures coverage is enabled for all tests
    pass 