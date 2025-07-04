/**
 * Client-side equipment filter configuration to avoid API calls for filter options
 */

// Maps slot groups to their database slots
const EQUIPMENT_SLOT_GROUPS = {
    "EAR": ["EAR", "LEFT_EAR", "RIGHT_EAR"],
    "LEFT_EAR": ["EAR", "LEFT_EAR"],
    "RIGHT_EAR": ["EAR", "RIGHT_EAR"],
    "NECK": ["NECK"],
    "POCKET": ["POCKET"],
    "WRIST": ["WRIST", "LEFT_WRIST", "RIGHT_WRIST"],
    "LEFT_WRIST": ["WRIST", "LEFT_WRIST"],
    "RIGHT_WRIST": ["WRIST", "RIGHT_WRIST"],
    "FINGER": ["FINGER", "LEFT_FINGER", "RIGHT_FINGER"],
    "LEFT_FINGER": ["FINGER", "LEFT_FINGER"],
    "RIGHT_FINGER": ["FINGER", "RIGHT_FINGER"],
    "HEAD": ["HEAD"],
    "SHOULDER": ["SHOULDER"],
    "BACK": ["BACK"],
    "CHEST": ["CHEST"],
    "HAND": ["HAND"],
    "LEGS": ["LEGS"],
    "FEET": ["FEET"],
    "MAIN_HAND": ["MAIN_HAND", "EITHER_HAND"],
    "OFF_HAND": ["OFF_HAND", "EITHER_HAND"],
    "RANGED_ITEM": ["RANGED_ITEM"],
    "CLASS_SLOT": ["CLASS_SLOT"]
};

// Slots only shown in character builder
const BUILDER_ONLY_SLOT_GROUPS = [
    "Left Ear", "Right Ear", "Left Wrist", "Right Wrist", "Left Finger", "Right Finger"
];

// Display order for slot dropdown
const EQUIPMENT_SLOT_GROUP_ORDER = [
    "Ear", "Left Ear", "Right Ear", "Neck", "Pocket", "Wrist", "Left Wrist", "Right Wrist", "Finger", "Left Finger", "Right Finger", 
    "Head", "Shoulder", "Back", "Chest", "Hand", "Legs", "Feet",
    "Main Hand", "Off Hand", "Ranged Item", "Class Slot"
];

// All valid equipment slots
const EQUIPMENT_SLOTS = [
    "EAR", "LEFT_EAR", "RIGHT_EAR",
    "NECK",
    "POCKET",
    "WRIST", "LEFT_WRIST", "RIGHT_WRIST",
    "FINGER", "LEFT_FINGER", "RIGHT_FINGER",
    "HEAD",
    "SHOULDER",
    "BACK",
    "CHEST",
    "HAND",
    "LEGS",
    "FEET",
    "MAIN_HAND", "OFF_HAND", "EITHER_HAND",
    "RANGED_ITEM",
    "CLASS_SLOT"
];

class EquipmentFilters extends BaseFilters {
    
    // Get slot groups for dropdown, excluding builder-only slots if not in builder mode
    static getSlotGroups(builderMode = false) {
        const groups = [];
        
        for (const groupName of EQUIPMENT_SLOT_GROUP_ORDER) {
            
            if (!builderMode && BUILDER_ONLY_SLOT_GROUPS.includes(groupName)) {
                continue;
            }
            
            groups.push({
                key: groupName.toUpperCase().replace(/\s+/g, "_"),
                label: groupName
            });
        }
        
        return groups;
    }
    
    // Get sort options, including EV if in builder mode
    static getSortOptions(builderMode = false) {
        const options = super.getSortOptions(builderMode);
        if (builderMode) {
            options.unshift({ value: 'ev', label: 'EV' });
        }
        return options;
    }
    
    // Get all filter options and their states
    static getAllFilters(builderMode = false) {
        const baseFilters = super.getAllFilters(builderMode);
        return {
            ...baseFilters,
            slot: {
                options: this.getSlotGroups(builderMode),
                locked: false
            }
        };
    }
    
    // Build API URL with current filters and pagination
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        
        if (filterState.slot) {
            const selectedGroup = EQUIPMENT_SLOT_GROUPS[filterState.slot];
            if (selectedGroup) {
                selectedGroup.forEach(slot => params.append('slots', slot));
            }
        }

        return `/api/data/equipment/?${params.toString()}`;
    }
}

window.EquipmentFilters = EquipmentFilters;