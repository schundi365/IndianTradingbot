# Indian Market Trading Bot - Project Structure

## Overview

This document describes the clean, organized structure of the Indian Market Trading Bot project after file organization on February 18, 2026.

## Root Directory

```
.
├── README.md                              # Main project documentation
├── USER_GUIDE.md                          # User guide
├── LICENSE                                # Project license
├── requirements.txt                       # Core dependencies
├── requirements_ml.txt                    # ML dependencies
├── requirements_web.txt                   # Web dashboard dependencies
├── kite_login.py                          # Kite Connect authentication
├── kite_token.json                        # Kite access token
├── run_bot.py                             # Main bot runner
├── run_bot_auto.py                        # Automated bot runner
├── start_dashboard.py                     # Dashboard starter
├── bot_config_quick_fix.json              # Quick fix configuration
├── organize_files.ps1                     # File organization script
├── ARCHIVE_ORGANIZATION_SUMMARY.md        # Archive summary
└── PROJECT_STRUCTURE.md                   # This file
```

## Core Directories

### `src/` - Core Trading Bot

The heart of the trading bot with all core functionality (31 files, Indian market only):

```
src/
├── broker_adapter.py              # Broker abstraction layer
├── kite_adapter.py                # Kite Connect integration
├── paper_trading_adapter.py       # Paper trading simulation
├── indian_trading_bot.py          # Main bot logic
├── config.py                      # Configuration management
├── config_manager.py              # Config loading/saving
├── config_migration.py            # Configuration migration
├── instrument_validator.py        # Instrument validation
├── error_handler.py               # Error handling
├── trading_decision_logger.py     # Trade logging
├── paper_trading.py               # Paper trading implementation
├── adaptive_risk_manager.py       # Adaptive risk management
├── aroon_indicator.py             # Aroon indicator
├── divergence_detector.py         # Divergence detection
├── dynamic_sl_manager.py          # Dynamic stop loss
├── dynamic_tp_manager.py          # Dynamic take profit
├── ema_momentum_analyzer.py       # EMA momentum analysis
├── enhanced_indicators.py         # Enhanced technical indicators
├── market_structure_analyzer.py   # Market structure analysis
├── ml_integration.py              # ML integration
├── ml_signal_generator.py         # ML signal generation
├── multi_timeframe_analyzer.py    # Multi-timeframe analysis
├── pattern_recognition.py         # Chart pattern recognition
├── reinforcement_learning.py      # RL integration
├── rl_log_trainer.py              # RL training from logs
├── scalping_manager.py            # Scalping strategy
├── sentiment_analyzer.py          # Sentiment analysis
├── split_order_calculator.py      # Order splitting
├── trailing_strategies.py         # Trailing stop strategies
├── trend_detection_engine.py      # Trend detection
├── trendline_analyzer.py          # Trendline analysis
└── volume_analyzer.py             # Volume analysis
```

**Key Features:**
- Multi-broker support (Kite, Paper Trading)
- Indian market specific logic (NSE/BSE/NFO)
- Risk management
- Position management
- Signal generation
- Technical indicators
- ML/RL integration
- Pattern recognition

**Note**: All MT5-related files have been moved to `archive/mt5_bot/`

### `indian_dashboard/` - Web Configuration Dashboard

Complete Flask-based web interface for bot configuration and monitoring:

```
indian_dashboard/
├── indian_dashboard.py            # Main Flask application
├── config.py                      # Dashboard configuration
├── run_dashboard.py               # Dashboard runner
├── rate_limiter.py                # API rate limiting
├── validators.py                  # Input validation
├── session_manager.py             # Session management
├── error_handler.py               # Error handling
│
├── api/                           # REST API endpoints
│   ├── broker.py                  # Broker management
│   ├── instruments.py             # Instrument selection
│   ├── config.py                  # Configuration management
│   ├── bot.py                     # Bot control
│   └── session.py                 # Session management
│
├── services/                      # Business logic
│   ├── broker_manager.py          # Broker connections
│   ├── instrument_service.py      # Instrument data
│   ├── credential_manager.py      # Credential encryption
│   ├── bot_controller.py          # Bot lifecycle
│   └── oauth_handler.py           # OAuth authentication
│
├── static/                        # Frontend assets
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript modules
│   └── logos/                     # Broker logos
│
├── templates/                     # HTML templates
│   └── dashboard.html             # Main dashboard
│
└── tests/                         # Dashboard tests
    ├── test_*.py                  # Python tests
    └── test_*.html                # HTML tests
```

**Key Features:**
- Broker selection and authentication
- OAuth integration (Kite Connect)
- Instrument search and selection
- Visual configuration builder
- Real-time monitoring
- Bot control (start/stop)
- Trade history
- Risk metrics calculation

### `configs/` - Configuration Files

Trading strategy configurations:

```
configs/
├── config_nifty_futures.json      # NIFTY futures strategy
├── config_banknifty_futures.json  # BANKNIFTY futures strategy
├── config_equity_intraday.json    # Equity intraday strategy
├── config_options_trading.json    # Options trading strategy
└── config_paper_trading.json      # Paper trading configuration
```

### `tests/` - Test Suite

Comprehensive test coverage:

```
tests/
├── test_broker_adapter.py         # Broker adapter tests
├── test_kite_adapter.py            # Kite adapter tests
├── test_indian_trading_bot.py      # Bot logic tests
├── test_*_property.py              # Property-based tests
└── test_*_integration.py           # Integration tests
```

**Test Types:**
- Unit tests
- Integration tests
- Property-based tests (Hypothesis)
- End-to-end tests

### `examples/` - Example Configurations

Sample configurations and documentation:

```
examples/
├── README_CONFIGURATIONS.md       # Configuration guide
├── CONFIGURATION_SELECTOR.md      # Strategy selector
└── sample_configs/                # Example configurations
```

### `data/` - Runtime Data

Runtime data storage:

```
data/
├── cache/                         # Cached data
├── credentials/                   # Encrypted credentials
├── oauth_tokens/                  # OAuth tokens
└── instruments/                   # Instrument data
```

### `logs/` - Log Files

Application logs:

```
logs/
├── dashboard.log                  # Dashboard logs
├── trading.log                    # Trading logs
└── error.log                      # Error logs
```

### `models/` - ML Models

Machine learning models (if ML features enabled):

```
models/
├── trained_models/                # Trained ML models
└── model_artifacts/               # Model metadata
```

### `docs/` - Documentation

Project documentation:

```
docs/
├── API.md                         # API documentation
├── ARCHITECTURE.md                # Architecture overview
└── DEPLOYMENT.md                  # Deployment guide
```

## Hidden Directories

### `.kiro/` - Kiro AI Specs

Kiro AI specifications and tasks:

```
.kiro/
├── specs/
│   ├── indian-market-broker-integration/
│   └── web-configuration-dashboard/
└── settings/
```

### `.github/` - GitHub Configuration

GitHub workflows and actions:

```
.github/
└── workflows/
    └── ci.yml                     # CI/CD pipeline
```

## Archive Directory

All non-essential files moved to archive:

```
archive/
├── mt5_bot/                       # 26 MT5 trading bot files
├── old_configs/                   # 7 config backup files
├── analysis_scripts/              # 50+ analysis scripts
├── build_scripts/                 # 30+ build scripts
├── config_backups/                # Configuration backups
├── debug_scripts/                 # 50+ debug scripts
├── documentation/                 # 100+ doc files
├── fix_scripts/                   # 100+ fix scripts
├── logs/                          # Old log files
├── test_scripts/                  # 150+ test scripts
├── verification_scripts/          # 50+ verification scripts
├── Bugs/                          # Bug tracking
├── ml_training/                   # ML training data
├── RSI_IMPLEMENTATION_GUIDE/      # Implementation guides
├── static/                        # Old static files
├── templates/                     # Old templates
└── README.md                      # Archive documentation
```

**Total Archived**: 534+ files (including 26 MT5 bot files and 7 config backups)

## File Count Summary

| Category | Count | Location |
|----------|-------|----------|
| Essential Files | 15 | Root |
| Core Source Files | 31 | src/ |
| Dashboard Files | 100+ | indian_dashboard/ |
| Test Files | 50+ | tests/ |
| Configuration Files | 10+ | configs/ |
| Documentation | 5+ | docs/ |
| Archived Files | 534+ | archive/ |

## Quick Start

### Running the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Configure bot
# Edit configs/config_paper_trading.json

# Run bot
python run_bot.py
```

### Running the Dashboard

```bash
# Install web dependencies
pip install -r requirements_web.txt

# Start dashboard
python start_dashboard.py

# Access at http://127.0.0.1:8080
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_kite_adapter.py
```

## Development Workflow

1. **Configuration**: Use dashboard or edit JSON configs
2. **Testing**: Run tests before deployment
3. **Deployment**: Use paper trading first
4. **Monitoring**: Use dashboard for real-time monitoring
5. **Logging**: Check logs/ directory for issues

## Key Features

### Trading Bot
- Multi-broker support (Kite Connect, Paper Trading)
- Indian market specific (NSE, BSE, NFO)
- Multiple strategies (Trend Following, Mean Reversion, Options)
- Risk management (Position sizing, Stop loss, Take profit)
- Technical indicators (RSI, MACD, EMA, ADX, etc.)
- Paper trading mode

### Web Dashboard
- Broker authentication (OAuth for Kite)
- Instrument search and selection
- Visual configuration builder
- Real-time monitoring
- Trade history
- Bot control
- Risk metrics

### Testing
- Unit tests
- Integration tests
- Property-based tests
- End-to-end tests
- 100+ test cases

## Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: Flask
- **Testing**: pytest, Hypothesis
- **Broker API**: KiteConnect
- **Frontend**: Vanilla JavaScript, HTML, CSS
- **Data Storage**: JSON files
- **Logging**: Python logging module

## Security

- Encrypted credential storage
- OAuth 2.0 authentication
- Session management
- Input validation
- Rate limiting
- CSRF protection

## Performance

- Instrument caching
- Request debouncing
- Optimized table rendering
- Background processing
- Efficient data structures

## Maintenance

### Regular Tasks
- Update dependencies
- Review logs
- Backup configurations
- Clean cache
- Archive old logs

### Monitoring
- Check dashboard logs
- Monitor bot performance
- Review trade history
- Verify broker connection

## Support

- **Documentation**: See README.md and USER_GUIDE.md
- **Issues**: Check logs/ directory
- **Configuration**: Use dashboard or edit configs/
- **Testing**: Run pytest tests/

## Version

- **Project**: Indian Market Trading Bot
- **Version**: 2.1
- **Last Updated**: February 18, 2026
- **Organization Date**: February 18, 2026

---

For archived files and historical reference, see `archive/README.md`
