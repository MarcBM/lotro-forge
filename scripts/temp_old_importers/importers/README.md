# LOTRO Forge Import Framework

This framework is designed for importing data from the `lotro_companion` repository into the LOTRO Forge database. It is intended for one-time or rare database operations, not for runtime use.

## Purpose

The import framework is used to:
- Populate the database with initial game data
- Update the database when game data changes
- Import new types of game data
- Maintain data consistency between `lotro_companion` and LOTRO Forge

## When to Use

Use this framework when:
- Setting up a new LOTRO Forge instance
- Updating the database after game patches
- Adding new data types to the database
- Fixing data inconsistencies

Do NOT use this framework for:
- Runtime data processing
- Frequent database updates
- Real-time data operations

## Available Importers

### Progressions Importer
Imports stat progression data from `progressions.xml`:
- Stat definitions (base values, scaling factors)
- Level-based stat values
- Progression types and caps

### Item Importer
Imports item definitions from `items.xml`:
- Item definitions (name, level, slot, quality)
- Item stats with scaling references
- Value table references
- Required player levels

## Usage

1. Ensure you have access to the `lotro_companion` repository
2. Run the import script:
```bash
# Import all data
python -m scripts.import.run_import \
    --source /path/to/lotro_companion \
    --db-url sqlite:///lotro_forge.db

# Import specific data types
python -m scripts.import.run_import \
    --source /path/to/lotro_companion \
    --db-url sqlite:///lotro_forge.db \
    --import-type items  # or 'progressions' or 'all'
```

## Architecture

The import framework follows a layered approach:

1. **Validation**: Checks source data exists and is valid
2. **Parsing**: Converts XML into intermediate objects
3. **Transformation**: Converts intermediate objects into database models
4. **Import**: Handles database operations with transaction support

Each importer implements these steps through the `BaseImporter` class.

## Adding New Importers

To add a new importer:

1. Create a new class inheriting from `BaseImporter`
2. Implement the required methods:
   - `validate_source()`
   - `parse_source()`
   - `transform_data()`
   - `import_data()`
3. Add the importer to `run_import.py`

## Best Practices

1. **Data Integrity**
   - Always validate source data
   - Use transactions for database operations
   - Handle errors gracefully
   - Log all operations

2. **Performance**
   - Import in bulk when possible
   - Use appropriate batch sizes
   - Consider database indexes

3. **Maintenance**
   - Document data structures
   - Add tests for importers
   - Version control import scripts
   - Track import history

## Related Systems

- **Database Models** (`web/models/`): Define the database schema
- **Domain Models** (`domain/`): Define the application's domain objects

## Migration Notes

The old parsers (`parsers/item_parser.py` and `scripts/import_items.py`) have been removed in favor of this framework. The new framework provides:
- Better error handling
- Transaction support
- Clearer separation of concerns
- More maintainable code structure
- Better documentation
- Consistent import process across all data types 