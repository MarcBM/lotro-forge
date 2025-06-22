// Database Base Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('databasePanel', (panelId) => ({
        loading: false,
        hasMore: true,
        offset: 0,
        limit: 99,
        items: [], // Track total items
        totalResults: null, // Track total results count
        sortBy: 'recent', // Default sort option

        handlePaginationUpdate(detail) {
            this.hasMore = detail.hasMore;
            
            // Determine if this is a fresh search or load-more
            // For fresh search: offset - limit should equal 0 (first load)
            // For load-more: offset - limit should equal current items length
            const expectedCurrentLength = detail.offset - 99; // 99 is our limit
            const isFreshSearch = expectedCurrentLength === 0;
            
            if (isFreshSearch) {
                // Fresh search - replace items
                this.items = detail.newItems || [];
            } else {
                // Load more - append items
                this.items = [...this.items, ...detail.newItems || []];
            }
            
            this.offset = detail.offset;
            
            // Update total results if provided
            if (detail.totalResults !== undefined) {
                this.totalResults = detail.totalResults;
            }
        },

        handlePaginationReset() {
            this.items = [];
            this.totalResults = null;
            this.hasMore = true;
            this.offset = 0;
        },

        handleSortChange() {
            // Dispatch a custom event that the panel component can listen for
            const event = new CustomEvent('sort-change', {
                detail: {
                    panelId,
                    sortBy: this.sortBy
                }
            });
            window.dispatchEvent(event);
        },

        async loadMore() {
            if (this.loading || !this.hasMore) return;

            try {
                this.loading = true;
                // Dispatch a custom event that the panel component can listen for
                const event = new CustomEvent('load-more', {
                    detail: {
                        panelId,
                        offset: this.offset,
                        limit: this.limit
                    }
                });
                window.dispatchEvent(event);
            } catch (error) {
                this.hasMore = false;
            } finally {
                this.loading = false;
            }
        },

        // Builder-specific methods
        isBuilderMode() {
            // Check if we're in the builder by looking for the builder component
            const builderComponent = document.getElementById('builder-component');
            return builderComponent && this.$el && builderComponent.contains(this.$el);
        },
        
        hasSelectedItem() {
            // Check if any item is selected by looking for selectedEquipment, selectedEssence, etc.
            const parentData = this.getParentPanelData();
            if (!parentData) return false;
            
            // Check for various selected item properties based on panel type
            const selectedItemProp = `selected${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            return parentData[selectedItemProp] && parentData[selectedItemProp] !== false;
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
            // Get the selected item from the parent panel component
            const parentData = this.getParentPanelData();
            if (!parentData) return;
            
            const selectedItemProp = `selected${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            const concreteItemProp = `concrete${panelId.charAt(0).toUpperCase() + panelId.slice(1)}`;
            
            const selectedItem = parentData[selectedItemProp];
            const concreteItem = parentData[concreteItemProp];
            
            if (!selectedItem) return;
            
            const builderSlot = this.getBuilderSlot();
            
            // Validate that the item can be equipped in this slot (for equipment only)
            if (panelId === 'equipment' && parentData.canItemBeEquippedInSlot) {
                const isValid = parentData.canItemBeEquippedInSlot(selectedItem, builderSlot);
                if (!isValid) {
                    // Show error message
                    alert(`Cannot equip "${selectedItem.name}" in ${builderSlot} slot. This item can only be equipped in slots compatible with ${selectedItem.slot}.`);
                    
                    // Reopen equipment panel with correct filter
                    setTimeout(() => {
                        window.dispatchEvent(new CustomEvent('load-slot-items', {
                            detail: { 
                                slotType: builderSlot,
                                currentlyEquipped: null
                            }
                        }));
                    }, 100);
                    
                    return; // Prevent equipping
                }
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