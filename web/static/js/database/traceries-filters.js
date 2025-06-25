/**
 * Traceries Filter Configuration
 * 
 * This file contains the client-side filter configuration for tracery types,
 * removing the need for API calls to get filter options.
 * 
 * NOTE: This is a placeholder implementation for future development.
 */

// Tracery type configuration (placeholder)
const TRACERY_TYPES = {
    'heraldric': 'Heraldric Traceries',
    'word': 'Word Traceries'
};

/**
 * Traceries Filter Helper Class
 */
class TraceriesFilters {
    
    /**
     * Get all tracery types with their display names
     * @returns {Array} Array of tracery type objects
     */
    static getTraceryTypes() {
        return Object.entries(TRACERY_TYPES).map(([key, name]) => ({
            key: key,
            label: name
        }));
    }
    
    /**
     * Build query parameters for traceries API call
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
window.TraceriesFilters = TraceriesFilters; 