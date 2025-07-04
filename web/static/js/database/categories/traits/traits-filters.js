/**
 * Client-side filter configuration for traits.
 * Provides static filter options and URL building.
 */

class TraitsFilters extends BaseFilters {
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        return `/api/data/traits/?${params.toString()}`;
    }
}

// Export globally
window.TraitsFilters = TraitsFilters; 