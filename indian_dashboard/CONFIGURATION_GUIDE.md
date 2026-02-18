# Configuration Guide

## Overview

This guide covers all configuration options for the Indian Market Web Dashboard.

## Table of Contents

1. [Environment Configuration](#environment-configuration)
2. [Application Configuration](#application-configuration)
3. [Broker Configuration](#broker-configuration)
4. [Security Configuration](#security-configuration)
5. [Performance Configuration](#performance-configuration)
6. [Advanced Configuration](#advanced-configuration)

---

## 1. Environment Configuration

### 1.1 Environment File (.env)

The `.env` file contains environment-specific settings.

**Creating .env file:**
```bash
cp .env.example .env
```

**Edit with your preferred editor:**
```bash
# Windows
notepad .env

# Linux/macOS
nano .env
# or
vim .env
```

### 1.2 Required Variables

**FLASK_SECRET_KEY**
- Purpose: Secures Flask sessions
- Type: String (hex)
- Required: Yes
- Example: `a1b2c3d4e5f6...` (64 characters)

**Generate:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

**ENCRYPTION_KEY**
- Purpose: Encrypts broker credentials
- Type: String (base64)
- Required: Yes
- Example: `gAAAAAB...` (44 characters)

**Generate:**
```python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 1.3 Optional Variables

**Dashboard Settings:**
```bash
# Host to bind to
DASHBOARD_HOST=127.0.0.1  # localhost only
# DASHBOARD_HOST=0.0.0.0  # all interfaces

# Port to listen on
DASHBOARD_PORT=8080

# Flask environment
FLASK_ENV=production  # or development
FLASK_DEBUG=False     # or True for debugging
```

**Session Settings:**
```bash
# Session timeout in seconds
SESSION_TIMEOUT=3600  # 1 hour

# Session cookie settings
SESSION_COOKIE_SECURE=False  # True for HTTPS only
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

**Logging Settings:**
```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file location
LOG_FILE=logs/dashboard.log

# Log format
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Directory Settings:**
```bash
# Data directory
DATA_DIR=data

# Configuration directory
CONFIG_DIR=configs

# Log directory
LOG_DIR=logs

# Cache directory
CACHE_DIR=data/cache
```

**Rate Limiting:**
```bash
# Enable rate limiting
RATE_LIMIT_ENABLED=True

# Requests per minute
RATE_LIMIT_PER_MINUTE=60

# Burst allowance
RATE_LIMIT_BURST=10
```

**Cache Settings:**
```bash
# Cache expiry in seconds
CACHE_EXPIRY=86400  # 24 hours

# Enable caching
CACHE_ENABLED=True
```

### 1.4 Complete .env Example

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-64-chars
FLASK_ENV=production
FLASK_DEBUG=False

# Dashboard Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8080

# Security
ENCRYPTION_KEY=your-encryption-key-here-44-chars
SESSION_TIMEOUT=3600
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Paths
DATA_DIR=data
CONFIG_DIR=configs
LOG_DIR=logs
CACHE_DIR=data/cache

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/dashboard.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Cache
CACHE_ENABLED=True
CACHE_EXPIRY=86400

# Auto-refresh
AUTO_REFRESH_INTERVAL=5
```

---

## 2. Application Configuration

### 2.1 config.py

Main application configuration file.

**Dashboard Configuration:**
```python
DASHBOARD_CONFIG = {
    # Server settings
    "host": os.getenv("DASHBOARD_HOST", "127.0.0.1"),
    "port": int(os.getenv("DASHBOARD_PORT", 8080)),
    "debug": os.getenv("FLASK_DEBUG", "False") == "True",
    
    # Auto-refresh interval (seconds)
    "auto_refresh_interval": int(os.getenv("AUTO_REFRESH_INTERVAL", 5)),
    
    # Cache expiry (seconds)
    "cache_expiry": int(os.getenv("CACHE_EXPIRY", 86400)),
    
    # Session timeout (seconds)
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", 3600)),
    
    # Rate limiting
    "rate_limit_enabled": os.getenv("RATE_LIMIT_ENABLED", "True") == "True",
    "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", 60)),
}
```

**Trading Configuration:**
```python
TRADING_CONFIG = {
    # Default timeframe
    "default_timeframe": "5min",
    
    # Default strategy
    "default_strategy": "trend_following",
    
    # Risk management defaults
    "default_risk_per_trade": 2.0,  # percentage
    "default_max_positions": 5,
    "default_max_daily_loss": 5.0,  # percentage
    
    # Position sizing
    "default_position_sizing": "fixed",
    "default_base_position_size": 10000,  # INR
    
    # Trading hours (IST)
    "market_open": "09:15",
    "market_close": "15:30",
}
```

**Broker Configuration:**
```python
BROKER_CONFIG = {
    # Supported brokers
    "supported_brokers": [
        "kite",
        "alice_blue",
        "angel_one",
        "upstox",
        "paper"
    ],
    
    # Default broker
    "default_broker": "paper",
    
    # Timeout for broker API calls (seconds)
    "api_timeout": 30,
    
    # Retry settings
    "max_retries": 3,
    "retry_delay": 1,  # seconds
}
```

### 2.2 Customizing Configuration

**Method 1: Edit config.py directly**
```python
# config.py
DASHBOARD_CONFIG = {
    "auto_refresh_interval": 10,  # Change from 5 to 10 seconds
    # ... other settings
}
```

**Method 2: Use environment variables**
```bash
# .env
AUTO_REFRESH_INTERVAL=10
```

**Method 3: Command-line arguments**
```bash
python run_dashboard.py --port 8081 --host 0.0.0.0
```

---

## 3. Broker Configuration

### 3.1 Kite Connect (Zerodha)

**Required Credentials:**
- API Key
- API Secret

**Optional:**
- Request Token (for OAuth)
- Access Token (generated)

**Configuration:**
```json
{
  "broker": "kite",
  "credentials": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
  }
}
```

**OAuth Flow:**
1. Click "Login with Kite" button
2. Authorize on Kite website
3. Redirect back with request token
4. Access token generated automatically

**API Limits:**
- 3 requests per second
- 3000 requests per day (varies by plan)

### 3.2 Alice Blue

**Required Credentials:**
- User ID
- API Key

**Configuration:**
```json
{
  "broker": "alice_blue",
  "credentials": {
    "user_id": "your_user_id",
    "api_key": "your_api_key"
  }
}
```

**API Limits:**
- 10 requests per second
- Check with broker for daily limits

### 3.3 Angel One

**Required Credentials:**
- Client ID
- Password
- TOTP (Time-based One-Time Password)

**Configuration:**
```json
{
  "broker": "angel_one",
  "credentials": {
    "client_id": "your_client_id",
    "password": "your_password",
    "totp": "your_totp_secret"
  }
}
```

**TOTP Setup:**
- Enable 2FA in Angel One account
- Note TOTP secret key
- Use authenticator app or library

**API Limits:**
- 5 requests per second
- Check with broker for daily limits

### 3.4 Upstox

**Required Credentials:**
- API Key
- API Secret
- Redirect URI

**Configuration:**
```json
{
  "broker": "upstox",
  "credentials": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "redirect_uri": "http://localhost:8080/callback"
  }
}
```

**OAuth Flow:**
- Similar to Kite Connect
- Requires redirect URI configuration

**API Limits:**
- Check with broker for limits

### 3.5 Paper Trading

**No Credentials Required**

**Configuration:**
```json
{
  "broker": "paper",
  "credentials": {},
  "initial_capital": 100000  # INR
}
```

**Features:**
- Simulated trading
- No real money
- Perfect for testing

---

## 4. Security Configuration

### 4.1 Credential Encryption

**Encryption Method:**
- Algorithm: Fernet (AES-128)
- Key: 32 bytes, base64-encoded
- Storage: data/credentials.enc

**Key Generation:**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

**Key Rotation:**
1. Generate new key
2. Update .env file
3. Delete data/credentials.enc
4. Re-enter credentials

### 4.2 Session Security

**Session Configuration:**
```python
app.config.update(
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY'),
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)
```

**Session Timeout:**
- Default: 1 hour
- Configurable via SESSION_TIMEOUT
- Auto-logout on expiry

### 4.3 HTTPS Configuration

**For Production:**
```python
# Use SSL certificate
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context=('cert.pem', 'key.pem')
    )
```

**Generate Self-Signed Certificate:**
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

**Use Let's Encrypt (Recommended):**
```bash
certbot certonly --standalone -d yourdomain.com
```

### 4.4 Firewall Configuration

**Windows:**
```cmd
netsh advfirewall firewall add rule name="Dashboard" dir=in action=allow protocol=TCP localport=8080
```

**Linux (UFW):**
```bash
sudo ufw allow 8080/tcp
sudo ufw enable
```

**Linux (iptables):**
```bash
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

---

## 5. Performance Configuration

### 5.1 Cache Configuration

**Cache Settings:**
```python
CACHE_CONFIG = {
    "enabled": True,
    "expiry": 86400,  # 24 hours
    "max_size": 1000,  # max items
    "backend": "file",  # or "memory"
}
```

**Cache Types:**
- Instrument cache: 24 hours
- Quote cache: 1 minute
- Configuration cache: No expiry

**Clear Cache:**
```bash
rm -rf data/cache/*
```

### 5.2 Auto-Refresh Configuration

**Refresh Intervals:**
```python
REFRESH_CONFIG = {
    "bot_status": 5,  # seconds
    "account_info": 5,
    "positions": 5,
    "trades": 30,
    "instruments": 86400,  # 24 hours
}
```

**Adjust for Performance:**
- Slower refresh = less CPU/network
- Faster refresh = more real-time

### 5.3 Rate Limiting

**Rate Limit Configuration:**
```python
RATE_LIMIT_CONFIG = {
    "enabled": True,
    "per_minute": 60,
    "burst": 10,
    "strategy": "fixed-window",
}
```

**Per-Endpoint Limits:**
```python
ENDPOINT_LIMITS = {
    "/api/broker/connect": "5 per minute",
    "/api/instruments": "10 per minute",
    "/api/bot/status": "60 per minute",
}
```

### 5.4 Database/Storage Optimization

**File-based Storage:**
- JSON files for configuration
- Encrypted files for credentials
- Cache files for instruments

**Optimization Tips:**
- Regular cleanup of old logs
- Compress old data
- Limit cache size
- Use SSD for better performance

---

## 6. Advanced Configuration

### 6.1 Logging Configuration

**Detailed Logging:**
```python
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/dashboard.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}
```

### 6.2 Multi-Instance Configuration

**Running Multiple Instances:**

**Instance 1:**
```bash
# .env.instance1
DASHBOARD_PORT=8080
DATA_DIR=data/instance1
CONFIG_DIR=configs/instance1
```

**Instance 2:**
```bash
# .env.instance2
DASHBOARD_PORT=8081
DATA_DIR=data/instance2
CONFIG_DIR=configs/instance2
```

**Start:**
```bash
# Terminal 1
python run_dashboard.py --env .env.instance1

# Terminal 2
python run_dashboard.py --env .env.instance2
```

### 6.3 Proxy Configuration

**Behind Corporate Proxy:**
```bash
# .env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,127.0.0.1
```

**In Python:**
```python
import os
proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY'),
}
```

### 6.4 Custom Presets

**Creating Custom Preset:**
```json
{
  "name": "My Custom Strategy",
  "description": "Custom configuration for my strategy",
  "instruments": [...],
  "strategy": "custom",
  "timeframe": "15min",
  "risk_per_trade": 1.5,
  "max_positions": 3,
  "indicators": {
    "rsi_period": 14,
    "ema_fast": 12,
    "ema_slow": 26
  }
}
```

**Save to:**
```
configs/presets/my_custom_strategy.json
```

### 6.5 Environment-Specific Configuration

**Development:**
```bash
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
CACHE_ENABLED=False
```

**Staging:**
```bash
FLASK_ENV=staging
FLASK_DEBUG=False
LOG_LEVEL=INFO
CACHE_ENABLED=True
```

**Production:**
```bash
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=WARNING
CACHE_ENABLED=True
SESSION_COOKIE_SECURE=True
```

---

## Configuration Validation

### Validate Configuration

**Run validation script:**
```bash
python -c "from config import validate_config; validate_config()"
```

**Check for:**
- Required variables present
- Valid values
- File permissions
- Directory structure

### Common Configuration Errors

**Missing SECRET_KEY:**
```
RuntimeError: The session is unavailable because no secret key was set
```
**Fix:** Set FLASK_SECRET_KEY in .env

**Invalid ENCRYPTION_KEY:**
```
ValueError: Fernet key must be 32 url-safe base64-encoded bytes
```
**Fix:** Generate new key with correct format

**Port in use:**
```
OSError: [Errno 98] Address already in use
```
**Fix:** Change port or kill process using port

---

## Configuration Best Practices

1. **Never commit .env file** - Add to .gitignore
2. **Use strong keys** - Generate cryptographically secure keys
3. **Rotate keys regularly** - Change keys periodically
4. **Backup configuration** - Keep backups of configs/
5. **Document changes** - Note any custom configurations
6. **Test changes** - Test in development first
7. **Use environment-specific configs** - Separate dev/prod
8. **Monitor logs** - Check for configuration errors
9. **Validate before deploy** - Run validation scripts
10. **Keep secrets secret** - Never share credentials

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-02-18

For more information, see:
- DEPLOYMENT_DOCUMENTATION.md
- SYSTEM_REQUIREMENTS.md
- TROUBLESHOOTING_REFERENCE.md
