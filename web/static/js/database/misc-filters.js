/**
 * Client-side filter configuration for misc items.
 * Provides static filter options and URL building.
 */

class MiscFilters extends BaseFilters {
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        return `/api/data/misc/?${params.toString()}`;
    }
}

// Export globally
window.MiscFilters = MiscFilters; 