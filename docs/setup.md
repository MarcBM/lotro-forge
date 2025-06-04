# 📋 Setup Guide

Complete installation and configuration guide for LOTRO Forge.

## Prerequisites

- **Python 3.12+**
- **PostgreSQL 12+**
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

### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

**macOS:** `brew install postgresql && brew services start postgresql`  
**Windows:** Download from [postgresql.org](https://www.postgresql.org/download/)

### Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE lotro_forge;
CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lotro_forge TO your_username;
ALTER SCHEMA public OWNER TO your_username;
\q
```

### Configure Connection

Create `.env` file in the project root:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lotro_forge
DB_USER=your_username
DB_PASSWORD=your_password
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
# Check PostgreSQL status
sudo service postgresql status

# Test connection
psql -h localhost -U your_username -d lotro_forge

# Reset database
python -m scripts.importers.run_import --wipe
```

### Permission Issues
```bash
sudo -u postgres psql
```
```sql
GRANT ALL PRIVILEGES ON DATABASE lotro_forge TO your_username;
ALTER SCHEMA public OWNER TO your_username;
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
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lotro_forge
DB_USER=your_username
DB_PASSWORD=your_password

# Application Settings (Optional)
LOTRO_FORGE_ENV=development
LOTRO_FORGE_HOST=127.0.0.1
LOTRO_FORGE_PORT=8000
LOTRO_FORGE_WORKERS=1
LOTRO_FORGE_SECRET_KEY=your-secret-key-here
``` 