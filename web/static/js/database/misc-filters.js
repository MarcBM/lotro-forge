/**
 * Misc Items Filter Configuration
 * 
 * This file contains the client-side filter configuration for miscellaneous item categories,
 * removing the need for API calls to get filter options.
 * 
 * NOTE: This is a placeholder implementation for future development.
 */

// Miscellaneous item category configuration (placeholder)
const MISC_CATEGORIES = {
    'quest': 'Quest Items',
    'crafting': 'Crafting Materials',
    'decorative': 'Decorative Items',
    'consumable': 'Consumable Items'
};

/**
 * Misc Items Filter Helper Class
 */
class MiscFilters {
    
    /**
     * Get all misc item categories with their display names
     * @returns {Array} Array of misc category objects
     */
    static getMiscCategories() {
        return Object.entries(MISC_CATEGORIES).map(([key, name]) => ({
            key: key,
            label: name
        }));
    }
    
    /**
     * Build query parameters for misc items API call
     * @param {Object} filters - Filter configuration object
     * @returns {URLSearchParams} URL search parameters
     */
    static buildQueryParams(filters) {
        const params = new URLSearchParams();
        
        // Pagination
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.skip) params.append('skip', filters.skip);
        
        // Category filtering
        if (filters.category) params.append('category', filters.category);
        
        // Sorting
        if (filters.sort) params.append('sort', filters.sort);
        
        return params;
    }
}

// Make available globally
window.MiscFilters = MiscFilters; 