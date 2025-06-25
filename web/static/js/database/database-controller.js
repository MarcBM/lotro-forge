// Database Controller - Pure pagination utility
// Provides pagination state and helpers for database content
// No panel-specific logic - just pagination coordination

document.addEventListener('alpine:init', () => {
    Alpine.data('databaseController', () => ({
        // Pagination state
        pagination: {
            loading: false,
            hasMore: true,
            offset: 0,
            totalResults: null,
            currentlyShowing: 0,
            sortBy: 'recent',
            searchQuery: ''
        },
        
        init() {
            console.log('Database Controller (pagination utility) initialized');
            
            // Listen for pagination updates from data providers
            window.addEventListener('update-database-pagination', this.handlePaginationUpdate.bind(this));
        },
        
        // Handle pagination updates from data providers
        handlePaginationUpdate(event) {
            this.updatePagination(event.detail);
        },
        
        // Results text helper
        getResultsText() {
            if (this.pagination.totalResults && this.pagination.currentlyShowing > 0) {
                return `Showing ${this.pagination.currentlyShowing} of ${this.pagination.totalResults} results`;
            } else if (this.pagination.loading) {
                return 'Loading...';
            } else if (this.pagination.totalResults === 0) {
                return 'No results found';
            } else {
                return '';
            }
        },
        
        // Load more handler - dispatches panel-specific event
        loadMore(panelId) {
            if (this.pagination.loading || !panelId) return;
            
            console.log(`Load more requested for ${panelId} panel`);
            this.pagination.loading = true;
            
            // Dispatch panel-specific event
            window.dispatchEvent(new CustomEvent(`database-load-more-${panelId}`, {
                detail: {
                    offset: this.pagination.offset,
                    limit: 99,
                    sortBy: this.pagination.sortBy,
                    searchQuery: this.pagination.searchQuery
                }
            }));
        },
        
        // Sort change handler - dispatches panel-specific event
        handleSort(panelId) {
            if (!panelId) return;
            
            console.log(`Sort changed to: ${this.pagination.sortBy} for ${panelId} panel`);
            
            // Reset pagination for new sort
            this.pagination.offset = 0;
            this.pagination.hasMore = true;
            this.pagination.loading = false;
            this.pagination.currentlyShowing = 0;
            
            // Dispatch panel-specific event
            window.dispatchEvent(new CustomEvent(`database-sort-changed-${panelId}`, {
                detail: {
                    sortBy: this.pagination.sortBy,
                    searchQuery: this.pagination.searchQuery
                }
            }));
        },
        
        // Search change handler - dispatches panel-specific event
        handleSearch(panelId) {
            if (!panelId) return;
            
            console.log(`Search changed to: ${this.pagination.searchQuery} for ${panelId} panel`);
            
            // Reset pagination for new search
            this.pagination.offset = 0;
            this.pagination.hasMore = true;
            this.pagination.loading = false;
            this.pagination.currentlyShowing = 0;
            
            // Dispatch panel-specific event
            window.dispatchEvent(new CustomEvent(`database-search-changed-${panelId}`, {
                detail: {
                    searchQuery: this.pagination.searchQuery,
                    sortBy: this.pagination.sortBy
                }
            }));
        },
        
        // Update pagination state (called by data providers after loading)
        updatePagination(paginationData) {
            this.pagination.hasMore = paginationData.hasMore;
            this.pagination.offset = paginationData.offset;
            this.pagination.loading = false;
            
            if (paginationData.totalResults !== undefined) {
                this.pagination.totalResults = paginationData.totalResults;
            }
            
            if (paginationData.currentlyShowing !== undefined) {
                this.pagination.currentlyShowing = paginationData.currentlyShowing;
            }
        }
    }));
}); 