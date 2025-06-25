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
            if (this.pagination.totalResults) {
                return `${this.pagination.totalResults} total results`;
            } else if (this.pagination.loading) {
                return 'Loading...';
            } else {
                return '';
            }
        },
        
        // Load more handler - dispatches event for consumers
        loadMore() {
            if (this.pagination.loading) return;
            
            console.log('Load more requested');
            this.pagination.loading = true;
            
            // Dispatch event for data providers to handle
            window.dispatchEvent(new CustomEvent('database-load-more', {
                detail: {
                    offset: this.pagination.offset,
                    limit: 99,
                    sortBy: this.pagination.sortBy,
                    searchQuery: this.pagination.searchQuery
                }
            }));
        },
        
        // Sort change handler - dispatches event for consumers
        handleSort() {
            console.log('Sort changed to:', this.pagination.sortBy);
            
            // Reset pagination for new sort
            this.pagination.offset = 0;
            this.pagination.hasMore = true;
            this.pagination.loading = false;
            
            // Dispatch event for data providers to handle
            window.dispatchEvent(new CustomEvent('database-sort-changed', {
                detail: {
                    sortBy: this.pagination.sortBy,
                    searchQuery: this.pagination.searchQuery
                }
            }));
        },
        
        // Search change handler - dispatches event for consumers
        handleSearch() {
            console.log('Search changed to:', this.pagination.searchQuery);
            
            // Reset pagination for new search
            this.pagination.offset = 0;
            this.pagination.hasMore = true;
            this.pagination.loading = false;
            
            // Dispatch event for data providers to handle
            window.dispatchEvent(new CustomEvent('database-search-changed', {
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
        }
    }));
}); 