// Alpine.js initialization and global store setup
window.addEventListener('alpine:init', () => {
    
    // Initialize Alpine stores globally
    Alpine.store('nav', {
        isBuilderPage: window.location.pathname === '/builder'
    });
    
    // Dispatch a custom event when Alpine is ready
    window.dispatchEvent(new CustomEvent('alpine-ready'));
}); 