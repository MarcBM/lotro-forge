# Old Import System - Temporary Storage

This directory contains the old import system that is being replaced by the new curation-based system.

## Contents

### Import Framework
- `importers/` - Complete old import framework
  - `base.py` - Base importer class
  - `run_import.py` - Main import script
  - `items.py` - Item importer (18KB, 443 lines)
  - `progressions.py` - Progression importer (13KB, 308 lines)
  - `dps_tables.py` - DPS tables importer (6KB, 151 lines)
  - `example_import.py` - Example import script
  - `README.md` - Old import framework documentation

### Icon System
- `copy_icons.py` - Old icon copying script (will be replaced by sprite system)

### Deployment
- `deploy_setup.sh` - Old Fly.io deployment setup (needs updating for new system)

### Database Utilities
- `check_data.py` - Database content inspection (needs updating)
- `list_items.py` - Item listing utility (needs updating)

### Testing
- `run_tests.py` - Old comprehensive test runner
- `test.sh` - Old bash test script

## Status

All files in this directory are **DEPRECATED** and will be replaced by:

1. **New Curation System** - Replaces importers/
2. **Sprite System** - Replaces copy_icons.py
3. **Updated Deployment** - Replaces deploy_setup.sh
4. **Simplified Test Runner** - Replaces run_tests.py and test.sh
5. **Updated Database Utilities** - Replaces check_data.py and list_items.py

## Migration Plan

These files are kept for reference during the migration to ensure no functionality is lost. They will be deleted once the new system is fully implemented and tested.

## Notes

- The old import system was complex and had dependency management issues
- The new curation system will be simpler, faster, and more maintainable
- Icon copying will be replaced by sprite sheet generation
- Database utilities will be updated to work with the new data structure 