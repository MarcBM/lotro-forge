// Builder Equipment Selection Component
document.addEventListener('alpine:init', () => {
    Alpine.data('builderEquipmentSelection', () => ({
        selectedSlot: '',
        
        init() {
            // Listen for slot loading events from builder
            window.addEventListener('load-slot-items', (event) => {
                this.selectedSlot = event.detail.slotType;
                // Set the slot filter in the equipment panel with a slight delay
                setTimeout(() => {
                    this.setSlotFilter(event.detail.slotType);
                }, 100);
            });
        },
        
        setSlotFilter(slotType) {
            // Find the equipment data component and set its slot filter
            const equipmentPanelEl = this.$el.querySelector('[x-data*="equipmentData"]');
            if (equipmentPanelEl) {
                // Access Alpine data through the element
                const equipmentComponent = Alpine.$data(equipmentPanelEl);
                if (equipmentComponent) {
                    equipmentComponent.selectedSlot = slotType;
                    if (equipmentComponent.applyFilters) {
                        equipmentComponent.applyFilters();
                    }
                }
            }
        },
        
        closeSelection() {
            // Close the equipment panel
            window.dispatchEvent(new CustomEvent('close-panel', {
                detail: 'equipment'
            }));
        }
    }));
}); 