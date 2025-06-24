// Builder Navigation Extension
document.addEventListener('alpine:init', () => {
    Alpine.data('builderNavigation', () => ({
        // Build management
        buildName: 'New Build',
        isEditingName: false,
        
        // Panel state for builder
        activePanel: null,
        
        init() {
            console.log('Builder Navigation component initialized');
            // Listen for panel-closed events
            window.addEventListener('panel-closed', () => {
                this.activePanel = null;
            });
        },
        
        // Panel management for builder
        openPanel(panel) {
            console.log('Builder Nav: Opening panel:', panel);
            this.activePanel = panel;
            window.dispatchEvent(new CustomEvent('open-panel', { 
                detail: panel,
                bubbles: true 
            }));
        }
    }));
}); 