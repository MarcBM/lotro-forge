/**
 * Sets Filter Configuration
 * 
 * This file contains the client-side filter configuration for set types,
 * removing the need for API calls to get filter options.
 * 
 * NOTE: This is a placeholder implementation for future development.
 */

// Set type configuration (placeholder)
const SET_TYPES = {
    'equipment': 'Equipment Sets',
    'jewelry': 'Jewelry Sets'
};

/**
 * Sets Filter Helper Class
 */
class SetsFilters {
    
    /**
     * Get all set types with their display names
     * @returns {Array} Array of set type objects
     */
    static getSetTypes() {
        return Object.entries(SET_TYPES).map(([key, name]) => ({
            key: key,
            label: name
        }));
    }
    
    /**
     * Get available sort options for sets
     * @returns {Array} Array of sort option objects
     */
    static getSortOptions() {
        return [
            { value: 'name', label: 'Name' },
            { value: 'recent', label: 'Recent' },
            { value: 'base_ilvl', label: 'Base iLvl' }
        ];
    }
    
    /**
     * Build query parameters for sets API call
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
window.SetsFilters = SetsFilters; 