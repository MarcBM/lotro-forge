// Main JavaScript file for LOTRO Forge

// Utility function to format item levels
function formatItemLevel(level) {
    return `Item Level ${level}`;
}

// Utility function to format quality names
function formatQuality(quality) {
    return quality.charAt(0).toUpperCase() + quality.slice(1).toLowerCase();
}

// Add quality color class to elements
function addQualityColors() {
    document.querySelectorAll('[data-quality]').forEach(element => {
        const quality = element.dataset.quality.toLowerCase();
        element.classList.add(`quality-${quality}`);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add quality colors to any elements that need them
    addQualityColors();
    
    // Add any other initialization code here
}); 