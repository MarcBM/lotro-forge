// Logging Utility - Structured logging with environment awareness
class Logger {
    constructor() {
        this.isDevelopment = window.location.hostname === 'localhost' || 
                            window.location.hostname === '127.0.0.1' ||
                            window.location.hostname.includes('dev');
        
        this.logLevel = this.isDevelopment ? 'debug' : 'warn';
    }
    
    // Set minimum log level
    setLogLevel(level) {
        const levels = ['debug', 'info', 'warn', 'error'];
        if (levels.includes(level)) {
            this.logLevel = level;
        }
    }
    
    // Check if level should be logged
    shouldLog(level) {
        const levels = ['debug', 'info', 'warn', 'error'];
        const currentLevelIndex = levels.indexOf(this.logLevel);
        const messageLevelIndex = levels.indexOf(level);
        return messageLevelIndex >= currentLevelIndex;
    }
    
    // Log methods
    debug(message, ...args) {
        if (this.shouldLog('debug')) {
            console.log(`[DEBUG] ${message}`, ...args);
        }
    }
    
    info(message, ...args) {
        if (this.shouldLog('info')) {
            console.info(`[INFO] ${message}`, ...args);
        }
    }
    
    warn(message, ...args) {
        if (this.shouldLog('warn')) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }
    
    error(message, ...args) {
        if (this.shouldLog('error')) {
            console.error(`[ERROR] ${message}`, ...args);
        }
    }
    
    // Component-specific logging
    component(componentName, message, level = 'debug', ...args) {
        const formattedMessage = `[${componentName.toUpperCase()}] ${message}`;
        this[level](formattedMessage, ...args);
    }
    
    // API logging
    api(endpoint, method, status, duration = null) {
        const message = `${method} ${endpoint} - ${status}`;
        if (duration) {
            this.info(`${message} (${duration}ms)`);
        } else {
            this.info(message);
        }
    }
}

// Create global logger instance
window.logger = new Logger();

// Convenience functions for common logging patterns
window.logDebug = (message, ...args) => window.logger.debug(message, ...args);
window.logInfo = (message, ...args) => window.logger.info(message, ...args);
window.logWarn = (message, ...args) => window.logger.warn(message, ...args);
window.logError = (message, ...args) => window.logger.error(message, ...args);
window.logComponent = (component, message, level, ...args) => 
    window.logger.component(component, message, level, ...args); 