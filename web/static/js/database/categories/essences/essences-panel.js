// Alpine.js component for essences database panel
document.addEventListener('alpine:init', () => {
    Alpine.data('essencesPanel', (panelId) => ({
        panelId: panelId,
        databaseController: null,
        
        // Filter state
        filterOptions: {},
        filterState: {
            sort: 'name',
            search: '',
            essence_type: ''
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
            window.addEventListener('database-load-more-essences', this.handleLoadMore.bind(this));
            window.addEventListener('panel-opened-essences', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-essences', this.handlePanelClosed.bind(this));
            
            logComponent('EssencesPanel', 'initialized');
        },
        
        loadFilterOptions() {
            // Load filter options from client-side config
            if (window.EssenceFilters) {
                this.filterOptions = window.EssenceFilters.getAllFilters();
            } else {
                logWarn('EssenceFilters not loaded, filter and sort options will be empty');
                this.filterOptions = {};
            }
        },

        handlePanelOpened() {
            this.loadData();
        },

        handlePanelClosed() {
            this.databaseController.clearData();
            this.filterState.search = '';
        },
        
        handleLoadMore(event) {
            this.loadData(event.detail.offset, event.detail.limit, true);
        },

        async loadData(offset = 0, limit = 99, append = false) {
            const apiUrl = window.EssenceFilters.buildApiUrl(this.filterState, offset, limit);
            const listOptions = {
                offset: offset,
                limit: limit,
                append: append
            };
            
            await this.databaseController.queryApi(apiUrl, listOptions);
        },

        async selectEssence(essence) {
            const apiUrl = `/api/data/items/${essence.key}/concrete`;
            await this.databaseController.selectSpecificData(apiUrl, essence);
        }
    }));
}); 