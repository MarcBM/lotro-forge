// Navigation Component - Core navigation functionality only
document.addEventListener('alpine:init', () => {
    Alpine.data('navigation', () => ({
        // Page detection (for navigation highlighting)
        isBuilderPage: window.location.pathname === '/builder',
        isDatabasePage: window.location.pathname === '/database',
        isBuildsPage: window.location.pathname === '/builds',
        
        // UI state for navigation-specific elements
        isAccountDropdownOpen: false,
        
        init() {
            // Navigation initialization (minimal)
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
            // Dispatch event to trigger login modal
            window.dispatchEvent(new CustomEvent('open-login-modal'));
        },
        
        logout() {
            // Dispatch event to trigger logout
            window.dispatchEvent(new CustomEvent('auth-logout'));
            this.closeAccountDropdown();
        }
    }));
}); 