/**
 * Equipment Manager - Alpine.js controller for equipment interactions
 * Handles equipment slot interactions and API calls
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentManager', () => ({
        // Reference to the build state component
        buildState: null,
        
        // Locked filters for equipment selection
        lockedFilters: {
            slot: null, // Will be set to 'HEAD', 'CHEST', etc.
            // Future: quality: null, level: null, etc.
        },
        
        // Methods will be added as needed
        init() {
            logComponent('EquipmentManager', 'initialized');
            // Get direct reference to build state component
            const buildStateElement = document.getElementById('builder-component');
            this.buildState = Alpine.$data(buildStateElement);
            logDebug('Build state reference obtained');
        },

        /**
         * Print the slot name to console when clicked
         * @param {string} slotName - The name of the equipment slot
         */
        printSlot(slotName) {
            try {
                const currentItem = this.getEquipment(slotName);
                if (currentItem) {
                    logDebug(`${slotName}: ${currentItem.name || 'Unknown Item'}`);
                } else {
                    logDebug(`${slotName}: Empty`);
                }
            } catch (error) {
                logError(`Equipment slot clicked: ${slotName} (Build state not accessible)`, error);
            }
        },

        /**
         * Get equipment from build state for a specific slot
         * @param {string} slotName - The name of the equipment slot
         * @returns {Object|null} The equipment item or null if empty
         */
        getEquipment(slotName) {
            return this.buildState.equipment[slotName] || null;
        },

        /**
         * Update equipment in build state for a specific slot
         * @param {string} slotName - The name of the equipment slot
         * @param {Object} item - The equipment item to set
         */
        updateEquipment(slotName, item) {
            this.buildState.equipment[slotName] = item;
            logInfo(`Updated equipment for ${slotName}:`, item);
        },

        /**
         * Open equipment selection modal for a specific slot
         * @param {string} slotName - The name of the equipment slot
         */
        openEquipmentSelection(slotName) {
            logInfo('Opening equipment selection for slot:', slotName);
            this.lockedFilters.slot = slotName;
            this.openPanel(['equipment-selection', 'equipment']);
        }
    }));
}); 