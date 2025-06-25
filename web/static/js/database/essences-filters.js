/**
 * Essences Filter Configuration
 * 
 * This file contains the client-side filter configuration for essence types and tiers,
 * removing the need for API calls to get filter options.
 */

// Essence type configuration
const ESSENCE_TYPES = {
    1: 'Basic',
    18: 'PVP', 
    19: 'Cloak',
    20: 'Necklace',
    22: 'Primary',
    23: 'Vital'
};

/**
 * Essence Filter Helper Class
 */
class EssenceFilters {
    
    /**
     * Get all essence types with their display names
     * @returns {Array} Array of essence type objects
     */
    static getEssenceTypes() {
        return Object.entries(ESSENCE_TYPES).map(([id, name]) => ({
            id: parseInt(id),
            name: name
        }));
    }
    
    /**
     * Get available sort options for essences
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
     * Build query parameters for essences API call
     * @param {Object} filters - Filter configuration object
     * @returns {URLSearchParams} URL search parameters
     */
    static buildQueryParams(filters) {
        const params = new URLSearchParams();
        
        // Pagination
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.skip) params.append('skip', filters.skip);
        
        // Essence type filtering
        if (filters.essence_type) params.append('essence_type', filters.essence_type);
        
        // Search
        if (filters.search) params.append('search', filters.search);
        
        // Sorting
        if (filters.sort) params.append('sort', filters.sort);
        
        return params;
    }
}

// Export for use in other modules
window.EssenceFilters = EssenceFilters;

// Also export constants for direct access
window.ESSENCE_TYPES = ESSENCE_TYPES;