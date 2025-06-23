// Essences Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('essencesPanel', () => ({
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
            // Set the base panel sort dropdown to match our default
            this.$dispatch('set-sort', { panelId: 'essences', sortBy: this.currentSort });
            // Load available filter options from client-side config
            this.loadFilterOptions();
            // Initial load with a fixed limit of 99
            this.loadEssences(0, 99);
            
            // Listen for load-more events from the base panel
            window.addEventListener('load-more', this.handleLoadMore.bind(this));
            // Listen for sort-change events from the base panel
            window.addEventListener('sort-change', this.handleSortChange.bind(this));
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
            this.essences = [];
            // Reset pagination state to indicate this is a fresh search
            this.$dispatch('reset-pagination-essences');
            this.loadEssences(0, 99);
        },
        
        handleLoadMore(event) {
            if (event.detail.panelId !== 'essences') return;
            this.loadEssences(event.detail.offset, event.detail.limit, true);
        },

        handleSortChange(event) {
            if (event.detail.panelId !== 'essences') return;
            this.currentSort = event.detail.sortBy;
            this.applyFilters(); // Reload with new sort
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
                
                // Update pagination state in the base panel
                this.$dispatch('update-pagination-essences', { 
                    panelId: 'essences',
                    hasMore: data.has_more,
                    offset: offset + limit,
                    newItems: data.essences,
                    totalResults: data.total
                });
            } catch (error) {
                // Handle error based on append mode
                if (!append) {
                    this.essences = [];
                }
                
                this.$dispatch('update-pagination-essences', { 
                    panelId: 'essences',
                    hasMore: false,
                    offset: offset,
                    newItems: [],
                    totalResults: append ? this.essences.length : 0
                });
            } finally {
                this.loading = false;
            }
        },

        async selectEssence(essence) {
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
            return false;
        }
    }));
}); 