# 🔄 Data Transformation Guide

This guide explains how LOTRO Forge transforms game data from the `lotro_companion` repository into our database format.

## Overview

The data transformation system is designed to:
- Import game data from XML files into our database
- Handle dependencies between different data types
- Maintain data integrity during imports
- Provide a consistent import process for all data types

## Architecture

### Base Importer Framework

All importers inherit from `BaseImporter`, which defines a standardized four-step process:

1. **Validation** (`validate_source()`)
   - Verifies source files exist
   - Validates XML structure
   - Checks required data presence
   - Returns success/failure status

2. **Parsing** (`parse_source()`)
   - Reads XML files
   - Converts to intermediate data structures
   - Handles basic type conversions
   - Returns standardized format

3. **Transformation** (`transform_data()`)
   - Converts to database models
   - Manages model relationships
   - Applies data transformations
   - Returns database-ready objects

4. **Import** (`import_data()`)
   - Handles database operations
   - Manages transactions
   - Handles updates vs inserts
   - Commits changes

### Available Importers

#### Progressions Importer
- Source: `progressions.xml`
- Handles: Stat progression tables
- Dependencies: None
- Used by: Item importer for stat calculations

#### Item Importer
- Source: `items.xml`
- Handles: Equipment, weapons, essences
- Dependencies: 
  - Progressions tables (for stats)
  - DPS tables (for weapons)
  - Icons (for display)

#### DPS Tables Importer
- Source: `dpsTables.xml`
- Handles: Weapon damage calculations
- Dependencies: None
- Used by: Item importer for weapons

## Usage

### Command Line Interface

```bash
# Import all data (items + dependencies)
python -m scripts.importers.run_import --import-type items

# Import only progression tables
python -m scripts.importers.run_import --import-type progressions

# Additional options
python -m scripts.importers.run_import \
    --import-type items \
    --wipe \                    # Drop and recreate tables
    --create-tables \           # Create tables if missing
    --log-dir /path/to/logs     # Custom log directory
```

### Import Process Flow

When importing items, the system automatically handles dependencies:

1. **Dependency Analysis**
   ```python
   # Get required progression tables
   required_tables = item_importer.get_required_progression_tables()
   
   # Get required DPS tables
   required_dps = item_importer.get_required_dps_tables()
   ```

2. **Dependency Import**
   ```python
   # Import progression tables
   progressions_importer.import_specific_tables(required_tables)
   
   # Import DPS tables
   item_importer.import_required_dps_tables(required_dps)
   ```

3. **Main Data Import**
   ```python
   # Import items with their stats
   item_importer.run()
   ```

4. **Post-Import Tasks**
   ```python
   # Collect and copy required icons
   copy_required_icons(web_dir)
   ```

## Best Practices

### Data Integrity
- Always validate source data before import
- Use transactions for database operations
- Handle errors gracefully with proper logging
- Maintain referential integrity

### Performance
- Import dependencies first
- Use bulk operations when possible
- Consider database indexes
- Monitor memory usage with large imports

### Maintenance
- Keep import scripts version controlled
- Document data structure changes
- Test imports with sample data
- Monitor import logs for issues

## Future Improvements

Planned enhancements to the import system:
- GitHub webhook integration for automatic imports
- CI/CD pipeline for deployment
- Automated testing of imports
- Better error recovery mechanisms

## Related Documentation

- [Setup Guide](setup.md) - Environment setup
- [Development Guide](development.md) - Development workflow
- [API Documentation](api.md) - API endpoints
- [Project Structure](structure.md) - Code organization 