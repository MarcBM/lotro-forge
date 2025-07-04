/**
 * Build State - Alpine.js reactive state container
 * Central state management for character builds
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('buildState', () => ({
        // Character basic info
        character: {
            name: '',
            level: 150,
            class: '',
            race: ''
        },

        // Equipment slots - all slots initialized as null
        equipment: {
            // Jewellery slots
            LEFT_EAR: null,
            RIGHT_EAR: null,
            NECK: null,
            POCKET: null,
            LEFT_WRIST: null,
            RIGHT_WRIST: null,
            LEFT_FINGER: null,
            RIGHT_FINGER: null,
            
            // Armour slots
            HEAD: null,
            SHOULDER: null,
            BACK: null,
            CHEST: null,
            HAND: null,
            LEGS: null,
            FEET: null,
            
            // Weapon slots
            MAIN_HAND: null,
            OFF_HAND: null,
            RANGED_ITEM: null,
            CLASS_SLOT: null
        },

        // Essences
        essences: {
            sockets: {
                basic: 0,
                primary: 0,
                vital: 0,
                cloak: 0,
                necklace: 0,
                pvp: 0
            }
        },

        // Character traits, buffs, etc.
        traits: [],
        buffs: [],

        // Build metadata
        buildName: '',
        buildNotes: '',

        // Methods will be added as needed
        init() {
            logComponent('BuildState', 'initialized');
            // Initialization logic
        },

        /**
         * Equip an item to a specific slot
         * @param {string} slotName - The name of the equipment slot
         * @param {Object} item - The equipment item to set
         * @returns {boolean} True if successful, false otherwise
         */
        equipItem(slotName, item) {
            if (!(slotName in this.equipment)) {
                logError(`Invalid equipment slot: ${slotName}`);
                return false;
            }
            
            this.equipment[slotName] = item;
            return true;
        },

        countEssenceSockets() {
            // TODO
        },
    }));
}); 