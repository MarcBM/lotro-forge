/**
 * Client-side filter configuration for essences.
 * Provides static filter options and URL building.
 */

// Essence type mapping
const ESSENCE_TYPES = {
    1: 'Basic',
    18: 'PVP', 
    19: 'Cloak',
    20: 'Necklace',
    22: 'Primary',
    23: 'Vital'
};

class EssenceFilters extends BaseFilters {
    
    /**
     * Returns essence types as {value, label} objects
     */
    static getEssenceTypes() {
        return Object.entries(ESSENCE_TYPES).map(([id, name]) => ({
            value: parseInt(id),
            label: name
        }));
    }
    
    /**
     * Returns all filter configurations
     */
    static getAllFilters(builderMode = false) {
        const baseFilters = super.getAllFilters(builderMode);
        return {
            ...baseFilters,
            essence_type: {
                options: this.getEssenceTypes(),
                locked: false
            }
        };
    }
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        
        if (filterState.essence_type) {
            params.append('essence_type', filterState.essence_type);
        }

        return `/api/data/essences/?${params.toString()}`;
    }
}

// Export globally
window.EssenceFilters = EssenceFilters;