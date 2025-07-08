// Alpine.js component for traits database panel
document.addEventListener('alpine:init', () => {
    Alpine.data('traitsPanel', (panelId) => ({
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
            window.addEventListener('database-load-more-traits', this.handleLoadMore.bind(this));
            window.addEventListener('panel-opened-traits', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-traits', this.handlePanelClosed.bind(this));
        },
        
        loadFilterOptions() {
            // Load filter options from client-side config
            if (window.TraitsFilters) {
                this.filterOptions = window.TraitsFilters.getAllFilters();
            } else {
                logWarn('TraitsFilters not loaded, filter and sort options will be empty');
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
            const apiUrl = window.TraitsFilters.buildApiUrl(this.filterState, offset, limit);
            const listOptions = {
                offset: offset,
                limit: limit,
                append: append
            };
            
            await this.databaseController.queryApi(apiUrl, listOptions);
        },

        async selectTrait(trait) {
            const apiUrl = `/api/data/items/${trait.key}/concrete`;
            await this.databaseController.selectSpecificData(apiUrl, trait);
        }
    }));
}); 