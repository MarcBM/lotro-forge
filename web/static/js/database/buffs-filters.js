/**
 * Client-side filter configuration for buffs.
 * Provides static filter options and URL building.
 */

class BuffsFilters {
    
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
        
        if (filterState.search) {
            params.append('search', filterState.search);
        }
        
        if (filterState.sort) {
            params.append('sort', filterState.sort);
        }

        return `/api/data/buffs/?${params.toString()}`;
    }
}

// Export globally
window.BuffsFilters = BuffsFilters; 