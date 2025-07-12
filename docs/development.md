# 🛠️ Development Guide

Development workflow, testing, and code quality guide for LOTRO Forge.

## Quick Start

```bash
# Setup development environment
source venv/bin/activate
python scripts/run_tests.py unit
python -m scripts.run_web

# Verify working (requires authentication)
# First login via web UI at http://localhost:8000
curl http://localhost:8000/api/items/equipment?limit=1 -H "Cookie: auth_session_token=YOUR_TOKEN"
```

## Authentication System

### Overview
LOTRO Forge uses session-based authentication with secure HTTP-only cookies. All functionality except the home page requires authentication.

### Protected Routes
- `/builder` - Character build creation tool
- `/database` - Item database browser
- `/builds` - Community builds repository
- All `/api/*` endpoints - Automatically protected by middleware

### Unprotected Routes
- `/` - Home page (only unprotected route)

### Authentication Architecture
- **Web Routes**: Use dependency injection with `get_current_user_for_web()` 
- **API Routes**: Use `AuthenticationMiddleware` for automatic protection
- **Excluded API paths**: `/api/auth/*`, `/docs`, `/redoc`, `/openapi.json`

### Authentication Flow
1. User clicks "Sign In" button in navigation
2. Modal opens with username/password form
3. Credentials sent to `/api/auth/login`
4. Server sets secure HTTP-only cookie
5. Subsequent requests include cookie automatically
6. Unauthenticated access to protected routes redirects to home page with message
7. API requests without authentication return 401 Unauthorized
8. Logout clears session and redirects to home page

### Testing Authentication
```bash
# Test protected web routes without auth (should redirect)
curl -i "http://localhost:8000/builder"
curl -i "http://localhost:8000/database"
curl -i "http://localhost:8000/builds"
# All return: 303 See Other, Location: /?login_required=1

# Test API without auth (should return 401)
curl -i "http://localhost:8000/api/items/equipment"
# Returns: 401 Unauthorized

# Login via API (for testing)
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password" \
  -c cookies.txt

# Use session cookie for API calls
curl "http://localhost:8000/api/items/equipment?limit=1" -b cookies.txt
```

### User Management
Admin users can create new accounts via `/api/auth/create_user` endpoint. Regular user registration is not implemented (beta-only access).

### Middleware Implementation
The `AuthenticationMiddleware` automatically protects all `/api/*` routes:
- Runs before any API endpoint
- Validates session cookie
- Returns 401 if not authenticated
- Adds `request.state.current_user` for endpoints that need user info
- Excludes auth endpoints and documentation from protection

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
python -c "from database.session import get_session; print('Database connection available')"

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