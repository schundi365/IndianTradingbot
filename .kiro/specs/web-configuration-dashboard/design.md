# Indian Market Web Dashboard - Design Document

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Web Browser (dashboard.html)                    │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Broker         │  │ Instruments  │  │ Configuration   │ │
│  │ Login          │  │ Selector     │  │ Builder         │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│           │                  │                   │           │
│           └──────────────────┴───────────────────┘           │
│                              │                               │
│                    JavaScript API Client                     │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────┴───────────────────────────────┐
│              Flask App (indian_dashboard.py)                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    API Routes                           │ │
│  │  /api/broker/*  /api/instruments/*  /api/config/*      │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                               │
│  ┌──────────────┬────────────┴────────────┬───────────────┐ │
│  │ Broker       │ Instrument              │ Config        │ │
│  │ Manager      │ Service                 │ Manager       │ │
│  └──────────────┴─────────────────────────┴───────────────┘ │
│         │                  │                      │          │
└─────────┼──────────────────┼──────────────────────┼──────────┘
          │                  │                      │
    ┌─────┴─────┐      ┌────┴─────┐         ┌─────┴──────┐
    │ Broker    │      │ Broker   │         │ Config     │
    │ Adapters  │      │ Adapter  │         │ JSON       │
    │ (Kite,    │      │ API      │         │ Files      │
    │ Alice,    │      │          │         └────────────┘
    │ Angel,    │      └──────────┘
    │ Upstox)   │
    └───────────┘
```

### 1.2 Component Responsibilities

**Frontend (Browser)**
- Render UI components
- Handle user interactions
- Client-side validation
- API communication
- State management

**Backend (Flask)**
- RESTful API endpoints
- Broker adapter management
- Configuration CRUD operations
- Authentication handling
- Session management

**Services**
- BrokerManager: Manage broker connections and authentication
- InstrumentService: Fetch and cache instruments from broker
- ConfigManager: Handle configuration file operations
- BotController: Start/stop/monitor bot

## 2. Data Models

### 2.1 Broker Configuration

```python
class BrokerConfig:
    """Broker configuration and credentials"""
    broker_type: str          # "kite", "alice_blue", "angel_one", "upstox", "paper"
    credentials: Dict         # Broker-specific credentials
    is_connected: bool        # Connection status
    user_info: Dict          # User profile from broker
    last_connected: datetime  # Last successful connection
```

### 2.2 Instrument Model

```python
class Instrument:
    """Tradeable instrument"""
    symbol: str               # Trading symbol
    name: str                 # Company/instrument name
    exchange: str             # NSE/BSE/NFO
    instrument_type: str      # EQ/FUT/CE/PE
    instrument_token: str     # Broker-specific token
    lot_size: int            # Lot size for F&O
    tick_size: float         # Minimum price movement
    last_price: float        # Current market price
    expiry: Optional[date]   # For F&O instruments
    strike: Optional[float]  # For options
```

### 2.3 Trading Configuration

```python
class TradingConfig:
    """Complete trading configuration"""
    name: str                 # Configuration name
    broker: str              # Selected broker
    
    # Instruments
    instruments: List[Dict]   # Selected instruments
    
    # Strategy
    strategy: str            # Strategy type
    timeframe: str          # Trading timeframe
    
    # Risk Management
    risk_per_trade: float   # Risk percentage
    max_positions: int      # Max concurrent positions
    max_daily_loss: float   # Max daily loss percentage
    
    # Position Sizing
    position_sizing: str    # Method
    base_position_size: float
    
    # Indicators
    indicators: Dict        # Indicator parameters
    
    # Trading Hours
    trading_hours: Dict     # Start/end times
    
    # Paper Trading
    paper_trading: bool
```

## 3. API Design

### 3.1 Broker API

**GET /api/broker/list**
- Get list of supported brokers
- Response: `{ "brokers": [{"id": "kite", "name": "Kite Connect", "logo": "..."}] }`

**POST /api/broker/connect**
- Connect to broker with credentials
- Body: `{ "broker": "kite", "credentials": {...} }`
- Response: `{ "status": "success", "user_info": {...} }`

**POST /api/broker/disconnect**
- Disconnect from broker
- Response: `{ "status": "success" }`

**GET /api/broker/status**
- Get current broker connection status
- Response: `{ "connected": true, "broker": "kite", "user": "..." }`

**GET /api/broker/credentials-form/:broker**
- Get credential form fields for specific broker
- Response: `{ "fields": [{"name": "api_key", "type": "text", "label": "API Key"}] }`

### 3.2 Instruments API

**GET /api/instruments**
- Fetch instruments from connected broker
- Query params: `exchange`, `instrument_type`, `search`
- Response: `{ "instruments": [Instrument], "count": int }`

**POST /api/instruments/refresh**
- Refresh instrument cache from broker
- Response: `{ "status": "success", "count": int }`

**GET /api/instruments/:token**
- Get single instrument details
- Response: `Instrument`

**GET /api/instruments/quote/:symbol**
- Get current quote for instrument
- Response: `{ "symbol": "...", "last_price": 100.50, "change": 2.5 }`

### 3.3 Configuration API

**GET /api/config**
- Get current configuration
- Response: `TradingConfig`

**POST /api/config**
- Save configuration
- Body: `TradingConfig`
- Response: `{ "status": "success", "file": "config.json" }`

**GET /api/config/list**
- List all saved configurations
- Response: `{ "configurations": [{"name": "...", "modified": "..."}] }`

**GET /api/config/:name**
- Load specific configuration
- Response: `TradingConfig`

**DELETE /api/config/:name**
- Delete configuration
- Response: `{ "status": "success" }`

**GET /api/config/presets**
- Get preset configurations
- Response: `{ "presets": [TradingConfig] }`

**POST /api/config/validate**
- Validate configuration
- Body: `TradingConfig`
- Response: `{ "valid": bool, "errors": [ValidationError] }`

### 3.4 Bot Control API

**POST /api/bot/start**
- Start trading bot
- Response: `{ "status": "success" }`

**POST /api/bot/stop**
- Stop trading bot
- Response: `{ "status": "success" }`

**GET /api/bot/status**
- Get bot status
- Response: `{ "running": bool, "uptime": int, "positions": int }`

**GET /api/bot/account**
- Get account information
- Response: `{ "balance": float, "equity": float, "margin_available": float }`

**GET /api/bot/positions**
- Get open positions
- Response: `{ "positions": [Position] }`

**GET /api/bot/trades**
- Get trade history
- Query params: `from_date`, `to_date`
- Response: `{ "trades": [Trade] }`

## 4. Frontend Design

### 4.1 Page Structure

**Main Dashboard** (`/`)
- Header with broker status
- Navigation tabs
- Content area
- Status cards

**Tabs:**
1. **Broker** - Broker selection and authentication
2. **Instruments** - Instrument selector
3. **Configuration** - Trading parameters
4. **Monitor** - Bot status and positions
5. **Trades** - Trade history
6. **Logs** - System logs

### 4.2 UI Components

**BrokerSelector Component**
```javascript
{
  brokers: ['kite', 'alice_blue', 'angel_one', 'upstox', 'paper'],
  selected: 'kite',
  connected: false,
  onSelect: (broker) => showCredentialsForm(broker),
  onConnect: (credentials) => connectBroker(credentials)
}
```

**CredentialsForm Component**
```javascript
{
  broker: 'kite',
  fields: [
    {name: 'api_key', type: 'text', label: 'API Key', required: true},
    {name: 'api_secret', type: 'password', label: 'API Secret', required: true}
  ],
  onSubmit: (credentials) => connectBroker(credentials),
  onOAuth: () => initiateOAuth()  // For Kite
}
```

**InstrumentTable Component**
```javascript
{
  instruments: [],
  selected: [],
  filters: {exchange: 'NSE', type: 'EQ', search: ''},
  onSelect: (instruments) => updateSelection(instruments),
  onFilter: (filters) => applyFilters(filters)
}
```

**ConfigurationForm Component**
```javascript
{
  config: TradingConfig,
  validation: {},
  onChange: (field, value) => updateConfig(field, value),
  onSave: () => saveConfig(),
  onLoad: (name) => loadConfig(name)
}
```

**BotMonitor Component**
```javascript
{
  status: {running: false, uptime: 0},
  account: {balance: 0, equity: 0},
  positions: [],
  onStart: () => startBot(),
  onStop: () => stopBot(),
  onRefresh: () => refreshStatus()
}
```

### 4.3 State Management

```javascript
const AppState = {
  // Broker
  broker: {
    type: null,
    connected: false,
    user_info: {},
    credentials: {}
  },
  
  // Instruments
  instruments: {
    all: [],
    filtered: [],
    selected: [],
    loading: false
  },
  
  // Configuration
  config: {
    current: {},
    saved: [],
    presets: [],
    validation: {},
    isDirty: false
  },
  
  // Bot
  bot: {
    running: false,
    status: {},
    account: {},
    positions: [],
    trades: []
  },
  
  // UI
  ui: {
    activeTab: 'broker',
    loading: false,
    notifications: []
  }
}
```

## 5. Backend Services

### 5.1 BrokerManager

```python
class BrokerManager:
    """Manages broker connections and adapters"""
    
    def __init__(self):
        self.current_broker = None
        self.broker_adapters = {
            'kite': KiteAdapter,
            'alice_blue': AliceBlueAdapter,
            'angel_one': AngelOneAdapter,
            'upstox': UpstoxAdapter,
            'paper': PaperTradingAdapter
        }
    
    def get_supported_brokers(self) -> List[Dict]:
        """Get list of supported brokers"""
        return [
            {'id': 'kite', 'name': 'Kite Connect', 'logo': '/static/logos/kite.png'},
            {'id': 'alice_blue', 'name': 'Alice Blue', 'logo': '/static/logos/alice.png'},
            {'id': 'angel_one', 'name': 'Angel One', 'logo': '/static/logos/angel.png'},
            {'id': 'upstox', 'name': 'Upstox', 'logo': '/static/logos/upstox.png'},
            {'id': 'paper', 'name': 'Paper Trading', 'logo': '/static/logos/paper.png'}
        ]
    
    def get_credentials_form(self, broker: str) -> List[Dict]:
        """Get credential form fields for broker"""
        forms = {
            'kite': [
                {'name': 'api_key', 'type': 'text', 'label': 'API Key', 'required': True},
                {'name': 'api_secret', 'type': 'password', 'label': 'API Secret', 'required': True},
                {'name': 'oauth', 'type': 'button', 'label': 'Login with Kite', 'action': 'oauth'}
            ],
            'alice_blue': [
                {'name': 'user_id', 'type': 'text', 'label': 'User ID', 'required': True},
                {'name': 'api_key', 'type': 'text', 'label': 'API Key', 'required': True}
            ],
            'angel_one': [
                {'name': 'client_id', 'type': 'text', 'label': 'Client ID', 'required': True},
                {'name': 'password', 'type': 'password', 'label': 'Password', 'required': True},
                {'name': 'totp', 'type': 'text', 'label': 'TOTP', 'required': True}
            ],
            'upstox': [
                {'name': 'api_key', 'type': 'text', 'label': 'API Key', 'required': True},
                {'name': 'api_secret', 'type': 'password', 'label': 'API Secret', 'required': True},
                {'name': 'redirect_uri', 'type': 'text', 'label': 'Redirect URI', 'required': True}
            ],
            'paper': []
        }
        return forms.get(broker, [])
    
    def connect(self, broker: str, credentials: Dict, config: Dict) -> Tuple[bool, Dict]:
        """Connect to broker"""
        try:
            adapter_class = self.broker_adapters.get(broker)
            if not adapter_class:
                return False, {'error': f'Unsupported broker: {broker}'}
            
            # Create adapter instance
            adapter = adapter_class(config)
            
            # Set credentials
            for key, value in credentials.items():
                setattr(adapter, key, value)
            
            # Connect
            if adapter.connect():
                self.current_broker = adapter
                user_info = adapter.get_user_info() if hasattr(adapter, 'get_user_info') else {}
                return True, {'user_info': user_info}
            else:
                return False, {'error': 'Connection failed'}
                
        except Exception as e:
            return False, {'error': str(e)}
    
    def disconnect(self):
        """Disconnect from broker"""
        if self.current_broker:
            self.current_broker.disconnect()
            self.current_broker = None
    
    def is_connected(self) -> bool:
        """Check if broker is connected"""
        return self.current_broker is not None and self.current_broker.is_connected()
    
    def get_adapter(self) -> Optional[BrokerAdapter]:
        """Get current broker adapter"""
        return self.current_broker
```

### 5.2 InstrumentService

```python
class InstrumentService:
    """Manages instrument data"""
    
    def __init__(self, broker_manager: BrokerManager):
        self.broker_manager = broker_manager
        self.cache_file = "data/instruments_cache.json"
        self.cache_expiry = 24 * 3600  # 24 hours
    
    def get_instruments(self, filters: Dict = None) -> List[Dict]:
        """Get instruments with optional filters"""
        # Load from cache
        instruments = self._load_from_cache()
        
        # Refresh if expired or empty
        if not instruments or self._is_cache_expired():
            instruments = self.refresh_instruments()
        
        # Apply filters
        if filters:
            instruments = self._apply_filters(instruments, filters)
        
        return instruments
    
    def refresh_instruments(self) -> List[Dict]:
        """Refresh instruments from broker"""
        adapter = self.broker_manager.get_adapter()
        if not adapter:
            raise Exception("No broker connected")
        
        # Fetch from broker
        instruments = adapter.get_instruments()
        
        # Save to cache
        self._save_to_cache(instruments)
        
        return instruments
    
    def get_instrument(self, token: str) -> Optional[Dict]:
        """Get single instrument"""
        instruments = self.get_instruments()
        for inst in instruments:
            if inst.get('instrument_token') == token:
                return inst
        return None
    
    def search_instruments(self, query: str) -> List[Dict]:
        """Search instruments"""
        instruments = self.get_instruments()
        query = query.lower()
        return [
            inst for inst in instruments
            if query in inst.get('symbol', '').lower() or
               query in inst.get('name', '').lower()
        ]
    
    def _apply_filters(self, instruments: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to instruments"""
        result = instruments
        
        if filters.get('exchange'):
            result = [i for i in result if i.get('exchange') == filters['exchange']]
        
        if filters.get('instrument_type'):
            result = [i for i in result if i.get('instrument_type') == filters['instrument_type']]
        
        if filters.get('search'):
            query = filters['search'].lower()
            result = [
                i for i in result
                if query in i.get('symbol', '').lower() or
                   query in i.get('name', '').lower()
            ]
        
        return result
    
    def _load_from_cache(self) -> List[Dict]:
        """Load instruments from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file) as f:
                    data = json.load(f)
                    return data.get('instruments', [])
        except Exception as e:
            logging.error(f"Failed to load cache: {e}")
        return []
    
    def _save_to_cache(self, instruments: List[Dict]):
        """Save instruments to cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'instruments': instruments
                }, f)
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")
    
    def _is_cache_expired(self) -> bool:
        """Check if cache is expired"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file) as f:
                    data = json.load(f)
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    age = (datetime.now() - timestamp).total_seconds()
                    return age > self.cache_expiry
        except Exception:
            pass
        return True
```

### 5.3 BotController

```python
class BotController:
    """Controls trading bot"""
    
    def __init__(self, broker_manager: BrokerManager, config_manager):
        self.broker_manager = broker_manager
        self.config_manager = config_manager
        self.bot = None
        self.bot_thread = None
        self.running = False
    
    def start(self) -> Tuple[bool, str]:
        """Start trading bot"""
        if self.running:
            return False, "Bot already running"
        
        # Get broker adapter
        adapter = self.broker_manager.get_adapter()
        if not adapter:
            return False, "No broker connected"
        
        # Get configuration
        config = self.config_manager.get_config()
        
        # Create bot instance
        from src.indian_trading_bot import IndianTradingBot
        self.bot = IndianTradingBot(config, adapter)
        
        # Start bot in thread
        self.running = True
        self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        self.bot_thread.start()
        
        return True, "Bot started successfully"
    
    def stop(self) -> Tuple[bool, str]:
        """Stop trading bot"""
        if not self.running:
            return False, "Bot not running"
        
        self.running = False
        
        # Wait for thread
        if self.bot_thread:
            self.bot_thread.join(timeout=10)
        
        return True, "Bot stopped successfully"
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'running': self.running,
            'uptime': self._get_uptime() if self.running else 0,
            'positions': len(self.bot.positions) if self.bot else 0
        }
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        adapter = self.broker_manager.get_adapter()
        if adapter:
            return adapter.get_account_info()
        return {}
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        adapter = self.broker_manager.get_adapter()
        if adapter:
            return adapter.get_positions()
        return []
    
    def _run_bot(self):
        """Run bot loop"""
        while self.running:
            try:
                self.bot.run_iteration()
                time.sleep(60)  # Wait 1 minute
            except Exception as e:
                logging.error(f"Bot error: {e}")
                time.sleep(60)
```

## 6. Security Considerations

### 6.1 Credential Storage
- Store credentials encrypted using Fernet (cryptography library)
- Never send credentials to frontend
- Use environment variables for encryption key
- Clear credentials on logout

### 6.2 Session Management
- Use Flask sessions with secure cookies
- Session timeout after 1 hour of inactivity
- CSRF protection for state-changing operations

### 6.3 API Security
- Rate limiting on API endpoints
- Input validation and sanitization
- SQL injection prevention (not applicable - using JSON files)
- XSS prevention in frontend

## 7. Error Handling

### 7.1 Frontend Error Handling
```javascript
const ErrorHandler = {
  handleAPIError(error) {
    if (error.status === 401) {
      showNotification('Session expired. Please login again.', 'error');
      redirectToLogin();
    } else if (error.status === 429) {
      showNotification('Too many requests. Please wait.', 'warning');
    } else {
      showNotification(error.message || 'An error occurred', 'error');
    }
  },
  
  handleBrokerError(error) {
    if (error.type === 'AUTH_ERROR') {
      showNotification('Authentication failed. Check credentials.', 'error');
    } else if (error.type === 'RATE_LIMIT') {
      showNotification('API rate limit exceeded. Please wait.', 'warning');
    } else {
      showNotification('Broker error: ' + error.message, 'error');
    }
  }
}
```

### 7.2 Backend Error Handling
```python
@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Error: {error}")
    return jsonify({
        'status': 'error',
        'message': str(error)
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404
```

## 8. Testing Strategy

### 8.1 Unit Tests
- Test each service independently
- Test API endpoints
- Test validation logic
- Test broker adapter integration

### 8.2 Integration Tests
- Test complete workflows
- Test broker connection flow
- Test configuration save/load
- Test bot start/stop

### 8.3 Property-Based Tests
- Configuration validation properties
- Instrument filtering properties
- API response format properties

## 9. Deployment

### 9.1 Local Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_SECRET_KEY="your-secret-key"
export ENCRYPTION_KEY="your-encryption-key"

# Run dashboard
python indian_dashboard.py --port 8080

# Access at http://localhost:8080
```

### 9.2 Configuration
```python
# config/dashboard_config.py
DASHBOARD_CONFIG = {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": False,
    "secret_key": os.getenv("FLASK_SECRET_KEY"),
    "encryption_key": os.getenv("ENCRYPTION_KEY"),
    "cache_dir": "data/cache",
    "config_dir": "configs",
    "log_file": "logs/dashboard.log",
    "session_timeout": 3600,  # 1 hour
    "auto_refresh_interval": 5,  # 5 seconds
}
```

## 10. Implementation Notes

### 10.1 Technology Choices

**Backend: Flask**
- Lightweight and simple
- Good for RESTful APIs
- Easy integration with existing Python code

**Frontend: Vanilla JavaScript**
- No build step required
- Fast development
- Easy to understand

**Data Storage: JSON Files**
- Simple and human-readable
- No database setup
- Easy backup

### 10.2 Code Organization

```
indian_dashboard/
├── indian_dashboard.py          # Flask app entry point
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
│
├── api/                         # API routes
│   ├── __init__.py
│   ├── broker.py               # Broker endpoints
│   ├── instruments.py          # Instrument endpoints
│   ├── config.py               # Configuration endpoints
│   └── bot.py                  # Bot control endpoints
│
├── services/                    # Business logic
│   ├── __init__.py
│   ├── broker_manager.py
│   ├── instrument_service.py
│   └── bot_controller.py
│
├── static/                      # Frontend assets
│   ├── css/
│   │   └── dashboard.css
│   ├── js/
│   │   ├── app.js
│   │   ├── api-client.js
│   │   └── components/
│   └── logos/
│
├── templates/                   # HTML templates
│   └── dashboard.html
│
└── tests/                       # Tests
    ├── test_broker_manager.py
    ├── test_instrument_service.py
    └── test_api_endpoints.py
```

---

**Version**: 1.0.0
**Last Updated**: 2024-02-18
