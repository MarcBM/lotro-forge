// Global Notification System
document.addEventListener('alpine:init', () => {
    Alpine.data('notifications', () => ({
        // Notification state
        notification: '',
        showNotification: false,
        notificationType: 'info', // 'success', 'error', 'warning', 'info', 'debug'
        
        init() {
            // Listen for global notification events
            window.addEventListener('show-notification', (event) => {
                this.displayNotification(event.detail.message, event.detail.type || 'info');
            });
        },
        
        // Display a notification
        displayNotification(message, type = 'info') {
            this.notification = message;
            this.notificationType = type;
            this.showNotification = true;
            
            // Auto-hide after configurable duration
            const duration = this.getNotificationDuration(type);
            setTimeout(() => {
                this.hideNotification();
            }, duration);
        },
        
        // Hide notification
        hideNotification() {
            this.showNotification = false;
        },
        
        // Get duration based on notification type
        getNotificationDuration(type) {
            switch (type) {
                case 'error':
                    return 6000; // 6 seconds for errors
                case 'warning':
                    return 5000; // 5 seconds for warnings
                case 'success':
                    return 4000; // 4 seconds for success
                case 'debug':
                    return 3000; // 3 seconds for debug
                case 'info':
                default:
                    return 3000; // 3 seconds for info
            }
        },
        
        // Get CSS classes based on notification type
        get notificationClasses() {
            const baseClasses = 'fixed top-4 right-4 z-50 px-4 py-2 rounded-md shadow-lg font-medium max-w-md';
            
            switch (this.notificationType) {
                case 'success':
                    return `${baseClasses} bg-green-600 text-white border-l-4 border-green-800`;
                case 'error':
                    return `${baseClasses} bg-red-600 text-white border-l-4 border-red-800`;
                case 'warning':
                    return `${baseClasses} bg-yellow-600 text-black border-l-4 border-yellow-800`;
                case 'debug':
                    return `${baseClasses} bg-gray-600 text-white border-l-4 border-gray-800`;
                case 'info':
                default:
                    return `${baseClasses} bg-lotro-gold text-lotro-dark border-l-4 border-yellow-600`;
            }
        }
    }));
    
    // Global notification helper functions
    window.showNotification = (message, type = 'info') => {
        window.dispatchEvent(new CustomEvent('show-notification', {
            detail: { message, type }
        }));
    };
    
    // Convenience methods for common notification types
    window.showSuccess = (message) => window.showNotification(message, 'success');
    window.showError = (message) => window.showNotification(message, 'error');
    window.showWarning = (message) => window.showNotification(message, 'warning');
    window.showInfo = (message) => window.showNotification(message, 'info');
    window.showDebug = (message) => window.showNotification(message, 'debug');
    
    // Enhanced error handling with automatic notification
    window.handleApiError = async (response, defaultMessage = 'An error occurred') => {
        try {
            const errorData = await response.json();
            const errorMessage = errorData.detail || errorData.message || defaultMessage;
            window.showError(errorMessage);
            return errorMessage;
        } catch (e) {
            const errorMessage = `${defaultMessage} (Status: ${response.status})`;
            window.showError(errorMessage);
            return errorMessage;
        }
    };
    
    // Network error handler
    window.handleNetworkError = (error, defaultMessage = 'Network error occurred') => {
        const errorMessage = `${defaultMessage}: ${error.message}`;
        window.showError(errorMessage);
        return errorMessage;
    };
}); 