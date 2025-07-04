// Database Controller - Handles pagination and data loading for database panels
// Manages loading states, data lists, and selected items
// Provides API query utilities and event dispatching

document.addEventListener('alpine:init', () => {
    Alpine.data('databaseController', () => ({
        // Pagination state
        pagination: {
            loading: false,
            hasMore: true,
            offset: 0,
            totalResults: null,
            currentlyShowing: 0
        },

        dataList: [],
        selectedData: null,
        loading: false,
        
        init() {
            logComponent('DatabaseController', 'initialized');
        },
        
        // Get current results status text
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
        
        // Trigger load more data for a panel
        loadMore(panelId) {
            if (this.pagination.loading || !panelId) return;
            
            logDebug(`Load more requested for ${panelId} panel`);
            this.pagination.loading = true;
            
            window.dispatchEvent(new CustomEvent(`database-load-more-${panelId}`, {
                detail: {
                    offset: this.pagination.offset,
                    limit: 99
                }
            }));
        },
        
        // Query API endpoint and handle pagination/list updates
        async queryApi(apiUrl, listOptions = null) {
            await this.waitForLoad();

            let result = null;

            try {
                this.loading = true;
                const response = await fetch(apiUrl);
                if (!response.ok) {
                    throw new Error('Failed to load data');
                }
                
                const data = await response.json();
                result = data.result;
                
                if (listOptions) {
                    if (listOptions.append) {
                        this.dataList = [...this.dataList, ...result];
                    } else {
                        this.dataList = result;
                    }
                    this.pagination.totalResults = data.total;
                    this.pagination.currentlyShowing = this.dataList.length;
                    this.pagination.hasMore = data.has_more;
                    this.pagination.offset = listOptions.offset + listOptions.limit;
                }
            } catch (error) {
                logError("Error loading data: ", error);

                if (listOptions) {
                    if (!listOptions.append) {
                        this.dataList = [];
                    }

                    this.pagination.hasMore = false;
                    this.pagination.offset = listOptions.offset;
                    this.pagination.totalResults = 0;
                    this.pagination.currentlyShowing = this.dataList.length;
                }
            } finally {
                this.loading = false;
            }

            return result;
        },

        // Load detailed data for a selected item
        async selectSpecificData(apiUrl, data) {
            await this.waitForLoad();

            if (this.selectedData && this.selectedData.key === data.key) {
                return;
            }
            try {
                this.selectedData = await this.queryApi(apiUrl);
            } catch (error) {
                logError("Error loading specific item: ", error);
            }
        },

        // Clear all data and reset pagination state
        clearData() {
            // Clear data immediately to prevent template errors
            // Use empty object instead of null to prevent Alpine.js evaluation issues
            this.selectedData = {};
            this.dataList = [];
            
            // Reset pagination state
            this.pagination.offset = 0;
            this.pagination.totalResults = null;
            this.pagination.currentlyShowing = 0;
            this.pagination.hasMore = false;
        },

        async waitForLoad() {
            let loadWaits = 0;
            while (this.loading) {
                await new Promise(resolve => setTimeout(resolve, 100));
                loadWaits++;
                if (loadWaits > 10) {
                    logWarn('Loading data took too long, skipping');
                    return;
                }
            }
        }
    }));
}); 