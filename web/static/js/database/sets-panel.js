// Alpine.js component for sets database panel
document.addEventListener('alpine:init', () => {
    Alpine.data('setsPanel', (panelId) => ({
        panelId: panelId,
        databaseController: null,
        
        // Filter state
        filterOptions: {},
        filterState: {
            sort: 'name',
            search: ''
        },
        
        async init() {
            const databaseControlElement = document.getElementById('database-controller');
            if (!databaseControlElement) {
                console.error('Database controller element not found');
                return;
            }
            this.databaseController = Alpine.$data(databaseControlElement);
            
            this.loadFilterOptions();
            
            // Setup event listeners
            
            window.addEventListener('database-load-more-sets', this.handleLoadMore.bind(this));
            window.addEventListener('panel-opened-sets', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-sets', this.handlePanelClosed.bind(this));
            
            console.log('Database Sets Panel component initialized');
        },
        
        async handlePanelOpened() {
            console.log('Sets panel opened - showing placeholder (fresh)');
            // For now, just show the placeholder content
            // When implemented, this would reload sets data with current filters
        },
        
        loadFilterOptions() {
            // Load filter options from client-side config
            if (window.SetsFilters) {
                this.filterOptions = window.SetsFilters.getAllFilters();
            } else {
                console.warn('SetsFilters not loaded, filter and sort options will be empty');
                this.filterOptions = {};
            }
        },

        handlePanelOpened() {
            // this.loadData(); // Commented out - placeholder panel
        },

        handlePanelClosed() {
            this.databaseController.clearData();
            this.filterState.search = '';
        },
        
        handleLoadMore(event) {
            this.loadData(event.detail.offset, event.detail.limit, true);
        },

        async loadData(offset = 0, limit = 99, append = false) {
            const apiUrl = window.SetsFilters.buildApiUrl(this.filterState, offset, limit);
            const listOptions = {
                offset: offset,
                limit: limit,
                append: append
            };
            
            await this.databaseController.queryApi(apiUrl, listOptions);
        },

        async selectSet(set) {
            const apiUrl = `/api/data/items/${set.key}/concrete`;
            await this.databaseController.selectSpecificData(apiUrl, set);
        }
    }));
}); 