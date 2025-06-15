// Global Notification System
document.addEventListener('alpine:init', () => {
    Alpine.data('notifications', () => ({
        // Notification state
        notification: '',
        showNotification: false,
        notificationType: 'info', // 'success', 'error', 'warning', 'info'
        
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
            
            // Auto-hide after 3 seconds (configurable)
            const duration = type === 'error' ? 5000 : 3000; // Errors stay longer
            setTimeout(() => {
                this.hideNotification();
            }, duration);
        },
        
        // Hide notification
        hideNotification() {
            this.showNotification = false;
        },
        
        // Get CSS classes based on notification type
        get notificationClasses() {
            const baseClasses = 'fixed top-4 right-4 z-50 px-4 py-2 rounded-md shadow-lg font-medium';
            
            switch (this.notificationType) {
                case 'success':
                    return `${baseClasses} bg-green-600 text-white`;
                case 'error':
                    return `${baseClasses} bg-red-600 text-white`;
                case 'warning':
                    return `${baseClasses} bg-yellow-600 text-black`;
                case 'info':
                default:
                    return `${baseClasses} bg-lotro-gold text-lotro-dark`;
            }
        }
    }));
    
    // Global notification helper function
    window.showNotification = (message, type = 'info') => {
        window.dispatchEvent(new CustomEvent('show-notification', {
            detail: { message, type }
        }));
    };
}); 