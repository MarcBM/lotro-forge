/**
 * Sources Filter Configuration
 * 
 * This file contains the client-side filter configuration for source types and categories,
 * removing the need for API calls to get filter options.
 * 
 * NOTE: This is a placeholder implementation for future development.
 */

// Source type configuration (placeholder)
const SOURCE_TYPES = {
    'instance': 'Instances',
    'quest': 'Quests',
    'vendor': 'Vendors',
    'crafting': 'Crafting'
};

/**
 * Sources Filter Helper Class
 */
class SourcesFilters {
    
    /**
     * Get all source types with their display names
     * @returns {Array} Array of source type objects
     */
    static getSourceTypes() {
        return Object.entries(SOURCE_TYPES).map(([key, name]) => ({
            key: key,
            label: name
        }));
    }
    
    /**
     * Build query parameters for sources API call
     * @param {Object} filters - Filter configuration object
     * @returns {URLSearchParams} URL search parameters
     */
    static buildQueryParams(filters) {
        const params = new URLSearchParams();
        
        // Pagination
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.skip) params.append('skip', filters.skip);
        
        // Type filtering
        if (filters.type) params.append('type', filters.type);
        
        // Sorting
        if (filters.sort) params.append('sort', filters.sort);
        
        return params;
    }
}

// Make available globally
window.SourcesFilters = SourcesFilters; 