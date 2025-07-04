// Global Authentication Component
document.addEventListener('alpine:init', () => {
    Alpine.data('authentication', () => ({
        // Authentication state
        isLoginModalOpen: false,
        loginUsername: '',
        loginPassword: '',
        loginError: '',
        currentUser: null,
        isAuthenticated: false,
        
        init() {
            logComponent('Authentication', 'initialized');
            // Initialize global auth state
            window.lotroAuth = {
                isAuthenticated: false,
                currentUser: null
            };
            
            // Check authentication status on component initialization
            this.checkAuthStatus();
            
            // Listen for authentication events
            window.addEventListener('open-login-modal', () => {
                this.openLoginModal();
            });
            
            window.addEventListener('auth-logout', () => {
                this.logout();
            });
        },
        
        // Authentication methods
        async checkAuthStatus() {
            // Avoid multiple simultaneous calls
            if (this._checkingAuth) {
                return;
            }
            this._checkingAuth = true;
            
            try {
                const res = await fetch('/api/auth/me');
                if (res.ok) {
                    const userData = await res.json();
                    // Handle null response (unauthenticated)
                    if (userData) {
                        this.currentUser = userData;
                        this.isAuthenticated = true;
                    } else {
                        this.currentUser = null;
                        this.isAuthenticated = false;
                    }
                } else {
                    this.currentUser = null;
                    this.isAuthenticated = false;
                }
                
                // Update global auth state
                window.lotroAuth.currentUser = this.currentUser;
                window.lotroAuth.isAuthenticated = this.isAuthenticated;
                
                // Notify navigation component
                window.dispatchEvent(new CustomEvent('auth-state-changed'));
                
            } catch (e) {
                logWarn('Auth check failed:', e);
                this.currentUser = null;
                this.isAuthenticated = false;
                
                // Update global auth state
                window.lotroAuth.currentUser = null;
                window.lotroAuth.isAuthenticated = false;
                
                // Notify navigation component
                window.dispatchEvent(new CustomEvent('auth-state-changed'));
            } finally {
                this._checkingAuth = false;
            }
        },
        
        async login() {
            logInfo('Attempting login for username:', this.loginUsername);
            const formData = new FormData();
            formData.append('username', this.loginUsername);
            formData.append('password', this.loginPassword);
            
            try {
                logger.api('/api/auth/login', 'POST', 'sending');
                const res = await fetch('/api/auth/login', { method: 'POST', body: formData });
                logger.api('/api/auth/login', 'POST', res.status);
                
                if (res.ok) {
                    // Success - close modal and refresh auth status
                    logInfo('Login successful');
                    this.isLoginModalOpen = false;
                    this.loginError = '';
                    
                    // Check auth status instead of full page reload
                    await this.checkAuthStatus();
                    
                    // Clear form
                    this.loginUsername = '';
                    this.loginPassword = '';
                    
                    // Show success notification using global system
                    window.showNotification('Logged in successfully!', 'success');
                } else {
                    logWarn('Login failed with status:', res.status);
                    try {
                        const err = await res.json();
                        logDebug('Error response:', err);
                        this.loginError = err.detail || `Login failed (Status: ${res.status})`;
                    } catch (jsonError) {
                        logWarn('Failed to parse error response as JSON:', jsonError);
                        this.loginError = `Login failed (Status: ${res.status})`;
                    }
                }
            } catch (e) {
                logError('Login request failed:', e);
                this.loginError = `Network error: ${e.message}`;
            }
        },
        
        async logout() {
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                this.currentUser = null;
                this.isAuthenticated = false;
                
                // Update global auth state
                window.lotroAuth.currentUser = null;
                window.lotroAuth.isAuthenticated = false;
                
                // Notify navigation component
                window.dispatchEvent(new CustomEvent('auth-state-changed'));
                
                // Show logout success notification using global system
                window.showNotification('Logged out successfully!', 'success');
                
                // Redirect to home page after logout
                window.location.href = '/';
            } catch (e) {
                logError('Logout failed:', e);
                // Show error notification using global system
                window.showNotification('Logout failed. Please try again.', 'error');
            }
        },
        
        // UI interaction methods
        openLoginModal() {
            logDebug('Login modal opened');
            this.isLoginModalOpen = true;
            // Focus the username field after the modal is shown
            this.$nextTick(() => {
                this.$refs.usernameInput.focus();
            });
        },
        
        closeLoginModal() {
            logDebug('Login modal closed');
            this.isLoginModalOpen = false;
            this.loginError = '';
        }
    }));
}); 