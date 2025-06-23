// Database Base Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('databasePanel', (panelId) => ({
        // Pagination state
        hasMore: true,
        offset: 0,
        items: [], // Track total items
        totalResults: null, // Track total results count
        
        // Sort state
        sortBy: 'recent', // Default sort option
        
        // Event handlers for pagination
        handlePaginationUpdate(detail) {
            this.hasMore = detail.hasMore;
            
            // Determine if this is a fresh search or load-more
            // For fresh search: offset - limit should equal 0 (first load)
            // For load-more: offset - limit should equal current items length
            const expectedCurrentLength = detail.offset - 99; // 99 is our limit
            const isFreshSearch = expectedCurrentLength === 0;
            
            if (isFreshSearch) {
                // Fresh search - replace items
                this.items = detail.newItems || [];
            } else {
                // Load more - append items
                this.items = [...this.items, ...detail.newItems || []];
            }
            
            this.offset = detail.offset;
            
            // Update total results if provided
            if (detail.totalResults !== undefined) {
                this.totalResults = detail.totalResults;
            }
        },

        handlePaginationReset() {
            this.items = [];
            this.totalResults = null;
            this.hasMore = true;
            this.offset = 0;
        },

        // Event dispatchers for panel components to override
        handleSortChange() {
            // Dispatch a custom event that the panel component can listen for
            const event = new CustomEvent('sort-change', {
                detail: {
                    panelId,
                    sortBy: this.sortBy
                }
            });
            window.dispatchEvent(event);
        },

        async loadMore() {
            // Dispatch a custom event that the panel component can listen for
            const event = new CustomEvent('load-more', {
                detail: {
                    panelId,
                    offset: this.offset,
                    limit: 99
                }
            });
            window.dispatchEvent(event);
        }
    }));
}); 