/**
 * Buffs Filter Configuration
 * 
 * This file contains the client-side filter configuration for buff types and categories,
 * removing the need for API calls to get filter options.
 * 
 * NOTE: This is a placeholder implementation for future development.
 */

// Buff type configuration (placeholder)
const BUFF_TYPES = {
    'food': 'Food Buffs',
    'scroll': 'Scroll Buffs',
    'consumable': 'Consumable Buffs',
    'potion': 'Potion Buffs'
};

/**
 * Buffs Filter Helper Class
 */
class BuffsFilters {
    
    /**
     * Get all buff types with their display names
     * @returns {Array} Array of buff type objects
     */
    static getBuffTypes() {
        return Object.entries(BUFF_TYPES).map(([key, name]) => ({
            key: key,
            label: name
        }));
    }
    
    /**
     * Build query parameters for buffs API call
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
window.BuffsFilters = BuffsFilters; 