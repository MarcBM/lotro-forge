# 🛠️ Development Guide

Development workflow, testing, and code quality guide for LOTRO Forge.

## Quick Start

```bash
# Setup development environment
source venv/bin/activate
python scripts/run_tests.py unit
python -m scripts.run_web

# Verify working
curl http://localhost:8000/api/items/equipment?limit=1
```

## Development Server

```bash
# Auto-reload development server
python -m scripts.run_web

# Or with uvicorn directly
uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

### Test Structure
- `tests/unit/` - Fast isolated tests
- `tests/integration/` - Full API tests
- `tests/conftest.py` - Shared fixtures

### Running Tests

```bash
# Unit tests (recommended for development)
python scripts/run_tests.py unit

# With coverage
python scripts/run_tests.py unit --coverage

# Specific test file
python -m pytest tests/unit/test_item.py -v

# Integration tests (requires httpx)
python scripts/run_tests.py integration
```

### Writing Tests

```python
import pytest
from database.models import Item

@pytest.mark.unit
class TestItem:
    def test_item_creation(self, db_session, sample_progression_table):
        item = Item(
            key=12345,
            name="Test Item",
            slot="CHEST",
            quality="UNCOMMON",
            item_level=500
        )
        db_session.add(item)
        db_session.commit()
        
        assert item.id is not None
        assert item.name == "Test Item"
```

## Code Quality

```bash
# Format code (required)
black .

# Lint code (required)
ruff check .
ruff check --fix .  # Auto-fix

# Type checking (optional)
mypy database/ web/ scripts/
```

## Database Management

### Migrations

```bash
# Check status
alembic current

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
alembic downgrade -1  # Rollback one
```

### Data Operations

```bash
# Reset database completely
python -m scripts.importers.run_import --wipe

# Import specific types
python -m scripts.importers.run_import --import-type items --wipe

# Verbose logging
python -m scripts.importers.run_import --verbose
```

## API Development

### Adding Endpoints

```python
from fastapi import APIRouter, Depends
from database.connection import get_session

router = APIRouter(prefix="/api/feature")

@router.get("/")
def list_items(session = Depends(get_session)):
    return session.query(Item).all()
```

Register in `web/app.py`:
```python
from web.api.feature import router as feature_router
app.include_router(feature_router)
```

### API Best Practices
- Use dependency injection for sessions
- Return consistent JSON structures
- Include proper HTTP status codes
- Add pagination for list endpoints
- Handle errors gracefully

## Project Structure

For detailed project organization and architecture overview, see [Project Structure Guide](structure.md).

## Common Tasks

### Database Access
```python
from database.connection import get_session
from database.models import Item

with get_session() as session:
    items = session.query(Item).filter(Item.quality == "LEGENDARY").limit(5).all()
```

### Debugging
```bash
# Check data files
ls -la example_data/

# Test database connection
python -c "from database.connection import get_engine; print(get_engine())"

# Single test with debugging
python -m pytest tests/unit/test_item.py::TestItem::test_creation -v -s
```

### Performance Tools
```bash
# API testing
pip install httpie
http GET localhost:8000/api/items/ slot==CHEST quality==rare

# Performance profiling
pip install py-spy
py-spy top --pid $(pgrep -f "python.*run_web")
```

## Configuration

### Environment Variables

For complete environment variable configuration, see [Setup Guide](setup.md#environment-variables).

### Code Style Rules
- Black formatting (no exceptions)
- Ruff linting (fix all issues)
- Descriptive names for functions/variables
- Type hints for parameters and returns
- Docstrings for public functions

## Deployment Workflow

1. Run tests: `python scripts/run_tests.py unit`
2. Format code: `black . && ruff check .`
3. Create migration (if needed): `alembic revision --autogenerate`
4. Test with fresh data: `python -m scripts.importers.run_import --wipe`
5. Verify web server: `python -m scripts.run_web`

---

See [Setup Guide](setup.md) for installation instructions.  
See [API Documentation](api.md) for endpoint details.  
See [Data Transformation Guide](data-transformation.md) for XML import process. 