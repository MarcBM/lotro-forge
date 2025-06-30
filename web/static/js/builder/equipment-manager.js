/**
 * Equipment Manager - Alpine.js controller for equipment interactions
 * Handles equipment slot interactions and API calls
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentManager', () => ({
        // Reference to the build state component
        buildState: null,
        
        // Methods will be added as needed
        init() {
            console.log('Equipment Manager initialized');
            // Get direct reference to build state component
            const buildStateElement = document.getElementById('builder-component');
            this.buildState = Alpine.$data(buildStateElement);
            console.log('Build state reference obtained');
        },

        /**
         * Print the slot name to console when clicked
         * @param {string} slotName - The name of the equipment slot
         */
        printSlot(slotName) {
            try {
                const currentItem = this.getEquipment(slotName);
                if (currentItem) {
                    console.log(`${slotName}: ${currentItem.name || 'Unknown Item'}`);
                } else {
                    console.log(`${slotName}: Empty`);
                }
            } catch (error) {
                console.log(`Equipment slot clicked: ${slotName} (Build state not accessible)`);
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
            console.log(`Updated equipment for ${slotName}:`, item);
        }
    }));
}); 