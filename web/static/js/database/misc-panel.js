// Misc Panel Alpine.js Component (Placeholder)
document.addEventListener('alpine:init', () => {
    Alpine.data('miscPanel', (panelId) => ({
        // Panel identification
        panelId: panelId,
        // Component state
        loading: false,
        miscItems: [],
        selectedItem: null,
        
        // Filter state
        selectedCategory: '',
        
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
            console.log('Database Misc Panel component initialized (placeholder)');
            this.loading = false;
            
            // Load available filter options
            this.loadFilterOptions();
            
            // Listen for misc-specific events from database controller
            window.addEventListener('database-load-more-misc', this.handleLoadMore.bind(this));
            
            // Listen for panel activation to load initial data
            window.addEventListener('panel-opened-misc', this.handlePanelOpened.bind(this));
        },
        
        async handlePanelOpened() {
            console.log('Misc panel opened - showing placeholder (fresh)');
            // For now, just show the placeholder content
            // When implemented, this would reload misc data with current filters
        },
        
        loadFilterOptions() {
            // Use client-side filter configuration
            if (window.MiscFilters) {
                this.filterOptions = window.MiscFilters.getMiscCategories();
            } else {
                console.warn('MiscFilters not loaded, filter options will be empty');
                this.filterOptions = [];
            }
        },
        
        applyFilters() {
            // Placeholder - would reset and reload with filters
            console.log('Misc filters applied (placeholder)');
        },
        
        handleLoadMore(event) {
            // Placeholder - would load more misc items
            console.log('Load more misc items requested (placeholder)');
        },

        handleSortChange() {
            // Handle sort change directly on the panel (placeholder)
            console.log(`Misc sort changed to: ${this.currentSort} (placeholder)`);
        },
        
        handleSearchChange() {
            // Handle search change directly on the panel (placeholder)
            console.log(`Misc search changed to: ${this.searchQuery} (placeholder)`);
        },
        
        // Builder mode detection
        isBuilderMode() {
            const builderComponent = document.getElementById('builder-component');
            return builderComponent && this.$el && builderComponent.contains(this.$el);
        }
    }));
}); 