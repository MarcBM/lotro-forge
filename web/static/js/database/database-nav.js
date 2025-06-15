// Database Navigation Extension
document.addEventListener('alpine:init', () => {
    Alpine.data('databaseNavigation', () => ({
        // Panel state for database
        activePanel: 'equipment', // Default to equipment panel
        
        init() {
            // Listen for panel-closed events
            window.addEventListener('panel-closed', () => {
                this.activePanel = null;
            });
        },
        
        // Panel management for database
        openPanel(panel) {
            console.log('Database Nav: Opening panel:', panel);
            this.activePanel = panel;
            window.dispatchEvent(new CustomEvent('open-panel', { 
                detail: panel,
                bubbles: true 
            }));
        }
    }));
}); 