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
        
        // Builder mode properties
        equipmentManager: null,

        // Filter properties
        filterOptions: {},
        filterState: {
            sort: 'name',
            search: '',
            slot: ''
            // Future filters...
        },
        
        async init() {
            console.log('Database Equipment Panel component initialized');
            this.loading = false;
            
            // Check builder context and setup
            this.checkBuilderContext();

            // Load available filter options
            this.loadFilterOptions();
            
            // Listen for equipment-specific events from database controller
            window.addEventListener('database-load-more-equipment', this.handleLoadMore.bind(this));
            
            // Listen for panel activation to load initial data
            window.addEventListener('panel-opened-equipment', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-equipment', this.handlePanelClosed.bind(this));
            
            // Check if we're on the database page and equipment is the default panel
            this.checkDatabasePageInitialLoad();
        },
        
        checkDatabasePageInitialLoad() {
            // Check if we're on the database page by looking for the database component
            const databaseComponent = document.getElementById('database-component');
            if (!databaseComponent) return;
            
            // Check if equipment is the default/active panel by checking the panel manager
            // Get the panel manager component from the database component
            const panelManagerData = Alpine.$data(databaseComponent);
            if (panelManagerData && panelManagerData.isPanelActive('equipment') && this.equipment.length === 0) {
                this.resetAndLoad();
            }
        },
        
        async checkBuilderContext() {
            const equipmentSection = document.getElementById('equipment-section');
            if (!equipmentSection) return;
            
            this.equipmentManager = Alpine.$data(equipmentSection);
            // this.filterState.sort = 'ev';
        },
        
        loadFilterOptions() {
            // Use client-side filter configuration instead of API call
            if (window.EquipmentFilters) {
                this.filterOptions = window.EquipmentFilters.getAllFilters(this.equipmentManager != null);
            } else {
                console.warn('EquipmentFilters not loaded, filter and sort options will be empty');
                this.filterOptions = {};
            }
        },
        
        resetAndLoad() {
            this.equipment = [];
            this.loadEquipment(0, 99);
        },

        handlePanelOpened() {
            if (this.equipmentManager) {
                Object.keys(this.equipmentManager.lockedFilters).forEach(filterKey => {
                    if (this.equipmentManager.lockedFilters[filterKey]) {
                        this.filterState[filterKey] = this.equipmentManager.lockedFilters[filterKey];
                        this.filterOptions[filterKey].locked = true;
                    }
                });
            }
            this.resetAndLoad();
        },

        handlePanelClosed() {
            this.selectedEquipment = null;
        },
        
        handleLoadMore(event) {
            this.loadEquipment(event.detail.offset, event.detail.limit, true);
        },

        async loadEquipment(offset, limit, append = false) {
            if (this.loading) return;

            try {
                this.loading = true;
                const response = await fetch(window.EquipmentFilters.buildApiUrl(this.filterState, offset, limit));
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
                console.error("Error loading equipment: ", error);
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
    }));
}); 