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
        
        // Reference to the build state component
        buildState: null,
        
        init() {
            // Get direct reference to build state component
            const buildStateElement = document.getElementById('build-state');
            this.buildState = Alpine.$data(buildStateElement);
            logComponent('StatsEngine', 'initialized');
            
            // Build the stats object dynamically
            this.buildStatsObject();
            
            // Listen for build changes
            this.listenForBuildChanges();
        },
        
        buildStatsObject() {
            // Create stat structure for each stat name
            window.ALL_STATS.forEach(statName => {
                this.stats[statName] = window.createStatStructure();
            });
            console.log(this.stats);
        },
        
        listenForBuildChanges() {
            // Listen for the generic build-changed event
            window.addEventListener('build-changed', () => {
                this.calculateStatsFromEquipment();
            });
        },
        
        calculateStatsFromEquipment() {
            // Reset all raw values to 0
            Object.keys(this.stats).forEach(statName => {
                this.stats[statName].raw_value = 0;
            });
            
            // Check if build state is available
            if (!this.buildState || !this.buildState.equipment) {
                logDebug('Build state not available for stat calculation');
                return;
            }
            
            // Iterate over each equipment slot
            Object.keys(this.buildState.equipment).forEach(slotName => {
                const equipment = this.buildState.equipment[slotName];
                if (equipment && equipment.stats) {
                    // Add stats from this equipment to the total
                    this.addEquipmentStats(equipment.stats);
                }
            });
            
            // Calculate final values (for now, just copy raw values)
            this.calculateFinalValues();
            
            logDebug('Stats recalculated from equipment');
            console.log(this.stats);
        },
        
        addEquipmentStats(equipmentStats) {
            // Add each stat from the equipment to the corresponding stat in our stats object
            equipmentStats.forEach(stat => {
                if (this.stats[stat.stat_name]) {
                    this.stats[stat.stat_name].raw_value += stat.value;
                }
            });
        },
        
        calculateFinalValues() {
            // For now, just copy raw values to final values
            // Later this can include modifiers, buffs, traits, etc.
            Object.keys(this.stats).forEach(statName => {
                this.stats[statName].final_value = this.stats[statName].raw_value;
            });
        }
    }));
}); 