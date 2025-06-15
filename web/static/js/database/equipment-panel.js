// Equipment Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentPanel', () => ({
        searchQuery: '',
        equipment: [],
        selectedEquipment: null,
        concreteEquipment: null,
        loading: false,
        
        // Filter state
        selectedSlot: '',
        filterOptions: [],
        
        // Sort state
        currentSort: 'ev',
        
        // Test mode
        testMode: false,
        
        // Pagination state for builder mode
        hasMore: true,
        items: [],
        totalResults: null,
        sortBy: 'ev',
        
        // New state for pre-selecting
        itemToPreselect: null,
        
        // New state for slot filter lock
        isSlotFilterLocked: false,
        
        // Computed getters for safe template access
        get selectedEquipmentIconUrls() {
            return this.selectedEquipment && Array.isArray(this.selectedEquipment.icon_urls) 
                ? this.selectedEquipment.icon_urls.slice().reverse() 
                : [];
        },
        
        get selectedEquipmentName() {
            return this.selectedEquipment ? this.selectedEquipment.name : '';
        },
        
        get selectedEquipmentBaseIlvl() {
            return this.selectedEquipment ? this.selectedEquipment.base_ilvl : '';
        },
        
        get selectedEquipmentEv() {
            return this.selectedEquipment ? (this.selectedEquipment.ev || '0.00') : '0.00';
        },
        
        get concreteEquipmentStats() {
            return this.concreteEquipment && Array.isArray(this.concreteEquipment.stat_values)
                ? this.concreteEquipment.stat_values.filter(s => s.stat_name !== 'ARMOUR')
                : [];
        },
        
        init() {
            // Initialize the component
            console.log('Equipment panel initialized');
            this.loadFilterOptions();
            this.search();
            
            // Listen for builder events
            window.addEventListener('equipment-search', (event) => {
                this.searchQuery = event.detail.query || '';
                this.selectedSlot = event.detail.slot || '';
                this.search();
            });
            
            // Listen for item preselection from builder
            window.addEventListener('preselect-item', (event) => {
                if (event.detail.panelType === 'equipment') {
                    this.itemToPreselect = event.detail.item;
                    this.preselectItem();
                }
            });
        },
        
        async loadFilterOptions() {
            try {
                const response = await fetch('/api/equipment/filters');
                if (response.ok) {
                    const data = await response.json();
                    this.filterOptions = data.slot_options || [];
                } else {
                    console.error('Failed to load filter options');
                }
            } catch (error) {
                console.error('Error loading filter options:', error);
            }
        },
        
        async search() {
            this.loading = true;
            try {
                const params = new URLSearchParams({
                    q: this.searchQuery,
                    slot: this.selectedSlot,
                    sort: this.currentSort,
                    limit: this.isBuilderMode() ? '33' : '99'
                });
                
                const response = await fetch(`/api/equipment/search?${params}`);
                if (response.ok) {
                    const result = await response.json();
                    this.equipment = result.items || [];
                    this.items = this.equipment; // For builder mode compatibility
                    this.totalResults = result.total;
                    this.hasMore = this.equipment.length < result.total;
                    
                    // Auto-select first item if in builder mode and no item is selected
                    if (this.isBuilderMode() && this.equipment.length > 0 && !this.selectedEquipment) {
                        this.selectEquipment(this.equipment[0]);
                    }
                    
                    // Handle preselection if there's an item to preselect
                    if (this.itemToPreselect) {
                        this.preselectItem();
                    }
                } else {
                    console.error('Search failed');
                }
            } catch (error) {
                console.error('Search error:', error);
            } finally {
                this.loading = false;
            }
        },
        
        async loadMore() {
            if (!this.hasMore || this.loading) return;
            
            this.loading = true;
            try {
                const params = new URLSearchParams({
                    q: this.searchQuery,
                    slot: this.selectedSlot,
                    sort: this.currentSort,
                    offset: this.equipment.length.toString(),
                    limit: this.isBuilderMode() ? '33' : '99'
                });
                
                const response = await fetch(`/api/equipment/search?${params}`);
                if (response.ok) {
                    const result = await response.json();
                    const newItems = result.items || [];
                    this.equipment = [...this.equipment, ...newItems];
                    this.items = this.equipment; // For builder mode compatibility
                    this.hasMore = this.equipment.length < result.total;
                } else {
                    console.error('Load more failed');
                }
            } catch (error) {
                console.error('Load more error:', error);
            } finally {
                this.loading = false;
            }
        },
        
        async selectEquipment(item) {
            this.selectedEquipment = item;
            
            // Load concrete equipment data
            if (item && item.key) {
                try {
                    const response = await fetch(`/api/equipment/${item.key}`);
                    if (response.ok) {
                        this.concreteEquipment = await response.json();
                    } else {
                        console.error('Failed to load concrete equipment');
                        this.concreteEquipment = null;
                    }
                } catch (error) {
                    console.error('Error loading concrete equipment:', error);
                    this.concreteEquipment = null;
                }
            } else {
                this.concreteEquipment = null;
            }
        },
        
        preselectItem() {
            if (!this.itemToPreselect) return;
            
            // Find the item in the current equipment list
            const item = this.equipment.find(eq => eq.key === this.itemToPreselect.key);
            if (item) {
                this.selectEquipment(item);
                this.itemToPreselect = null; // Clear preselection
            }
        },
        
        applyFilters() {
            this.search();
        },
        
        sortBy(field) {
            this.currentSort = field;
            this.search();
        },
        
        toggleTestMode() {
            this.testMode = !this.testMode;
        },
        
        getEvColorClass(ev) {
            const value = parseFloat(ev) || 0;
            if (value >= 90) return 'text-red-400';
            if (value >= 80) return 'text-orange-400';
            if (value >= 70) return 'text-yellow-400';
            if (value >= 60) return 'text-green-400';
            if (value >= 50) return 'text-blue-400';
            return 'text-gray-400';
        },
        
        getTestColorClass(index) {
            const colors = ['text-red-400', 'text-orange-400', 'text-yellow-400', 'text-green-400', 'text-blue-400', 'text-purple-400'];
            return colors[index % colors.length];
        },
        
        isBuilderMode() {
            return window.location.pathname === '/builder';
        }
    }));
}); 