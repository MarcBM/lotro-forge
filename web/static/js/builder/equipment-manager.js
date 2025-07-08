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
        
        // Currently selected item key for pre-selection
        selectedItem: null,
        
        // Methods will be added as needed
        init() {
            // Get direct reference to build state component
            const buildStateElement = document.getElementById('build-state');
            this.buildState = Alpine.$data(buildStateElement);
            
            // Get direct reference to database controller
            const databaseControllerElement = document.getElementById('database-controller');
            if (databaseControllerElement) {
                this.databaseController = Alpine.$data(databaseControllerElement);
            } else {
                logWarn('Database controller not found during initialization');
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

                // Update the build state with the new equipment
                if (targetSlot in this.buildState.equipment) {
                    this.buildState.equipment[targetSlot] = equipmentObject;
                    // Dispatch equipment change event
                    this.dispatchEquipmentChange();
                } else {
                    logError(`Invalid equipment slot: ${targetSlot}`);
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
            this.lockedFilters.slot = slotName;
            
            // Set the currently equipped item key for pre-selection
            const currentItem = this.getEquipment(slotName);
            this.selectedItem = currentItem ? currentItem : null;
            
            this.openPanel(['equipment-selection', 'equipment']);
        },

        /**
         * Remove equipment from a specific slot
         * @param {string} slotName - The name of the equipment slot
         */
        removeEquipment(slotName) {
            const currentItem = this.getEquipment(slotName);
            if (!currentItem) {
                logDebug(`No item to remove from ${slotName}`);
                return;
            }
            
            if (slotName in this.buildState.equipment) {
                this.buildState.equipment[slotName] = null;
                // Dispatch equipment change event
                this.dispatchEquipmentChange();
            } else {
                logError(`Invalid equipment slot: ${slotName}`);
            }
        },

        /**
         * Dispatch equipment change event using the centralized dispatcher
         */
        dispatchEquipmentChange() {
            BuildEventDispatcher.dispatch('build-state:equipment-changed');
        }
    }));
}); 