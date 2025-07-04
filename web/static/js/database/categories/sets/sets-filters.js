/**
 * Client-side filter configuration for sets.
 * Provides static filter options and URL building.
 */

class SetsFilters extends BaseFilters {
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        return `/api/data/sets/?${params.toString()}`;
    }
}

// Export globally
window.SetsFilters = SetsFilters; 