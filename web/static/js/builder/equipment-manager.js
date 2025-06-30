/**
 * Equipment Manager - Alpine.js controller for equipment interactions
 * Handles equipment slot interactions and API calls
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentManager', () => ({
        // Properties will be defined as needed
        
        // Methods will be added as needed
        init() {
            console.log('Equipment Manager initialized');
            // Initialization logic
        },

        /**
         * Print the slot name to console when clicked
         * @param {string} slotName - The name of the equipment slot
         */
        printSlot(slotName) {
            console.log(`Equipment slot clicked: ${slotName}`);
        },

        /**
         * Get equipment from build state for a specific slot
         * @param {string} slotName - The name of the equipment slot
         * @returns {Object|null} The equipment item or null if empty
         */
        getEquipment(slotName) {
            return this.$parent.equipment[slotName] || null;
        },

        /**
         * Update equipment in build state for a specific slot
         * @param {string} slotName - The name of the equipment slot
         * @param {Object} item - The equipment item to set
         */
        updateEquipment(slotName, item) {
            this.$parent.equipment[slotName] = item;
            console.log(`Updated equipment for ${slotName}:`, item);
        }
    }));
}); 