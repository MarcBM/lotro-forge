# LOTRO Forge Data Definitions

This document defines the standardized values used throughout the LOTRO Forge application for various item properties and characteristics.

## Quality Values

Quality values represent the rarity and power level of items in LOTRO. All quality values are stored as uppercase strings in the database.

### Valid Quality Values:
- `"COMMON"` - Basic quality items
- `"UNCOMMON"` - Uncommon quality items  
- `"RARE"` - Rare quality items
- `"INCOMPARABLE"` - Incomparable quality items
- `"LEGENDARY"` - Legendary quality items

### Usage:
- **Database Field**: `items.quality` (String(16))
- **API Responses**: Uppercase strings
- **Frontend Display**: Quality-based color coding and styling

### Quality Index Mapping (for Lookup Tables):
When used with quality modifiers in lookup tables, qualities are mapped to array indices:
- `"COMMON"` → index 0
- `"UNCOMMON"` → index 1  
- `"RARE"` → index 2
- `"INCOMPARABLE"` → index 3
- `"LEGENDARY"` → index 4

---

## Essence Types

Essence types define the category and socket compatibility of essence items. All essence types are stored as uppercase strings in the database.

### Valid Essence Types:
- `"BASIC"` - Basic essences (socket type: Basic)
- `"PVP"` - PvP essences (socket type: PvP)
- `"CLOAK"` - Cloak essences (socket type: Cloak)
- `"NECKLACE"` - Necklace essences (socket type: Necklace)
- `"PRIMARY"` - Primary essences (socket type: Primary)
- `"VITAL"` - Vital essences (socket type: Vital)

### Usage:
- **Database Field**: `essences.essence_type` (String(8))
- **API Responses**: Uppercase strings
- **Frontend Display**: Direct display of essence type

### Import Mapping:
During data import, XML integer values are mapped to strings:
- `1` → `"BASIC"`
- `18` → `"PVP"`
- `19` → `"CLOAK"`
- `20` → `"NECKLACE"`
- `22` → `"PRIMARY"`
- `23` → `"VITAL"`

---

## Equipment Types

Equipment types define the category and characteristics of equipment items. All equipment types are stored as uppercase strings in the database.

### Armor Types:
- `"HEAVY"` - Heavy armor (Champion, Guardian, etc.)
- `"MEDIUM"` - Medium armor (Hunter, Warden, etc.) 
- `"LIGHT"` - Light armor (Lore-master, Minstrel, etc.)
- `"SHIELD"` - Standard shields
- `"WARDEN_SHIELD"` - Warden-specific shields
- `"HEAVY_SHIELD"` - Heavy shields for Guardian class

### Weapon Types:
- `"BOW"` - Bows
- `"CROSSBOW"` - Crossbows
- `"ONE_HANDED_SWORD"` - One-handed swords
- `"TWO_HANDED_SWORD"` - Two-handed swords
- `"ONE_HANDED_AXE"` - One-handed axes
- `"TWO_HANDED_AXE"` - Two-handed axes
- `"ONE_HANDED_MACE"` - One-handed maces
- `"TWO_HANDED_MACE"` - Two-handed maces
- `"DAGGER"` - Daggers
- `"SPEAR"` - Spears
- `"STAFF"` - Staves
- `"CLUB"` - Clubs
- `"HAMMER"` - Hammers
- `"HALBERD"` - Halberds

### Usage:
- **Database Field**: `equipment_items.type` (String(50))
- **API Responses**: Uppercase strings
- **Frontend Display**: Direct display of equipment type

---

## Socket Types

Socket types define the different categories of essence sockets on equipment items. Socket types match essence types exactly for consistency.

### Valid Socket Types:
- `"BASIC"` - Basic essence sockets
- `"PRIMARY"` - Primary essence sockets
- `"VITAL"` - Vital essence sockets
- `"CLOAK"` - Cloak essence sockets
- `"NECKLACE"` - Necklace essence sockets
- `"PVP"` - PvP essence sockets

### Usage:
- **Database Fields**: `equipment_items.sockets_basic`, `sockets_primary`, etc. (Integer)
- **API Responses**: Nested object structure: `{ "sockets": { "BASIC": 1, "PRIMARY": 2, ... } }`
- **Frontend Display**: Socket count display and essence compatibility

### Socket String Mapping:
During import, XML socket strings are parsed:
- `'S'` → `"BASIC"`
- `'P'` → `"PRIMARY"`
- `'V'` → `"VITAL"`
- `'C'` → `"CLOAK"`
- `'N'` → `"NECKLACE"`
- `'W'` → `"PVP"`

Example: `"SPV"` → `{ "BASIC": 1, "PRIMARY": 1, "VITAL": 1, ... }`

---

## Data Consistency Rules

### Field Naming:
- Database columns use `snake_case`
- API responses preserve database field names unless data transformation occurs
- Frontend adapts to standardized data structures

### Data Types:
- Quality and essence types: Uppercase strings
- Equipment types: Uppercase strings
- Socket counts: Integers
- Stat values: Floats

### Null Handling:
- Missing values should be `null` in JSON responses
- Database uses `NULL` for missing values
- Frontend handles `null` values gracefully

### Validation:
- All enum-like values should be validated during import
- Invalid values should be logged and handled appropriately
- Frontend should display fallback text for unknown values 