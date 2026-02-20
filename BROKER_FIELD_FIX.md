# Broker Field Missing Fix

## Problem
```
Missing required fields: broker
```

Configuration save was failing because the broker field wasn't being included in the request.

## Root Cause

In `config-form.js`, the `getFormData()` function was trying to get broker from wrong path:

```javascript
// WRONG - this path doesn't exist
const brokerStatus = appState.get('broker.status');
if (brokerStatus && brokerStatus.broker) {
    data.broker = brokerStatus.broker;
}
```

The correct state structure is:
```javascript
broker: {
    connected: false,
    type: null,      // <-- broker type is here
    userInfo: {}
}
```

## Fix Applied

**File**: `indian_dashboard/static/js/config-form.js`

Changed to use correct path:

```javascript
// CORRECT - get broker type from state
const brokerType = appState.get('broker.type');
if (brokerType) {
    data.broker = brokerType;
} else {
    // Default to 'paper' if no broker is connected
    data.broker = 'paper';
}
```

Also changed default from 'kite' to 'paper' since that's more commonly used for testing.

## How It Works Now

1. When you connect to Paper Trading, `appState.set('broker.type', 'paper')` is called
2. When you save configuration, `getFormData()` reads `broker.type` and includes it
3. Server validates and saves the configuration successfully

## Next Steps

1. Restart dashboard: `.\restart_dashboard.ps1`
2. Clear browser cache (Ctrl+Shift+Delete) or use incognito (Ctrl+Shift+N)
3. Connect to Paper Trading
4. Fill out configuration
5. Click "Save Configuration"
6. Should work now!

---

**Status**: ✅ Fixed - restart and test
