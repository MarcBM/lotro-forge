// Equipment panel component - handles equipment data loading, filtering, and selection
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentPanel', (panelId) => ({
        panelId: panelId,
        databaseController: null,
        equipmentManager: null,

        // Filter state and options
        filterOptions: {},
        filterState: {
            sort: 'name',
            search: '',
            slot: ''
        },
        
        async init() {
            // Initialize database controller reference
            const databaseControlElement = document.getElementById('database-controller');
            if (!databaseControlElement) {
                logError('Database controller element not found');
                return;
            }
            this.databaseController = Alpine.$data(databaseControlElement);
            
            this.checkBuilderContext();
            this.loadFilterOptions();
            
            // Setup event listeners
            window.addEventListener('database-load-more-equipment', this.handleLoadMore.bind(this));
            window.addEventListener('panel-opened-equipment', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-equipment', this.handlePanelClosed.bind(this));
            
            this.checkDatabasePageInitialLoad();
            logComponent('EquipmentPanel', 'initialized');
        },
        
        checkDatabasePageInitialLoad() {
            // Load initial data if equipment panel is active by default
            const databaseComponent = document.getElementById('database-component');
            if (!databaseComponent) return;
            
            const panelManagerData = Alpine.$data(databaseComponent);
            if (panelManagerData && panelManagerData.isPanelActive('equipment') && this.databaseController.dataList.length === 0) {
                this.loadData();
            }
        },
        
        async checkBuilderContext() {
            // Check if in builder mode and get equipment manager reference
            const equipmentSection = document.getElementById('equipment-section');
            if (!equipmentSection) return;
            
            this.equipmentManager = Alpine.$data(equipmentSection);
        },
        
        loadFilterOptions() {
            // Load client-side filter options
            if (window.EquipmentFilters) {
                this.filterOptions = window.EquipmentFilters.getAllFilters(this.equipmentManager != null);
            } else {
                logWarn('EquipmentFilters not loaded, filter and sort options will be empty');
                this.filterOptions = {};
            }
        },

        handlePanelOpened() {
            // Apply locked filters from builder mode if present
            if (this.equipmentManager) {
                Object.keys(this.equipmentManager.lockedFilters).forEach(filterKey => {
                    if (this.equipmentManager.lockedFilters[filterKey]) {
                        this.filterState[filterKey] = this.equipmentManager.lockedFilters[filterKey];
                        this.filterOptions[filterKey].locked = true;
                    }
                });
            }
            this.loadData();
        },

        handlePanelClosed() {
            // Reset panel state on close
            this.databaseController.clearData();
            this.filterState.search = '';
        },
        
        handleLoadMore(event) {
            this.loadData(event.detail.offset, event.detail.limit, true);
        },

        async loadData(offset = 0, limit = 99, append = false) {
            // Load equipment data with current filters
            apiUrl = window.EquipmentFilters.buildApiUrl(this.filterState, offset, limit);
            listOptions = {
                offset: offset,
                limit: limit,
                append: append
            }
            
            await this.databaseController.queryApi(apiUrl, listOptions);
        },

        async selectEquipment(item) {
            // Load detailed item data
            apiUrl = `/api/data/items/${item.key}/concrete`;
            await this.databaseController.selectSpecificData(apiUrl, item);
        },
        
        async updateItemLevel(event) {
            // Update item level and recalculate stats
            if (!this.databaseController.selectedData) return;
            
            const newIlvl = parseInt(event.target.textContent.trim());
            const currentIlvl = this.databaseController.selectedData.concrete_ilvl || this.databaseController.selectedData.base_ilvl;
            
            if (isNaN(newIlvl) || newIlvl < 1 || newIlvl > 999) {
                event.target.textContent = currentIlvl;
                return;
            }
            
            if (newIlvl === currentIlvl) return;
            
            try {
                apiUrl = `/api/data/items/${this.databaseController.selectedData.key}/stats?ilvl=${newIlvl}`;
                const newStats = await this.databaseController.queryApi(apiUrl);
                
                this.databaseController.selectedData.stats = newStats.stat_values;
                this.databaseController.selectedData.concrete_ilvl = newStats.ilvl;
                
            } catch (error) {
                logError('Error updating item level:', error);
                event.target.textContent = currentIlvl;
            }
        },
    }));
}); 