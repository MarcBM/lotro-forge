// Alpine.js component for sources database panel
document.addEventListener('alpine:init', () => {
    Alpine.data('sourcesPanel', (panelId) => ({
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
            
            // Event listeners
            window.addEventListener('database-load-more-sources', this.handleLoadMore.bind(this));
            window.addEventListener('panel-opened-sources', this.handlePanelOpened.bind(this));
            window.addEventListener('panel-closed-sources', this.handlePanelClosed.bind(this));
            
            console.log('Database Sources Panel component initialized');
        },
        
        loadFilterOptions() {
            // Load filter options from client-side config
            if (window.SourcesFilters) {
                this.filterOptions = window.SourcesFilters.getAllFilters();
            } else {
                console.warn('SourcesFilters not loaded, filter and sort options will be empty');
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
            const apiUrl = window.SourcesFilters.buildApiUrl(this.filterState, offset, limit);
            const listOptions = {
                offset: offset,
                limit: limit,
                append: append
            };
            
            await this.databaseController.queryApi(apiUrl, listOptions);
        },

        async selectSource(source) {
            const apiUrl = `/api/data/items/${source.key}/concrete`;
            await this.databaseController.selectSpecificData(apiUrl, source);
        }
    }));
}); 