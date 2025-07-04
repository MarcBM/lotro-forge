/**
 * Client-side filter configuration for sources.
 * Provides static filter options and URL building.
 */

class SourcesFilters extends BaseFilters {
    
    /**
     * Builds API URL with filter parameters
     */
    static buildApiUrl(filterState, offset = 0, limit = 99) {
        const params = super.buildBaseParams(filterState, offset, limit);
        return `/api/data/sources/?${params.toString()}`;
    }
}

// Export globally
window.SourcesFilters = SourcesFilters; 