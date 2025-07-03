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

class EssenceFilters {
    
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
     * Returns available sort options
     */
    static getSortOptions() {
        return [
            { value: 'name', label: 'Name' },
            { value: 'recent', label: 'Recent' },
            { value: 'base_ilvl', label: 'Base iLvl' }
        ];
    }
    
    /**
     * Returns all filter configurations
     */
    static getAllFilters() {
        return {
            sort: {
                options: this.getSortOptions()
            },
            search: {
                value: ''
            },
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
        const params = new URLSearchParams();
        
        params.append('limit', limit);
        params.append('skip', offset);
        
        if (filterState.essence_type) {
            params.append('essence_type', filterState.essence_type);
        }
        
        if (filterState.search) {
            params.append('search', filterState.search);
        }
        
        if (filterState.sort) {
            params.append('sort', filterState.sort);
        }

        return `/api/data/essences/?${params.toString()}`;
    }
}

// Export globally
window.EssenceFilters = EssenceFilters;