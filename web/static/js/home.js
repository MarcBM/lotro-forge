// Home Page Authentication Component
document.addEventListener('alpine:init', () => {
    Alpine.data('homeAuth', () => ({
        showAuthMessage: false,
        authMessage: '',
        authMessageType: 'info',
        
        init() {
            logComponent('HomeAuth', 'initialized');
            // Check URL parameters for authentication messages
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('login_required')) {
                this.showAuthMessage = true;
                this.authMessage = 'Please sign in to access that page.';
                this.authMessageType = 'info';
            } else if (urlParams.has('session_expired')) {
                this.showAuthMessage = true;
                this.authMessage = 'Your session has expired. Please sign in again.';
                this.authMessageType = 'warning';
            } else if (urlParams.has('user_inactive')) {
                this.showAuthMessage = true;
                this.authMessage = 'Your account is inactive. Please contact support.';
                this.authMessageType = 'error';
            }
            
            // Auto-hide message after 5 seconds
            if (this.showAuthMessage) {
                setTimeout(() => {
                    this.showAuthMessage = false;
                    // Clean up URL parameters
                    const url = new URL(window.location);
                    url.searchParams.delete('login_required');
                    url.searchParams.delete('session_expired');
                    url.searchParams.delete('user_inactive');
                    window.history.replaceState({}, '', url);
                }, 5000);
            }
        }
    }));
}); 