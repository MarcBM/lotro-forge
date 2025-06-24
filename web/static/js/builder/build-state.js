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

        // Equipment slots
        equipment: {
            // Equipment slots will be defined as needed
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
            console.log('Build State initialized');
            // Initialization logic
        }
    }));
}); 