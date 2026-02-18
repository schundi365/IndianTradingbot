# Session Management Implementation Guide

## Overview

This document describes the session management implementation for the Indian Market Web Dashboard, including Flask sessions, session timeout, and CSRF protection.

## Components

### 1. SessionManager (Backend)

**File**: `session_manager.py`

The `SessionManager` class handles all session-related operations on the backend:

- **Session Creation**: Creates new sessions with CSRF tokens
- **Session Validation**: Validates sessions before each request
- **Session Timeout**: Automatically expires inactive sessions
- **CSRF Protection**: Generates and validates CSRF tokens
- **User Data Storage**: Stores user-specific data in sessions

#### Key Methods

```python
# Initialize with Flask app
session_manager = SessionManager(app=app, session_timeout=3600)

# Create a new session
session_data = session_manager.create_session(user_data={'broker': 'kite'})

# Get session information
session_info = session_manager.get_session_info()

# Extend session
session_manager.extend_session()

# Clear session
session_manager.clear_session()

# CSRF token operations
csrf_token = session_manager.get_csrf_token()
is_valid = session_manager.validate_csrf_token(token)

# User data operations
session_manager.store_user_data('key', 'value')
value = session_manager.get_user_data('key')
```

### 2. Session API Endpoints

**File**: `api/session.py`

RESTful API endpoints for session management:

#### GET /api/session/info
Get current session information including:
- Session ID
- Creation time
- Last activity time
- Elapsed seconds
- Remaining seconds
- Active status

**Response**:
```json
{
  "status": "success",
  "session": {
    "session_id": "abc123...",
    "created_at": "2024-02-18T10:00:00",
    "last_activity": "2024-02-18T10:30:00",
    "elapsed_seconds": 1800,
    "remaining_seconds": 1800,
    "is_active": true
  }
}
```

#### GET /api/session/csrf-token
Get CSRF token for the current session.

**Response**:
```json
{
  "status": "success",
  "csrf_token": "xyz789..."
}
```

#### POST /api/session/extend
Extend the current session by resetting last activity time.

**Response**:
```json
{
  "status": "success",
  "message": "Session extended",
  "session": { ... }
}
```

#### POST /api/session/clear
Clear the current session (logout).

**Response**:
```json
{
  "status": "success",
  "message": "Session cleared"
}
```

#### POST /api/session/validate-csrf
Validate a CSRF token (for testing).

**Request**:
```json
{
  "csrf_token": "token_to_validate"
}
```

**Response**:
```json
{
  "status": "success",
  "valid": true
}
```

### 3. SessionManagerClient (Frontend)

**File**: `static/js/session-manager.js`

JavaScript client for session management in the browser:

#### Features

- **Automatic CSRF Token Management**: Fetches and includes CSRF tokens in requests
- **Session Monitoring**: Periodically checks session status
- **Auto-Extension**: Automatically extends sessions before expiry
- **Event Notifications**: Dispatches events for session expiration and warnings
- **Authenticated Fetch**: Wrapper for fetch API with CSRF token injection

#### Usage

```javascript
// Initialize (automatic on page load)
await window.sessionManager.init();

// Get CSRF token
const token = window.sessionManager.getCSRFToken();

// Get session info
const info = window.sessionManager.getSessionInfo();

// Extend session
await window.sessionManager.extendSession();

// Clear session
await window.sessionManager.clearSession();

// Make authenticated request
const response = await window.sessionManager.fetch('/api/endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: 'value' })
});

// Configure auto-extension
window.sessionManager.setAutoExtend(true);
window.sessionManager.setWarningThreshold(300); // 5 minutes
```

#### Events

Listen for session events:

```javascript
// Session expired
window.addEventListener('sessionExpired', (event) => {
  console.log('Session expired:', event.detail.message);
  // Show modal, redirect to login, etc.
});

// Session warning (about to expire)
window.addEventListener('sessionWarning', (event) => {
  console.log(`Session expiring in ${event.detail.remainingSeconds} seconds`);
  // Show warning notification
});
```

### 4. Decorators

**File**: `session_manager.py`

#### @require_csrf

Decorator to require CSRF token validation for routes.

```python
from session_manager import require_csrf

@app.route('/api/endpoint', methods=['POST'])
@require_csrf
def endpoint():
    return jsonify({'status': 'success'})
```

The decorator checks for CSRF token in:
1. `X-CSRF-Token` header (preferred)
2. Form data (`csrf_token` field)
3. JSON body (`csrf_token` field)

#### @require_session

Decorator to require an active session for routes.

```python
from session_manager import require_session

@app.route('/api/endpoint')
@require_session
def endpoint():
    return jsonify({'status': 'success'})
```

## Configuration

### Environment Variables

```bash
# Flask secret key (required)
export FLASK_SECRET_KEY="your-secret-key-here"

# Session timeout in seconds (default: 3600 = 1 hour)
export SESSION_TIMEOUT="3600"
```

### Flask Configuration

The following Flask session settings are configured:

```python
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=3600)
```

## Security Features

### 1. CSRF Protection

- **Token Generation**: Cryptographically secure random tokens
- **Constant-Time Comparison**: Prevents timing attacks
- **Token Validation**: Required for all state-changing operations
- **Token Rotation**: New token generated for each session

### 2. Session Security

- **HttpOnly Cookies**: Prevents XSS attacks
- **SameSite Cookies**: Prevents CSRF attacks
- **Secure Cookies**: HTTPS-only in production
- **Session Timeout**: Automatic expiration after inactivity
- **Session ID**: Unique, unpredictable session identifiers

### 3. Automatic Validation

- **Before Request**: Validates session before each request
- **Activity Tracking**: Updates last activity timestamp
- **Expiration Check**: Automatically expires inactive sessions
- **API Error Handling**: Returns appropriate error codes

## Testing

### Unit Tests

**File**: `tests/test_session_manager.py`

Run unit tests:
```bash
cd indian_dashboard
pytest tests/test_session_manager.py -v
```

Tests cover:
- Session creation and lifecycle
- CSRF token generation and validation
- Session timeout
- User data storage
- Decorator functionality
- Security features

### Integration Tests

**File**: `tests/test_session_api.py`

Run integration tests:
```bash
cd indian_dashboard
pytest tests/test_session_api.py -v
```

Tests cover:
- API endpoint functionality
- Session lifecycle through API
- CSRF token persistence
- Error handling

## Best Practices

### Backend

1. **Always use decorators** for protected routes:
   ```python
   @require_csrf  # For POST/PUT/DELETE
   @require_session  # For authenticated routes
   ```

2. **Store sensitive data in sessions**, not cookies:
   ```python
   session_manager.store_user_data('api_key', encrypted_key)
   ```

3. **Clear sessions on logout**:
   ```python
   session_manager.clear_session()
   ```

### Frontend

1. **Use sessionManager.fetch()** for API calls:
   ```javascript
   // Automatically includes CSRF token
   await window.sessionManager.fetch('/api/endpoint', {
     method: 'POST',
     body: JSON.stringify(data)
   });
   ```

2. **Handle session events**:
   ```javascript
   window.addEventListener('sessionExpired', () => {
     // Redirect to login or show modal
   });
   ```

3. **Enable auto-extension** for better UX:
   ```javascript
   window.sessionManager.setAutoExtend(true);
   ```

## Troubleshooting

### Session Expires Too Quickly

Increase session timeout:
```bash
export SESSION_TIMEOUT="7200"  # 2 hours
```

### CSRF Validation Fails

1. Ensure CSRF token is included in requests
2. Check that session is active
3. Verify token hasn't expired
4. Check browser console for errors

### Session Not Persisting

1. Verify Flask secret key is set
2. Check that cookies are enabled
3. Ensure session.permanent is True
4. Check browser cookie settings

## Production Deployment

### Required Changes

1. **Set secure secret key**:
   ```bash
   export FLASK_SECRET_KEY="$(openssl rand -hex 32)"
   ```

2. **Enable secure cookies** (HTTPS only):
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   ```

3. **Configure session timeout** appropriately:
   ```bash
   export SESSION_TIMEOUT="3600"  # 1 hour
   ```

4. **Use HTTPS** for all connections

5. **Monitor session activity** in logs

## API Integration

### Using CSRF Tokens in API Calls

All state-changing API calls (POST, PUT, DELETE) must include CSRF token:

```javascript
// Method 1: Using sessionManager.fetch()
const response = await window.sessionManager.fetch('/api/broker/connect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ broker: 'kite', credentials: {...} })
});

// Method 2: Manual header
const token = window.sessionManager.getCSRFToken();
const response = await fetch('/api/broker/connect', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': token
  },
  body: JSON.stringify({ broker: 'kite', credentials: {...} })
});
```

## Summary

The session management implementation provides:

✅ **Flask Sessions**: Secure server-side session storage  
✅ **Session Timeout**: Automatic expiration after 1 hour of inactivity  
✅ **CSRF Protection**: Token-based protection for all state-changing operations  
✅ **Auto-Extension**: Optional automatic session extension  
✅ **Event Notifications**: Browser events for session lifecycle  
✅ **Security Best Practices**: HttpOnly, SameSite, Secure cookies  
✅ **Comprehensive Testing**: Unit and integration tests  
✅ **Easy Integration**: Decorators and client library for simple usage  

The implementation follows security best practices and provides a robust foundation for user session management in the dashboard.
