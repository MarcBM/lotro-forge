# Notification System

## Quick Usage

```javascript
// Basic notifications
window.showSuccess('Operation completed!');
window.showError('Something went wrong');
window.showWarning('Please check input');
window.showInfo('Information message');

// Enhanced error handling
await window.handleApiError(response, 'Failed to save data');
window.handleNetworkError(e, 'Connection failed');
```

## Available Types

| Type | Duration | Use Case |
|------|----------|----------|
| `success` | 4s | Successful operations |
| `error` | 6s | Errors and failures |
| `warning` | 5s | Warnings and cautions |
| `info` | 3s | General information |
| `debug` | 3s | Debug information |

## Migration

**Replace alerts:**
```javascript
// ❌ Old
alert('Error occurred');

// ✅ New
window.showError('Error occurred');
```

**Replace manual error handling:**
```javascript
// ❌ Old
if (!response.ok) {
    const error = await response.json();
    alert(error.detail || 'Error');
}

// ✅ New
if (!response.ok) {
    await window.handleApiError(response, 'Error');
}
```

## Best Practices

- Use descriptive messages
- Choose appropriate notification types
- Never use `alert()` - use notifications instead
- Use `handleApiError()` and `handleNetworkError()` for consistent error handling 