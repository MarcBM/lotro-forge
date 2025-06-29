# Builder Page Design

## Overview

The builder page is a comprehensive character build planner for LOTRO that allows players to:
- Replicate their in-game builds with 100% accuracy
- Plan potential builds with confidence that in-game stats will match
- Use the build data as a foundation for future optimization tools

User Experience is paramount - the system should provide immediate feedback and smooth interactions.

## Core Architecture

### Alpine.js Component Hierarchy

```
panelManager (top level)
└── buildState (central data store)
    ├── utility-panel
    ├── equipment-manager
    ├── essence-manager
    ├── legendary-manager
    ├── traits-manager
    ├── buffs-manager
    ├── stats-engine
    └── ... (future managers)
```

### Build State - Central Data Store

The `buildState` serves as the single source of truth for all build data. It contains:

#### Data Structure
```javascript
{
  // Character metadata
  character: {
    name: string,
    level: number,
    class: string,
    race: string
  },
  
  // Raw equipment data (no derived stats)
  equipment: {
    HEAD: EquipmentItem | null,
    CHEST: EquipmentItem | null,
    // ... all equipment slots
  },
  
  // Essence data
  essences: {
    [slotId]: EssenceItem[]
  },
  
  // Legendary items and tracery data
  legendary: {
    mainHand: LegendaryItem,
    classItem: LegendaryItem
  },
  
  // Character traits and buffs
  traits: Trait[],
  buffs: Buff[],
  
  // Build metadata
  buildName: string,
  buildNotes: string,
  lastModified: Date
}
```

#### Principles
- **Raw Data Only**: Build state stores only the base data, no derived calculations
- **Immutable Updates**: Managers update build state through defined methods
- **Reactive Foundation**: All managers can react to build state changes automatically
- **No Business Logic**: Build state is purely data storage

## Manager System

### Manager Responsibilities

Each manager is responsible for:
1. **Editing specific aspects** of the character build
2. **Opening/closing panels** for item selection
3. **Updating build state** when changes are made
4. **Providing UI interactions** for their domain

### Manager Examples

#### Equipment Manager
- Manages equipment slot interactions
- Opens equipment selection panel
- Updates build state when equipment is selected
- Handles equipment-specific validation

#### Stats Engine
- **Reads** from build state (no writes)
- Calculates derived statistics from raw data
- Provides reactive stat displays
- Handles complex stat calculations and formulas

#### Essence Manager
- Manages essence slot interactions
- Opens essence selection panel
- Updates build state when essences are added/removed
- Handles essence compatibility validation

### Manager Communication

#### State-First Architecture (Primary Pattern)
**Managers only interface with the central build state.** Since users can only take one action at a time, when a manager updates the build state, all other managers automatically receive the most up-to-date information through Alpine.js reactivity.

```javascript
// Equipment manager updates build state
updateEquipment(slot, item) {
  this.equipment[slot] = item;
  // Alpine.js automatically triggers reactivity
  // Stats engine recalculates automatically
  // Essence manager can access updated equipment data
}

// Stats engine automatically reacts to changes
calculateTotalMight() {
  // Always has the most current equipment data
  return Object.values(this.equipment)
    .filter(item => item)
    .reduce((total, item) => total + (item.might || 0), 0);
}
```

#### Benefits of State-First Communication
- **Simplified Architecture**: No complex event systems or direct manager-to-manager communication
- **Guaranteed Consistency**: All managers always see the same, current state
- **Automatic Updates**: Alpine.js handles all reactivity automatically
- **Easier Debugging**: Single source of truth makes issues easier to trace
- **Predictable Data Flow**: Changes always flow through the central state

#### Direct Access (When Needed)
Managers can access build state properties directly:
```javascript
// Access build state properties
this.character.name
this.equipment.HEAD
this.essences
```

#### Event System (Rare Cases Only)
Events should only be used for:
- External integrations
- Complex UI interactions that span multiple components
- Performance optimizations (when necessary)

```javascript
// Example: Notify external systems of build changes
window.dispatchEvent(new CustomEvent('build-changed', {
  detail: { buildId: this.buildId, timestamp: Date.now() }
}));
```

## Reactive Data Flow

### Automatic Updates
Alpine.js's reactivity means that when build state changes, all dependent displays update automatically:

```javascript
// Stats engine automatically recalculates when equipment changes
// No manual update calls needed
```

### Complex Calculations
The stats engine can access build state properties directly for calculations:

```javascript
// Example: Calculate total might from equipment
calculateTotalMight() {
  return Object.values(this.equipment)
    .filter(item => item)
    .reduce((total, item) => total + (item.might || 0), 0);
}
```

### Performance Considerations
- Alpine.js efficiently tracks dependencies
- Complex calculations can be memoized if needed
- Reactive updates are batched for performance

## Panel Integration

### Database Panel Reuse
Many builder panels will reuse database panels:
- Equipment selection → database equipment panel
- Essence selection → database essence panel
- Tracery selection → database tracery panel

### Panel Communication
```javascript
// Builder panel opens database panel with context
openEquipmentPanel(slotName) {
  this.selectedSlot = slotName;
  this.$parent.openPanel('equipment');
}

// Database panel communicates selection back
selectEquipment(item) {
  this.$parent.equipmentManager.updateSlot(this.selectedSlot, item);
  this.$parent.closePanel('equipment');
}
``` 