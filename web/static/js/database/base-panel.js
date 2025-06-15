// Base Panel Component - Shared functionality for database panels
document.addEventListener('alpine:init', () => {
    Alpine.data('basePanel', (panelId) => ({
        // Shared state
        loading: false,
        hasMore: true,
        items: [],
        totalResults: null,
        sortBy: 'ev',
        
        // Methods available to all panels
        isBuilderMode() {
            return window.location.pathname === '/builder';
        },
        
        hasSelectedItem() {
            const parentData = this.getParentPanelData();
            if (!parentData) return false;
            
            const selectedItemProp = `selected${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            return parentData[selectedItemProp] !== null;
        },
        
        getSelectedItemName() {
            // Get the name of the currently selected item
            const parentData = this.getParentPanelData();
            if (!parentData) return '';
            
            const selectedItemProp = `selected${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            const selectedItem = parentData[selectedItemProp];
            
            return selectedItem ? selectedItem.name || 'Item' : '';
        },
        
        getBuilderSlot() {
            // Get the current builder slot from the equipment selection component
            const builderSelectionEl = document.querySelector('[x-data*="builderEquipmentSelection"]');
            if (builderSelectionEl && Alpine.$data(builderSelectionEl)) {
                return Alpine.$data(builderSelectionEl).selectedSlot;
            }
            return '';
        },
        
        selectItemForBuild() {
            // Get the parent panel data to access selected item
            const parentData = this.getParentPanelData();
            if (!parentData) {
                console.error('Could not find parent panel data');
                return;
            }
            
            const selectedItemProp = `selected${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            const concreteItemProp = `concrete${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            
            const selectedItem = parentData[selectedItemProp];
            const concreteItem = parentData[concreteItemProp];
            
            if (!selectedItem) {
                console.error('No item selected');
                return;
            }
            
            // Get the builder slot
            const builderSlot = this.getBuilderSlot();
            if (!builderSlot) {
                console.error('No builder slot available');
                return;
            }
            
            // Dispatch event to builder with selected item
            window.dispatchEvent(new CustomEvent('item-selected', {
                detail: {
                    slot: builderSlot,
                    item: selectedItem,
                    concreteItem: concreteItem,
                    panelType: panelId
                }
            }));
            
            // Close the selection panel
            window.dispatchEvent(new CustomEvent('close-panel', {
                detail: panelId
            }));
        },
        
        getParentPanelData() {
            // Check for the specific property we're looking for based on panel type
            const selectedItemProp = `selected${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            
            // First, try the immediate parent
            try {
                const immediateParent = this.$el.parentElement;
                if (immediateParent) {
                    const data = Alpine.$data(immediateParent);
                    if (data && data[selectedItemProp] !== undefined) {
                        return data;
                    }
                }
            } catch (e) {
                // Continue to next method
            }
            
            // If not found on immediate parent, try to find the panel specifically
            try {
                const panelElement = document.querySelector(`[x-data*="${panelId}Panel"]`);
                if (panelElement) {
                    const data = Alpine.$data(panelElement);
                    if (data && data[selectedItemProp] !== undefined) {
                        return data;
                    }
                }
            } catch (e) {
                // Continue
            }
            
            return null;
        }
    }));
}); 