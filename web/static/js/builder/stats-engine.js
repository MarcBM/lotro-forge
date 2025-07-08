/**
 * Stats Engine - Alpine.js component for character statistics
 * 
 * This component defines all the stats that need to be tracked for a character build.
 * Stat names match the database naming convention (UPPERCASE with underscores).
 * Each stat has a raw value, modifiers array, and calculated final value.
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('statsEngine', () => ({
        stats: {},
        
        init() {
            // Build the stats object dynamically
            this.buildStatsObject();
        },
        
        buildStatsObject() {
            // Create stat structure for each stat name
            window.ALL_STATS.forEach(statName => {
                this.stats[statName] = window.createStatStructure();
            });
        }
    }));
}); 