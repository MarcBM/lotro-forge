// Equipment Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentPanel', () => ({
        // Component state
        loading: false,
        equipment: [],
        selectedEquipment: null,
        concreteEquipment: null,
        
        // Builder-specific properties
        isSlotFilterLocked: false, // Always false for now - builder mode integration comes later
        selectedSlot: '',
        
        // Filter options
        filterOptions: [], // Will be populated from API
        
        // Sort state
        currentSort: 'recent',
        
        async init() {
            // Set the base panel sort dropdown to match our default
            this.$dispatch('set-sort', { panelId: 'equipment', sortBy: this.currentSort });
            // Load available filter options
            await this.loadFilterOptions();
            // Initial load with a fixed limit of 99
            this.loadEquipment(0, 99);
            
            // Listen for load-more events from the base panel
            window.addEventListener('load-more', this.handleLoadMore.bind(this));
            // Listen for sort-change events from the base panel
            window.addEventListener('sort-change', this.handleSortChange.bind(this));
        },
        
        async loadFilterOptions() {
            try {
                const response = await fetch('/api/data/equipment/slots');
                if (!response.ok) {
                    throw new Error('Failed to load equipment slots');
                }
                const data = await response.json();
                this.filterOptions = data.slots || [];
            } catch (error) {
                this.filterOptions = [];
            }
        },
        
        applyFilters() {
            // Reset to first page and reload with filters
            this.equipment = [];
            // Reset pagination state to indicate this is a fresh search
            this.$dispatch('reset-pagination-equipment');
            this.loadEquipment(0, 99);
        },
        
        handleLoadMore(event) {
            if (event.detail.panelId !== 'equipment') return;
            this.loadMoreEquipment(event.detail.offset, event.detail.limit);
        },

        handleSortChange(event) {
            if (event.detail.panelId !== 'equipment') return;
            this.currentSort = event.detail.sortBy;
            this.applyFilters(); // Reload with new sort
        },
        
        buildApiUrl(offset, limit) {
            const params = new URLSearchParams({
                limit: limit.toString(),
                skip: offset.toString()
            });
            
            // Add filter parameters
            if (this.selectedSlot) {
                params.append('slot_group', this.selectedSlot);
            }
            
            // Always add sort parameter
            if (this.currentSort) {
                params.append('sort', this.currentSort);
            }
            
            return `/api/data/equipment?${params.toString()}`;
        },

        async loadEquipment(offset, limit) {
            if (this.loading) return;
            
            try {
                this.loading = true;
                const response = await fetch(this.buildApiUrl(offset, limit));
                if (!response.ok) {
                    throw new Error('Failed to load equipment');
                }
                
                const data = await response.json();
                // Use Alpine's reactive array update
                this.equipment = data.equipment;
                // Update pagination state in the base panel
                this.$dispatch('update-pagination-equipment', { 
                    panelId: 'equipment',
                    hasMore: data.has_more,
                    offset: offset + limit,
                    newItems: data.equipment,
                    totalResults: data.total
                });
            } catch (error) {
                this.equipment = [];
                this.$dispatch('update-pagination-equipment', { 
                    panelId: 'equipment',
                    hasMore: false,
                    offset: offset,
                    newItems: [],
                    totalResults: 0
                });
            } finally {
                this.loading = false;
            }
        },

        async loadMoreEquipment(offset, limit) {
            if (this.loading) return;
            
            try {
                this.loading = true;
                const response = await fetch(this.buildApiUrl(offset, limit));
                if (!response.ok) {
                    throw new Error('Failed to load more equipment');
                }
                
                const data = await response.json();
                // Use Alpine's reactive array update
                this.equipment = [...this.equipment, ...data.equipment];
                // Update pagination state in the base panel
                this.$dispatch('update-pagination-equipment', { 
                    panelId: 'equipment',
                    hasMore: data.has_more,
                    offset: offset + limit,
                    newItems: data.equipment,
                    totalResults: data.total
                });
            } catch (error) {
                this.$dispatch('update-pagination-equipment', { 
                    panelId: 'equipment',
                    hasMore: false,
                    offset: offset,
                    newItems: [],
                    totalResults: this.equipment.length
                });
            } finally {
                this.loading = false;
            }
        },

        async selectEquipment(equipment) {
            this.selectedEquipment = equipment;
            // Reset concrete equipment to prevent showing stale data
            this.concreteEquipment = null;
            
            // Fetch concrete equipment details
            try {
                const response = await fetch(`/api/data/equipment/${equipment.key}/concrete?ilvl=${equipment.base_ilvl}`);
                if (!response.ok) {
                    return; // Keep concreteEquipment as null
                }
                this.concreteEquipment = await response.json();
            } catch (error) {
                this.concreteEquipment = null;
            }
        },
        
        // EV Color coding methods using percentiles
        getEvColorClass(ev) {
            // Find the item with this EV value to get its percentile
            const item = this.equipment.find(item => item.ev === ev);
            if (!item || item.ev_percentile === undefined) {
                return 'text-lotro-common';
            }
            
            const percentile = item.ev_percentile;
            
            // Color based on percentile ranges
            if (percentile >= 90) return 'text-lotro-legendary';      // Top 10%
            if (percentile >= 75) return 'text-lotro-incomparable';   // Top 25%
            if (percentile >= 50) return 'text-lotro-rare';           // Top 50%
            if (percentile >= 25) return 'text-lotro-uncommon';       // Top 75%
            return 'text-lotro-common';                               // Bottom 25%
        },
        
        getTestColorClass(index) {
            // For test mode - cycle through colors
            const colors = ['text-red-400', 'text-blue-400', 'text-green-400', 'text-yellow-400', 'text-purple-400'];
            return colors[index % colors.length];
        },
        
        // Test mode property (always false for now)
        get testMode() {
            return false; // TODO: Implement test mode toggle
        },
        
        // Computed properties for selected equipment
        get selectedEquipmentIconUrls() {
            // Reverse the icon URLs so the base icon renders first and overlays render on top
            const urls = this.selectedEquipment?.icon_urls || [];
            return [...urls].reverse();
        },
        
        get selectedEquipmentName() {
            return this.selectedEquipment?.name || '';
        },
        
        get selectedEquipmentBaseIlvl() {
            return this.selectedEquipment?.base_ilvl || 0;
        },
        
        get selectedEquipmentEv() {
            // Only show EV in builder mode
            if (!this.isBuilderMode()) return '';
            return this.selectedEquipment?.ev ? this.selectedEquipment.ev.toFixed(2) : '0.00';
        },
        
        // Computed properties for concrete equipment stats
        get concreteEquipmentStats() {
            if (!this.concreteEquipment?.stat_values) return [];
            // Filter out ARMOUR since it's displayed separately
            return this.concreteEquipment.stat_values.filter(stat => stat.stat_name !== 'ARMOUR');
        },
        
        // Safely get ARMOUR stat value
        get concreteEquipmentArmour() {
            if (!this.concreteEquipment?.stat_values || !Array.isArray(this.concreteEquipment.stat_values)) {
                return null;
            }
            const armourStat = this.concreteEquipment.stat_values.find(s => s.stat_name === 'ARMOUR');
            return armourStat ? Math.floor(armourStat.value) : null;
        },
        
        // Builder mode detection
        isBuilderMode() {
            // Check if we're in the builder by looking for the builder component
            const builderComponent = document.getElementById('builder-component');
            return builderComponent && this.$el && builderComponent.contains(this.$el);
        }
    }));
}); 