// Alpine.js component for misc database panel
document.addEventListener('alpine:init', () => {
    Alpine.data('miscPanel', (panelId) => ({
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
                logError('Database controller element not found');
                return;
            }
            this.databaseController = Alpine.$data(databaseControlElement);
            
            this.loadFilterOptions();
            
            // Event listeners
            window.addEventListener('database-load-more-misc', this.handleLoadMore.bind(this));
            window.addEventListener('panel-opened-misc', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-misc', this.handlePanelClosed.bind(this));
            
            logComponent('MiscPanel', 'initialized');
        },
        
        loadFilterOptions() {
            // Load filter options from client-side config
            if (window.MiscFilters) {
                this.filterOptions = window.MiscFilters.getAllFilters();
            } else {
                logWarn('MiscFilters not loaded, filter and sort options will be empty');
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
            const apiUrl = window.MiscFilters.buildApiUrl(this.filterState, offset, limit);
            const listOptions = {
                offset: offset,
                limit: limit,
                append: append
            };
            
            await this.databaseController.queryApi(apiUrl, listOptions);
        },

        async selectMisc(misc) {
            const apiUrl = `/api/data/items/${misc.key}/concrete`;
            await this.databaseController.selectSpecificData(apiUrl, misc);
        }
    }));
}); 