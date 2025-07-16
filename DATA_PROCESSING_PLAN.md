# 🚀 LOTRO Forge Data Processing & Deployment Plan

## Overview

Transform the current deployment process to use locally pre-processed, curated data with sprite sheet optimization.

## Phase 1: Data Curation System

### 1.1 Create Data Curation Script
**File:** `scripts/curate_data.py`

**Purpose:** Process full LOTRO companion repositories into minimal, optimized data files

**Process:**
```python
def curate_lotro_data():
    # 1. Parse full items.xml and extract only needed items
    # 2. Parse progressions.xml and extract only used progression tables
    # 3. Parse dpsTables.xml and extract only used DPS tables
    # 4. Create optimized XML files with only required data
    # 5. Generate sprite sheets from individual icons
    # 6. Create CSS file with sprite positioning
```

**Output Structure:**
```
curated_data/
├── items.xml              # Optimized items data
├── progressions.xml       # Only used progression tables
├── dps_tables.xml         # Only used DPS tables
├── sprites/
│   ├── items-sprite.png   # Combined sprite sheet
│   └── items-sprite.css   # CSS positioning rules
└── metadata.json          # Version info, file sizes, etc.
```

### 1.2 Data Optimization Strategies

**XML Optimization:**
- Remove unused attributes
- Compress text content
- Use shorter element names where possible
- Remove whitespace and comments

**Icon Optimization:**
- Convert to optimized PNG format
- Standardize icon sizes (32x32, 64x64)
- Remove duplicate icons
- Create sprite sheets with minimal padding

## Phase 2: Sprite Sheet System

### 2.1 Sprite Generation
**File:** `scripts/generate_sprites.py`

**Process:**
```python
def generate_item_sprites():
    # 1. Collect all required item icons
    # 2. Arrange in optimal grid layout
    # 3. Create sprite sheet image
    # 4. Generate CSS with background-position
    # 5. Create mapping file (icon_id -> sprite_position)
```

**Sprite Sheet Layout:**
- Grid-based arrangement (e.g., 16x16 icons per row)
- Minimal padding between icons
- Power-of-2 dimensions for optimal compression
- Multiple sprite sheets if needed (e.g., items, equipment, essences)

### 2.2 CSS Generation
**Output:** `curated_data/sprites/items-sprite.css`
```css
.icon-item-12345 {
    background-image: url('/static/sprites/items-sprite.png');
    background-position: -32px -64px;
    width: 32px;
    height: 32px;
    display: inline-block;
}
```

## Phase 3: Import System Refactoring

### 3.1 Modify Import Scripts
**Files to update:**
- `scripts/importers/run_import.py`
- `scripts/importers/items.py`
- `scripts/importers/progressions.py`

**Changes:**
```python
# Update data path configuration
def get_curated_data_paths():
    return {
        'items': 'curated_data/items.xml',
        'progressions': 'curated_data/progressions.xml',
        'dps_tables': 'curated_data/dps_tables.xml',
        'sprites': 'curated_data/sprites/'
    }
```

### 3.2 Remove Icon Copying
**File:** `scripts/copy_icons.py` (deprecate)

**Replace with:** Sprite sheet deployment in Dockerfile

## Phase 4: Template System Updates

### 4.1 Update Item Templates
**Files to update:**
- `web/templates/items/`
- `web/templates/components/`

**Changes:**
```html
<!-- Old: Individual icon files -->
<img src="/static/icons/items/{{ item.icon }}.png" alt="{{ item.name }}">

<!-- New: CSS sprite -->
<div class="icon-item-{{ item.icon_id }}" title="{{ item.name }}"></div>
```

### 4.2 Add Sprite CSS to Base Template
**File:** `web/templates/base.html`
```html
<head>
    <!-- Add sprite CSS -->
    <link rel="stylesheet" href="/static/sprites/items-sprite.css">
</head>
```

## Phase 5: Deployment Process

### 5.1 Update Dockerfile
```dockerfile
# Copy curated data instead of full repositories
COPY curated_data/ /app/curated_data/

# Copy sprite sheets
COPY curated_data/sprites/ /app/web/static/sprites/
```

### 5.2 Update Environment Configuration
**File:** `config/data_paths.py`
```python
def get_curated_data_paths():
    """Get paths for curated data files."""
    project_root = Path(__file__).parent.parent
    return {
        'items': project_root / 'curated_data' / 'items.xml',
        'progressions': project_root / 'curated_data' / 'progressions.xml',
        'dps_tables': project_root / 'curated_data' / 'dps_tables.xml',
    }
```

### 5.3 Server-Side Import Process
**File:** `scripts/deploy_import.py`
```python
def import_curated_data():
    """Import curated data on Fly.io instance."""
    # 1. Run database migrations
    # 2. Import curated items data
    # 3. Import curated progressions data
    # 4. Import curated DPS tables
    # 5. Verify import success
```

## Phase 6: Update Process

### 6.1 Local Update Script
**File:** `scripts/update_curated_data.py`
```python
def update_curated_data():
    """Update curated data from latest LOTRO companion data."""
    # 1. Pull latest LOTRO companion data
    # 2. Re-run curation process
    # 3. Generate new sprite sheets
    # 4. Commit changes to repository
    # 5. Deploy to Fly.io
```

### 6.2 Preserve User Data
**Strategy:**
- Use Alembic migrations for schema changes
- Keep user data in separate tables
- Only update game data tables during imports
- Implement backup/restore for user data

## Implementation Steps

### Step 1: Create Curation System
1. Write `scripts/curate_data.py`
2. Test with sample data
3. Optimize XML output format

### Step 2: Implement Sprite System
1. Write `scripts/generate_sprites.py`
2. Create CSS generation
3. Test sprite rendering

### Step 3: Update Import System
1. Modify import scripts for curated data
2. Update data path configuration
3. Test import process

### Step 4: Update Templates
1. Modify item templates for sprites
2. Update base template
3. Test rendering

### Step 5: Update Deployment
1. Modify Dockerfile
2. Update environment configuration
3. Test deployment process

### Step 6: Create Update Process
1. Write update scripts
2. Implement user data preservation
3. Test update workflow

## Expected Benefits

### Performance Improvements:
- **50-100x fewer HTTP requests** for icons
- **2-5x faster page loading**
- **20-40% smaller total file size**
- **Better browser caching**

### Deployment Benefits:
- **Faster deployments** (smaller data files)
- **More reliable** (no server-side cloning)
- **Version controlled** (curated data in git)
- **Preserves user data** (server-side processing)

### Maintenance Benefits:
- **Easier updates** (local processing)
- **Better debugging** (curated data format)
- **Reduced server load** (fewer files)
- **Scalable** (sprite sheets scale well)

## File Size Estimates

### Current State:
- Full LOTRO companion repos: ~500MB
- Individual icons: ~2-5MB
- Total deployment data: ~50-100MB

### After Optimization:
- Curated XML files: ~1-2MB
- Sprite sheets: ~0.5-1MB
- Total deployment data: ~2-3MB

**Result: 95% reduction in deployment data size**

## Technical Details

### Data Curation Process:
1. **Parse full repositories** - Read complete LOTRO companion data
2. **Filter required data** - Extract only items, progressions, and DPS tables used by the application
3. **Optimize structure** - Remove unused attributes, compress content
4. **Generate metadata** - Track what was included and why

### Sprite Sheet Generation:
1. **Collect icons** - Gather all required item icons
2. **Optimize images** - Standardize sizes, remove duplicates
3. **Arrange grid** - Create optimal layout for sprite sheet
4. **Generate CSS** - Create positioning rules for each icon
5. **Create mapping** - Link icon IDs to sprite positions

### Import System Changes:
1. **Update paths** - Point to curated data instead of full repositories
2. **Modify parsers** - Handle optimized XML format
3. **Remove icon copying** - Icons now come from sprite sheets
4. **Add validation** - Ensure curated data integrity

### Template Updates:
1. **Replace img tags** - Use CSS sprites instead of individual files
2. **Add sprite CSS** - Include positioning styles
3. **Update components** - Modify all icon-using templates
4. **Test rendering** - Ensure sprites display correctly

## Migration Strategy

### Phase 1: Development
- Implement curation system locally
- Test with sample data
- Validate sprite generation

### Phase 2: Testing
- Deploy to staging environment
- Test import process
- Verify performance improvements

### Phase 3: Production
- Deploy to production
- Monitor performance metrics
- Validate user experience

### Phase 4: Optimization
- Fine-tune curation process
- Optimize sprite layouts
- Implement caching strategies

---

**Created:** 2024-12-19  
**Status:** Planning Phase  
**Next Review:** 2025-01-19 