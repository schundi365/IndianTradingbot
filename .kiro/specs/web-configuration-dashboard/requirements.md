# Indian Market Web Dashboard - Requirements

## 1. Overview

Create a web-based dashboard for Indian market trading that works with any broker through the broker adapter system. Users can select their broker (Kite Connect, Alice Blue, Angel One, Upstox, etc.), enter credentials, browse instruments, configure trading parameters, and monitor their bot - all through a modern web interface.

## 2. User Stories

### 2.1 Broker Selection and Authentication
As a trader, I want to select my broker from a list of supported brokers and enter my credentials so that I can connect to my trading account.

### 2.2 Instrument Selection
As a trader, I want to browse and select multiple stocks/instruments from NSE/BSE/NFO so that I can easily configure which instruments to trade without manually looking up symbols.

### 2.3 Visual Configuration
As a trader, I want to visually configure trading parameters with real-time validation so that I understand my settings before deploying.

### 2.4 Configuration Presets
As a trader, I want to load preset configurations for common Indian market strategies (NIFTY futures, equity intraday, options) so that I can quickly get started.

### 2.5 Bot Monitoring
As a trader, I want to monitor my bot's status, positions, and performance in real-time so that I can track my trading activity.

### 2.6 Configuration Management
As a trader, I want to save and load different configurations so that I can quickly switch between trading strategies.

## 3. Acceptance Criteria

### 3.1 Broker Selection and Authentication

**3.1.1** The dashboard shall display a broker selector
- Dropdown list of supported brokers (Kite Connect, Alice Blue, Angel One, Upstox, Paper Trading)
- Show broker logo and name
- Selection persists in configuration
- Change broker option available

**3.1.2** The dashboard shall provide broker-specific login forms
- Dynamic form based on selected broker
- Kite Connect: API Key, API Secret, Request Token button
- Alice Blue: User ID, API Key
- Angel One: Client ID, Password, TOTP
- Upstox: API Key, API Secret, Redirect URL
- Paper Trading: No credentials needed

**3.1.3** The dashboard shall handle broker authentication
- Test connection button
- Show connection status (Connected/Disconnected)
- Display user info after successful connection
- Store credentials securely (encrypted)
- Auto-reconnect on page refresh

**3.1.4** The dashboard shall support Kite Connect OAuth flow
- "Login with Kite" button opens OAuth page
- Handle redirect callback
- Store access token
- Show token expiry time
- Re-authenticate when token expires

### 3.2 Instrument Selector

**3.2.1** The dashboard shall display a searchable list of instruments
- Search by symbol or company name
- Filter by exchange (NSE/BSE/NFO)
- Filter by instrument type (EQ/FUT/CE/PE)
- Multi-select with checkboxes
- Fetch from connected broker's API

**3.2.2** The dashboard shall fetch instruments from broker adapter
- Use broker_adapter.get_instruments() method
- Cache instrument list locally (24 hours)
- Refresh button to update cache
- Handle API errors gracefully
- Show loading indicator

**3.2.3** The dashboard shall display instrument information
- Trading symbol
- Company name
- Exchange
- Instrument type
- Last traded price (if available)
- Lot size (for F&O)

**3.2.4** The dashboard shall save selected instruments to configuration
- Store as array of instrument configurations
- Include symbol, exchange, instrument_token
- Validate at least one instrument selected
- Compatible with existing bot config format

### 3.3 Configuration Interface

**3.3.1** The dashboard shall provide visual controls for trading parameters
- Strategy selection (trend following, mean reversion, etc.)
- Timeframe selection (1min, 5min, 15min, 1hour, 1day)
- Risk parameters (sliders with numeric input)
- Position sizing controls
- Indicator parameters

**3.3.2** The dashboard shall validate configuration in real-time
- Show validation errors inline
- Prevent invalid values
- Display parameter constraints
- Show helpful suggestions

**3.3.3** The dashboard shall calculate and display risk metrics
- Maximum position size per trade (₹)
- Risk per trade (₹ and %)
- Maximum number of concurrent positions
- Margin requirements

**3.3.4** The dashboard shall provide parameter help
- Tooltip for each parameter
- Example values
- Links to documentation
- Indian market-specific guidance

### 3.4 Indian Market Configuration

**3.4.1** The dashboard shall support Indian market settings
- Trading hours (09:15 - 15:30 IST default)
- Position limits per instrument
- Paper trading toggle
- Broker selection

**3.4.2** The dashboard shall validate Indian market constraints
- Trading hours within market hours
- Position limits comply with exchange rules
- Valid broker credentials

**3.4.3** The dashboard shall support Indian market presets
- NIFTY 50 futures
- BANKNIFTY futures
- Equity intraday
- Options trading
- Load preset with one click

### 3.5 Bot Monitoring

**3.5.1** The dashboard shall display bot status
- Running/Stopped status
- Broker connection status
- Current capital
- Open positions count

**3.5.2** The dashboard shall display account information
- Account balance
- Available margin
- Used margin
- Today's P&L

**3.5.3** The dashboard shall display open positions
- Symbol
- Quantity
- Entry price
- Current price
- P&L
- Close position button

**3.5.4** The dashboard shall display trade history
- Date/time
- Symbol
- Type (BUY/SELL)
- Quantity
- Entry/Exit price
- P&L
- Filter by date range

### 3.6 Bot Control

**3.6.1** The dashboard shall provide bot control buttons
- Start bot
- Stop bot
- Restart bot
- Test broker connection

**3.6.2** The dashboard shall show real-time status updates
- Auto-refresh every 5 seconds
- Manual refresh button
- Loading indicators
- Error notifications

### 3.7 Configuration Management

**3.7.1** The dashboard shall support saving configurations
- Save current configuration
- Name configurations
- Overwrite existing
- Backup before overwrite

**3.7.2** The dashboard shall support loading configurations
- List all saved configurations
- Load configuration
- Show configuration details
- Delete configurations

**3.7.3** The dashboard shall export/import configurations
- Download as JSON
- Upload JSON file
- Copy to clipboard
- Validate imported config

### 3.8 Web Interface

**3.8.1** The dashboard shall provide a modern web interface
- Clean, intuitive design
- Responsive layout
- Dark theme (optional)
- Mobile-friendly

**3.8.2** The dashboard shall run as a local web server
- Flask backend on port 8080 (configurable)
- RESTful API
- Session management
- Error handling

## 4. Technical Constraints

### 4.1 Technology Stack
- Backend: Python Flask
- Frontend: HTML/CSS/JavaScript (vanilla)
- Data: JSON files for configuration
- API: Broker adapters (broker_adapter.py)

### 4.2 Integration Points
- Use existing broker_adapter.py abstraction
- Support all broker adapters (Kite, Alice Blue, Angel One, Upstox, Paper Trading)
- Use existing config format (JSON)
- Integrate with indian_trading_bot.py
- Reuse authentication modules (kite_login.py, etc.)

### 4.3 Performance
- Instrument list loads within 2 seconds
- Configuration validation instant (<100ms)
- Support 1000+ instruments
- Auto-refresh every 5 seconds

### 4.4 Compatibility
- Work with existing Indian market bot
- Support existing config file format
- No breaking changes to bot code
- Support all broker adapters

## 5. Non-Functional Requirements

### 5.1 Usability
- Intuitive interface requiring minimal training
- Clear error messages and validation feedback
- Helpful tooltips and documentation links

### 5.2 Reliability
- Graceful handling of API failures
- Data validation before saving configurations
- Backup existing configurations before overwriting

### 5.3 Security
- No sensitive data in browser localStorage
- API keys stored securely on server side
- HTTPS support for production deployment (optional)

### 5.4 Maintainability
- Clean separation between frontend and backend
- Well-documented API endpoints
- Modular code structure

## 6. Future Enhancements (Out of Scope for v1)

- Advanced charting with technical indicators
- Backtesting with P&L calculation
- Alert and notification system
- Mobile native app
- Multi-user support
- Cloud deployment
- Advanced analytics and reporting
- Strategy marketplace

## 7. Dependencies

- Existing indian_trading_bot.py
- broker_adapter.py (abstraction layer)
- Broker-specific adapters (kite_adapter.py, alice_adapter.py, etc.)
- Authentication modules (kite_login.py, etc.)
- Existing configuration schema

## 8. Success Metrics

- Users can select broker and authenticate in under 2 minutes
- Users can configure a strategy in under 5 minutes
- 90% reduction in configuration errors vs manual JSON editing
- Users can discover and select instruments without external tools
- Configuration validation catches 100% of invalid parameters
- Dashboard loads and responds within 2 seconds
- Support for 4+ brokers (Kite, Alice Blue, Angel One, Upstox)
