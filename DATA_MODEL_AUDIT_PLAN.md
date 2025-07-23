# Data Model Structure Consistency Audit Plan

## Overview
Standardize data models across the application to ensure consistency from database through API to frontend. The database is the source of truth - field names should match database column names, and API endpoints should not rename fields unless data is being transformed.

## Key Principles
- **Database is the source of truth** - field names should match database column names
- **No unnecessary field renaming** in API responses unless data is being transformed
- **Consistent data types** across all serialization methods
- **Frontend adapts** to standardized data, not the other way around

## Phase 1: Database Model Audit
**Status:** Complete  
**Estimated Time:** 1 day

### Tasks:
- [x] Examine all database models and their serialization methods (`to_json`, `to_list_json`, `get_stats_json`)
- [x] Identify inconsistencies in field naming and data types across serialization methods
- [x] Create unified ValueLookupTable system to replace DpsTable and ProgressionTable
- [x] Standardize serialization methods to use consistent field names and data types

### Notes:
- Focus on items, equipment, essences, and other core data models
- Document any field name mismatches between database columns and serialized output
- Ensure consistent handling of null values, empty strings, and data types

### Findings:
**Database Models Examined:**
- `Item` (base model) - has `to_json()`, `to_list_json()`, `get_stats_json()`
- `EquipmentItem` - extends Item, adds equipment-specific fields
- `Essence` - extends Item, adds essence-specific fields  
- `ItemStat` - represents stats on items
- `LookupTable` & `LookupValue` - for any progression-based calculations
- `User` & `UserSession` - user authentication models

**Key Inconsistencies Identified:**
1. **Field Naming Inconsistencies:**
   - Database uses `snake_case` (e.g., `base_ilvl`, `armour_type`, `essence_type`)
   - **RESOLVED**: Quality values now consistently use uppercase strings
   - **RESOLVED**: Essence types now consistently use uppercase strings (BASIC, PVP, CLOAK, etc.)
   - **RESOLVED**: Removed `essence_type_name` property - now using `essence_type` directly
   - **RESOLVED**: Socket types now consistently use uppercase strings to match essence types (BASIC, PRIMARY, VITAL, etc.)

2. **Data Type Inconsistencies:**
   - **RESOLVED**: Quality values now consistently use uppercase strings (no more enum conversion)
   - **RESOLVED**: Essence types now consistently use uppercase strings (no more integer mapping)
   - **RESOLVED**: Icon URLs now return null when no icon exists (instead of empty array)
   - **RESOLVED**: Socket fields now always included in API responses (null when no sockets)
   - **RESOLVED**: Stat values now return null for missing stats (instead of 0.0)
   - **RESOLVED**: Optional fields always included in API responses (even when null)
   - **RESOLVED**: Null handling now consistently returns null for missing data (instead of 0.0)
   - **RESOLVED**: Icon URLs now consistently use processed format across all serialization methods
   - **IMPROVED**: Created generic Icon and EntityIcon models in single file for better performance and storage efficiency
   - **ENHANCED**: Added required dimensions, sprite sheet versioning, and validation methods for production sprite sheet support
   - **OPTIMIZED**: Separated sprite sheet versioning into dedicated table for improved space efficiency
   - **ENHANCED**: Added proper foreign key relationships for sprite sheets with referential integrity

3. **Serialization Method Inconsistencies:**
   - **RESOLVED**: Maintained original purpose of serialization methods
   - **RESOLVED**: Ensured consistent inheritance patterns for subclasses
   - **RESOLVED**: Kept calculated fields in appropriate methods
   
   **CORRECTED UNDERSTANDING:**
   
   **Method Purposes:**
   - `to_json()`: Complete item data for full object views (includes calculated fields)
   - `to_list_json()`: Minimal data for list views (performance optimized)
   - `get_stats_json()`: Stats-only data for stat calculations
   
   **Consistent Inheritance:**
   - EquipmentItem.to_json() adds: slot, type, total_sockets, sockets
   - EquipmentItem.to_list_json() adds: slot (minimal for lists)
   - Essence.to_json() adds: tier, essence_type
   - Essence.to_list_json() adds: essence_type (minimal for lists)
   
   **Database vs Calculated Fields:**
   - Base Item: stat_names (database field via relationship)
   - EquipmentItem: total_sockets, sockets (calculated fields)

4. **Value Table System Inconsistencies:**
   - **RESOLVED**: Created unified `ValueLookupTable` system to replace `DpsTable` and `ProgressionTable`
   - Updated `ItemStat` and `Weapon` models to use the new unified system
   - **IMPROVED**: Quality modifiers are now nullable (most tables won't use them)
   - **IMPROVED**: Exact level lookup with quality modifier support and warning system
   - **IMPROVED**: Simplified API - pass quality string directly instead of index mapping
   - **CLEANUP**: Deleted old `dps.py` and `progressions.py` model files
   - **CLEANUP**: Updated imports to remove references to old models

5. **Equipment Model Consolidation:**
   - **RESOLVED**: Merged `Weapon` model into `EquipmentItem` 
   - **RESOLVED**: Replaced `armour_type` and `weapon_type` with unified `type` field
   - **RESOLVED**: Removed DPS-specific fields (DPS will be handled as a stat)
   - **IMPROVED**: Updated `ItemStat.get_value()` to support quality modifiers for DPS stats
   - **IMPROVED**: Updated `Item.get_stats_at_ilvl()` to pass quality to stat calculations
   - **CLEANUP**: Deleted `weapon.py` model file
   - **CLEANUP**: Updated imports to remove Weapon model references

---

## Phase 2: API Endpoint Standardization
**Status:** Not Started  
**Estimated Time:** 1-2 days

### Tasks:
- [ ] Audit all API endpoints to ensure they preserve database field names
- [ ] Fix any endpoints that rename fields unnecessarily
- [ ] Ensure consistent data types across all endpoints (strings, integers, booleans, nulls)

### Notes:
- API responses should maintain database field names unless data transformation is occurring
- Check for any camelCase vs snake_case inconsistencies
- Verify nested object structures are consistent across similar endpoints

---

## Phase 3: Frontend Updates
**Status:** Not Started  
**Estimated Time:** 1 day

### Tasks:
- [ ] Update frontend code that expects different field names
- [ ] Test all frontend functionality to ensure it works with standardized data

### Notes:
- Identify any hardcoded field name assumptions in frontend code
- Update any JavaScript/TypeScript interfaces or type definitions
- Test all pages and components that consume API data

---

## Phase 4: Testing and Validation
**Status:** Not Started  
**Estimated Time:** 1 day

### Tasks:
- [ ] Comprehensive testing of all endpoints and frontend functionality
- [ ] Verify no regressions in existing functionality
- [ ] Test edge cases (null values, empty data, etc.)

### Notes:
- Run existing test suite to ensure no breaking changes
- Test all major user workflows
- Verify data consistency across different pages and features

---

## Progress Tracking

### Completed Tasks:
*(None yet)*

### Current Blockers:
*(None identified)*

### Notes and Decisions:
*(To be filled as work progresses)*

---

## Success Criteria
- [ ] All serialization methods use consistent field names matching database columns
- [ ] All API endpoints preserve database field names (unless data transformation occurs)
- [ ] Frontend code works with standardized data structures
- [ ] No regressions in existing functionality
- [ ] Consistent data types across all layers of the application 