# 📋 Setup Guide

Complete installation and configuration guide for LOTRO Forge.

## Prerequisites

- **Python 3.12+**
- **Git**

## 1. Clone and Install

```bash
git clone https://github.com/MarcBM/lotro_forge.git
cd lotro_forge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Database Setup

### SQLite Database

LOTRO Forge uses SQLite for both development and production. SQLite is included with Python and requires no additional installation.

### Configure Database

Create `.env` file in the project root:
```env
# SQLite database file (relative to project root)
DATABASE_URL=sqlite:///lotro_forge.db
```

### Initialize Schema

```bash
alembic upgrade head
```

## 3. Import Data

### Full Import (Recommended)
```bash
python -m scripts.importers.run_import --wipe
```

### Test Data Only
```bash
python -m scripts.importers.example_import --wipe
```

## 4. Start Application

```bash
python -m scripts.run_web
```

Visit: http://localhost:8000

## Troubleshooting

### Database Issues
```bash
# Check SQLite database file
ls -la lotro_forge.db

# Test database connection
python -c "from database.session import get_session; print('Database connection available')"

# Reset database
python -m scripts.importers.run_import --wipe
```

### Port Conflicts
```bash
# Use different port
uvicorn web.app:app --host 0.0.0.0 --port 8080
```

## Verification

After setup, test these URLs:
- **Home**: http://localhost:8000
- **Database**: http://localhost:8000/database
- **API**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/items/equipment?limit=1

## Next Steps

1. Run tests: `python scripts/run_tests.py unit`
2. Read [Development Guide](development.md)
3. Explore API at http://localhost:8000/docs

## Environment Variables

```env
# Database Configuration (Required)
DATABASE_URL=sqlite:///lotro_forge.db

# Application Settings (Optional)
LOTRO_FORGE_ENV=development
LOTRO_FORGE_HOST=127.0.0.1
LOTRO_FORGE_PORT=8000
LOTRO_FORGE_WORKERS=1
LOTRO_FORGE_SECRET_KEY=your-secret-key-here
``` 