# Kite OAuth Flow - Visual Diagram

## Complete OAuth Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                                 │
└─────────────────────────────────────────────────────────────────────────┘

1. User opens Dashboard → Broker Tab
   ↓
2. User selects "Kite Connect"
   ↓
3. User enters API Key & API Secret
   ↓
4. User clicks "Login with Kite" button

┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND FLOW                                    │
└─────────────────────────────────────────────────────────────────────────┘

credentials-form.js: _handleOAuth()
   ↓
   • Validates API Key & Secret
   • Calls api.initiateOAuth(broker, apiKey, apiSecret)
   ↓
api-client.js: initiateOAuth()
   ↓
   • POST /api/broker/oauth/initiate
   • Receives OAuth URL
   ↓
credentials-form.js: Opens popup window
   ↓
   • window.open(oauth_url)
   • Popup shows Kite login page
   • User authenticates with Zerodha

┌─────────────────────────────────────────────────────────────────────────┐
│                         KITE OAUTH                                       │
└─────────────────────────────────────────────────────────────────────────┘

Kite Login Page (kite.zerodha.com)
   ↓
   • User enters Zerodha credentials
   • User enters TOTP (2FA)
   • User authorizes app
   ↓
Kite redirects to callback URL:
   http://127.0.0.1:8080/api/broker/oauth/callback?request_token=xxx&status=success

┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND FLOW                                     │
└─────────────────────────────────────────────────────────────────────────┘

api/broker.py: oauth_callback()
   ↓
   • Receives request_token
   • Retrieves stored credentials from session
   ↓
broker_manager.py: complete_oauth()
   ↓
   • Creates KiteConnect instance
   • Calls kite.generate_session(request_token, api_secret)
   • Receives access_token
   ↓
   • Calculates token expiry (6 AM next day)
   • Stores access_token & expiry
   ↓
   • Calls broker_manager.connect() with token
   • Gets user profile from Kite
   ↓
   • Returns success with:
     - access_token
     - token_expiry
     - user_info (user_id, name, email)

┌─────────────────────────────────────────────────────────────────────────┐
│                         CALLBACK RESPONSE                                │
└─────────────────────────────────────────────────────────────────────────┘

api/broker.py: Returns HTML page
   ↓
   • Shows success message
   • Displays user info & token expiry
   • JavaScript sends postMessage to parent:
     {
       type: 'oauth_success',
       broker: 'kite',
       user_info: {...},
       token_expiry: '2026-02-19 06:00:00'
     }
   ↓
   • Popup closes after 3 seconds

┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND UPDATE                                  │
└─────────────────────────────────────────────────────────────────────────┘

credentials-form.js: _handleOAuthCallback()
   ↓
   • Receives postMessage from popup
   • Shows success notification
   ↓
app.js: Updates UI
   ↓
   • Calls updateBrokerStatus()
   • Calls loadBrokers()
   ↓
   • Hides credentials form
   • Shows connection status
   • Displays:
     - Broker: kite
     - User: USER_ID
     - Connected: 2026-02-18 10:30:00
     - Access Token: abc123... (truncated)
     - Expires: 2026-02-19 06:00:00

┌─────────────────────────────────────────────────────────────────────────┐
│                         TOKEN STORAGE                                    │
└─────────────────────────────────────────────────────────────────────────┘

BrokerManager instance stores:
   • self.access_token = "full_access_token_string"
   • self.token_expiry = "2026-02-19 06:00:00"
   • self.user_info = {user_id, user_name, email, broker}
   • self.current_broker = KiteAdapter instance (connected)

Flask session stores:
   • session['broker'] = 'kite'
   • session['connected'] = True

┌─────────────────────────────────────────────────────────────────────────┐
│                         TOKEN EXPIRY DISPLAY                             │
└─────────────────────────────────────────────────────────────────────────┘

app.js: updateBrokerStatus()
   ↓
Calculates hours until expiry:
   • > 6 hours: Normal display (white)
   • < 6 hours: Warning display (yellow)
   • < 1 hour: Expired display (red)
   ↓
Shows in UI:
   ┌─────────────────────────────────────┐
   │ Access Token                        │
   │ abc123def456ghi789...               │
   │ Expires: 2026-02-19 06:00:00        │
   └─────────────────────────────────────┘
```

## Key Features

### Security
- ✅ Credentials stored server-side in Flask session
- ✅ Access token not exposed to client (only truncated)
- ✅ OAuth flow uses secure popup window
- ✅ postMessage for safe cross-window communication

### User Experience
- ✅ One-click OAuth authentication
- ✅ Popup window for seamless flow
- ✅ Auto-close popup after success
- ✅ Real-time status updates
- ✅ Token expiry warnings

### Error Handling
- ✅ Validation before OAuth initiation
- ✅ Session expiry detection
- ✅ OAuth failure handling
- ✅ User-friendly error messages
- ✅ Popup blocked detection

## API Endpoints

### POST /api/broker/oauth/initiate
**Request:**
```json
{
  "broker": "kite",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret"
}
```

**Response:**
```json
{
  "success": true,
  "oauth_url": "https://kite.zerodha.com/connect/login?api_key=..."
}
```

### GET /api/broker/oauth/callback
**Query Parameters:**
- `request_token`: Token from Kite OAuth
- `status`: success/failure

**Response:**
HTML page with JavaScript that:
1. Displays success/error message
2. Sends postMessage to parent window
3. Auto-closes after 3 seconds

## Token Lifecycle

```
Token Created (OAuth Success)
   ↓
Token Valid (Until 6 AM next day)
   ↓
< 6 hours remaining → Warning displayed
   ↓
< 1 hour remaining → Expired warning
   ↓
Past 6 AM → Token expired
   ↓
User must re-authenticate
```

## Testing Checklist

- [x] OAuth URL generation works
- [x] Popup window opens correctly
- [x] Kite authentication completes
- [x] Callback receives request_token
- [x] Token exchange succeeds
- [x] Access token stored
- [x] Token expiry calculated
- [x] User info retrieved
- [x] Connection status updated
- [x] Token displayed (truncated)
- [x] Expiry time shown
- [x] Warning colors work
- [x] Error handling works
- [x] Session management works
