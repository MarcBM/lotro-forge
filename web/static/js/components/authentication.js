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
            try {
                const res = await fetch('/api/auth/me');
                if (res.ok) {
                    this.currentUser = await res.json();
                    this.isAuthenticated = true;
                } else {
                    this.currentUser = null;
                    this.isAuthenticated = false;
                }
            } catch (e) {
                this.currentUser = null;
                this.isAuthenticated = false;
            }
        },
        
        async login() {
            console.log('Attempting login for username:', this.loginUsername);
            const formData = new FormData();
            formData.append('username', this.loginUsername);
            formData.append('password', this.loginPassword);
            
            try {
                console.log('Sending login request to /api/auth/login');
                const res = await fetch('/api/auth/login', { method: 'POST', body: formData });
                console.log('Response status:', res.status);
                console.log('Response ok:', res.ok);
                
                if (res.ok) {
                    // Success - close modal and refresh auth status
                    console.log('Login successful');
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
                    console.log('Login failed with status:', res.status);
                    try {
                        const err = await res.json();
                        console.log('Error response:', err);
                        this.loginError = err.detail || `Login failed (Status: ${res.status})`;
                    } catch (jsonError) {
                        console.log('Failed to parse error response as JSON:', jsonError);
                        this.loginError = `Login failed (Status: ${res.status})`;
                    }
                }
            } catch (e) {
                console.log('Login request failed:', e);
                this.loginError = `Network error: ${e.message}`;
            }
        },
        
        async logout() {
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                this.currentUser = null;
                this.isAuthenticated = false;
                
                // Show logout success notification using global system
                window.showNotification('Logged out successfully!', 'success');
                
                // Redirect to home page after logout
                window.location.href = '/';
            } catch (e) {
                console.log('Logout failed:', e);
                // Show error notification using global system
                window.showNotification('Logout failed. Please try again.', 'error');
            }
        },
        
        // UI interaction methods
        openLoginModal() {
            this.isLoginModalOpen = true;
            // Focus the username field after the modal is shown
            this.$nextTick(() => {
                this.$refs.usernameInput.focus();
            });
        },
        
        closeLoginModal() {
            this.isLoginModalOpen = false;
            this.loginError = '';
        }
    }));
}); 