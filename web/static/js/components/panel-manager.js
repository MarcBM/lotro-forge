// Panel Manager - Simple panel state management
// Handles panel open/close/state for both database and builder contexts
// Pure in-page state management - no URL synchronization

document.addEventListener('alpine:init', () => {
    Alpine.data('panelManager', (config = {}) => ({
        // Panel state
        activePanel: config.defaultPanel || null,
        
        init() {
            console.log('Panel Manager initialized');
        },
        
        // Core panel management
        openPanel(panelId) {
            if (!panelId) {
                console.warn('No panel ID provided');
                return false;
            }
            
            console.log('Opening panel:', panelId);
            const previousPanel = this.activePanel;
            this.activePanel = panelId;
            
            // Dispatch panel-specific event for components to listen to
            window.dispatchEvent(new CustomEvent(`panel-opened-${panelId}`, {
                detail: {
                    panelId: panelId,
                    previousPanel: previousPanel,
                    timestamp: Date.now()
                },
                bubbles: true 
            }));
            
            return true;
        },
        
        closePanel(panelId = null) {
            const targetPanel = panelId || this.activePanel;
            if (!targetPanel) return false;
            
            console.log('Closing panel:', targetPanel);
            const previousPanel = this.activePanel;
            this.activePanel = null;
            
            // Dispatch panel-specific close event
            window.dispatchEvent(new CustomEvent(`panel-closed-${targetPanel}`, {
                detail: {
                    panelId: targetPanel,
                    previousPanel: previousPanel,
                    timestamp: Date.now()
                },
                bubbles: true 
            }));
            
            return true;
        },
        
        // Panel state queries
        isPanelActive(panelId) {
            return this.activePanel === panelId;
        },
        
        getActivePanel() {
            return this.activePanel;
        }
    }));
}); 