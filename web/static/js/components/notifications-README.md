# Global Notification System

The notification system provides a consistent way to display user feedback throughout the application.

## Usage

### Simple Notification
```javascript
// Show a basic info notification
window.showNotification('Data saved successfully!');
```

### Typed Notifications
```javascript
// Success notification (green)
window.showNotification('Login successful!', 'success');

// Error notification (red, stays longer)
window.showNotification('Failed to save data', 'error');

// Warning notification (yellow)
window.showNotification('Please review your input', 'warning');

// Info notification (gold - default)
window.showNotification('New feature available', 'info');
```

## From Alpine.js Components

### Using Events
```javascript
// In any Alpine.js component
someMethod() {
    try {
        // ... some operation
        window.showNotification('Operation completed!', 'success');
    } catch (error) {
        window.showNotification('Operation failed: ' + error.message, 'error');
    }
}
```

### Using Custom Events
```javascript
// Dispatch a custom event with notification
window.dispatchEvent(new CustomEvent('show-notification', {
    detail: { 
        message: 'Custom notification!',
        type: 'success' 
    }
}));
```

## Notification Types

- **`success`**: Green background, white text, 3-second duration
- **`error`**: Red background, white text, 5-second duration
- **`warning`**: Yellow background, black text, 3-second duration  
- **`info`**: Gold background, dark text, 3-second duration (default)

## Features

- **Auto-dismiss**: Notifications automatically disappear after 3-5 seconds
- **Click to dismiss**: Users can click notifications to dismiss them immediately
- **Close button**: Each notification has a close button
- **Type-based icons**: Different icons for each notification type
- **Responsive**: Works well on mobile and desktop
- **Z-index safe**: Positioned above all other content

## Global Availability

The notification system is available everywhere because:
- It's loaded in the base template before other scripts
- The `window.showNotification()` function is globally accessible
- The notification component listens for events globally

## Examples in Practice

### Form Validation
```javascript
validateForm() {
    if (!this.email) {
        window.showNotification('Email is required', 'warning');
        return false;
    }
    if (!this.isValidEmail(this.email)) {
        window.showNotification('Please enter a valid email address', 'error');
        return false;
    }
    return true;
}
```

### API Calls
```javascript
async saveData() {
    try {
        const response = await fetch('/api/save', { 
            method: 'POST', 
            body: JSON.stringify(this.data) 
        });
        
        if (response.ok) {
            window.showNotification('Data saved successfully!', 'success');
        } else {
            window.showNotification('Failed to save data', 'error');
        }
    } catch (error) {
        window.showNotification('Network error: ' + error.message, 'error');
    }
}
```

### User Actions
```javascript
deleteItem(id) {
    if (confirm('Are you sure?')) {
        // ... delete logic
        window.showNotification('Item deleted', 'info');
    }
}
``` 