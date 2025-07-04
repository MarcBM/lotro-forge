class BaseFilters { 
    // Get baseline sort options
    static getSortOptions(builderMode = false) {
        const options = [];
        options.push({ value: 'name', label: 'Name' });
        options.push({ value: 'recent', label: 'Recent' });
        options.push({ value: 'base_ilvl', label: 'Base iLvl' });
        return options;
    }
    
    // Get all filter options and their states
    static getAllFilters(builderMode = false) {
        return {
            sort: {
                options: this.getSortOptions(builderMode)
            },
            search: {
                value: ''
            }
        };
    }
    
    // Build API URL with current filters and pagination
    static buildBaseParams(filterState, offset = 0, limit = 99) {
        const params = new URLSearchParams();
        
        params.append('limit', limit);
        params.append('skip', offset);
        
        if (filterState.search) {
            params.append('search', filterState.search);
        }
        
        if (filterState.sort) {
            params.append('sort', filterState.sort);
        }

        return params;
    }
}

window.BaseFilters = BaseFilters;