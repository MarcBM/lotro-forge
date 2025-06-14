# Release Workflow Documentation

## Current Release Files (Root Level)
- `TODO.md` - Items ready to be worked on
- `IN_PROGRESS.md` - Items currently being worked on  
- `COMPLETED.md` - Items finished in current release
- `RELEASE_NOTES.md` - Core deliverables and goals for current release

## Release Lifecycle

### During Release Development
1. **Starting Work:** Move item from `TODO.md` to `IN_PROGRESS.md`
   - Update description with current status and next steps
   - Keep original ID and priority

2. **Completing Work:** Move item from `IN_PROGRESS.md` to `COMPLETED.md`
   - Add brief note about solution implemented
   - Keep original ID for reference
   - Update relevant checkboxes in `RELEASE_NOTES.md`

### End of Release (Archiving)

1. **Archive Current Release:**
   ```bash
   # Create archive folder with release version and date
   mkdir releases/archive/release-0.1a-YYYY-MM-DD
   
   # Move current files to archive
   mv TODO.md releases/archive/release-0.1a-YYYY-MM-DD/
   mv IN_PROGRESS.md releases/archive/release-0.1a-YYYY-MM-DD/
   mv COMPLETED.md releases/archive/release-0.1a-YYYY-MM-DD/
   mv RELEASE_NOTES.md releases/archive/release-0.1a-YYYY-MM-DD/
   ```

2. **Create New Release Files:**
   - **New TODO.md:** 
     - Migrate incomplete items from archived TODO.md (no changes)
     - Migrate incomplete items from archived IN_PROGRESS.md (update description to show previous work and remaining tasks)
   - **New IN_PROGRESS.md:** Start empty
   - **New COMPLETED.md:** Start empty
   - **New RELEASE_NOTES.md:** Define goals and deliverables for next release

## Item ID Management
- IDs continue sequentially across releases (don't restart at 1)
- When migrating from IN_PROGRESS, keep original ID but update description
- New items get next available ID

## Example Migration

**From Previous Release IN_PROGRESS.md:**
```
### 3. Refactor Templates Directory Structure
**Priority:** High  
**Status:** Partially complete - moved baseline components, still need to reorganize builder templates
**Description:** [Previous work] Moved baseline components to builder section. [Remaining] Need to reorganize remaining builder templates and update imports.
```

**To New Release TODO.md:**
```
### 3. Refactor Templates Directory Structure  
**Priority:** High  
**Previous Work:** Moved baseline components to builder section in Release 0.1a
**Description:** Complete template reorganization by restructuring remaining builder templates and updating all imports to match new structure.
``` 