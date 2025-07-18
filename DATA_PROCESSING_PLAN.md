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
    # 4. Create optimized JSON files with only required data
    # 5. Compress JSON files using gzip for minimal deployment size
    # 6. Generate sprite sheets from individual icons
    # 7. Create CSS file with sprite positioning
```

**Output Structure:**
```
curated_data/
├── items.json.gz          # Compressed optimized items data
├── progressions.json.gz   # Compressed progression tables
├── dps_tables.json.gz     # Compressed DPS tables
├── sprites/
│   ├── items-sprite.png   # Combined sprite sheet
│   └── items-sprite.css   # CSS positioning rules
└── metadata.json          # Version info, file sizes, etc.
```

### 1.2 Data Optimization Strategies

**JSON Optimization:**
- Remove unused fields
- Use shorter field names where possible
- Minimize nested structures
- Use arrays instead of objects where appropriate
- Compress with gzip for deployment (90-95% compression ratio)

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
        'items': 'curated_data/items.json.gz',
        'progressions': 'curated_data/progressions.json.gz',
        'dps_tables': 'curated_data/dps_tables.json.gz',
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
        'items': project_root / 'curated_data' / 'items.json.gz',
        'progressions': project_root / 'curated_data' / 'progressions.json.gz',
        'dps_tables': project_root / 'curated_data' / 'dps_tables.json.gz',
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

## Phase 7: Incremental Update System

### 7.1 Version Tracking System
**File:** `scripts/version_tracker.py`
```python
class DataVersionTracker:
    def __init__(self):
        self.version_file = "curated_data/version_metadata.json"
    
    def track_item_versions(self, items_data):
        """Track version info for each item."""
        versions = {}
        for item in items_data:
            versions[item['id']] = {
                'last_updated': item.get('last_modified', datetime.now().isoformat()),
                'hash': self._calculate_item_hash(item),
                'version': item.get('version', '1.0')
            }
        return versions
    
    def get_changed_items(self, new_data, existing_versions):
        """Identify items that have changed since last import."""
        changed_items = []
        for item in new_data:
            item_id = item['id']
            new_hash = self._calculate_item_hash(item)
            
            if item_id not in existing_versions:
                changed_items.append(('new', item))
            elif existing_versions[item_id]['hash'] != new_hash:
                changed_items.append(('updated', item))
        
        return changed_items
```

### 7.2 Incremental Import Script
**File:** `scripts/incremental_import.py`
```python
def incremental_import_items():
    """Import only new/changed items efficiently."""
    # 1. Load existing version metadata
    tracker = DataVersionTracker()
    existing_versions = tracker.load_versions()
    
    # 2. Parse new curated data
    new_items = load_curated_items()
    
    # 3. Identify changes
    changes = tracker.get_changed_items(new_items, existing_versions)
    
    # 4. Process changes by type
    for change_type, item in changes:
        if change_type == 'new':
            insert_new_item(item)
        elif change_type == 'updated':
            update_existing_item(item)
    
    # 5. Update version metadata
    new_versions = tracker.track_item_versions(new_items)
    tracker.save_versions(new_versions)
    
    # 6. Generate incremental sprite updates
    if changes:
        update_sprites_incrementally(changes)
```

### 7.3 Database Update Strategies
**File:** `scripts/database_updater.py`
```python
class DatabaseUpdater:
    def insert_new_item(self, item_data):
        """Insert a new item efficiently."""
        # Use UPSERT pattern for idempotency
        query = """
        INSERT INTO items (id, name, description, icon_id, ...)
        VALUES (:id, :name, :description, :icon_id, ...)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            icon_id = EXCLUDED.icon_id,
            updated_at = NOW()
        """
        return self.db.execute(query, item_data)
    
    def batch_update_items(self, items_data):
        """Update multiple items in a single transaction."""
        with self.db.transaction():
            for item in items_data:
                self.insert_new_item(item)
    
    def update_progressions_incrementally(self, new_progressions):
        """Update only changed progression values."""
        # Compare existing vs new progression data
        # Update only changed level ranges
        pass
```

### 7.4 Sprite Sheet Incremental Updates
**File:** `scripts/sprite_updater.py`
```python
def update_sprites_incrementally(changes):
    """Update sprite sheets with only new/changed icons."""
    # 1. Extract new/changed icon IDs
    new_icon_ids = set()
    for change_type, item in changes:
        if 'icon_id' in item:
            new_icon_ids.add(item['icon_id'])
    
    # 2. Check if sprite sheet needs regeneration
    if len(new_icon_ids) > 0:
        # Regenerate sprite sheet with new icons
        generate_updated_sprites(new_icon_ids)
        
        # Update CSS with new positioning
        update_sprite_css(new_icon_ids)
    
    return len(new_icon_ids) > 0
```

### 7.5 Smart Update Detection
**File:** `scripts/update_detector.py`
```python
class UpdateDetector:
    def detect_lotro_updates(self):
        """Detect if LOTRO companion data has new updates."""
        # 1. Check LOTRO companion repository for new commits
        # 2. Compare with last known good commit
        # 3. Return list of changed files
        
        changed_files = self.git_diff()
        return {
            'items.xml': 'items.xml' in changed_files,
            'progressions.xml': 'progressions.xml' in changed_files,
            'dpsTables.xml': 'dpsTables.xml' in changed_files
        }
    
    def should_update(self, changes):
        """Determine if update is needed based on changes."""
        # Only update if relevant files changed
        relevant_files = ['items.xml', 'progressions.xml', 'dpsTables.xml']
        return any(changes.get(file, False) for file in relevant_files)
```

### 7.6 Automated Update Workflow
**File:** `scripts/automated_update.py`
```python
def automated_update_workflow():
    """Complete automated update workflow."""
    # 1. Check for updates
    detector = UpdateDetector()
    changes = detector.detect_lotro_updates()
    
    if not detector.should_update(changes):
        print("No relevant updates detected")
        return
    
    # 2. Pull latest data
    pull_latest_lotro_data()
    
    # 3. Run incremental curation
    curate_incremental_data(changes)
    
    # 4. Perform incremental import
    incremental_import_items()
    
    # 5. Update sprites if needed
    update_sprites_if_needed()
    
    # 6. Deploy changes
    deploy_incremental_changes()
    
    print(f"Update completed: {len(changes)} files processed")
```

### 7.7 Performance Optimizations
**Strategy:**
- **Batch Processing**: Update multiple items in single transactions
- **Indexed Updates**: Use database indexes for fast item lookups
- **Caching**: Cache frequently accessed progression data
- **Parallel Processing**: Update sprites and database concurrently
- **Rollback Strategy**: Implement transaction rollback for failed updates

### 7.8 Monitoring and Logging
**File:** `scripts/update_monitor.py`
```python
class UpdateMonitor:
    def log_update(self, changes, duration, success):
        """Log update performance and results."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'changes_count': len(changes),
            'duration_seconds': duration,
            'success': success,
            'items_updated': len([c for c in changes if c[0] == 'updated']),
            'items_new': len([c for c in changes if c[0] == 'new'])
        }
        self.append_to_log(log_entry)
    
    def get_update_stats(self):
        """Get update performance statistics."""
        # Return average update time, success rate, etc.
        pass
```

## Implementation Steps

### Step 1: Create Curation System
1. Write `scripts/curate_data.py`
2. Test with sample data
3. Optimize JSON output format
4. Implement gzip compression for deployment

### Step 2: Implement Progression Optimization
1. Create `scripts/optimize_progressions.py`
2. Transform progression data into lookup tables
3. Update stat calculation queries
4. Test performance improvements

### Step 3: Implement Sprite System
1. Write `scripts/generate_sprites.py`
2. Create CSS generation
3. Test sprite rendering

### Step 4: Update Import System
1. Modify import scripts for curated compressed JSON data
2. Update data path configuration
3. Implement lookup table creation
4. Test import process with compressed files

### Step 5: Update Templates
1. Modify item templates for sprites
2. Update base template
3. Test rendering

### Step 6: Update Deployment
1. Modify Dockerfile
2. Update environment configuration
3. Test deployment process

### Step 7: Create Update Process
1. Write update scripts
2. Implement user data preservation
3. Test update workflow

### Step 8: Implement Incremental Updates
1. Create version tracking system
2. Implement incremental import logic
3. Add sprite sheet incremental updates
4. Create automated update workflow
5. Add monitoring and logging
6. Test incremental update performance

## Expected Benefits

### Performance Improvements:
- **50-100x fewer HTTP requests** for icons
- **2-5x faster page loading**
- **50-75% smaller data files** (JSON vs XML)
- **90-95% compression** for deployment files
- **Better browser caching**
- **5-10x faster stat calculations** (progression lookup tables)
- **30-50% reduced memory usage** (optimized data structures)
- **3-5x faster parsing** (JSON vs XML)

### Deployment Benefits:
- **Faster deployments** (compressed data files)
- **More reliable** (no server-side cloning)
- **Version controlled** (curated data in git)
- **Preserves user data** (server-side processing)
- **Reduced database size** (13% storage reduction)
- **Minimal bandwidth usage** (99% smaller deployment files)

### Maintenance Benefits:
- **Easier updates** (local processing)
- **Better debugging** (JSON is human-readable)
- **Reduced server load** (fewer files)
- **Scalable** (sprite sheets scale well)
- **Simplified queries** (no complex joins for stats)
- **Type safety** (Pydantic validation)

### Incremental Update Benefits:
- **10-50x faster updates** (only changed items)
- **Reduced downtime** (partial updates vs full rebuilds)
- **Better reliability** (smaller transaction scope)
- **Efficient resource usage** (minimal processing)
- **Automated detection** (smart update triggers)
- **Rollback capability** (transaction safety)
- **Performance monitoring** (update metrics tracking)

## File Size Estimates

### Current State:
- Full LOTRO companion repos: ~500MB
- Individual icons: ~2-5MB
- Total deployment data: ~50-100MB

### After Optimization:
- Curated JSON files: ~0.5-1MB (50-75% smaller than XML)
- Compressed JSON files: ~0.05-0.1MB (90-95% compression)
- Sprite sheets: ~0.5-1MB
- Total deployment data: ~0.6-1.1MB

**Result: 99% reduction in deployment data size**

## Technical Details

### Data Curation Process:
1. **Parse full repositories** - Read complete LOTRO companion XML data
2. **Filter required data** - Extract only items, progressions, and DPS tables used by the application
3. **Transform to JSON** - Convert XML to optimized JSON format with Pydantic validation
4. **Compress for deployment** - Apply gzip compression for minimal file sizes
5. **Generate metadata** - Track what was included and why

### Progression Table Optimization:
1. **Analyze level ranges** - Current data shows levels 500-550 are most relevant
2. **Create lookup table** - Denormalize progression data into direct level-value mapping
3. **Optimize storage** - Replace 5,038 individual values with 13,464 lookup entries
4. **Improve performance** - Eliminate joins for 5-10x faster stat calculations

**Current Structure:**
- 264 progression tables with 5,038 individual values
- Complex joins required for stat calculations
- Redundant storage of table metadata

**Optimized Structure:**
```sql
CREATE TABLE progression_lookup (
    table_id VARCHAR(50) PRIMARY KEY,
    level_500 FLOAT,
    level_501 FLOAT,
    -- ... up to level_550
    level_550 FLOAT
);
```

**Benefits:**
- **13% storage reduction** (15,400 → 13,464 data points)
- **5-10x faster queries** (direct lookup vs joins)
- **30-50% memory reduction** (single table structure)
- **Simplified queries** (no complex joins needed)

### Sprite Sheet Generation:
1. **Collect icons** - Gather all required item icons
2. **Optimize images** - Standardize sizes, remove duplicates
3. **Arrange grid** - Create optimal layout for sprite sheet
4. **Generate CSS** - Create positioning rules for each icon
5. **Create mapping** - Link icon IDs to sprite positions

### Import System Changes:
1. **Update paths** - Point to curated compressed JSON data instead of full repositories
2. **Modify parsers** - Handle compressed JSON format with automatic decompression
3. **Remove icon copying** - Icons now come from sprite sheets
4. **Add validation** - Ensure curated data integrity with Pydantic validation
5. **Implement lookup tables** - Transform progression data into optimized format

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