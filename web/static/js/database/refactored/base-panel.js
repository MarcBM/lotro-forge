/**
 * Base Database Panel Class
 * 
 * Simplified version that provides truly generic functionality without forcing
 * false uniformities. Panels provide URLs and handle their own response parsing.
 */
class BaseDatabasePanel {
    constructor(panelId) {
        this.panelId = panelId;
    }
    
    /**
     * Initialize common state properties that all panels share
     * @returns {Object} Common state object
     */
    initializeCommonState() {
        return {
            // Panel identification
            panelId: this.panelId,
            
            // Component state - generic names
            loading: false,
            itemList: [], // Generic name for all data arrays
            selectedItem: null, // Generic name for selected item
            loadingDetails: false, // Generic name for loading item details
            
            // Sort state
            currentSort: 'name',
            availableSortOptions: [],
            
            // Search state
            searchQuery: '',
            
            // Filter options (populated by panel-specific logic)
            filterOptions: []
        };
    }
    
    /**
     * Get all common methods that can be shared across panels
     * @returns {Object} Object containing common methods
     */
    getCommonMethods() {
        return {
            // Panel lifecycle
            handlePanelOpened: this.handlePanelOpened.bind(this),
            checkDatabasePageInitialLoad: this.checkDatabasePageInitialLoad.bind(this),
            
            // Data loading
            resetAndLoad: this.resetAndLoad.bind(this),
            
            // Event handlers
            applyFilters: this.applyFilters.bind(this),
            handleLoadMore: this.handleLoadMore.bind(this),
            handleSortChange: this.handleSortChange.bind(this),
            handleSearchChange: this.handleSearchChange.bind(this),
            
            // Utility methods
            isBuilderMode: this.isBuilderMode.bind(this),
            updatePaginationState: this.updatePaginationState.bind(this),
            handleLoadError: this.handleLoadError.bind(this)
        };
    }
    
    /**
     * Common initialization logic that should be called from the panel's init() method
     * Panels should call this from their Alpine.js init() method: await basePanel.initializePanel.call(this);
     */
    async initializePanel() {
        console.log(`Database ${this.panelId} Panel component initialized`);
        this.loading = false;
        
        // Listen for panel-specific events from database controller
        window.addEventListener(`database-load-more-${this.panelId}`, this.handleLoadMore.bind(this));
        
        // Listen for panel activation to load initial data
        window.addEventListener(`panel-opened-${this.panelId}`, this.handlePanelOpened.bind(this));
        
        // Check if we're on the database page and this is the default panel
        this.checkDatabasePageInitialLoad();
    }
    
    /**
     * Check if this panel should load initial data on database page load
     */
    checkDatabasePageInitialLoad() {
        // Check if we're on the database page by looking for the database component
        const databaseComponent = document.getElementById('database-component');
        if (!databaseComponent) return;
        
        // Check if this panel is the default/active panel by checking the panel manager
        // We'll use a small delay to ensure the panel manager has initialized
        setTimeout(() => {
            // Get the panel manager component from the database component
            const panelManagerData = Alpine.$data(databaseComponent);
            if (panelManagerData && 
                panelManagerData.activePanel === this.panelId && 
                this.itemList.length === 0) {
                console.log(`Database page loaded with ${this.panelId} as default panel - loading initial data`);
                this.handlePanelOpened();
            }
        }, 100);
    }
    
    /**
     * Handle panel being opened - always reload fresh data
     */
    async handlePanelOpened() {
        console.log(`${this.panelId} panel opened - loading fresh data`);
        // Always reload data when panel is opened (fresh start)
        this.resetAndLoad();
    }
    
    /**
     * Reset data and load from the beginning
     * Panel must implement this to call their specific load method
     */
    resetAndLoad() {
        this.itemList = [];
        // Panel-specific implementation should override this
        console.warn(`Panel ${this.panelId} should implement resetAndLoad()`);
    }
    
    /**
     * Apply current filters by resetting and reloading data
     */
    applyFilters() {
        // Reset to first page and reload with filters
        this.resetAndLoad();
    }
    
    /**
     * Handle load more request from database controller
     */
    handleLoadMore(event) {
        // Panel-specific implementation should override this
        console.warn(`Panel ${this.panelId} should implement handleLoadMore()`);
    }
    
    /**
     * Handle sort change
     */
    handleSortChange() {
        // Handle sort change directly on the panel
        console.log(`${this.panelId} sort changed to: ${this.currentSort}`);
        this.resetAndLoad(); // Reload with new sort
    }
    
    /**
     * Handle search change
     */
    handleSearchChange() {
        // Handle search change directly on the panel
        console.log(`${this.panelId} search changed to: ${this.searchQuery}`);
        this.resetAndLoad(); // Reload with search
    }
    
    /**
     * Update pagination state in the database controller
     */
    updatePaginationState(hasMore, offset, totalResults) {
        window.dispatchEvent(new CustomEvent('update-database-pagination', {
            detail: {
                hasMore: hasMore,
                offset: offset,
                totalResults: totalResults,
                currentlyShowing: this.itemList.length
            }
        }));
    }
    
    /**
     * Handle errors during data loading
     */
    handleLoadError(error, append, offset) {
        console.error(`Error loading ${this.panelId}:`, error);
        
        // Handle error based on append mode
        if (!append) {
            this.itemList = [];
        }
        
        // Update pagination state on error
        this.updatePaginationState(false, offset, 0);
    }
    
    /**
     * Detect if we're in builder mode
     */
    isBuilderMode() {
        // Check if we're in the builder by looking for the builder component
        const builderComponent = document.getElementById('builder-component');
        return builderComponent && this.$el && builderComponent.contains(this.$el);
    }
    
    /**
     * Generic data loading method that accepts a URL and returns raw response data
     * Panels can use this for consistent loading behavior without forced structure
     */
    async loadDataFromUrl(url, append = false) {
        if (this.loading) return null;
        
        try {
            this.loading = true;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed to load data from ${url}`);
            }
            
            const data = await response.json();
            return data; // Return raw data - let panel handle structure
        } catch (error) {
            console.error(`Error loading data from ${url}:`, error);
            throw error; // Re-throw so panel can handle appropriately
        } finally {
            this.loading = false;
        }
    }
    
    /**
     * Generic item selection method
     * This method should be called by panel-specific select methods
     */
    async selectItem(item) {
        if (this.selectedItem && this.selectedItem.key === item.key) {
            return;
        }
        
        // Set loading state and show basic item info immediately
        this.loadingDetails = true;
        this.selectedItem = item;
        
        // Fetch complete concrete item (full item data + stats) using the concrete endpoint
        try {
            const response = await fetch(`/api/data/items/${item.key}/concrete`);
            if (!response.ok) {
                this.selectedItem = item; // Keep basic item data
                return;
            }
            this.selectedItem = await response.json();
        } catch (error) {
            console.error(`Error loading concrete item data:`, error);
            this.selectedItem = item; // Keep basic item data
        } finally {
            this.loadingDetails = false;
        }
    }
}

// Export for use in other modules
window.BaseDatabasePanel = BaseDatabasePanel; 