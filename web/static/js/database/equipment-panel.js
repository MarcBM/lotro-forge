// Equipment Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentPanel', () => ({
        // Component state
        loading: false,
        dataLoaded: false,
        equipment: [],
        selectedEquipment: null,
        loadingStats: false,
        
        // Builder-specific properties
        isSlotFilterLocked: false, // Always false for now - builder mode integration comes later
        selectedSlot: '',
        
        // Filter options
        filterOptions: [], // Will be populated from equipment-filters.js
        
        // Sort state
        currentSort: 'recent',
        
        async init() {
            console.log('Database Equipment Panel component initialized');
            this.loading = false;
            // Load available filter options
            await this.loadFilterOptions();
            
            // Listen for events from database controller
            window.addEventListener('database-load-more', this.handleLoadMore.bind(this));
            window.addEventListener('database-sort-changed', this.handleSortChange.bind(this));
            window.addEventListener('database-search-changed', this.handleSearchChange.bind(this));
            
            // Listen for panel activation to load initial data
            window.addEventListener('panel-opened-equipment', this.handlePanelOpened.bind(this));
        },
        
        async handlePanelOpened() {
            if (this.dataLoaded) return;
            console.log('Equipment panel opened - loading initial data');
            this.dataLoaded = true;
            // Reset pagination and load initial data
            this.resetAndLoad();
        },
        
        resetAndLoad() {
            this.equipment = [];
            this.loadEquipment(0, 99);
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
            this.resetAndLoad();
        },
        
        handleLoadMore(event) {
            this.loadEquipment(event.detail.offset, event.detail.limit, true);
        },

        handleSortChange(event) {
            this.currentSort = event.detail.sortBy;
            this.resetAndLoad(); // Reload with new sort
        },
        
        handleSearchChange(event) {
            // Handle search from centralized controller
            this.resetAndLoad(); // Reload with search
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
            
            return `/api/data/equipment/?${params.toString()}`;
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
                
                // Update pagination state in the database controller
                window.dispatchEvent(new CustomEvent('update-database-pagination', {
                    detail: {
                        hasMore: data.has_more,
                        offset: offset + limit,
                        totalResults: data.total
                    }
                }));
            } catch (error) {
                // Handle error based on append mode
                if (!append) {
                    this.equipment = [];
                }
                
                // Update pagination state on error
                window.dispatchEvent(new CustomEvent('update-database-pagination', {
                    detail: {
                        hasMore: false,
                        offset: offset,
                        totalResults: 0
                    }
                }));
            } finally {
                this.loading = false;
            }
        },

        async selectEquipment(equipment) {
            if (this.selectedEquipment && this.selectedEquipment.key === equipment.key) {
                return;
            }
            // Set loading state and show basic item info immediately
            this.loadingStats = true;
            this.selectedEquipment = equipment;
            
            // Fetch complete concrete item (full item data + stats) using the concrete endpoint
            try {
                const response = await fetch(`/api/data/items/${equipment.key}/concrete`);
                if (!response.ok) {
                    this.selectedEquipment = equipment; // Keep basic item data
                    return;
                }
                this.selectedEquipment = await response.json();
            } catch (error) {
                this.selectedEquipment = equipment; // Keep basic item data
            } finally {
                this.loadingStats = false;
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