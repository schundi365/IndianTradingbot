# Indian Market Dashboard - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8080/api`  
**Last Updated:** 2024-02-18

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Codes](#error-codes)
5. [Broker API](#broker-api)
6. [Instruments API](#instruments-api)
7. [Configuration API](#configuration-api)
8. [Bot Control API](#bot-control-api)
9. [Session API](#session-api)

---

## Overview

The Indian Market Dashboard API provides RESTful endpoints for managing broker connections, instruments, trading configurations, and bot control. All endpoints return JSON responses with a consistent structure.

### Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "error": "Error message if success is false"
}
```

### Content Type

All requests and responses use `application/json` content type.

---

## Authentication

Currently, the API uses Flask session-based authentication. After connecting to a broker via `/api/broker/connect`, the session is maintained for subsequent requests.

### Session Management

- Sessions expire after 1 hour of inactivity
- CSRF protection is enabled for state-changing operations
- Use `/api/session/info` to check session status

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

| Limit Type | Rate | Applies To |
|------------|------|------------|
| READ | 100/minute | GET endpoints |
| WRITE | 30/minute | POST/PUT/DELETE endpoints |
| AUTH | 10/minute | Authentication endpoints |
| STATUS | 200/minute | Status check endpoints |
| EXPENSIVE | 5/minute | Resource-intensive operations |


### Rate Limit Headers

When rate limited, responses include:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645123456
```

### Rate Limit Error Response

```json
{
  "success": false,
  "error": "Rate limit exceeded. Please try again later."
}
```

**Status Code:** `429 Too Many Requests`

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Broker not connected" | No active broker connection | Connect to a broker first |
| "Invalid configuration" | Config validation failed | Check configuration format |
| "Session expired" | Session timeout | Re-authenticate |
| "Instrument not found" | Invalid instrument token | Verify instrument exists |
| "Bot already running" | Attempted to start running bot | Stop bot first |

---


## Broker API

Base path: `/api/broker`

### List Supported Brokers

Get a list of all supported brokers.

**Endpoint:** `GET /api/broker/list`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/broker/list HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "brokers": [
    {
      "id": "kite",
      "name": "Kite Connect",
      "logo": "/static/logos/kite.png",
      "supports_oauth": true
    },
    {
      "id": "alice_blue",
      "name": "Alice Blue",
      "logo": "/static/logos/alice.png",
      "supports_oauth": false
    },
    {
      "id": "paper",
      "name": "Paper Trading",
      "logo": "/static/logos/paper.png",
      "supports_oauth": false
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

### Get Credentials Form

Get the credential form fields required for a specific broker.

**Endpoint:** `GET /api/broker/credentials-form/:broker`

**Rate Limit:** 100/minute

**Path Parameters:**
- `broker` (string, required) - Broker ID (e.g., "kite", "alice_blue")

**Request:**
```http
GET /api/broker/credentials-form/kite HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "broker": "kite",
  "fields": [
    {
      "name": "api_key",
      "type": "text",
      "label": "API Key",
      "required": true,
      "placeholder": "Enter your API key"
    },
    {
      "name": "api_secret",
      "type": "password",
      "label": "API Secret",
      "required": true,
      "placeholder": "Enter your API secret"
    },
    {
      "name": "oauth",
      "type": "button",
      "label": "Login with Kite",
      "action": "oauth"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid broker ID
- `500 Internal Server Error` - Server error

**Error Example:**
```json
{
  "success": false,
  "error": "Invalid broker type. Must be one of: kite, alice_blue, angel_one, upstox, paper"
}
```

---


### Connect to Broker

Connect to a broker using credentials.

**Endpoint:** `POST /api/broker/connect`

**Rate Limit:** 10/minute (AUTH)

**Request Body:**
```json
{
  "broker": "kite",
  "credentials": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_access_token"
  },
  "save_credentials": true
}
```

**Request:**
```http
POST /api/broker/connect HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "broker": "kite",
  "credentials": {
    "api_key": "abc123xyz",
    "api_secret": "secret456",
    "access_token": "token789"
  },
  "save_credentials": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to kite",
  "user_info": {
    "user_id": "AB1234",
    "user_name": "John Doe",
    "email": "john@example.com",
    "broker": "ZERODHA"
  },
  "credentials_saved": true
}
```

**Status Codes:**
- `200 OK` - Connection successful
- `400 Bad Request` - Invalid credentials or broker
- `500 Internal Server Error` - Server error

**Error Examples:**
```json
{
  "success": false,
  "error": "Invalid broker type. Must be one of: kite, alice_blue, angel_one, upstox, paper"
}
```

```json
{
  "success": false,
  "error": "Authentication failed: Invalid API credentials"
}
```

---

### Disconnect from Broker

Disconnect from the currently connected broker.

**Endpoint:** `POST /api/broker/disconnect`

**Rate Limit:** 30/minute

**Request:**
```http
POST /api/broker/disconnect HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Disconnected from broker"
}
```

**Status Codes:**
- `200 OK` - Disconnection successful
- `400 Bad Request` - No broker connected
- `500 Internal Server Error` - Server error

---


### Get Broker Status

Get the current broker connection status.

**Endpoint:** `GET /api/broker/status`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/broker/status HTTP/1.1
Host: localhost:8080
```

**Response (Connected):**
```json
{
  "success": true,
  "status": {
    "connected": true,
    "broker": "kite",
    "user_id": "AB1234",
    "user_name": "John Doe",
    "connected_at": "2024-02-18T10:30:00Z"
  }
}
```

**Response (Not Connected):**
```json
{
  "success": true,
  "status": {
    "connected": false,
    "broker": null
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

### Test Connection

Test the current broker connection.

**Endpoint:** `POST /api/broker/test`

**Rate Limit:** 30/minute

**Request:**
```http
POST /api/broker/test HTTP/1.1
Host: localhost:8080
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Connection test successful"
}
```

**Response (Failure):**
```json
{
  "success": false,
  "message": "Connection test failed: Token expired"
}
```

**Status Codes:**
- `200 OK` - Test successful
- `400 Bad Request` - Test failed
- `500 Internal Server Error` - Server error

---


### Initiate OAuth Flow

Initiate OAuth authentication flow for supported brokers (e.g., Kite Connect).

**Endpoint:** `POST /api/broker/oauth/initiate`

**Rate Limit:** 10/minute (AUTH)

**Request Body:**
```json
{
  "broker": "kite",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret"
}
```

**Request:**
```http
POST /api/broker/oauth/initiate HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "broker": "kite",
  "api_key": "abc123xyz",
  "api_secret": "secret456"
}
```

**Response:**
```json
{
  "success": true,
  "oauth_url": "https://kite.zerodha.com/connect/login?api_key=abc123xyz&v=3"
}
```

**Status Codes:**
- `200 OK` - OAuth URL generated
- `400 Bad Request` - OAuth not supported or invalid parameters
- `500 Internal Server Error` - Server error

**Error Example:**
```json
{
  "success": false,
  "error": "OAuth not supported for this broker"
}
```

---

### OAuth Callback

Handle OAuth callback from broker (internal endpoint).

**Endpoint:** `GET /api/broker/oauth/callback`

**Query Parameters:**
- `request_token` (string) - Token from OAuth provider
- `status` (string) - "success" or "failure"

**Note:** This endpoint is called by the OAuth provider and returns HTML, not JSON.

---

### List Saved Credentials

Get a list of brokers with saved encrypted credentials.

**Endpoint:** `GET /api/broker/credentials/saved`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/broker/credentials/saved HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "brokers": ["kite", "alice_blue"]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---


### Load Saved Credentials

Load saved credentials and connect to broker.

**Endpoint:** `POST /api/broker/credentials/load/:broker`

**Rate Limit:** 10/minute (AUTH)

**Path Parameters:**
- `broker` (string, required) - Broker ID

**Request:**
```http
POST /api/broker/credentials/load/kite HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to kite using saved credentials",
  "user_info": {
    "user_id": "AB1234",
    "user_name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Status Codes:**
- `200 OK` - Connection successful
- `400 Bad Request` - Connection failed
- `404 Not Found` - No saved credentials found
- `500 Internal Server Error` - Server error

---

### Delete Saved Credentials

Delete saved credentials for a broker.

**Endpoint:** `DELETE /api/broker/credentials/delete/:broker`

**Rate Limit:** 30/minute

**Path Parameters:**
- `broker` (string, required) - Broker ID

**Request:**
```http
DELETE /api/broker/credentials/delete/kite HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted saved credentials for kite"
}
```

**Status Codes:**
- `200 OK` - Deletion successful
- `404 Not Found` - No saved credentials found
- `500 Internal Server Error` - Server error

---


## Instruments API

Base path: `/api/instruments`

### Get Instruments

Get list of tradeable instruments with optional filtering.

**Endpoint:** `GET /api/instruments`

**Rate Limit:** 100/minute

**Query Parameters:**
- `search` (string, optional) - Search query for symbol or name
- `exchange` (string, optional) - Comma-separated exchanges (e.g., "NSE,BSE")
- `instrument_type` (string, optional) - Comma-separated types (e.g., "EQ,FUT")
- `segment` (string, optional) - Comma-separated segments

**Request:**
```http
GET /api/instruments?exchange=NSE&instrument_type=EQ&search=RELIANCE HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "instruments": [
    {
      "instrument_token": 738561,
      "exchange_token": 2884,
      "tradingsymbol": "RELIANCE",
      "name": "RELIANCE INDUSTRIES LTD",
      "last_price": 2450.50,
      "expiry": null,
      "strike": null,
      "tick_size": 0.05,
      "lot_size": 1,
      "instrument_type": "EQ",
      "segment": "NSE",
      "exchange": "NSE"
    }
  ],
  "count": 1,
  "cache_info": {
    "cached": true,
    "timestamp": "2024-02-18T10:00:00Z",
    "age_seconds": 1800
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Broker not connected
- `500 Internal Server Error` - Server error

**Error Example:**
```json
{
  "success": false,
  "error": "Broker not connected"
}
```

---

### Refresh Instruments

Force refresh instruments from broker API.

**Endpoint:** `POST /api/instruments/refresh`

**Rate Limit:** 5/minute (EXPENSIVE)

**Request:**
```http
POST /api/instruments/refresh HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Instruments refreshed",
  "count": 5432
}
```

**Status Codes:**
- `200 OK` - Refresh successful
- `400 Bad Request` - Broker not connected
- `500 Internal Server Error` - Server error

---


### Get Instrument by Token

Get details of a specific instrument by its token.

**Endpoint:** `GET /api/instruments/:token`

**Rate Limit:** 100/minute

**Path Parameters:**
- `token` (integer, required) - Instrument token

**Request:**
```http
GET /api/instruments/738561 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "instrument": {
    "instrument_token": 738561,
    "exchange_token": 2884,
    "tradingsymbol": "RELIANCE",
    "name": "RELIANCE INDUSTRIES LTD",
    "last_price": 2450.50,
    "expiry": null,
    "strike": null,
    "tick_size": 0.05,
    "lot_size": 1,
    "instrument_type": "EQ",
    "segment": "NSE",
    "exchange": "NSE"
  }
}
```

**Status Codes:**
- `200 OK` - Instrument found
- `400 Bad Request` - Invalid token or broker not connected
- `404 Not Found` - Instrument not found
- `500 Internal Server Error` - Server error

---

### Get Quote

Get real-time quote for a trading symbol.

**Endpoint:** `GET /api/instruments/quote/:symbol`

**Rate Limit:** 100/minute

**Path Parameters:**
- `symbol` (string, required) - Trading symbol

**Request:**
```http
GET /api/instruments/quote/RELIANCE HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "symbol": "RELIANCE",
  "quote": {
    "last_price": 2450.50,
    "last_traded_quantity": 100,
    "average_traded_price": 2448.75,
    "volume_traded": 1234567,
    "total_buy_quantity": 50000,
    "total_sell_quantity": 45000,
    "ohlc": {
      "open": 2445.00,
      "high": 2455.00,
      "low": 2440.00,
      "close": 2448.00
    },
    "change": 2.50,
    "change_percent": 0.10
  }
}
```

**Status Codes:**
- `200 OK` - Quote retrieved
- `400 Bad Request` - Invalid symbol or broker not connected
- `404 Not Found` - Quote not available
- `500 Internal Server Error` - Server error

---


### Get Cache Info

Get information about the instruments cache.

**Endpoint:** `GET /api/instruments/cache-info`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/instruments/cache-info HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "cache_info": {
    "cached": true,
    "timestamp": "2024-02-18T10:00:00Z",
    "age_seconds": 1800,
    "expires_in_seconds": 84600,
    "broker": "kite"
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - No broker connected
- `500 Internal Server Error` - Server error

---

## Configuration API

Base path: `/api/config`

### Get Current Configuration

Get the currently active trading configuration.

**Endpoint:** `GET /api/config`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/config HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "config": {
    "name": "NIFTY Futures Strategy",
    "broker": "kite",
    "instruments": [
      {
        "symbol": "NIFTY24FEB24000CE",
        "exchange": "NFO",
        "instrument_token": 12345678
      }
    ],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0,
    "max_positions": 3,
    "max_daily_loss": 5.0,
    "position_sizing": "fixed",
    "base_position_size": 50000,
    "indicators": {
      "ema_fast": 9,
      "ema_slow": 21,
      "rsi_period": 14
    },
    "trading_hours": {
      "start": "09:15",
      "end": "15:30"
    },
    "paper_trading": false
  }
}
```

**Status Codes:**
- `200 OK` - Configuration found
- `404 Not Found` - No active configuration
- `500 Internal Server Error` - Server error

---


### Save Configuration

Save a trading configuration.

**Endpoint:** `POST /api/config`

**Rate Limit:** 30/minute

**Request Body:**
```json
{
  "config": {
    "name": "NIFTY Futures Strategy",
    "broker": "kite",
    "instruments": [...],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0,
    "max_positions": 3,
    "max_daily_loss": 5.0
  },
  "name": "nifty_futures_v1"
}
```

**Request:**
```http
POST /api/config HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "config": {
    "broker": "kite",
    "instruments": [{"symbol": "NIFTY24FEB24000CE", "exchange": "NFO"}],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0,
    "max_positions": 3
  },
  "name": "my_strategy"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration saved as \"my_strategy\""
}
```

**Status Codes:**
- `200 OK` - Configuration saved
- `400 Bad Request` - Invalid configuration
- `500 Internal Server Error` - Server error

**Error Example:**
```json
{
  "success": false,
  "error": "Invalid configuration",
  "details": [
    "instruments: Must have at least 1 item",
    "risk_per_trade: Must be between 0.1 and 100"
  ]
}
```

---

### List Configurations

Get a list of all saved configurations.

**Endpoint:** `GET /api/config/list`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/config/list HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "configs": [
    {
      "name": "nifty_futures_v1",
      "description": "NIFTY Futures Strategy",
      "broker": "kite",
      "strategy": "trend_following",
      "instruments_count": 1
    },
    {
      "name": "banknifty_options",
      "description": "BANKNIFTY Options Strategy",
      "broker": "kite",
      "strategy": "mean_reversion",
      "instruments_count": 3
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---


### Get Configuration by Name

Load a specific saved configuration.

**Endpoint:** `GET /api/config/:name`

**Rate Limit:** 100/minute

**Path Parameters:**
- `name` (string, required) - Configuration name

**Request:**
```http
GET /api/config/nifty_futures_v1 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "name": "nifty_futures_v1",
  "config": {
    "broker": "kite",
    "instruments": [...],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0
  }
}
```

**Status Codes:**
- `200 OK` - Configuration found
- `404 Not Found` - Configuration not found
- `500 Internal Server Error` - Server error

---

### Delete Configuration

Delete a saved configuration.

**Endpoint:** `DELETE /api/config/:name`

**Rate Limit:** 30/minute

**Path Parameters:**
- `name` (string, required) - Configuration name

**Request:**
```http
DELETE /api/config/nifty_futures_v1 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration \"nifty_futures_v1\" deleted"
}
```

**Status Codes:**
- `200 OK` - Deletion successful
- `404 Not Found` - Configuration not found
- `500 Internal Server Error` - Server error

---

### Get Preset Configurations

Get available preset configurations.

**Endpoint:** `GET /api/config/presets`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/config/presets HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "presets": [
    {
      "id": "nifty_futures",
      "name": "NIFTY 50 Futures",
      "description": "Trend following strategy for NIFTY futures",
      "strategy": "trend_following",
      "config": {
        "strategy": "trend_following",
        "timeframe": "15min",
        "risk_per_trade": 2.0,
        "max_positions": 2
      }
    },
    {
      "id": "banknifty_futures",
      "name": "BANKNIFTY Futures",
      "description": "Trend following strategy for BANKNIFTY futures",
      "strategy": "trend_following",
      "config": {...}
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---


### Validate Configuration

Validate a configuration without saving it.

**Endpoint:** `POST /api/config/validate`

**Rate Limit:** 30/minute

**Request Body:**
```json
{
  "config": {
    "broker": "kite",
    "instruments": [...],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0
  }
}
```

**Request:**
```http
POST /api/config/validate HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "config": {
    "broker": "kite",
    "instruments": [],
    "strategy": "invalid_strategy",
    "timeframe": "15min",
    "risk_per_trade": 150
  }
}
```

**Response:**
```json
{
  "success": true,
  "valid": false,
  "errors": [
    "instruments: Must have at least 1 item",
    "strategy: Invalid strategy type",
    "risk_per_trade: Must be between 0.1 and 100"
  ],
  "warnings": [
    "Risk per trade above 5% is considered high"
  ]
}
```

**Status Codes:**
- `200 OK` - Validation complete
- `500 Internal Server Error` - Server error

---

## Bot Control API

Base path: `/api/bot`

### Start Bot

Start the trading bot with a configuration.

**Endpoint:** `POST /api/bot/start`

**Rate Limit:** 30/minute

**Request Body:**
```json
{
  "config": {
    "broker": "kite",
    "instruments": [...],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0,
    "max_positions": 3
  }
}
```

**Request:**
```http
POST /api/bot/start HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "config": {
    "broker": "kite",
    "instruments": [{"symbol": "NIFTY24FEB24000CE"}],
    "strategy": "trend_following",
    "timeframe": "15min"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bot started successfully"
}
```

**Status Codes:**
- `200 OK` - Bot started
- `400 Bad Request` - Invalid config or broker not connected
- `500 Internal Server Error` - Server error

**Error Examples:**
```json
{
  "success": false,
  "error": "Broker not connected"
}
```

```json
{
  "success": false,
  "error": "Bot already running"
}
```

---


### Stop Bot

Stop the running trading bot.

**Endpoint:** `POST /api/bot/stop`

**Rate Limit:** 30/minute

**Request:**
```http
POST /api/bot/stop HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Bot stopped successfully"
}
```

**Status Codes:**
- `200 OK` - Bot stopped
- `400 Bad Request` - Bot not running
- `500 Internal Server Error` - Server error

---

### Restart Bot

Restart the trading bot.

**Endpoint:** `POST /api/bot/restart`

**Rate Limit:** 30/minute

**Request:**
```http
POST /api/bot/restart HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Bot restarted successfully"
}
```

**Status Codes:**
- `200 OK` - Bot restarted
- `400 Bad Request` - Bot not running
- `500 Internal Server Error` - Server error

---

### Get Bot Status

Get the current status of the trading bot.

**Endpoint:** `GET /api/bot/status`

**Rate Limit:** 200/minute (STATUS)

**Request:**
```http
GET /api/bot/status HTTP/1.1
Host: localhost:8080
```

**Response (Running):**
```json
{
  "success": true,
  "status": {
    "running": true,
    "uptime": 3600,
    "positions": 2,
    "started_at": "2024-02-18T10:00:00Z",
    "broker": "kite",
    "strategy": "trend_following"
  }
}
```

**Response (Stopped):**
```json
{
  "success": true,
  "status": {
    "running": false,
    "uptime": 0,
    "positions": 0
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---


### Get Account Information

Get account balance and margin information.

**Endpoint:** `GET /api/bot/account`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/bot/account HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "account": {
    "balance": 100000.00,
    "equity": 105000.00,
    "margin_available": 95000.00,
    "margin_used": 10000.00,
    "today_pnl": 5000.00,
    "today_pnl_percent": 5.0
  }
}
```

**Status Codes:**
- `200 OK` - Account info retrieved
- `404 Not Found` - Account info not available
- `500 Internal Server Error` - Server error

---

### Get Positions

Get current open positions.

**Endpoint:** `GET /api/bot/positions`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/bot/positions HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "positions": [
    {
      "symbol": "NIFTY24FEB24000CE",
      "exchange": "NFO",
      "quantity": 50,
      "entry_price": 150.50,
      "current_price": 155.75,
      "pnl": 262.50,
      "pnl_percent": 3.49,
      "side": "BUY",
      "opened_at": "2024-02-18T10:30:00Z"
    },
    {
      "symbol": "BANKNIFTY24FEB48000PE",
      "exchange": "NFO",
      "quantity": 25,
      "entry_price": 200.00,
      "current_price": 195.50,
      "pnl": -112.50,
      "pnl_percent": -2.25,
      "side": "BUY",
      "opened_at": "2024-02-18T11:00:00Z"
    }
  ],
  "count": 2
}
```

**Status Codes:**
- `200 OK` - Positions retrieved
- `500 Internal Server Error` - Server error

---

### Close Position

Close a specific open position.

**Endpoint:** `DELETE /api/bot/positions/:symbol`

**Rate Limit:** 30/minute

**Path Parameters:**
- `symbol` (string, required) - Trading symbol

**Request:**
```http
DELETE /api/bot/positions/NIFTY24FEB24000CE HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "message": "Position closed successfully"
}
```

**Status Codes:**
- `200 OK` - Position closed
- `400 Bad Request` - Failed to close position
- `500 Internal Server Error` - Server error

---


### Get Trade History

Get historical trades with optional date filtering.

**Endpoint:** `GET /api/bot/trades`

**Rate Limit:** 100/minute

**Query Parameters:**
- `from_date` (string, optional) - Start date (YYYY-MM-DD)
- `to_date` (string, optional) - End date (YYYY-MM-DD)

**Request:**
```http
GET /api/bot/trades?from_date=2024-02-01&to_date=2024-02-18 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "trades": [
    {
      "id": "T001",
      "symbol": "NIFTY24FEB24000CE",
      "exchange": "NFO",
      "type": "BUY",
      "quantity": 50,
      "entry_price": 150.50,
      "entry_time": "2024-02-18T10:30:00Z",
      "exit_price": 155.75,
      "exit_time": "2024-02-18T14:30:00Z",
      "pnl": 262.50,
      "pnl_percent": 3.49,
      "status": "CLOSED"
    },
    {
      "id": "T002",
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "type": "BUY",
      "quantity": 10,
      "entry_price": 2450.00,
      "entry_time": "2024-02-17T09:30:00Z",
      "exit_price": 2465.50,
      "exit_time": "2024-02-17T15:00:00Z",
      "pnl": 155.00,
      "pnl_percent": 0.63,
      "status": "CLOSED"
    }
  ],
  "count": 2
}
```

**Status Codes:**
- `200 OK` - Trades retrieved
- `500 Internal Server Error` - Server error

---

### Get Bot Configuration

Get the current bot configuration.

**Endpoint:** `GET /api/bot/config`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/bot/config HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "success": true,
  "config": {
    "broker": "kite",
    "instruments": [...],
    "strategy": "trend_following",
    "timeframe": "15min",
    "risk_per_trade": 2.0,
    "max_positions": 3
  }
}
```

**Status Codes:**
- `200 OK` - Configuration retrieved
- `404 Not Found` - No bot configuration available
- `500 Internal Server Error` - Server error

---


## Session API

Base path: `/api/session`

### Get Session Information

Get information about the current session.

**Endpoint:** `GET /api/session/info`

**Rate Limit:** 200/minute (STATUS)

**Request:**
```http
GET /api/session/info HTTP/1.1
Host: localhost:8080
```

**Response (Active Session):**
```json
{
  "status": "success",
  "session": {
    "session_id": "abc123xyz",
    "created_at": "2024-02-18T10:00:00Z",
    "last_activity": "2024-02-18T10:30:00Z",
    "expires_at": "2024-02-18T11:00:00Z",
    "time_remaining": 1800,
    "broker": "kite",
    "user_id": "AB1234"
  }
}
```

**Response (No Session):**
```json
{
  "status": "success",
  "session": null,
  "message": "No active session"
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

### Get CSRF Token

Get a CSRF token for the current session.

**Endpoint:** `GET /api/session/csrf-token`

**Rate Limit:** 100/minute

**Request:**
```http
GET /api/session/csrf-token HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "status": "success",
  "csrf_token": "a1b2c3d4e5f6g7h8i9j0"
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

**Note:** Include this token in the `X-CSRF-Token` header for state-changing requests.

---

### Extend Session

Extend the current session timeout.

**Endpoint:** `POST /api/session/extend`

**Rate Limit:** 30/minute

**Request:**
```http
POST /api/session/extend HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "status": "success",
  "message": "Session extended",
  "session": {
    "session_id": "abc123xyz",
    "expires_at": "2024-02-18T11:30:00Z",
    "time_remaining": 3600
  }
}
```

**Status Codes:**
- `200 OK` - Session extended
- `400 Bad Request` - No active session
- `500 Internal Server Error` - Server error

---


### Clear Session

Clear the current session (logout).

**Endpoint:** `POST /api/session/clear`

**Rate Limit:** 30/minute

**Request:**
```http
POST /api/session/clear HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "status": "success",
  "message": "Session cleared"
}
```

**Status Codes:**
- `200 OK` - Session cleared
- `500 Internal Server Error` - Server error

---

### Validate CSRF Token

Validate a CSRF token (for testing purposes).

**Endpoint:** `POST /api/session/validate-csrf`

**Rate Limit:** 30/minute

**Request Body:**
```json
{
  "csrf_token": "a1b2c3d4e5f6g7h8i9j0"
}
```

**Request:**
```http
POST /api/session/validate-csrf HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "csrf_token": "a1b2c3d4e5f6g7h8i9j0"
}
```

**Response:**
```json
{
  "status": "success",
  "valid": true
}
```

**Status Codes:**
- `200 OK` - Validation complete
- `400 Bad Request` - CSRF token required
- `500 Internal Server Error` - Server error

---

## Appendix

### Data Types

#### Instrument Object
```json
{
  "instrument_token": 738561,
  "exchange_token": 2884,
  "tradingsymbol": "RELIANCE",
  "name": "RELIANCE INDUSTRIES LTD",
  "last_price": 2450.50,
  "expiry": "2024-02-29",
  "strike": 24000.0,
  "tick_size": 0.05,
  "lot_size": 50,
  "instrument_type": "EQ",
  "segment": "NSE",
  "exchange": "NSE"
}
```

#### Configuration Object
```json
{
  "name": "Strategy Name",
  "broker": "kite",
  "instruments": [Instrument],
  "strategy": "trend_following",
  "timeframe": "15min",
  "risk_per_trade": 2.0,
  "max_positions": 3,
  "max_daily_loss": 5.0,
  "position_sizing": "fixed",
  "base_position_size": 50000,
  "indicators": {
    "ema_fast": 9,
    "ema_slow": 21
  },
  "trading_hours": {
    "start": "09:15",
    "end": "15:30"
  },
  "paper_trading": false
}
```


#### Position Object
```json
{
  "symbol": "NIFTY24FEB24000CE",
  "exchange": "NFO",
  "quantity": 50,
  "entry_price": 150.50,
  "current_price": 155.75,
  "pnl": 262.50,
  "pnl_percent": 3.49,
  "side": "BUY",
  "opened_at": "2024-02-18T10:30:00Z"
}
```

#### Trade Object
```json
{
  "id": "T001",
  "symbol": "NIFTY24FEB24000CE",
  "exchange": "NFO",
  "type": "BUY",
  "quantity": 50,
  "entry_price": 150.50,
  "entry_time": "2024-02-18T10:30:00Z",
  "exit_price": 155.75,
  "exit_time": "2024-02-18T14:30:00Z",
  "pnl": 262.50,
  "pnl_percent": 3.49,
  "status": "CLOSED"
}
```

### Valid Values

#### Broker Types
- `kite` - Kite Connect (Zerodha)
- `alice_blue` - Alice Blue
- `angel_one` - Angel One
- `upstox` - Upstox
- `paper` - Paper Trading

#### Strategy Types
- `trend_following` - Trend Following Strategy
- `mean_reversion` - Mean Reversion Strategy
- `breakout` - Breakout Strategy
- `momentum` - Momentum Strategy

#### Timeframes
- `1min` - 1 Minute
- `5min` - 5 Minutes
- `15min` - 15 Minutes
- `30min` - 30 Minutes
- `1hour` - 1 Hour
- `1day` - 1 Day

#### Exchanges
- `NSE` - National Stock Exchange
- `BSE` - Bombay Stock Exchange
- `NFO` - NSE Futures & Options
- `BFO` - BSE Futures & Options
- `CDS` - Currency Derivatives Segment
- `MCX` - Multi Commodity Exchange

#### Instrument Types
- `EQ` - Equity
- `FUT` - Futures
- `CE` - Call Option
- `PE` - Put Option

### Example Workflows

#### Complete Trading Setup Flow

1. **List Brokers**
   ```
   GET /api/broker/list
   ```

2. **Get Credentials Form**
   ```
   GET /api/broker/credentials-form/kite
   ```

3. **Connect to Broker**
   ```
   POST /api/broker/connect
   Body: {"broker": "kite", "credentials": {...}}
   ```

4. **Get Instruments**
   ```
   GET /api/instruments?exchange=NSE&instrument_type=EQ
   ```

5. **Create Configuration**
   ```
   POST /api/config
   Body: {"config": {...}, "name": "my_strategy"}
   ```

6. **Validate Configuration**
   ```
   POST /api/config/validate
   Body: {"config": {...}}
   ```

7. **Start Bot**
   ```
   POST /api/bot/start
   Body: {"config": {...}}
   ```

8. **Monitor Bot**
   ```
   GET /api/bot/status
   GET /api/bot/positions
   GET /api/bot/account
   ```


#### OAuth Flow (Kite Connect)

1. **Initiate OAuth**
   ```
   POST /api/broker/oauth/initiate
   Body: {"broker": "kite", "api_key": "...", "api_secret": "..."}
   Response: {"oauth_url": "https://kite.zerodha.com/..."}
   ```

2. **User Authenticates** (External)
   - User opens oauth_url in browser
   - User logs in to Kite
   - Kite redirects to callback URL

3. **OAuth Callback** (Automatic)
   ```
   GET /api/broker/oauth/callback?request_token=...&status=success
   ```

4. **Check Connection Status**
   ```
   GET /api/broker/status
   ```

#### Load Saved Credentials Flow

1. **List Saved Credentials**
   ```
   GET /api/broker/credentials/saved
   Response: {"brokers": ["kite", "alice_blue"]}
   ```

2. **Load Credentials**
   ```
   POST /api/broker/credentials/load/kite
   ```

3. **Verify Connection**
   ```
   GET /api/broker/status
   ```

### Security Best Practices

1. **Always use HTTPS in production**
   - Protects credentials in transit
   - Prevents man-in-the-middle attacks

2. **Store API keys securely**
   - Never commit credentials to version control
   - Use environment variables
   - Enable credential encryption

3. **Implement CSRF protection**
   - Get CSRF token: `GET /api/session/csrf-token`
   - Include in headers: `X-CSRF-Token: <token>`

4. **Monitor rate limits**
   - Check `X-RateLimit-Remaining` header
   - Implement exponential backoff on 429 errors

5. **Handle session expiry**
   - Monitor session info: `GET /api/session/info`
   - Extend session: `POST /api/session/extend`
   - Re-authenticate when expired

### Testing

#### Using cURL

**Connect to Broker:**
```bash
curl -X POST http://localhost:8080/api/broker/connect \
  -H "Content-Type: application/json" \
  -d '{
    "broker": "paper",
    "credentials": {}
  }'
```

**Get Instruments:**
```bash
curl http://localhost:8080/api/instruments?exchange=NSE&instrument_type=EQ
```

**Start Bot:**
```bash
curl -X POST http://localhost:8080/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "broker": "paper",
      "instruments": [{"symbol": "RELIANCE", "exchange": "NSE"}],
      "strategy": "trend_following",
      "timeframe": "15min"
    }
  }'
```

#### Using Python

```python
import requests

BASE_URL = "http://localhost:8080/api"

# Connect to broker
response = requests.post(f"{BASE_URL}/broker/connect", json={
    "broker": "paper",
    "credentials": {}
})
print(response.json())

# Get instruments
response = requests.get(f"{BASE_URL}/instruments", params={
    "exchange": "NSE",
    "instrument_type": "EQ"
})
instruments = response.json()["instruments"]

# Start bot
response = requests.post(f"{BASE_URL}/bot/start", json={
    "config": {
        "broker": "paper",
        "instruments": instruments[:1],
        "strategy": "trend_following",
        "timeframe": "15min"
    }
})
print(response.json())
```


#### Using JavaScript (Fetch API)

```javascript
const BASE_URL = 'http://localhost:8080/api';

// Connect to broker
async function connectBroker() {
  const response = await fetch(`${BASE_URL}/broker/connect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      broker: 'paper',
      credentials: {}
    })
  });
  
  const data = await response.json();
  console.log(data);
}

// Get instruments
async function getInstruments() {
  const response = await fetch(
    `${BASE_URL}/instruments?exchange=NSE&instrument_type=EQ`
  );
  
  const data = await response.json();
  return data.instruments;
}

// Start bot
async function startBot(config) {
  const response = await fetch(`${BASE_URL}/bot/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ config })
  });
  
  const data = await response.json();
  console.log(data);
}

// Usage
connectBroker()
  .then(() => getInstruments())
  .then(instruments => {
    const config = {
      broker: 'paper',
      instruments: instruments.slice(0, 1),
      strategy: 'trend_following',
      timeframe: '15min'
    };
    return startBot(config);
  });
```

### Troubleshooting

#### Common Issues

**Issue: "Broker not connected"**
- **Cause:** No active broker connection
- **Solution:** Call `POST /api/broker/connect` first

**Issue: "Session expired"**
- **Cause:** Session timeout (1 hour inactivity)
- **Solution:** Re-authenticate or extend session

**Issue: "Rate limit exceeded"**
- **Cause:** Too many requests in short time
- **Solution:** Implement rate limiting in client, add delays

**Issue: "Invalid configuration"**
- **Cause:** Configuration validation failed
- **Solution:** Use `POST /api/config/validate` to check errors

**Issue: "Instrument not found"**
- **Cause:** Invalid instrument token or symbol
- **Solution:** Refresh instruments list, verify token

**Issue: "Bot already running"**
- **Cause:** Attempted to start already running bot
- **Solution:** Stop bot first with `POST /api/bot/stop`

### Support

For issues or questions:
- Check the User Guide: `indian_dashboard/USER_GUIDE.md`
- Review FAQ: `indian_dashboard/FAQ.md`
- Check logs: `logs/dashboard.log`

### Changelog

**Version 1.0.0** (2024-02-18)
- Initial API release
- Broker management endpoints
- Instruments endpoints
- Configuration endpoints
- Bot control endpoints
- Session management endpoints
- Rate limiting implementation
- Input validation and sanitization
- CSRF protection
- Credential encryption

---

**End of API Documentation**

