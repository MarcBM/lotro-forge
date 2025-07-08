// Panel Manager - Simple panel state management
// Handles panel open/close/state for both database and builder contexts
// Pure in-page state management - no URL synchronization

document.addEventListener('alpine:init', () => {
    Alpine.data('panelManager', (config = {}) => ({
        // Panel state - now a list of active panels
        activePanels: config.defaultPanels || [],
        
        // Core panel management
        openPanel(panelIds) {
            // Handle both single panel ID (string) and multiple panel IDs (array)
            const panelsToOpen = Array.isArray(panelIds) ? panelIds : [panelIds];
            
            if (panelsToOpen.length === 0) {
                logWarn('No panel IDs provided');
                return false;
            }
            
            // Add panels to active list if they're not already there
            const newlyOpened = [];
            panelsToOpen.forEach(panelId => {
                if (!this.activePanels.includes(panelId)) {
                    this.activePanels.push(panelId);
                    newlyOpened.push(panelId);
                }
            });
            
            // Dispatch panel-specific events for newly opened panels
            newlyOpened.forEach(panelId => {
                window.dispatchEvent(new CustomEvent(`panel-opened-${panelId}`, {
                    detail: {
                        panelId: panelId,
                        allActivePanels: [...this.activePanels],
                        timestamp: Date.now()
                    },
                    bubbles: true 
                }));
            });
            
            return true;
        },
        
        closePanel(panelIds = null) {
            // Handle both single panel ID (string) and multiple panel IDs (array)
            let panelsToClose;
            if (panelIds) {
                if (Array.isArray(panelIds)) {
                    panelsToClose = panelIds;
                } else {
                    panelsToClose = [panelIds];
                }
            } else {
                panelsToClose = [...this.activePanels];
            }
            
            if (panelsToClose.length === 0) return false;
            
            // Remove panels from active list
            const newlyClosed = [];
            panelsToClose.forEach(panelId => {
                const index = this.activePanels.indexOf(panelId);
                if (index > -1) {
                    this.activePanels.splice(index, 1);
                    newlyClosed.push(panelId);
                }
            });
            
            // Dispatch panel-specific close events for newly closed panels
            newlyClosed.forEach(panelId => {
                window.dispatchEvent(new CustomEvent(`panel-closed-${panelId}`, {
                    detail: {
                        panelId: panelId,
                        allActivePanels: [...this.activePanels],
                        timestamp: Date.now()
                    },
                    bubbles: true 
                }));
            });
            
            return true;
        },
        
        // Panel state queries
        isPanelActive(panelId) {
            return this.activePanels.includes(panelId);
        },
        
        getActivePanels() {
            return [...this.activePanels];
        }
    }));
}); 