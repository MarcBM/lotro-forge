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
            console.error('BuildEventDispatcher: eventName parameter is required and must be a string');
            return;
        }
        
        // Dispatch the event with no details, but with bubbling enabled
        window.dispatchEvent(new CustomEvent(eventName, {
            bubbles: true
        }));
        
        // Log the event dispatch
        if (window.logDebug) {
            window.logDebug(`BuildEventDispatcher: Dispatched ${eventName}`);
        } else {
            console.debug(`BuildEventDispatcher: Dispatched ${eventName}`);
        }
    }
}

// Make it globally available
window.BuildEventDispatcher = BuildEventDispatcher; 