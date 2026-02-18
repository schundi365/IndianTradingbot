# Indian Market Web Dashboard

Multi-broker web dashboard for Indian stock market trading.

## Features

- **Multi-Broker Support**: Kite Connect, Alice Blue, Angel One, Upstox, Paper Trading
- **Instrument Selection**: Browse and select NSE/BSE/NFO instruments
- **Visual Configuration**: Configure trading parameters without editing JSON
- **Real-time Monitoring**: Monitor bot status, positions, and P&L
- **Preset Configurations**: Quick start with NIFTY, BANKNIFTY, equity, options presets

## Requirements

- Python 3.8+
- Broker account (Kite Connect, Alice Blue, Angel One, or Upstox)
- API credentials from your broker

## Quick Start

### Automated Setup (Recommended)

**Linux/macOS:**
```bash
./start_dashboard.sh
```

**Windows:**
```cmd
start_dashboard.bat
```

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create and configure `.env` file:
```bash
cp .env.example .env
# Edit .env and set your secret keys
```

3. Run troubleshooting:
```bash
python troubleshoot.py
```

4. Start the dashboard:
```bash
python indian_dashboard.py
```

5. Open browser:
```
http://localhost:8080
```

## Documentation

- **[Quick Deployment](DEPLOYMENT_README.md)** - Get started in 5 minutes
- **[Full Deployment Guide](DEPLOYMENT_GUIDE.md)** - Complete installation and configuration
- **[User Guide](USER_GUIDE.md)** - How to use the dashboard
- **[API Documentation](API_DOCUMENTATION.md)** - API reference
- **[FAQ](FAQ.md)** - Frequently asked questions
- **[Troubleshooting](DEPLOYMENT_GUIDE.md#6-troubleshooting)** - Common issues and solutions

## Configuration

Edit `config.py` to customize:
- Server host and port
- Session timeout
- Cache settings
- Broker configurations

## Usage

1. **Select Broker**: Choose your broker from the dropdown
2. **Enter Credentials**: Fill in your API credentials
3. **Connect**: Click "Connect" to authenticate
4. **Select Instruments**: Browse and select instruments to trade
5. **Configure Strategy**: Set trading parameters and risk management
6. **Start Bot**: Click "Start Bot" to begin trading

## Security

- Credentials are encrypted before storage
- Session timeout after 1 hour
- HTTPS recommended for production
- Never commit credentials to version control

## Development

Run in debug mode:
```bash
python indian_dashboard.py --debug
```

Run tests:
```bash
pytest
```

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
