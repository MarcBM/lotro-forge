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
            SHOULDERS: null,
            BACK: null,
            CHEST: null,
            HANDS: null,
            LEGS: null,
            FEET: null,
            
            // Weapon slots
            MAIN_HAND: null,
            OFF_HAND: null,
            RANGED: null,
            CLASS: null
        },

        // Essences
        essences: {
            // Essence data will be defined as needed
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
        }
    }));
}); 