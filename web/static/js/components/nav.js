// Navigation Component - Core navigation functionality only
document.addEventListener('alpine:init', () => {
    Alpine.data('navigation', () => ({
        // Page detection (for navigation highlighting)
        isBuilderPage: window.location.pathname === '/builder',
        isDatabasePage: window.location.pathname === '/database',
        isBuildsPage: window.location.pathname === '/builds',
        
        // UI state for navigation-specific elements
        isAccountDropdownOpen: false,
        
        // Authentication state (reactive)
        isAuthenticated: false,
        currentUser: null,
        
        init() {
            logComponent('Navigation', 'initialized');
            // Navigation initialization (minimal)
            this.updateAuthState();
            
            // Listen for auth state changes
            window.addEventListener('auth-state-changed', () => {
                this.updateAuthState();
            });
        },
        
        updateAuthState() {
            this.isAuthenticated = window.lotroAuth?.isAuthenticated || false;
            this.currentUser = window.lotroAuth?.currentUser || null;
        },
        
        // Navigation UI methods
        toggleAccountDropdown() {
            this.isAccountDropdownOpen = !this.isAccountDropdownOpen;
        },
        
        closeAccountDropdown() {
            this.isAccountDropdownOpen = false;
        },
        
        // Methods to trigger global authentication actions
        openLoginModal() {
            logDebug('Opening login modal');
            // Dispatch event to trigger login modal
            window.dispatchEvent(new CustomEvent('open-login-modal'));
        },
        
        logout() {
            logInfo('User logout initiated');
            // Dispatch event to trigger logout
            window.dispatchEvent(new CustomEvent('auth-logout'));
            this.closeAccountDropdown();
        }
    }));
}); 