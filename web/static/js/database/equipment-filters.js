/**
 * Equipment Filter Configuration
 * 
 * This file contains the client-side filter configuration for equipment slots,
 * removing the need for API calls to get filter options.
 */

// Slot grouping configuration for dropdown display
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

const BUILDER_ONLY_SLOT_GROUPS = [
    "Left Ear", "Right Ear", "Left Wrist", "Right Wrist", "Left Finger", "Right Finger"
];

// Ordered list for consistent dropdown display
const EQUIPMENT_SLOT_GROUP_ORDER = [
    "Ear", "Left Ear", "Right Ear", "Neck", "Pocket", "Wrist", "Left Wrist", "Right Wrist", "Finger", "Left Finger", "Right Finger", 
    "Head", "Shoulder", "Back", "Chest", "Hand", "Legs", "Feet",
    "Main Hand", "Off Hand", "Ranged Item", "Class Slot"
];

// All possible equipment slots (for reference and validation)
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

/**
 * Equipment Filter Helper Class
 */
class EquipmentFilters {
    
    /**
     * Get all slot groups with their display names and database slots
     * @returns {Array} Array of slot group objects
     */
    static getSlotGroups(builderMode = false) {
        const groups = [];
        
        for (const groupName of EQUIPMENT_SLOT_GROUP_ORDER) {
            
            // If not builder mode, exclude groups that are only available in builder mode
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
    
    /**
     * Get available sort options for equipment
     * @returns {Array} Array of sort option objects
     */
    static getSortOptions(builderMode = false) {
        const options = [];
        if (builderMode) {
            options.push({ value: 'ev', label: 'EV' });
        }
        options.push({ value: 'name', label: 'Name' });
        options.push({ value: 'recent', label: 'Recent' });
        options.push({ value: 'base_ilvl', label: 'Base iLvl' });
        return options;
    }
    
    /**
     * Get all available filters with their options and lock status
     * @returns {Object} Object containing all filter configurations
     */
    static getAllFilters(builderMode = false) {
        return {
            sort: {
                options: this.getSortOptions(builderMode)
            },
            search: {
                value: ''
            },
            slot: {
                options: this.getSlotGroups(builderMode),
                locked: false
            }
            // Future filters (quality, level, etc.) will be added here
        };
    }
    
    /**
     * Build the complete API URL for equipment requests using filterState
     * @param {Object} filterState - The current filter state object
     * @param {number} offset - Pagination offset
     * @param {number} limit - Pagination limit
     * @returns {string} Complete API URL with query parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = new URLSearchParams();
        
        // Pagination
        params.append('limit', limit);
        params.append('skip', offset);
        
        // Slot filtering - convert slot filter to actual slots array
        if (filterState.slot) {
            const selectedGroup = EQUIPMENT_SLOT_GROUPS[filterState.slot];
            if (selectedGroup) {
                selectedGroup.forEach(slot => params.append('slots', slot));
            }
        }
        
        // Search
        if (filterState.search) {
            params.append('search', filterState.search);
        }
        
        // Sorting
        if (filterState.sort) {
            params.append('sort', filterState.sort);
        }

        return `/api/data/equipment/?${params.toString()}`;
    }
}

// Export for use in other modules
window.EquipmentFilters = EquipmentFilters;