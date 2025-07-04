/**
 * Equipment Manager - Alpine.js controller for equipment interactions
 * Handles equipment slot interactions and API calls
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentManager', () => ({
        // Reference to the build state component
        buildState: null,
        
        // Reference to the database controller
        databaseController: null,
        
        // Locked filters for equipment selection
        lockedFilters: {
            slot: null, // Will be set to 'HEAD', 'CHEST', etc.
            // Future: quality: null, level: null, etc.
        },
        
        // Methods will be added as needed
        init() {
            logComponent('EquipmentManager', 'initialized');
            // Get direct reference to build state component
            const buildStateElement = document.getElementById('build-state');
            this.buildState = Alpine.$data(buildStateElement);
            logDebug('Build state reference obtained');
            
            // Get direct reference to database controller
            const databaseControllerElement = document.getElementById('database-controller');
            if (databaseControllerElement) {
                this.databaseController = Alpine.$data(databaseControllerElement);
                logDebug('Database controller reference obtained');
            } else {
                logWarn('Database controller not found during initialization');
            }
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
         * Equip the currently selected item from the database panel
         * Creates appropriate Equipment/Weapon object and places it in the build state
         */
        equipSelectedItem() {
            if (!this.databaseController) {
                logError('Database controller not available');
                return;
            }
            
            if (!this.databaseController.selectedData || !this.databaseController.selectedData.key) {
                logWarn('No item selected to equip');
                return;
            }

            const item = this.databaseController.selectedData;
            const targetSlot = this.lockedFilters.slot;
            
            if (!targetSlot) {
                logError('No target slot specified for equipping');
                return;
            }

            try {
                // Create the appropriate equipment object based on item type
                let equipmentObject;
                
                if (item.weapon_type) {
                    // Create Weapon object for weapon items
                    equipmentObject = new Weapon(item);
                } else {
                    // Create Equipment object for regular equipment
                    equipmentObject = new Equipment(item);
                }

                logInfo(`Build State:`, this.buildState);

                // Update the build state with the new equipment
                if (this.buildState.equipItem(targetSlot, equipmentObject)) {
                    logInfo(`Updated equipment for ${targetSlot}:`, equipmentObject);
                } else {
                    logError(`Failed to equip ${item.name} to ${targetSlot}`);
                }
                
                // Close the equipment selection panel
                this.closePanel(['equipment-selection', 'equipment']);
            } catch (error) {
                logError('Error equipping item:', error);
            }
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