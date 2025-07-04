/**
 * Equipment Model - Pure JavaScript class for equipment items
 * Represents individual equipment pieces with their properties
 * Inherits from Item base class
 */
class Equipment extends Item {
    constructor(data = {}) {
        super(data); // Call parent constructor
        
        // Equipment-specific properties
        this.slot = data.slot || '';
        this.armour_type = data.armour_type || '';
        
        // Socket information
        this.sockets = data.sockets || {};
        this.total_sockets = data.total_sockets || 0;
        
        // Equipment-specific methods will be added as needed
    }
} 