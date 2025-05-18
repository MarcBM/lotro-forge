# Item System

The item system is designed to handle both primitive (definition) and instantiated (concrete) forms of items in LOTRO.

## Overview

The item system consists of several key components:
- `ItemDefinition`: The primitive form of an item, containing base stats and scaling references
- `Item`: The instantiated form of an item, with concrete stat values
- `ItemStat`: Represents a stat with its scaling reference
- `ConcreteStat`: A stat with a concrete value at a specific item level

## Key Concepts

### Item Definition
The primitive form of an item, containing:
- Base attributes (name, slot, category, etc.)
- Stat definitions with scaling references
- Level requirements and restrictions
- Quality and binding information

### Item Instantiation
The process of creating a concrete item from a definition:
- Selecting an item level
- Calculating concrete stat values
- Applying any modifications or enhancements
- Validating the resulting item

### Stat System
Handles stat definitions and calculations:
- Stat definitions with scaling references
- Stat calculation at specific item levels
- Stat validation and constraints
- Stat combination and modification

## Implementation Details

### Data Structures

#### ItemStat
```python
@dataclass
class ItemStat:
    name: str
    scaling_ref: str
    value: float
```

#### ItemDefinition
```python
@dataclass
class ItemDefinition:
    key: int
    name: str
    min_ilvl: int
    required_player_level: int
    slot: str
    category: str
    binding: str
    durability: int
    quality: str
    stats: List[ItemStat]
```

#### ConcreteStat
```python
@dataclass
class ConcreteStat:
    name: str
    value: float
```

### Item Level System
- Items have a minimum item level (`min_ilvl`)
- Stats scale based on item level
- Item level affects stat calculations
- Item level validation ensures valid ranges

### Player Level Requirements
- Items have a required player level
- Separate from item level
- Affects item usability
- Used for validation

## Future Considerations

### Planned Features
- Essence system integration
- Enhancement system
- Item set bonuses
- Legacy item support
- Item comparison tools

### Potential Improvements
- Performance optimizations
- Additional stat types
- Enhanced validation
- More flexible scaling system 