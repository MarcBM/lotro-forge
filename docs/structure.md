# 📁 Project Structure

Overview of the LOTRO Forge codebase organization.

## Architecture

LOTRO Forge follows a layered architecture:

- **Database Layer** (`database/`) - Data models and connections
- **Web Layer** (`web/`) - FastAPI application and frontend
- **Scripts Layer** (`scripts/`) - Import and management tools
- **Testing** (`tests/`) - Unit and integration tests

## Directory Tree

```
lotro_forge/
├── database/                    # Database layer
│   ├── models/                  # SQLAlchemy data models
│   ├── config.py               # Database configuration
│   └── connection.py           # Connection management
│
├── web/                         # Web application
│   ├── api/                    # REST API endpoints
│   ├── static/                 # Frontend assets (CSS, JS, images)
│   ├── templates/              # Jinja2 HTML templates
│   ├── config/                 # Application configuration
│   ├── middleware/             # Security and request middleware
│   └── app.py                  # FastAPI application setup
│
├── scripts/                     # Management and utility scripts
│   ├── importers/              # Data import tools and parsers
│   └── run_*.py               # Application launchers
│
├── tests/                       # Test suite
│   ├── unit/                   # Fast isolated tests
│   ├── integration/            # Full API and workflow tests
│   └── conftest.py             # Shared test fixtures
│
├── docs/                        # Project documentation
├── migrations/                  # Database schema migrations
├── example_data/               # Sample data for development
├── requirements.txt            # Python dependencies
└── configuration files         # pytest.ini, alembic.ini, etc.
```

## Key Components

### Database Models (`database/models/`)

Core data models using SQLAlchemy:

- **`Item`** - Base item model with stats and properties
- **`EquipmentItem`** - Equipment with sockets and armor types
- **`Weapon`** - Weapons with damage and DPS data
- **`Essence`** - Special essence items
- **`StatProgression`** - Stat scaling tables
- **`DpsTable`** - Damage calculation tables

### API Layer (`web/api/`)

REST API endpoints:

- **`items.py`** - Item browsing, filtering, and retrieval
- **`services/`** - Business logic and calculations

### Import System (`scripts/importers/`)

Data import pipeline:

1. Parse LOTRO XML data files
2. Transform to database models
3. Handle dependencies (progressions before items)
4. Batch insert for performance
5. Generate item icons

### Test Suite (`tests/`)

Comprehensive testing:

- **Unit tests** - Fast, isolated model tests
- **Integration tests** - Full API testing
- **Test fixtures** - Shared database and sample data

## File Organization

### Naming Conventions

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_CASE`
- **Templates**: `lowercase.html`

### Import Patterns

**Within packages** (relative):
```python
from .base import BaseModel
from .progressions import StatProgression
```

**Cross-package** (absolute):
```python
from database.models import Item
from database.connection import get_session
```

## Configuration

### Database
- PostgreSQL for production
- SQLite for testing
- Alembic for migrations

### Environment Variables
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lotro_forge
DB_USER=your_username
DB_PASSWORD=your_password

# Application Settings
LOTRO_FORGE_ENV=development
LOTRO_FORGE_HOST=127.0.0.1
LOTRO_FORGE_PORT=8000
```

### Dependencies
- **FastAPI** - Web framework
- **SQLAlchemy** - Database ORM
- **Alembic** - Migrations
- **pytest** - Testing
- **lxml** - XML parsing

## Development Workflow

1. **Models** - Define in `database/models/`
2. **Migrations** - Generate with `alembic revision --autogenerate`
3. **API** - Add endpoints in `web/api/`
4. **Tests** - Write tests in `tests/unit/`
5. **Import** - Update importers if needed

## Key Files

| File | Purpose |
|------|---------|
| `web/app.py` | FastAPI application setup |
| `database/connection.py` | Database session management |
| `scripts/run_import.py` | Main data import script |
| `tests/conftest.py` | Test fixtures and configuration |
| `pytest.ini` | Test runner configuration |
| `alembic.ini` | Database migration configuration |
| `requirements.txt` | Python dependencies |

## Data Flow

```
LOTRO XML Files → Import Scripts → Database → API → Web Interface
                                     ↓
                               Comprehensive Test Suite
```

---

For development details, see [Development Guide](development.md).  
For setup instructions, see [Setup Guide](setup.md). 