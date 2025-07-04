/**
 * Weapon Model - Pure JavaScript class for weapon items
 * Represents weapon equipment with weapon-specific properties
 * Inherits from Equipment class
 */
class Weapon extends Equipment {
    constructor(data = {}) {
        super(data); // Call parent constructor
        
        // Weapon-specific properties
        this.weapon_type = data.weapon_type || '';
        this.damage_type = data.damage_type || '';
        
        // Weapon-specific methods will be added as needed
    }
} 