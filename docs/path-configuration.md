# Path Configuration Guide

This guide explains how to configure external data paths for LOTRO Forge import scripts.

## Overview

LOTRO Forge import scripts need access to data from the `lotro_companion` repository. Previously, these paths were hardcoded, making the system non-portable. The new configuration system uses environment variables to make the system flexible and portable.

## Quick Setup

### 1. Automatic Setup (Recommended)

Run the setup script to automatically configure your paths:

```bash
python scripts/setup_paths.py
```

This script will:
- Auto-detect your `lotro_companion` directory
- Validate that all required files exist
- Create a `.env` file with the correct configuration

### 2. Manual Setup

If automatic setup doesn't work, you can configure manually:

1. Copy the template:
   ```bash
   cp config/env.template .env
   ```

2. Edit `.env` and set your paths:
   ```bash
   # Required: Path to your lotro_companion repository
   LOTRO_COMPANION_ROOT=/path/to/your/lotro_companion
   
   # Optional: Path to this project (auto-detected if not set)
   LOTRO_FORGE_PROJECT_ROOT=/path/to/lotro_forge
   ```

## Required Directory Structure

Your `lotro_companion` directory must contain:

```
lotro_companion/
├── lotro-items-db/
│   └── items.xml
├── lotro-data/
│   └── lore/
│       ├── progressions.xml
│       └── dpsTables.xml
└── lotro-icons/
    └── items/
        └── *.png
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LOTRO_COMPANION_ROOT` | Path to lotro_companion repository | `/home/user/workspace/lotro/lotro_companion` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOTRO_FORGE_PROJECT_ROOT` | Path to this project | Auto-detected |
| `DATABASE_URL` | SQLite database URL | `sqlite:///lotro_forge.db` |

## Validation

The configuration system validates that all required files exist before allowing imports to proceed. If validation fails, you'll see specific error messages indicating what's missing.

## Usage in Code

### Import the Configuration

```python
from config.data_paths import get_data_paths

# Get all configured paths
data_paths = get_data_paths()

# Access specific paths
items_xml = data_paths.items_xml
progressions_xml = data_paths.progressions_xml
icons_source = data_paths.icons_source_dir
```

### Convenience Functions

```python
from config.data_paths import (
    get_items_xml_path,
    get_progressions_xml_path,
    get_icons_source_dir
)

# Get individual paths
items_path = get_items_xml_path()
progressions_path = get_progressions_xml_path()
icons_dir = get_icons_source_dir()
```

## Troubleshooting

### Common Issues

1. **"LOTRO_COMPANION_ROOT environment variable not set"**
   - Make sure you have a `.env` file in the project root
   - Ensure `LOTRO_COMPANION_ROOT` is set correctly

2. **"Required file not found"**
   - Verify your `lotro_companion` directory structure
   - Check that all required XML files exist
   - Ensure the icons directory exists

3. **"Data path validation failed"**
   - Run the setup script to validate your configuration
   - Check the specific error messages for missing files

### Validation Commands

Test your configuration:

```bash
# Test path configuration
python -c "from config.data_paths import get_data_paths; print('✅ Configuration valid')"

# Test specific paths
python -c "from config.data_paths import get_data_paths; paths = get_data_paths(); print(f'Items: {paths.items_xml}')"
```

## Migration from Hardcoded Paths

If you're migrating from the old hardcoded system:

1. **Old code:**
   ```python
   # ❌ Hardcoded paths
   items_path = Path('/home/marcb/workspace/lotro/lotro_companion/lotro-items-db/items.xml')
   ```

2. **New code:**
   ```python
   # ✅ Configured paths
   from config.data_paths import get_data_paths
   data_paths = get_data_paths()
   items_path = data_paths.items_xml
   ```

## Best Practices

1. **Never hardcode paths** - Always use the configuration system
2. **Use environment variables** - Keep paths out of version control
3. **Validate early** - Test configuration before running imports
4. **Document your setup** - Keep notes on your specific directory structure

## Examples

### Development Setup

```bash
# .env file for development
LOTRO_COMPANION_ROOT=/home/developer/workspace/lotro/lotro_companion
DATABASE_URL=sqlite:///lotro_forge.db
```

### Production Setup

```bash
# .env file for production
LOTRO_COMPANION_ROOT=/opt/lotro_data/lotro_companion
DATABASE_URL=sqlite:///lotro_forge.db
``` 