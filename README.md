# LOTRO Forge

A tool for working with LOTRO item data and stat calculations.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/MarcBM/lotro_forge.git
   cd lotro_forge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

This project uses PostgreSQL as its database. Follow these steps to set up the database:

1. Install PostgreSQL:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. Start the PostgreSQL service:
   ```bash
   sudo service postgresql start
   ```

3. Create the database and user:
   ```bash
   # Switch to postgres user
   sudo -u postgres psql

   # In the PostgreSQL prompt, create database and user:
   CREATE DATABASE lotro_forge;
   CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE lotro_forge TO your_username;
   \q
   ```

4. Set up database permissions:
   ```bash
   # Switch to postgres user
   sudo -u postgres psql

   # In the PostgreSQL prompt, grant necessary permissions:
   # First, make the user a superuser temporarily to change schema ownership
   ALTER USER your_username WITH SUPERUSER;
   \q

   # Connect as your user and change schema ownership
   psql -U your_username lotro_forge
   ALTER SCHEMA public OWNER TO your_username;
   \q

   # Switch back to postgres to remove superuser privileges
   sudo -u postgres psql
   ALTER USER your_username WITH NOSUPERUSER;
   \q
   ```

5. Verify the installation:
   ```bash
   psql -d lotro_forge -U your_username
   ```

Note: Replace `your_username` and `your_password` with your preferred database credentials. Make sure to keep these credentials secure and never commit them to version control.

## Database Migrations

This project uses Alembic for database migrations. Migrations help track and apply database schema changes in a controlled way.

### Initial Setup

1. Install Alembic (should be in requirements.txt):
   ```bash
   pip install alembic
   ```

2. Initialize Alembic in the project:
   ```bash
   alembic init migrations
   ```

3. Configure Alembic:
   - The `alembic.ini` file is already configured to use environment variables
   - The `migrations/env.py` file is set up to use our database models

### Working with Migrations

1. Create a new migration:
   ```bash
   # After making changes to models
   alembic revision --autogenerate -m "Description of changes"
   ```

2. Apply migrations:
   ```bash
   # Apply all pending migrations
   alembic upgrade head
   
   # Rollback one migration
   alembic downgrade -1
   
   # Rollback all migrations
   alembic downgrade base
   ```

3. Check migration status:
   ```bash
   alembic current  # Show current migration
   alembic history  # Show migration history
   ```

### Migration Best Practices

- Always review auto-generated migrations before applying them
- Keep migrations focused and atomic (one logical change per migration)
- Test migrations both up and down before committing
- Never modify existing migrations that have been applied to production
- Document any manual steps required in migration messages

## Development

- Always work within the virtual environment (activate it using `source venv/bin/activate`)
- Install new dependencies with `pip install <package-name>` and update requirements.txt with `pip freeze > requirements.txt`
- The main code is in the `models/` and `parsers/` directories
- See `RULES.md` for important project rules and terminology

### Running the Web Server

To start the web server in development mode:

```bash
python -m scripts.run_web
```

This will start a development server with hot-reloading enabled. The server will automatically restart when you make changes to the code.

## Project Structure

```
lotro_forge/
├── models/          # Data models for items and stats
├── parsers/         # XML parsers for game data
├── scripts/         # Utility scripts
├── .gitignore      # Git ignore rules
├── README.md       # This file
├── RULES.md        # Project rules and terminology
└── requirements.txt # Project dependencies
```

## Database Management

### Data Import

The import system automatically handles dependencies to ensure everything works correctly. When importing items, the system automatically includes required progression tables (for stat calculations) and icons (for display).

To completely reset and import all equipment data:

```bash
python -m scripts.importers.run_import --wipe
```

This command will:
1. Drop all existing tables
2. Recreate the tables with their original schema
3. Analyze items to determine required progression tables
4. Import required progression tables
5. Import all equipment items (level 500+) with correct stat ordering
6. Copy required icons to the static folder

### Import Options

```bash
# Import everything (default) - most common usage
python -m scripts.importers.run_import --wipe

# Import items with dependencies (same as above)
python -m scripts.importers.run_import --import-type items --wipe

# Import only progression tables (for development/testing)
python -m scripts.importers.run_import --import-type progressions --wipe

# Create tables without wiping existing data
python -m scripts.importers.run_import --create-tables
```

### Example Data

To run with example data for testing:

```bash
python -m scripts.importers.example_import --wipe
```

This command will:
1. Drop all existing tables
2. Recreate the tables with their original schema
3. Import progression tables needed by example items
4. Import items found in example_items.xml
5. Copy required icons to the static folder

### Key Features

- **Intelligent Dependencies**: Items automatically include required progression tables and icons
- **No Foreign Key Errors**: Dependencies are imported in the correct order
- **Correct Stat Ordering**: Stats appear in the same order as the original LOTRO game data
- **Comprehensive Coverage**: Imports all equipment items level 500+ (armor, weapons, jewelry, etc.)