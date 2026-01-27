# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-27

### Added
- Initial release of MT5 Trading Bot
- Adaptive risk management system
- Split orders with multiple take profit levels
- 6 different trailing stop strategies
- Smart position sizing based on account balance and free margin
- Trade filtering with confidence scores
- Market condition analysis (trend, volatility, momentum)
- Moving average crossover strategy
- ATR-based stop loss calculation
- Dynamic take profit targets
- Safety limits (daily loss, max trades, drawdown protection)
- Comprehensive documentation
- Example configurations (conservative, balanced, aggressive)
- Test scripts for validation
- Setup automation

### Features
- **Adaptive Risk Management**
  - Analyzes 6 market conditions in real-time
  - Adjusts SL width (1.5× to 3.0× ATR)
  - Modifies TP targets based on market type
  - Changes position size (0.3× to 1.5× multiplier)
  - Filters trades by confidence score (60%+ required)

- **Split Orders**
  - Divides position into 2-5 separate orders
  - Multiple take profit levels
  - Progressive profit-taking
  - Configurable percentage allocation

- **Trailing Strategies**
  - ATR-based trailing
  - Percentage trailing
  - Swing high/low trailing
  - Chandelier exit
  - Breakeven plus
  - Parabolic SAR

- **Safety Features**
  - Daily loss limits
  - Maximum trades per day
  - Drawdown protection
  - Minimum account balance checks
  - Trading hours restrictions
  - Position size limits

### Documentation
- Complete setup guide
- Adaptive risk management guide
- Split orders guide
- Trailing strategies guide
- Quick start guide
- Contributing guidelines
- Deployment checklist

### Examples
- Conservative configuration
- Aggressive configuration
- Quick test script
- Adaptive risk demo

### Testing
- Connection test script
- Setup validation script
- Quick test functionality

## [Unreleased]

### Planned Features
- Backtesting module
- Web dashboard for monitoring
- Telegram notifications
- Email alerts
- Multiple strategy support
- Machine learning integration
- News filter integration
- Multi-timeframe analysis
- Portfolio management
- Performance analytics

---

## Version History

- **1.0.0** (2026-01-27) - Initial release
