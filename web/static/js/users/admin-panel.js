// Admin Panel Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('adminPanel', () => ({
        // User creation form
        newUsername: '',
        selectedRole: 'beta_tester',
        isCreating: false,
        createMessage: '',
        isCreateSuccess: false,
        generatedPassword: '',
        showPassword: false,
        
        // User management
        allUsers: [],
        isLoadingUsers: false,
        editingUserId: null,
        editingRole: '',
        isUpdatingRole: false,
        isDeletingUser: false,
        
        async createUser() {
            this.isCreating = true;
            this.createMessage = '';
            this.generatedPassword = '';
            this.showPassword = false;
            
            try {
                const response = await fetch('/api/auth/admin/users/simple', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.newUsername,
                        role: this.selectedRole
                    })
                });
                
                if (response.ok) {
                    const newUser = await response.json();
                    this.isCreateSuccess = true;
                    this.createMessage = 'User created successfully!';
                    this.generatedPassword = newUser.generated_password;
                    this.showPassword = true;
                    
                    // Refresh the user management list
                    await this.loadUsers();
                    
                    // Clear form
                    this.newUsername = '';
                    this.selectedRole = 'beta_tester';
                    
                } else {
                    const error = await response.json();
                    this.isCreateSuccess = false;
                    this.createMessage = error.detail || 'Failed to create user';
                }
            } catch (e) {
                this.isCreateSuccess = false;
                this.createMessage = 'Network error. Please try again.';
            } finally {
                this.isCreating = false;
            }
        },
        
        copyPassword() {
            navigator.clipboard.writeText(this.generatedPassword).then(() => {
                // Could add a brief 'copied!' message here if needed
            });
        },
        
        clearPassword() {
            this.generatedPassword = '';
            this.showPassword = false;
            this.createMessage = '';
        },
        
        async loadUsers() {
            this.isLoadingUsers = true;
            try {
                const response = await fetch('/api/auth/admin/users');
                if (response.ok) {
                    this.allUsers = await response.json();
                } else {
                    console.error('Failed to load users');
                }
            } catch (e) {
                console.error('Error loading users:', e);
            } finally {
                this.isLoadingUsers = false;
            }
        },
        
        startEditRole(user) {
            this.editingUserId = user.id;
            this.editingRole = user.role;
        },
        
        cancelEditRole() {
            this.editingUserId = null;
            this.editingRole = '';
        },
        
        async saveRole(userId) {
            this.isUpdatingRole = true;
            try {
                const response = await fetch(`/api/auth/admin/users/${userId}/role`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        role: this.editingRole
                    })
                });
                
                if (response.ok) {
                    const updatedUser = await response.json();
                    // Update the user in the list
                    const userIndex = this.allUsers.findIndex(u => u.id === userId);
                    if (userIndex !== -1) {
                        this.allUsers[userIndex] = updatedUser;
                    }
                    this.editingUserId = null;
                    this.editingRole = '';
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Failed to update user role');
                }
            } catch (e) {
                alert('Network error. Please try again.');
            } finally {
                this.isUpdatingRole = false;
            }
        },
        
        async deleteUser(userId, username) {
            if (!confirm(`Are you sure you want to delete user '${username}'? This action cannot be undone.`)) {
                return;
            }
            
            this.isDeletingUser = true;
            try {
                const response = await fetch(`/api/auth/admin/users/${userId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    // Remove user from the list
                    this.allUsers = this.allUsers.filter(u => u.id !== userId);
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Failed to delete user');
                }
            } catch (e) {
                alert('Network error. Please try again.');
            } finally {
                this.isDeletingUser = false;
            }
        }
    }));
}); 