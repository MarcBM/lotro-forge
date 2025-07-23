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
**Status:** Complete ✅  
**Estimated Time:** 1-2 days

### Tasks:
- [x] Audit all API endpoints to identify current response structures and field naming
- [x] Standardize response format across data and authentication APIs
- [x] Verify all API responses use database field names (no unnecessary renaming)
- [x] Ensure consistent data types across all endpoints (strings, integers, booleans, nulls)
- [x] Standardize error response format across all endpoints
- [x] Update API documentation to reflect standardized responses

### Current API Endpoints Analysis:

**Data API Endpoints** (`/api/data/`):
- `GET /api/data/items/{item_key}` - Individual item details
- `GET /api/data/items/{item_key}/stats` - Item stats at specific ilvl  
- `GET /api/data/items/{item_key}/concrete` - Combined item + stats
- `GET /api/data/equipment/` - Equipment list with filtering/pagination
- `GET /api/data/essences/` - Essence list with filtering/pagination

**Authentication API Endpoints** (`/api/auth/`):
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Current user info
- `PUT /api/auth/users/profile` - Update user profile
- `PUT /api/auth/users/password` - Change password
- `POST /api/auth/admin/users` - Admin create user
- `GET /api/auth/admin/users` - Admin list users
- `PUT /api/auth/admin/users/{user_id}/role` - Admin update user role
- `DELETE /api/auth/admin/users/{user_id}` - Admin delete user

### Response Format Standardization Plan:

**Current State:**
- Data APIs use `{"result": data, "metadata": {...}}` format
- Auth APIs return direct Pydantic models
- Inconsistent response structure across API types

**Proposed Standard:**
- All APIs should use consistent `{"result": data, "metadata": {...}}` format
- Benefits: Consistent structure, easier pagination for auth endpoints, better error handling
- Auth endpoints will wrap Pydantic models in result field
- Metadata can include pagination info, timestamps, etc.

### Field Naming Verification:
- Database uses snake_case (e.g., `base_ilvl`, `essence_type`, `created_at`)
- API responses should preserve database field names
- No camelCase conversion unless data transformation occurs
- Verify all endpoints maintain snake_case consistency

### Data Type Consistency:
- Quality values: uppercase strings (`"COMMON"`, `"UNCOMMON"`, etc.)
- Essence types: uppercase strings (`"BASIC"`, `"PVP"`, etc.)
- Null handling: consistent null values for missing data
- Boolean fields: true/false (not 1/0)
- Timestamps: ISO 8601 format with timezone

### Phase 2 Progress:

**Task 1: Response Format Standardization - COMPLETE ✅**

**Changes Made:**
1. **Created Standardized Response Utilities** (`web/api/utils.py`):
   - `create_api_response()` - Wraps data in consistent `{"result": data, "metadata": {...}}` format
   - `create_paginated_response()` - Handles pagination metadata consistently
   - `create_error_response()` - Standardized error response format

2. **Updated Authentication API Endpoints:**
   - **Public Auth** (`/api/auth/public.py`):
     - `POST /login` - Now returns `{"result": user_data, "metadata": {"session_created": true, "expires_at": "..."}}`
     - `GET /me` - Now returns `{"result": user_data}` or `{"result": null}`
     - `POST /logout` - Unchanged (204 No Content)
   
   - **User Management** (`/api/auth/users.py`):
     - `PUT /profile` - Now returns `{"result": user_data, "metadata": {"updated_at": "..."}}`
     - `PUT /password` - Unchanged (204 No Content)
   
       - **Admin Management** (`/api/auth/admin.py`):
      - `POST /users/simple` - Now returns `{"result": admin_data, "metadata": {"created_at": "...", "temp_email": true}}`
      - `GET /users` - Now returns `{"result": user_list, "metadata": {"total_users": N, "retrieved_at": "..."}}`
      - `PUT /users/{user_id}/role` - Now returns `{"result": user_data, "metadata": {"updated_at": "...", "role_changed": true}}`
      - `DELETE /users/{user_id}` - Unchanged (204 No Content)

**Benefits Achieved:**
- ✅ Consistent response structure across all APIs
- ✅ Metadata support for pagination, timestamps, and status info
- ✅ Easier frontend handling with predictable response format
- ✅ Foundation for future pagination in auth endpoints
- ✅ Better error handling capabilities with standardized format
- ✅ Simplified implementation by removing unnecessary Pydantic response models
- ✅ Consistent with data API endpoints that use plain JSON dictionaries
- ✅ All APIs now use standardized utility functions (`create_api_response`, `create_paginated_response`)

**Phase 2 Summary:**
All API endpoints now use standardized response formats with consistent field naming, data types, and error handling. The API is ready for frontend integration with predictable response structures across all endpoints.

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