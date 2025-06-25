/**
 * Equipment Filter Configuration
 * 
 * This file contains the client-side filter configuration for equipment slots,
 * removing the need for API calls to get filter options.
 */

// Slot grouping configuration for dropdown display
const EQUIPMENT_SLOT_GROUPS = {
    "Ear": ["EAR", "LEFT_EAR", "RIGHT_EAR"],
    "Neck": ["NECK"],
    "Pocket": ["POCKET"],
    "Wrist": ["WRIST", "LEFT_WRIST", "RIGHT_WRIST"],
    "Finger": ["FINGER", "LEFT_FINGER", "RIGHT_FINGER"],
    "Head": ["HEAD"],
    "Shoulder": ["SHOULDER"],
    "Back": ["BACK"],
    "Chest": ["CHEST"],
    "Hands": ["HAND"],
    "Legs": ["LEGS"],
    "Feet": ["FEET"],
    "Main Hand": ["MAIN_HAND", "EITHER_HAND"],
    "Off Hand": ["OFF_HAND", "EITHER_HAND"],
    "Ranged Item": ["RANGED_ITEM"],
    "Class Slot": ["CLASS_SLOT"]
};

// Ordered list for consistent dropdown display
const EQUIPMENT_SLOT_GROUP_ORDER = [
    "Ear", "Neck", "Pocket", "Wrist", "Finger", 
    "Head", "Shoulder", "Back", "Chest", "Hands", "Legs", "Feet",
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
     * @param {Array} availableSlots - Optional array of slots available in database
     * @returns {Array} Array of slot group objects
     */
    static getSlotGroups(availableSlots = null) {
        const groups = [];
        
        for (const groupName of EQUIPMENT_SLOT_GROUP_ORDER) {
            const slots = EQUIPMENT_SLOT_GROUPS[groupName];
            
            // If availableSlots is provided, filter to only groups with available slots
            if (availableSlots) {
                const hasAvailableSlots = slots.some(slot => availableSlots.includes(slot));
                if (!hasAvailableSlots) continue;
            }
            
            groups.push({
                key: groupName.toUpperCase().replace(/\s+/g, "_"),  // e.g., "MAIN_HAND"
                label: groupName,  // e.g., "Main Hand"
                slots: slots  // The actual database slots this group represents
            });
        }
        
        return groups;
    }
    
    /**
     * Get available sort options for equipment
     * @returns {Array} Array of sort option objects
     */
    static getSortOptions() {
        return [
            { value: 'name', label: 'Name' },
            { value: 'recent', label: 'Recent' },
            { value: 'base_ilvl', label: 'Base iLvl' }
        ];
    }
    
    /**
     * Build query parameters for equipment API call
     * @param {Object} filters - Filter configuration object
     * @returns {URLSearchParams} URL search parameters
     */
    static buildQueryParams(filters) {
        const params = new URLSearchParams();
        
        // Pagination
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.skip) params.append('skip', filters.skip);
        
        // Slot filtering - supports both groups and individual slots
        if (filters.slots && filters.slots.length > 0) {
            filters.slots.forEach(slot => params.append('slots', slot));
        }
        
        // Search
        if (filters.search) params.append('search', filters.search);
        
        // Sorting
        if (filters.sort) params.append('sort', filters.sort);
        
        return params;
    }
}

// Export for use in other modules
window.EquipmentFilters = EquipmentFilters;

// Also export constants for direct access
window.EQUIPMENT_SLOT_GROUPS = EQUIPMENT_SLOT_GROUPS;
window.EQUIPMENT_SLOT_GROUP_ORDER = EQUIPMENT_SLOT_GROUP_ORDER;
window.EQUIPMENT_SLOTS = EQUIPMENT_SLOTS;