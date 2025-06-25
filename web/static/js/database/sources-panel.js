// Sources Panel Alpine.js Component (Placeholder)
document.addEventListener('alpine:init', () => {
    Alpine.data('sourcesPanel', (panelId) => ({
        // Panel identification
        panelId: panelId,
        // Component state
        loading: false,
        sources: [],
        selectedSource: null,
        
        // Filter state
        selectedType: '',
        
        // Filter options
        filterOptions: [],
        
        // Sort state
        currentSort: 'name',
        availableSortOptions: [
            { value: 'name', label: 'Name' },
            { value: 'recent', label: 'Recent' },
            { value: 'base_ilvl', label: 'Base iLvl' }
        ],
        
        // Search state
        searchQuery: '',
        
        async init() {
            console.log('Database Sources Panel component initialized (placeholder)');
            this.loading = false;
            
            // Load available filter options
            this.loadFilterOptions();
            
            // Listen for sources-specific events from database controller
            window.addEventListener('database-load-more-sources', this.handleLoadMore.bind(this));
            
            // Listen for panel activation to load initial data
            window.addEventListener('panel-opened-sources', this.handlePanelOpened.bind(this));
        },
        
        async handlePanelOpened() {
            console.log('Sources panel opened - showing placeholder (fresh)');
            // For now, just show the placeholder content
            // When implemented, this would reload sources data with current filters
        },
        
        loadFilterOptions() {
            // Use client-side filter configuration
            if (window.SourcesFilters) {
                this.filterOptions = window.SourcesFilters.getSourceTypes();
            } else {
                console.warn('SourcesFilters not loaded, filter options will be empty');
                this.filterOptions = [];
            }
        },
        
        applyFilters() {
            // Placeholder - would reset and reload with filters
            console.log('Sources filters applied (placeholder)');
        },
        
        handleLoadMore(event) {
            // Placeholder - would load more sources
            console.log('Load more sources requested (placeholder)');
        },

        handleSortChange() {
            // Handle sort change directly on the panel (placeholder)
            console.log(`Sources sort changed to: ${this.currentSort} (placeholder)`);
        },
        
        handleSearchChange() {
            // Handle search change directly on the panel (placeholder)
            console.log(`Sources search changed to: ${this.searchQuery} (placeholder)`);
        },
        
        // Builder mode detection
        isBuilderMode() {
            const builderComponent = document.getElementById('builder-component');
            return builderComponent && this.$el && builderComponent.contains(this.$el);
        }
    }));
}); 