// Essences Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('essencesPanel', (panelId) => ({
        // Panel identification
        panelId: panelId,
        // Component state
        loading: false,
        essences: [],
        selectedEssence: null,
        loadingStats: false,
        
        // Filter state
        selectedEssenceType: '',
        
        // Filter options (populated from client-side config)
        availableEssenceTypes: [],
        
        // Sort state
        currentSort: 'recent',
        
        async init() {
            console.log('Database Essences Panel component initialized');
            this.loading = false;
            
            // Load available filter options from client-side config
            this.loadFilterOptions();
            
            // Listen for essences-specific events from database controller
            window.addEventListener('database-load-more-essences', this.handleLoadMore.bind(this));
            window.addEventListener('database-sort-changed-essences', this.handleSortChange.bind(this));
            window.addEventListener('database-search-changed-essences', this.handleSearchChange.bind(this));
            
            // Listen for panel activation to load initial data
            window.addEventListener('panel-opened-essences', this.handlePanelOpened.bind(this));
        },
        
        async handlePanelOpened() {
            console.log('Essences panel opened - loading fresh data');
            // Always reload data when panel is opened (fresh start)
            this.resetAndLoad();
        },
        
        resetAndLoad() {
            this.essences = [];
            this.loadEssences(0, 99);
        },
        
        loadFilterOptions() {
            // Use client-side filter configuration instead of API calls
            if (window.EssenceFilters) {
                this.availableEssenceTypes = window.EssenceFilters.getEssenceTypes();
            } else {
                console.warn('EssenceFilters not loaded, filter options will be empty');
                this.availableEssenceTypes = [];
            }
        },
        
        applyFilters() {
            // Reset to first page and reload with filters
            this.resetAndLoad();
        },
        
        handleLoadMore(event) {
            this.loadEssences(event.detail.offset, event.detail.limit, true);
        },

        handleSortChange(event) {
            this.currentSort = event.detail.sortBy;
            this.resetAndLoad(); // Reload with new sort
        },
        
        handleSearchChange(event) {
            // Handle search from centralized controller
            this.resetAndLoad(); // Reload with search
        },
        
        buildApiUrl(offset, limit) {
            const filters = {
                limit: limit,
                skip: offset,
                sort: this.currentSort
            };
            
            // Add filter parameters
            if (this.selectedEssenceType) {
                filters.essence_type = this.selectedEssenceType;
            }
            
            const params = window.EssenceFilters ? 
                window.EssenceFilters.buildQueryParams(filters) :
                new URLSearchParams(filters);
            
            return `/api/data/essences/?${params.toString()}`;
        },

        async loadEssences(offset, limit, append = false) {
            if (this.loading) return;
            
            try {
                this.loading = true;
                const response = await fetch(this.buildApiUrl(offset, limit));
                if (!response.ok) {
                    throw new Error('Failed to load essences');
                }
                
                const data = await response.json();
                
                // Update essences array based on append flag
                if (append) {
                    this.essences = [...this.essences, ...data.essences];
                } else {
                    this.essences = data.essences;
                }
                
                // Update pagination state in the database controller
                window.dispatchEvent(new CustomEvent('update-database-pagination', {
                    detail: {
                        hasMore: data.has_more,
                        offset: offset + limit,
                        totalResults: data.total,
                        currentlyShowing: this.essences.length
                    }
                }));
            } catch (error) {
                // Handle error based on append mode
                if (!append) {
                    this.essences = [];
                }
                
                // Update pagination state on error
                window.dispatchEvent(new CustomEvent('update-database-pagination', {
                    detail: {
                        hasMore: false,
                        offset: offset,
                        totalResults: 0,
                        currentlyShowing: this.essences.length
                    }
                }));
            } finally {
                this.loading = false;
            }
        },

        async selectEssence(essence) {
            if (this.selectedEssence && this.selectedEssence.key === essence.key) {
                return;
            }
            // Set loading state and show basic item info immediately
            this.loadingStats = true;
            this.selectedEssence = essence;
            
            // Fetch complete concrete item (full item data + stats) using the concrete endpoint
            try {
                const response = await fetch(`/api/data/items/${essence.key}/concrete`);
                if (!response.ok) {
                    this.selectedEssence = essence; // Keep basic item data
                    return;
                }
                this.selectedEssence = await response.json();
            } catch (error) {
                this.selectedEssence = essence; // Keep basic item data
            } finally {
                this.loadingStats = false;
            }
        },
        
        // Builder mode detection (essences don't have builder mode currently)
        isBuilderMode() {
            // Check if we're in the builder by looking for the builder component
            const builderComponent = document.getElementById('builder-component');
            return builderComponent && this.$el && builderComponent.contains(this.$el);
        }
    }));
}); 