// User Account Management Component
document.addEventListener('alpine:init', () => {
    Alpine.data('accountManagement', () => ({
        // User data
        currentUser: null,
        isLoading: true,
        
        // Form data
        displayName: '',
        email: '',
        
        // Form state
        isEditing: false,
        isSaving: false,
        message: '',
        isSuccess: false,
        
        // Password form data
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
        isChangingPassword: false,
        isSavingPassword: false,
        passwordMessage: '',
        isPasswordSuccess: false,
        
        // Original values for cancel functionality
        originalDisplayName: '',
        originalEmail: '',
        
        init() {
            // Will be called from template x-init
        },
        
        async loadUserData() {
            this.isLoading = true;
            try {
                // Use the global auth state if available, otherwise fetch
                if (window.lotroAuth && window.lotroAuth.currentUser) {
                    this.currentUser = window.lotroAuth.currentUser;
                    this.setInitialData(this.currentUser.display_name, this.currentUser.email);
                } else {
                    // Fallback to API call
                    const response = await fetch('/api/auth/me');
                    if (response.ok) {
                        this.currentUser = await response.json();
                        if (this.currentUser) {
                            this.setInitialData(this.currentUser.display_name, this.currentUser.email);
                        }
                    }
                }
            } catch (e) {
                console.error('Failed to load user data:', e);
            } finally {
                this.isLoading = false;
            }
        },
        
        setInitialData(displayName, email) {
            this.displayName = displayName || '';
            this.email = email || '';
            this.originalDisplayName = displayName || '';
            this.originalEmail = email || '';
        },
        
        formatCreatedDate() {
            if (!this.currentUser) return 'Loading...';
            try {
                const date = new Date(this.currentUser.created_at);
                return date.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
            } catch (e) {
                return 'Unknown';
            }
        },
        
        async saveProfile() {
            this.isSaving = true;
            this.message = '';
            
            try {
                const response = await fetch('/api/auth/users/profile', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        display_name: this.displayName || null,
                        email: this.email
                    })
                });
                
                if (response.ok) {
                    const updatedUser = await response.json();
                    // Update original values
                    this.originalDisplayName = updatedUser.display_name || '';
                    this.originalEmail = updatedUser.email;
                    
                    this.isEditing = false;
                    this.isSuccess = true;
                    this.message = 'Profile updated successfully! Refreshing page...';
                    
                    // Refresh the page after a short delay to show the success message
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    const error = await response.json();
                    this.isSuccess = false;
                    this.message = error.detail || 'Failed to update profile';
                }
            } catch (e) {
                this.isSuccess = false;
                this.message = 'Network error. Please try again.';
            } finally {
                this.isSaving = false;
            }
        },
        
        cancelEdit() {
            this.displayName = this.originalDisplayName;
            this.email = this.originalEmail;
            this.isEditing = false;
            this.message = '';
        },
        
        async savePassword() {
            this.isSavingPassword = true;
            this.passwordMessage = '';
            
            try {
                const response = await fetch('/api/auth/users/password', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        current_password: this.currentPassword,
                        new_password: this.newPassword,
                        confirm_password: this.confirmPassword
                    })
                });
                
                if (response.ok) {
                    this.isChangingPassword = false;
                    this.isPasswordSuccess = true;
                    this.passwordMessage = 'Password changed successfully!';
                    
                    // Clear form
                    this.currentPassword = '';
                    this.newPassword = '';
                    this.confirmPassword = '';
                    
                    // Hide success message after 3 seconds
                    setTimeout(() => {
                        this.passwordMessage = '';
                        this.isPasswordSuccess = false;
                    }, 3000);
                } else {
                    const error = await response.json();
                    this.isPasswordSuccess = false;
                    this.passwordMessage = error.detail || 'Failed to change password';
                }
            } catch (e) {
                this.isPasswordSuccess = false;
                this.passwordMessage = 'Network error. Please try again.';
            } finally {
                this.isSavingPassword = false;
            }
        },
        
        cancelPasswordEdit() {
            this.currentPassword = '';
            this.newPassword = '';
            this.confirmPassword = '';
            this.isChangingPassword = false;
            this.passwordMessage = '';
        }
    }));
}); 