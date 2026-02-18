# Indian Market Web Dashboard - Deployment Documentation

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Deployment Options](#deployment-options)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Security Considerations](#security-considerations)
7. [Maintenance](#maintenance)
8. [FAQ](#faq)

---

## 1. System Requirements

### 1.1 Hardware Requirements

**Minimum Requirements:**
- CPU: 2 cores, 2.0 GHz
- RAM: 2 GB
- Storage: 500 MB free space
- Network: Stable internet connection (for broker API access)

**Recommended Requirements:**
- CPU: 4 cores, 2.5 GHz or higher
- RAM: 4 GB or more
- Storage: 1 GB free space
- Network: High-speed internet connection (low latency preferred)

### 1.2 Software Requirements

**Operating System:**
- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)
- macOS 10.15+ (Catalina or later)

**Python:**
- Python 3.8 or higher (3.9+ recommended)
- pip (Python package manager)
- virtualenv or venv (recommended for isolation)

**Web Browser (for accessing dashboard):**
- Google Chrome 90+ (recommended)
- Mozilla Firefox 88+
- Microsoft Edge 90+
- Safari 14+ (macOS)

**Additional Tools:**
- Git (for cloning repository)
- Text editor (for configuration)

### 1.3 Network Requirements

**Firewall Rules:**
- Outbound HTTPS (443) access to broker APIs
- Inbound access to dashboard port (default: 8080)
- Local network access if accessing from other devices

**Broker API Access:**
- Kite Connect: api.kite.trade
- Alice Blue: ant.aliceblueonline.com
- Angel One: apiconnect.angelbroking.com
- Upstox: api.upstox.com

---

## 2. Installation Steps

### 2.1 Quick Installation (Recommended)

**Step 1: Clone or Download Repository**

```bash
# Using Git
git clone <repository-url>
cd indian_dashboard

# Or download and extract ZIP file
```

**Step 2: Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Configure Environment**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# Windows: notepad .env
# Linux/macOS: nano .env
```

**Step 5: Run Dashboard**

```bash
# Using startup script (recommended)
python run_dashboard.py

# Or directly
python indian_dashboard.py --port 8080
```

**Step 6: Access Dashboard**

Open your web browser and navigate to:
```
http://localhost:8080
```

### 2.2 Detailed Installation

#### 2.2.1 Python Installation

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer, check "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

**macOS:**
```bash
# Using Homebrew
brew install python3
python3 --version
```

#### 2.2.2 Repository Setup

**Option A: Using Git**
```bash
git clone <repository-url>
cd indian_dashboard
```

**Option B: Manual Download**
1. Download ZIP from repository
2. Extract to desired location
3. Open terminal/command prompt in extracted folder

#### 2.2.3 Virtual Environment Setup

**Why use virtual environment?**
- Isolates project dependencies
- Prevents conflicts with system Python packages
- Easy to manage and reproduce environment

**Creating Virtual Environment:**

```bash
# Windows
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

**Activating Virtual Environment:**

```bash
# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate
```

**Deactivating (when done):**
```bash
deactivate
```

#### 2.2.4 Dependency Installation

**Install all required packages:**
```bash
pip install -r requirements.txt
```

**Verify installation:**
```bash
pip list
```

**Expected packages:**
- Flask (web framework)
- cryptography (credential encryption)
- requests (HTTP client)
- python-dotenv (environment variables)
- Additional broker-specific packages

#### 2.2.5 Directory Structure Verification

Ensure the following structure exists:
```
indian_dashboard/
├── indian_dashboard.py
├── run_dashboard.py
├── config.py
├── requirements.txt
├── .env.example
├── api/
├── services/
├── static/
├── templates/
├── data/
└── logs/
```

---

## 3. Configuration

### 3.1 Environment Variables

**Create .env file from template:**
```bash
cp .env.example .env
```

**Required Environment Variables:**

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-change-this
FLASK_ENV=production
FLASK_DEBUG=False

# Dashboard Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8080

# Security
ENCRYPTION_KEY=your-encryption-key-here-change-this
SESSION_TIMEOUT=3600

# Paths
DATA_DIR=data
CONFIG_DIR=configs
LOG_DIR=logs
CACHE_DIR=data/cache

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/dashboard.log

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

**Generating Secure Keys:**

```python
# Run this Python script to generate secure keys
from cryptography.fernet import Fernet
import secrets

print("FLASK_SECRET_KEY:", secrets.token_hex(32))
print("ENCRYPTION_KEY:", Fernet.generate_key().decode())
```

### 3.2 Broker Configuration

**Supported Brokers:**

1. **Kite Connect** (Zerodha)
   - Requires: API Key, API Secret
   - OAuth flow supported
   - Documentation: https://kite.trade/docs/connect/v3/

2. **Alice Blue**
   - Requires: User ID, API Key
   - Documentation: https://ant.aliceblueonline.com/

3. **Angel One**
   - Requires: Client ID, Password, TOTP
   - Documentation: https://smartapi.angelbroking.com/

4. **Upstox**
   - Requires: API Key, API Secret, Redirect URI
   - Documentation: https://upstox.com/developer/api-documentation/

5. **Paper Trading**
   - No credentials required
   - For testing without real money

**Obtaining Broker Credentials:**

Each broker requires you to register as a developer:
- Visit broker's developer portal
- Create an app/API key
- Note down credentials securely
- Never share or commit credentials to version control

### 3.3 Application Configuration

**Edit config.py for advanced settings:**

```python
# Dashboard settings
DASHBOARD_CONFIG = {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": False,
    "auto_refresh_interval": 5,  # seconds
    "cache_expiry": 86400,  # 24 hours
}

# Trading settings
TRADING_CONFIG = {
    "default_timeframe": "5min",
    "max_positions": 5,
    "risk_per_trade": 2.0,  # percentage
}
```

### 3.4 Firewall Configuration

**Windows Firewall:**
```cmd
netsh advfirewall firewall add rule name="Indian Dashboard" dir=in action=allow protocol=TCP localport=8080
```

**Linux (UFW):**
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

**Linux (iptables):**
```bash
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save
```

---

## 4. Deployment Options

### 4.1 Local Development Deployment

**Best for:** Testing, development, personal use

**Steps:**

1. Follow installation steps above
2. Run: `python run_dashboard.py`
3. Access: `http://localhost:8080`

**Pros:**
- Simple setup
- Easy debugging
- No external dependencies

**Cons:**
- Not accessible from other devices
- Stops when terminal closes
- No automatic restart

### 4.2 Production Deployment (Windows)

**Using Windows Service:**

1. Install NSSM (Non-Sucking Service Manager):
   - Download from https://nssm.cc/download
   - Extract to C:\nssm

2. Create service:
   ```cmd
   cd C:\nssm\win64
   nssm install IndianDashboard "C:\path\to\venv\Scripts\python.exe" "C:\path\to\indian_dashboard\run_dashboard.py"
   nssm set IndianDashboard AppDirectory "C:\path\to\indian_dashboard"
   nssm start IndianDashboard
   ```

3. Configure service:
   - Set startup type to Automatic
   - Configure recovery options

**Using Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `C:\path\to\indian_dashboard\run_dashboard.py`
7. Start in: `C:\path\to\indian_dashboard`

### 4.3 Production Deployment (Linux)

**Using systemd service:**

1. Create service file:
   ```bash
   sudo nano /etc/systemd/system/indian-dashboard.service
   ```

2. Add configuration:
   ```ini
   [Unit]
   Description=Indian Market Web Dashboard
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/path/to/indian_dashboard
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/python run_dashboard.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable indian-dashboard
   sudo systemctl start indian-dashboard
   ```

4. Check status:
   ```bash
   sudo systemctl status indian-dashboard
   ```

### 4.4 Docker Deployment

**Using provided Dockerfile:**

1. Build image:
   ```bash
   docker build -t indian-dashboard .
   ```

2. Run container:
   ```bash
   docker run -d \
     --name indian-dashboard \
     -p 8080:8080 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/configs:/app/configs \
     -v $(pwd)/logs:/app/logs \
     --env-file .env \
     indian-dashboard
   ```

3. View logs:
   ```bash
   docker logs -f indian-dashboard
   ```

4. Stop container:
   ```bash
   docker stop indian-dashboard
   ```

**Using Docker Compose:**

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./configs:/app/configs
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

### 4.5 Network Deployment

**Accessing from other devices on local network:**

1. Find your local IP address:
   ```bash
   # Windows
   ipconfig
   
   # Linux/macOS
   ifconfig
   ```

2. Update .env file:
   ```bash
   DASHBOARD_HOST=0.0.0.0  # Listen on all interfaces
   ```

3. Access from other devices:
   ```
   http://YOUR_LOCAL_IP:8080
   ```

**Security Warning:** Only expose on trusted networks!

---

## 5. Troubleshooting Guide

### 5.1 Installation Issues

**Problem: Python not found**
```
'python' is not recognized as an internal or external command
```

**Solution:**
- Reinstall Python with "Add to PATH" option checked
- Or use full path: `C:\Python39\python.exe`
- On Linux/macOS, use `python3` instead of `python`

**Problem: pip install fails**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Try installing packages individually
pip install Flask cryptography requests python-dotenv
```

**Problem: Permission denied**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or run with elevated privileges (not recommended)
# Windows: Run as Administrator
# Linux: sudo pip install -r requirements.txt
```

### 5.2 Runtime Issues

**Problem: Port already in use**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8080
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8080
kill -9 <PID>

# Or use different port
python run_dashboard.py --port 8081
```

**Problem: Module not found**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: Encryption key error**
```
cryptography.fernet.InvalidToken
```

**Solution:**
- Generate new encryption key
- Delete data/credentials.enc file
- Re-enter broker credentials

### 5.3 Broker Connection Issues

**Problem: Kite Connect authentication fails**
```
TokenException: Invalid API credentials
```

**Solution:**
- Verify API Key and Secret are correct
- Check if API subscription is active
- Ensure request token is fresh (expires in few minutes)
- Try OAuth flow instead

**Problem: Rate limit exceeded**
```
HTTPError: 429 Too Many Requests
```

**Solution:**
- Wait before retrying
- Reduce auto-refresh frequency
- Check broker's rate limit policy
- Implement request throttling

**Problem: Network timeout**
```
requests.exceptions.ConnectionError: Connection timeout
```

**Solution:**
- Check internet connection
- Verify firewall settings
- Check broker API status
- Increase timeout in config

### 5.4 Dashboard Access Issues

**Problem: Cannot access dashboard**
```
This site can't be reached
```

**Solution:**
- Verify dashboard is running: check terminal/logs
- Check correct URL: http://localhost:8080
- Try 127.0.0.1 instead of localhost
- Check firewall settings
- Verify port is not blocked

**Problem: Blank page or errors in browser**
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
```

**Solution:**
- Check browser console for errors (F12)
- Clear browser cache
- Try different browser
- Check static files are present
- Verify Flask is serving static files

### 5.5 Data and Configuration Issues

**Problem: Configuration not saving**
```
PermissionError: [Errno 13] Permission denied: 'configs/config.json'
```

**Solution:**
```bash
# Check directory permissions
# Windows
icacls configs

# Linux/macOS
ls -la configs
chmod 755 configs
```

**Problem: Instruments not loading**
```
Failed to fetch instruments
```

**Solution:**
- Check broker connection
- Verify broker adapter is working
- Clear instrument cache: delete data/instruments_cache.json
- Check broker API status

### 5.6 Performance Issues

**Problem: Dashboard slow or unresponsive**

**Solution:**
- Reduce auto-refresh frequency
- Clear browser cache
- Check system resources (CPU, RAM)
- Reduce number of selected instruments
- Check network latency

**Problem: High memory usage**

**Solution:**
- Restart dashboard
- Clear cache files
- Reduce cache expiry time
- Check for memory leaks in logs

### 5.7 Logging and Debugging

**Enable debug mode:**
```bash
# In .env file
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

**View logs:**
```bash
# Real-time log viewing
# Windows
type logs\dashboard.log
Get-Content logs\dashboard.log -Wait

# Linux/macOS
tail -f logs/dashboard.log
```

**Common log locations:**
- Application logs: `logs/dashboard.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

**Troubleshooting script:**
```bash
python troubleshoot.py
```

This will check:
- Python version
- Dependencies
- Configuration
- File permissions
- Network connectivity

---

## 6. Security Considerations

### 6.1 Credential Security

**Best Practices:**
- Never commit .env file to version control
- Use strong encryption keys
- Rotate keys periodically
- Store credentials encrypted
- Use environment variables for sensitive data

**Encryption:**
- Credentials encrypted using Fernet (AES-128)
- Encryption key stored in .env file
- Never expose encryption key

### 6.2 Network Security

**Recommendations:**
- Run on localhost for personal use
- Use HTTPS for remote access (requires SSL certificate)
- Implement authentication for multi-user setup
- Use VPN for remote access
- Keep firewall enabled

**HTTPS Setup (Optional):**
```python
# Use SSL certificate
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context=('cert.pem', 'key.pem')
    )
```

### 6.3 Application Security

**Implemented Security Features:**
- CSRF protection
- Input validation and sanitization
- Rate limiting
- Session management with timeout
- Secure cookie flags
- XSS prevention

**Additional Recommendations:**
- Keep dependencies updated
- Regular security audits
- Monitor logs for suspicious activity
- Implement IP whitelisting if needed

### 6.4 Broker API Security

**Best Practices:**
- Use read-only API keys when possible
- Set position limits
- Enable 2FA on broker account
- Monitor API usage
- Revoke unused API keys

---

## 7. Maintenance

### 7.1 Regular Maintenance Tasks

**Daily:**
- Monitor dashboard logs
- Check bot status
- Verify broker connection

**Weekly:**
- Review trade history
- Check disk space
- Backup configurations

**Monthly:**
- Update dependencies
- Review security settings
- Clean old logs
- Rotate encryption keys (optional)

### 7.2 Backup and Recovery

**What to backup:**
- Configuration files (configs/)
- Credentials (data/credentials.enc)
- Environment file (.env)
- Custom presets
- Trade history (if stored locally)

**Backup script:**
```bash
# Create backup
tar -czf backup_$(date +%Y%m%d).tar.gz configs/ data/ .env

# Restore backup
tar -xzf backup_20240218.tar.gz
```

### 7.3 Updates and Upgrades

**Updating dependencies:**
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade Flask
```

**Updating dashboard:**
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Restart dashboard
```

### 7.4 Log Management

**Log rotation:**
```bash
# Manual log rotation
mv logs/dashboard.log logs/dashboard.log.$(date +%Y%m%d)
touch logs/dashboard.log
```

**Automatic log rotation (Linux):**
Create `/etc/logrotate.d/indian-dashboard`:
```
/path/to/indian_dashboard/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 7.5 Monitoring

**Health check endpoint:**
```bash
curl http://localhost:8080/api/health
```

**System monitoring:**
- CPU usage
- Memory usage
- Disk space
- Network connectivity
- Broker API status

**Monitoring tools:**
- Built-in troubleshoot.py script
- System monitoring tools (htop, Task Manager)
- Log analysis tools

---

## 8. FAQ

### 8.1 General Questions

**Q: Can I run multiple instances?**
A: Yes, use different ports for each instance:
```bash
python run_dashboard.py --port 8080
python run_dashboard.py --port 8081
```

**Q: Can I access from mobile device?**
A: Yes, if on same network:
1. Set DASHBOARD_HOST=0.0.0.0
2. Access via http://YOUR_IP:8080
3. Dashboard is mobile-responsive

**Q: Does it work offline?**
A: No, requires internet for:
- Broker API access
- Market data
- Order placement

**Q: Can I use multiple brokers?**
A: One broker at a time per instance. Run multiple instances for multiple brokers.

### 8.2 Technical Questions

**Q: What database does it use?**
A: JSON files for configuration, no database required.

**Q: Can I customize the UI?**
A: Yes, edit files in static/css/ and static/js/

**Q: How to change port?**
A: Edit .env file or use --port flag:
```bash
python run_dashboard.py --port 9000
```

**Q: How to enable HTTPS?**
A: Requires SSL certificate. See Security Considerations section.

### 8.3 Trading Questions

**Q: Is paper trading safe?**
A: Yes, no real orders placed. Perfect for testing.

**Q: What are the trading hours?**
A: Default: 09:15 - 15:30 IST (Indian market hours)
Configurable in dashboard.

**Q: Can I trade options?**
A: Yes, select options instruments and use options preset.

**Q: How to set stop loss?**
A: Configure in Risk Management section of dashboard.

### 8.4 Troubleshooting Questions

**Q: Dashboard won't start?**
A: Run troubleshoot.py for diagnostics:
```bash
python troubleshoot.py
```

**Q: Broker connection fails?**
A: Check:
- Credentials are correct
- API subscription is active
- Internet connection
- Broker API status

**Q: Configuration not saving?**
A: Check:
- File permissions
- Disk space
- configs/ directory exists

**Q: How to reset everything?**
A: Delete data/ and configs/ directories, restart dashboard.

---

## 9. Support and Resources

### 9.1 Documentation

- User Guide: `USER_GUIDE.md`
- Quick Reference: `QUICK_REFERENCE.md`
- API Documentation: `API_DOCUMENTATION.md`
- FAQ: `FAQ.md`

### 9.2 Broker Documentation

- Kite Connect: https://kite.trade/docs/connect/v3/
- Alice Blue: https://ant.aliceblueonline.com/
- Angel One: https://smartapi.angelbroking.com/
- Upstox: https://upstox.com/developer/api-documentation/

### 9.3 Getting Help

**Before asking for help:**
1. Check this documentation
2. Review FAQ.md
3. Run troubleshoot.py
4. Check logs for errors

**When reporting issues:**
- Include error messages
- Describe steps to reproduce
- Share relevant log entries
- Mention OS and Python version

---

## 10. Appendix

### 10.1 Directory Structure

```
indian_dashboard/
├── indian_dashboard.py          # Main Flask application
├── run_dashboard.py             # Startup script
├── config.py                    # Configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Environment variables (create this)
│
├── api/                         # API endpoints
│   ├── broker.py
│   ├── instruments.py
│   ├── config.py
│   ├── bot.py
│   └── session.py
│
├── services/                    # Business logic
│   ├── broker_manager.py
│   ├── instrument_service.py
│   ├── bot_controller.py
│   └── credential_manager.py
│
├── static/                      # Frontend assets
│   ├── css/
│   ├── js/
│   └── logos/
│
├── templates/                   # HTML templates
│   └── dashboard.html
│
├── data/                        # Runtime data
│   ├── credentials.enc          # Encrypted credentials
│   └── instruments_cache.json   # Cached instruments
│
├── configs/                     # Saved configurations
│   └── *.json
│
├── logs/                        # Application logs
│   └── dashboard.log
│
└── tests/                       # Test files
```

### 10.2 Port Reference

- Default dashboard: 8080
- Alternative: 8081, 8082, etc.
- HTTPS (if configured): 8443

### 10.3 File Permissions

**Linux/macOS:**
```bash
chmod 755 indian_dashboard/
chmod 644 *.py
chmod 755 run_dashboard.py
chmod 700 data/
chmod 600 .env
```

### 10.4 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| FLASK_SECRET_KEY | (required) | Flask session secret |
| ENCRYPTION_KEY | (required) | Credential encryption key |
| DASHBOARD_HOST | 127.0.0.1 | Host to bind to |
| DASHBOARD_PORT | 8080 | Port to listen on |
| FLASK_ENV | production | Flask environment |
| FLASK_DEBUG | False | Debug mode |
| SESSION_TIMEOUT | 3600 | Session timeout (seconds) |
| LOG_LEVEL | INFO | Logging level |
| RATE_LIMIT_ENABLED | True | Enable rate limiting |

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-02-18  
**Maintained By:** Indian Dashboard Team

For the latest version of this documentation, check the repository.
