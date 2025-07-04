# Logging Migration Guide

## Quick Reference

```javascript
// Replace console.log with appropriate level
console.log('Component initialized');           // → logComponent('Component', 'initialized')
console.log('API call successful');             // → logInfo('API call successful')
console.log('Debug info:', data);               // → logDebug('Debug info:', data)
console.warn('Warning message');                // → logWarn('Warning message')
console.error('Error occurred');                // → logError('Error occurred')
```

## Migration Patterns

### Component Initialization
```javascript
// ❌ Old
console.log('Equipment Manager initialized');

// ✅ New
logComponent('EquipmentManager', 'initialized');
```

### API Calls
```javascript
// ❌ Old
console.log('Sending login request to /api/auth/login');

// ✅ New
logInfo('Sending login request to /api/auth/login');
// Or use the API logger
logger.api('/api/auth/login', 'POST', 'sending');
```

### Debug Information
```javascript
// ❌ Old
console.log('Updated equipment for', slotName, ':', item);

// ✅ New
logDebug('Updated equipment for', slotName, ':', item);
```

### Error Logging
```javascript
// ❌ Old
console.error('Failed to load data:', error);

// ✅ New
logError('Failed to load data:', error);
```

## Log Levels

| Level | Use Case | Production |
|-------|----------|------------|
| `debug` | Development debugging | ❌ Hidden |
| `info` | General information | ✅ Visible |
| `warn` | Warnings | ✅ Visible |
| `error` | Errors | ✅ Visible |

## Environment Behavior

- **Development**: Shows all log levels
- **Production**: Shows only `warn` and `error` by default
- **Configurable**: Can override with `logger.setLogLevel('debug')` 