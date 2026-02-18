# Quick Start Installation Guide

## 5-Minute Setup

### Prerequisites
- Python 3.8+ installed
- Internet connection
- Web browser

### Installation Steps

**1. Download/Clone**
```bash
git clone <repository-url>
cd indian_dashboard
```

**2. Setup Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Configure**
```bash
cp .env.example .env
# Edit .env with your settings
```

**4. Run**
```bash
python run_dashboard.py
```

**5. Access**
```
http://localhost:8080
```

## First Time Setup

1. **Select Broker** - Choose your broker from the dropdown
2. **Enter Credentials** - Provide API credentials
3. **Connect** - Test connection
4. **Select Instruments** - Browse and select stocks/instruments
5. **Configure Strategy** - Set trading parameters
6. **Start Bot** - Begin trading

## Common Issues

**Port in use?**
```bash
python run_dashboard.py --port 8081
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Can't access dashboard?**
- Check if running: look for "Running on http://..." message
- Try http://127.0.0.1:8080 instead
- Check firewall settings

## Next Steps

- Read full documentation: `DEPLOYMENT_DOCUMENTATION.md`
- Review user guide: `USER_GUIDE.md`
- Check FAQ: `FAQ.md`

## Getting Help

Run diagnostics:
```bash
python troubleshoot.py
```

Check logs:
```bash
# Windows
type logs\dashboard.log

# Linux/macOS
tail -f logs/dashboard.log
```
