// Equipment Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentPanel', () => ({
        // Component state
        loading: false,
        equipment: [],
        selectedEquipment: null,
        concreteEquipment: null,
        
        // Builder-specific properties
        isSlotFilterLocked: false, // Always false for now - builder mode integration comes later
        selectedSlot: '',
        
        // Filter options
        filterOptions: [], // Will be populated from API
        
        // Sort state
        currentSort: 'recent',
        
        async init() {
            // Set the base panel sort dropdown to match our default
            this.$dispatch('set-sort', { panelId: 'equipment', sortBy: this.currentSort });
            // Load available filter options
            await this.loadFilterOptions();
            // Initial load with a fixed limit of 99
            this.loadEquipment(0, 99);
            
            // Listen for load-more events from the base panel
            window.addEventListener('load-more', this.handleLoadMore.bind(this));
            // Listen for sort-change events from the base panel
            window.addEventListener('sort-change', this.handleSortChange.bind(this));
        },
        
        loadFilterOptions() {
            // Use client-side filter configuration instead of API call
            if (window.EquipmentFilters) {
                this.filterOptions = window.EquipmentFilters.getSlotGroups();
            } else {
                console.warn('EquipmentFilters not loaded, filter options will be empty');
                this.filterOptions = [];
            }
        },
        
        applyFilters() {
            // Reset to first page and reload with filters
            this.equipment = [];
            // Reset pagination state to indicate this is a fresh search
            this.$dispatch('reset-pagination-equipment');
            this.loadEquipment(0, 99);
        },
        
        handleLoadMore(event) {
            if (event.detail.panelId !== 'equipment') return;
            this.loadEquipment(event.detail.offset, event.detail.limit, true);
        },

        handleSortChange(event) {
            if (event.detail.panelId !== 'equipment') return;
            this.currentSort = event.detail.sortBy;
            this.applyFilters(); // Reload with new sort
        },
        
        buildApiUrl(offset, limit) {
            const filters = {
                limit: limit,
                skip: offset,
                sort: this.currentSort
            };
            
            // Convert selected slot to actual slot values
            if (this.selectedSlot && window.EquipmentFilters) {
                const selectedGroup = this.filterOptions.find(option => option.key === this.selectedSlot);
                if (selectedGroup) {
                    filters.slots = selectedGroup.slots;
                }
            }
            
            const params = window.EquipmentFilters ? 
                window.EquipmentFilters.buildQueryParams(filters) :
                new URLSearchParams(filters);
            
            return `/api/data/equipment?${params.toString()}`;
        },

        async loadEquipment(offset, limit, append = false) {
            if (this.loading) return;
            
            try {
                this.loading = true;
                const response = await fetch(this.buildApiUrl(offset, limit));
                if (!response.ok) {
                    throw new Error('Failed to load equipment');
                }
                
                const data = await response.json();
                
                // Update equipment array based on append flag
                if (append) {
                    this.equipment = [...this.equipment, ...data.equipment];
                } else {
                    this.equipment = data.equipment;
                }
                
                // Update pagination state in the base panel
                this.$dispatch('update-pagination-equipment', { 
                    panelId: 'equipment',
                    hasMore: data.has_more,
                    offset: offset + limit,
                    newItems: data.equipment,
                    totalResults: data.total
                });
            } catch (error) {
                // Handle error based on append mode
                if (!append) {
                    this.equipment = [];
                }
                
                this.$dispatch('update-pagination-equipment', { 
                    panelId: 'equipment',
                    hasMore: false,
                    offset: offset,
                    newItems: [],
                    totalResults: append ? this.equipment.length : 0
                });
            } finally {
                this.loading = false;
            }
        },

        async selectEquipment(equipment) {
            this.selectedEquipment = equipment;
            // Reset concrete equipment to prevent showing stale data
            this.concreteEquipment = null;
            
            // Fetch complete concrete item (full item data + stats) using the concrete endpoint
            try {
                const response = await fetch(`/api/data/items/${equipment.key}/concrete`);
                if (!response.ok) {
                    return; // Keep concreteEquipment as null
                }
                this.concreteEquipment = await response.json();
            } catch (error) {
                this.concreteEquipment = null;
            }
        },
        
        // Builder mode detection
        isBuilderMode() {
            // Check if we're in the builder by looking for the builder component
            const builderComponent = document.getElementById('builder-component');
            return builderComponent && this.$el && builderComponent.contains(this.$el);
        }
    }));
}); 