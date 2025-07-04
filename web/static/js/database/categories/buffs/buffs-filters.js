/**
 * Client-side filter configuration for buffs.
 * Provides static filter options and URL building.
 */

class BuffsFilters extends BaseFilters {
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        return `/api/data/buffs/?${params.toString()}`;
    }
}

// Export globally
window.BuffsFilters = BuffsFilters; 