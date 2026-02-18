# Deployment Testing Guide

This guide provides comprehensive instructions for testing the Indian Market Web Dashboard deployment.

## Overview

The deployment testing suite verifies:
1. Fresh installation requirements
2. Server startup and configuration
3. API endpoint functionality
4. Broker integration (all supported brokers)
5. Frontend assets and UI
6. Security features
7. Error handling
8. All dashboard features

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip package manager
- 2GB RAM minimum
- 500MB disk space

### Required Python Packages
```bash
pip install -r requirements.txt
```

Key dependencies:
- Flask
- cryptography
- requests (for testing)

## Test Categories

### 1. Fresh Installation Test

Verifies all required files and directories exist:

**Files:**
- `indian_dashboard.py` - Main Flask application
- `run_dashboard.py` - Startup script
- `config.py` - Configuration management
- `requirements.txt` - Dependencies
- `.env.example` - Environment template
- `templates/dashboard.html` - Main UI
- `static/css/dashboard.css` - Styles
- `static/js/app.js` - Frontend logic

**Directories:**
- `api/` - API endpoints
- `services/` - Business logic
- `static/` - Frontend assets
- `templates/` - HTML templates
- `tests/` - Test suite
- `data/` - Data storage
- `configs/` - Configuration files

### 2. Server Startup Test

Verifies the server can start and respond:
- Server starts on configured port (default: 8080)
- Main page loads successfully
- No startup errors

### 3. API Endpoints Test

Tests all API endpoints are accessible:

**Broker Endpoints:**
- `GET /api/broker/list` - List supported brokers
- `GET /api/broker/status` - Connection status
- `POST /api/broker/connect` - Connect to broker
- `POST /api/broker/disconnect` - Disconnect
- `GET /api/broker/credentials-form/:broker` - Get form fields

**Instruments Endpoints:**
- `GET /api/instruments` - List instruments
- `POST /api/instruments/refresh` - Refresh cache
- `GET /api/instruments/:token` - Get instrument details

**Configuration Endpoints:**
- `GET /api/config` - Get current config
- `POST /api/config` - Save configuration
- `GET /api/config/list` - List saved configs
- `GET /api/config/:name` - Load specific config
- `DELETE /api/config/:name` - Delete config
- `GET /api/config/presets` - Get presets
- `POST /api/config/validate` - Validate config

**Bot Control Endpoints:**
- `GET /api/bot/status` - Bot status
- `POST /api/bot/start` - Start bot
- `POST /api/bot/stop` - Stop bot
- `GET /api/bot/account` - Account info
- `GET /api/bot/positions` - Open positions
- `GET /api/bot/trades` - Trade history

**Session Endpoints:**
- `GET /api/session/status` - Session status

### 4. Broker Integration Tests

Tests each supported broker:

#### Paper Trading Broker
- No credentials required
- Connects successfully
- Provides sample instruments
- Supports all operations

#### Kite Connect
- Form has api_key, api_secret fields
- OAuth flow available
- Proper error handling

#### Alice Blue
- Form has user_id, api_key fields
- Credential validation

#### Angel One
- Form has client_id, password, totp fields
- Multi-factor authentication support

#### Upstox
- Form has api_key, api_secret, redirect_uri fields
- OAuth support

### 5. Configuration Features Test

Verifies configuration management:
- Load preset configurations
- Validate configurations
- Save configurations
- List saved configurations
- Export/import configurations

**Preset Configurations:**
- NIFTY Futures
- BANKNIFTY Futures
- Equity Intraday
- Options Trading

### 6. Bot Control Test

Tests bot lifecycle management:
- Get bot status
- Get account information
- Get open positions
- Get trade history
- Start/stop bot (if connected)

### 7. Frontend Assets Test

Verifies all frontend files are accessible:
- CSS files load correctly
- JavaScript files load correctly
- No 404 errors
- Proper MIME types

### 8. Security Features Test

Tests security implementations:
- Session management active
- Rate limiting enforced
- Input validation working
- Credential encryption
- CSRF protection

### 9. Error Handling Test

Verifies proper error responses:
- 404 for missing resources
- 400 for invalid requests
- Proper error messages
- Graceful degradation

## Running the Tests

### Quick Test (Automated)

Run the complete test suite:

```bash
# Start the dashboard first
python run_dashboard.py

# In another terminal, run tests
cd indian_dashboard/tests
python test_deployment.py --wait
```

### Broker-Specific Tests

Test broker integration:

```bash
python test_broker_deployment.py
```

### Manual Testing

For manual verification, follow these steps:

#### 1. Fresh Installation Test

```bash
# Check all files exist
ls -la indian_dashboard.py
ls -la run_dashboard.py
ls -la requirements.txt
ls -la .env.example

# Check directories
ls -la api/
ls -la services/
ls -la static/
ls -la templates/
```

#### 2. Start Server

```bash
python run_dashboard.py
```

Expected output:
```
Starting Indian Market Dashboard...
✓ Configuration loaded
✓ Services initialized
✓ Dashboard running at http://localhost:8080
```

#### 3. Test in Browser

Open http://localhost:8080 and verify:

**Broker Tab:**
- [ ] Broker selector displays all brokers
- [ ] Can select different brokers
- [ ] Credentials form changes based on broker
- [ ] Paper trading connects without credentials
- [ ] Connection status updates

**Instruments Tab:**
- [ ] Instrument table loads
- [ ] Search functionality works
- [ ] Filters work (exchange, type)
- [ ] Can select instruments
- [ ] Selected instruments panel updates
- [ ] Refresh button works

**Configuration Tab:**
- [ ] Configuration form displays
- [ ] Can load presets
- [ ] Real-time validation works
- [ ] Risk metrics calculate correctly
- [ ] Can save configuration
- [ ] Can load saved configurations
- [ ] Export/import works

**Monitor Tab:**
- [ ] Bot status card displays
- [ ] Account info shows (if connected)
- [ ] Positions table works
- [ ] Auto-refresh works
- [ ] Start/stop buttons work

**Trades Tab:**
- [ ] Trade history table displays
- [ ] Date range filter works
- [ ] Statistics calculate correctly
- [ ] Export works

#### 4. Test Each Broker

**Paper Trading:**
```bash
# In browser console or using curl:
curl -X POST http://localhost:8080/api/broker/connect \
  -H "Content-Type: application/json" \
  -d '{"broker":"paper","credentials":{}}'
```

Expected: Connection successful

**Kite Connect:**
- Get credentials form
- Verify OAuth button present
- Test with valid credentials (if available)

**Other Brokers:**
- Verify form fields are correct
- Test error handling with invalid credentials

#### 5. Test Configuration Presets

Load each preset and verify:
- NIFTY Futures: Appropriate parameters for index futures
- BANKNIFTY Futures: Bank index specific settings
- Equity Intraday: Stock trading parameters
- Options Trading: Options-specific configuration

#### 6. Test Security Features

**Session Management:**
```bash
# Check session endpoint
curl http://localhost:8080/api/session/status
```

**Rate Limiting:**
```bash
# Make rapid requests
for i in {1..20}; do
  curl http://localhost:8080/api/broker/list
done
```

Expected: 429 Too Many Requests after threshold

**Input Validation:**
```bash
# Send invalid data
curl -X POST http://localhost:8080/api/config/validate \
  -H "Content-Type: application/json" \
  -d '{"invalid":"data"}'
```

Expected: 400 Bad Request with validation errors

## Test Results

### Automated Test Output

The test suite generates:
1. Console output with pass/fail status
2. JSON report with detailed results
3. Summary statistics

Example output:
```
=== Testing Fresh Installation ===
✓ PASS: File exists: indian_dashboard.py
✓ PASS: File exists: run_dashboard.py
...

=== TEST SUMMARY ===
✓ PASS: Fresh Installation
✓ PASS: Server Startup
✓ PASS: API Endpoints
✓ PASS: Paper Trading Broker
✓ PASS: Configuration Features
✓ PASS: Bot Control
✓ PASS: Frontend Assets
✓ PASS: Security Features
✓ PASS: Error Handling

Total: 9/9 test categories passed
Success Rate: 100.0%
```

### Test Reports

Reports are saved to:
- `tests/deployment_test_report.json` - Full deployment test results
- `tests/broker_deployment_test_report.json` - Broker-specific results

## Troubleshooting

### Server Won't Start

**Issue:** Port already in use
```
Solution: Change port in config.py or use --port flag
python run_dashboard.py --port 8081
```

**Issue:** Missing dependencies
```
Solution: Install requirements
pip install -r requirements.txt
```

**Issue:** Permission errors
```
Solution: Check file permissions
chmod +x run_dashboard.py
```

### Tests Fail

**Issue:** Server not running
```
Solution: Start server first
python run_dashboard.py
```

**Issue:** Connection refused
```
Solution: Check firewall settings
Allow connections on port 8080
```

**Issue:** Import errors
```
Solution: Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Broker Connection Issues

**Issue:** Paper trading won't connect
```
Solution: Check broker adapter exists
ls -la src/paper_trading_adapter.py
```

**Issue:** Real broker authentication fails
```
Solution: Verify credentials are correct
Check broker API status
Review error messages in logs
```

### Frontend Issues

**Issue:** Assets not loading
```
Solution: Check static file serving
Verify files exist in static/ directory
Check browser console for errors
```

**Issue:** JavaScript errors
```
Solution: Check browser console
Verify all JS files loaded
Check for syntax errors
```

## Success Criteria

Deployment is successful when:

1. ✓ All required files and directories exist
2. ✓ Server starts without errors
3. ✓ All API endpoints respond correctly
4. ✓ Paper trading broker connects successfully
5. ✓ All broker forms display correctly
6. ✓ Configuration presets load
7. ✓ Frontend assets load without errors
8. ✓ Security features are active
9. ✓ Error handling works properly
10. ✓ All UI features are functional

## Continuous Testing

### Pre-Deployment Checklist

Before deploying to production:

- [ ] Run full test suite
- [ ] Test with paper trading
- [ ] Test with at least one real broker (if credentials available)
- [ ] Verify all presets load
- [ ] Test configuration save/load
- [ ] Check security features
- [ ] Review error logs
- [ ] Test on target environment
- [ ] Verify performance (response times < 2s)
- [ ] Check resource usage (memory, CPU)

### Post-Deployment Verification

After deployment:

- [ ] Server starts successfully
- [ ] Dashboard accessible from browser
- [ ] Can connect to broker
- [ ] Can select instruments
- [ ] Can configure bot
- [ ] Can monitor bot status
- [ ] No errors in logs
- [ ] Performance acceptable

## Additional Resources

- **User Guide:** `USER_GUIDE.md`
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Troubleshooting:** `TROUBLESHOOTING_REFERENCE.md`
- **API Documentation:** `API_DOCUMENTATION.md`
- **Configuration Guide:** `CONFIGURATION_GUIDE.md`

## Support

If tests fail or issues occur:

1. Check the troubleshooting section above
2. Review error logs in `logs/dashboard.log`
3. Run diagnostic script: `python troubleshoot.py`
4. Check system requirements
5. Verify all dependencies installed

## Conclusion

This comprehensive test suite ensures the Indian Market Web Dashboard is properly deployed and all features work as expected. Regular testing helps maintain quality and catch issues early.
