/**
 * Client-side filter configuration for traceries.
 * Provides static filter options and URL building.
 */

class TraceriesFilters extends BaseFilters {
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        return `/api/data/traceries/?${params.toString()}`;
    }
}

// Export globally
window.TraceriesFilters = TraceriesFilters; 