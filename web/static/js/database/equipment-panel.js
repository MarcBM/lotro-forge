// Equipment Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentPanel', (panelId) => ({
        // Panel identification
        panelId: panelId,
        // Component state
        loading: false,
        equipment: [],
        selectedEquipment: null,
        loadingStats: false,
        
        // Builder-specific properties
        isSlotFilterLocked: false, // Always false for now - builder mode integration comes later
        selectedSlot: '',
        
        // Filter options
        filterOptions: [], // Will be populated from equipment-filters.js
        
        // Sort state
        currentSort: 'name',
        availableSortOptions: [],
        
        // Search state
        searchQuery: '',
        
        async init() {
            console.log('Database Equipment Panel component initialized');
            this.loading = false;
            // Load available filter options
            await this.loadFilterOptions();
            
            // Listen for equipment-specific events from database controller
            window.addEventListener('database-load-more-equipment', this.handleLoadMore.bind(this));
            
            // Listen for panel activation to load initial data
            window.addEventListener('panel-opened-equipment', this.handlePanelOpened.bind(this));
            
            // Check if we're on the database page and equipment is the default panel
            this.checkDatabasePageInitialLoad();
        },
        
        checkDatabasePageInitialLoad() {
            // Check if we're on the database page by looking for the database component
            const databaseComponent = document.getElementById('database-component');
            if (!databaseComponent) return;
            
            // Check if equipment is the default/active panel by checking the panel manager
            // We'll use a small delay to ensure the panel manager has initialized
            setTimeout(() => {
                // Get the panel manager component from the database component
                const panelManagerData = Alpine.$data(databaseComponent);
                if (panelManagerData && panelManagerData.activePanel === 'equipment' && this.equipment.length === 0) {
                    console.log('Database page loaded with equipment as default panel - loading initial data');
                    this.handlePanelOpened();
                }
            }, 100);
        },
        
        async handlePanelOpened() {
            console.log('Equipment panel opened - loading fresh data');
            // Always reload data when panel is opened (fresh start)
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
                this.availableSortOptions = window.EquipmentFilters.getSortOptions();
            } else {
                console.warn('EquipmentFilters not loaded, filter and sort options will be empty');
                this.filterOptions = [];
                this.availableSortOptions = [];
            }
        },
        
        applyFilters() {
            // Reset to first page and reload with filters
            this.resetAndLoad();
        },
        
        handleLoadMore(event) {
            this.loadEquipment(event.detail.offset, event.detail.limit, true);
        },

        handleSortChange() {
            // Handle sort change directly on the panel
            console.log(`Equipment sort changed to: ${this.currentSort}`);
            this.resetAndLoad(); // Reload with new sort
        },
        
        handleSearchChange() {
            // Handle search change directly on the panel
            console.log(`Equipment search changed to: ${this.searchQuery}`);
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
            
            // Add search query from database controller
            if (this.searchQuery) {
                filters.search = this.searchQuery;
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
                        totalResults: data.total,
                        currentlyShowing: this.equipment.length
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
                        totalResults: 0,
                        currentlyShowing: this.equipment.length
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
        
        async updateItemLevel(event) {
            if (!this.selectedEquipment) return;
            
            const newIlvl = parseInt(event.target.textContent.trim());
            const currentIlvl = this.selectedEquipment.concrete_ilvl || this.selectedEquipment.base_ilvl;
            
            // Validate the input
            if (isNaN(newIlvl) || newIlvl < 1 || newIlvl > 999) {
                // Reset to current value
                event.target.textContent = currentIlvl;
                return;
            }
            
            // Don't update if it's the same level
            if (newIlvl === currentIlvl) return;
            
            console.log(`Updating equipment ${this.selectedEquipment.name} to ilvl ${newIlvl}`);
            
            try {
                this.loadingStats = true;
                const response = await fetch(`/api/data/items/${this.selectedEquipment.key}/stats?ilvl=${newIlvl}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch stats at new level');
                }
                const newStats = await response.json();
                
                // Update the stats in selectedEquipment while keeping all other data
                this.selectedEquipment.stats = newStats;
                this.selectedEquipment.concrete_ilvl = newIlvl;
                
            } catch (error) {
                console.error('Error updating item level:', error);
                // Reset to previous ilvl on error
                event.target.textContent = currentIlvl;
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