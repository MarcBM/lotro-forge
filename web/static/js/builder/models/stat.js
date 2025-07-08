/**
 * Stat Model Definitions
 * 
 * Defines the structure and organization of character stats.
 * Stat names match the database naming convention (UPPERCASE with underscores).
 */

// Define the stat structure
window.createStatStructure = () => {
    return {
        raw_value: 0,
        modifiers: [],
        final_value: 0
    };
};

// Define stat names in organized lists
window.PRIMARY_STATS = [
    'ARMOUR',
    'MIGHT', 
    'AGILITY',
    'VITALITY',
    'WILL',
    'FATE'
];

window.SECONDARY_STATS = [
    'MORALE',
    'POWER',
    'CRITICAL_RATING',
    'FINESSE',
    'PHYSICAL_MASTERY',
    'TACTICAL_MASTERY',
    'RESISTANCE',
    'CRITICAL_DEFENCE',
    'INCOMING_HEALING',
    'BLOCK',
    'PARRY',
    'EVADE',
    'PHYSICAL_MITIGATION',
    'TACTICAL_MITIGATION'
];

window.TERTIARY_STATS = [
    'OUTGOING_HEALING'
];

// Export all stats as a single array for convenience
window.ALL_STATS = [...PRIMARY_STATS, ...SECONDARY_STATS, ...TERTIARY_STATS]; 