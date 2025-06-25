/**
 * Traits Filter Configuration
 * 
 * This file contains the client-side filter configuration for trait categories and types,
 * removing the need for API calls to get filter options.
 * 
 * NOTE: This is a placeholder implementation for future development.
 */

// Trait category configuration (placeholder)
const TRAIT_CATEGORIES = {
    'class': 'Class Traits',
    'virtue': 'Virtue Traits', 
    'deed': 'Deed Traits',
    'racial': 'Racial Traits'
};

/**
 * Traits Filter Helper Class
 */
class TraitsFilters {
    
    /**
     * Get all trait categories with their display names
     * @returns {Array} Array of trait category objects
     */
    static getTraitCategories() {
        return Object.entries(TRAIT_CATEGORIES).map(([key, name]) => ({
            key: key,
            label: name
        }));
    }
    
    /**
     * Build query parameters for traits API call
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
window.TraitsFilters = TraitsFilters; 