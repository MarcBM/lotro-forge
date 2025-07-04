/**
 * Item Model - Base class for all game items
 * Provides common properties and methods for equipment, essences, etc.
 */
class Item {
    constructor(data = {}) {
        // Basic properties common to all items
        this.key = data.key || null;
        this.name = data.name || '';
        this.quality = data.quality || 'COMMON';
        this.ilvl = data.concrete_ilvl || data.base_ilvl || 0;
        
        // Icon data
        this.icon_urls = data.icon_urls || [];
        
        // Stats data
        this.stats = data.stats || {};
        
        // Additional base properties will be added as requirements are clarified
    }

    // Base methods will be added as needed
} 