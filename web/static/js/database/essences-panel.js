// Essences Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('essencesPanel', () => ({
        searchQuery: '',
        essences: [],
        selectedEssence: null,
        concreteEssence: null,
        loading: false,
        
        // Filter state
        selectedLevel: '',
        availableLevels: [],
        selectedEssenceType: '',
        availableEssenceTypes: [],
        
        // Sort state
        currentSort: 'name',
        
        init() {
            // Initialize with empty array to ensure reactivity
            this.essences = [];
            // Set the base panel sort dropdown to match our default
            this.$dispatch('set-sort', { panelId: 'essences', sortBy: this.currentSort });
            // Load available filter options
            this.loadAvailableLevels();
            this.loadAvailableEssenceTypes();
            // Initial load with a fixed limit of 99 (multiple of 3)
            this.loadEssences(0, 99);
            
            // Listen for load-more events from the base panel
            window.addEventListener('load-more', this.handleLoadMore.bind(this));
            // Listen for sort-change events from the base panel
            window.addEventListener('sort-change', this.handleSortChange.bind(this));
        },

        async loadAvailableLevels() {
            try {
                const response = await fetch('/api/data/essences/levels');
                if (!response.ok) {
                    throw new Error('Failed to load levels');
                }
                const data = await response.json();
                this.availableLevels = data.levels;
            } catch (error) {
                this.availableLevels = [];
            }
        },

        async loadAvailableEssenceTypes() {
            try {
                const response = await fetch('/api/data/essences/types');
                if (!response.ok) {
                    throw new Error('Failed to load essence types');
                }
                const data = await response.json();
                this.availableEssenceTypes = data.types;
            } catch (error) {
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
            this.loadMoreEssences(event.detail.offset, event.detail.limit);
        },

        handleSortChange(event) {
            if (event.detail.panelId !== 'essences') return;
            this.currentSort = event.detail.sortBy;
            this.applyFilters(); // Reload with new sort
        },
        
        buildApiUrl(offset, limit) {
            const params = new URLSearchParams({
                limit: limit.toString(),
                skip: offset.toString()
            });
            
            // Add filter parameters
            if (this.selectedLevel) {
                params.append('ilvl', this.selectedLevel);
            }
            if (this.selectedEssenceType) {
                params.append('essence_type', this.selectedEssenceType);
            }
            
            // Always add sort parameter
            if (this.currentSort) {
                params.append('sort', this.currentSort);
            }
            
            return `/api/data/essences?${params.toString()}`;
        },

        async loadEssences(offset, limit) {
            if (this.loading) return;
            
            try {
                this.loading = true;
                const response = await fetch(this.buildApiUrl(offset, limit));
                if (!response.ok) {
                    throw new Error('Failed to load essences');
                }
                
                const data = await response.json();
                // Use Alpine's reactive array update
                this.essences = data.essences;
                // Update pagination state in the base panel
                this.$dispatch('update-pagination-essences', { 
                    panelId: 'essences',
                    hasMore: data.essences.length === limit,
                    offset: offset + limit,
                    newItems: data.essences,
                    totalResults: data.total
                });
            } catch (error) {
                this.essences = [];
                this.$dispatch('update-pagination-essences', { 
                    panelId: 'essences',
                    hasMore: false,
                    offset: offset,
                    newItems: [],
                    totalResults: 0
                });
            } finally {
                this.loading = false;
            }
        },

        async loadMoreEssences(offset, limit) {
            if (this.loading) return;
            
            try {
                this.loading = true;
                const response = await fetch(this.buildApiUrl(offset, limit));
                if (!response.ok) {
                    throw new Error('Failed to load more essences');
                }
                
                const data = await response.json();
                // Use Alpine's reactive array update
                this.essences = [...this.essences, ...data.essences];
                // Update pagination state in the base panel
                this.$dispatch('update-pagination-essences', { 
                    panelId: 'essences',
                    hasMore: data.essences.length === limit,
                    offset: offset + limit,
                    newItems: data.essences,
                    totalResults: data.total
                });
            } catch (error) {
                this.$dispatch('update-pagination-essences', { 
                    panelId: 'essences',
                    hasMore: false,
                    offset: offset,
                    newItems: [],
                    totalResults: this.essences.length
                });
            } finally {
                this.loading = false;
            }
        },

        async selectEssence(essence) {
            this.selectedEssence = essence;
            try {
                const response = await fetch(`/api/data/essences/${essence.key}/concrete?ilvl=${essence.base_ilvl}`);
                if (!response.ok) {
                    throw new Error('Failed to load concrete essence');
                }
                this.concreteEssence = await response.json();
            } catch (error) {
                this.concreteEssence = null;
            }
        }
    }));
}); 