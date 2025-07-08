/**
 * Build Event Dispatcher - Simple utility for dispatching build-state events
 * 
 * This utility provides a centralized way for managers to dispatch build-state change events.
 * The event name defines what aspect of the build-state changed, and responding managers
 * can inspect the build-state object directly to find relevant changes.
 * 
 * Usage:
 * BuildEventDispatcher.dispatch('equipment-changed');
 * BuildEventDispatcher.dispatch('essences-changed');
 * BuildEventDispatcher.dispatch('traits-changed');
 */

class BuildEventDispatcher {
    
    /**
     * Dispatch a build-state change event
     * @param {string} eventName - The name of the event to dispatch
     */
    static dispatch(eventName) {
        if (!eventName || typeof eventName !== 'string') {
            logError('BuildEventDispatcher: eventName parameter is required and must be a string');
            return;
        }
        
        // Dispatch the specific event with bubbling enabled
        window.dispatchEvent(new CustomEvent(eventName, {
            bubbles: true
        }));
        
        // Also dispatch a general "build-changed" event for any non-general event
        if (eventName !== 'build-changed') {
            window.dispatchEvent(new CustomEvent('build-changed', {
                bubbles: true
            }));
        }
        
        // Log the event dispatch using structured logging
        logComponent('BuildEventDispatcher', `Dispatched ${eventName}`, 'debug');
        if (eventName !== 'build-changed') {
            logComponent('BuildEventDispatcher', 'Also dispatched build-changed', 'debug');
        }
    }
}

// Make it globally available
window.BuildEventDispatcher = BuildEventDispatcher; 