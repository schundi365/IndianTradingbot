# Indian Market Web Dashboard - Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Dashboard](#running-the-dashboard)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)
8. [Maintenance](#maintenance)

---

## 1. System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 500 MB for application + space for logs and data
- **Network**: Stable internet connection for broker API access

### Software Dependencies
- Python 3.8+
- pip (Python package manager)
- Git (for cloning repository)
- Web browser (Chrome, Firefox, Edge, Safari - latest versions)

### Broker Requirements
- Active trading account with supported broker (Kite Connect, Alice Blue, Angel One, Upstox)
- API credentials from your broker
- For Kite Connect: API Key and API Secret from https://kite.zerodha.com/apps

---

## 2. Installation

### Step 1: Clone or Download the Repository

```bash
# If using Git
git clone <repository-url>
cd <repository-directory>

# Or download and extract the ZIP file
```

### Step 2: Set Up Python Virtual Environment (Recommended)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Navigate to the dashboard directory
cd indian_dashboard

# Install required packages
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check Python version
python --version

# Verify Flask installation
python -c "import flask; print(f'Flask {flask.__version__} installed')"

# Verify cryptography installation
python -c "import cryptography; print('Cryptography installed')"
```

---

## 3. Configuration

### Step 1: Create Environment File

Create a `.env` file in the `indian_dashboard` directory:

```bash
# Copy the example file
cp .env.example .env

# Or create manually
```

### Step 2: Configure Environment Variables

Edit the `.env` file with your settings:

```env
# Server Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8080
DASHBOARD_DEBUG=False

# Security (IMPORTANT: Change these in production!)
FLASK_SECRET_KEY=your-random-secret-key-here-change-this
ENCRYPTION_KEY=your-encryption-key-here-change-this

# Session Configuration
SESSION_TIMEOUT=3600

# Auto-refresh interval (seconds)
AUTO_REFRESH_INTERVAL=5

# Instrument cache TTL (seconds)
INSTRUMENT_CACHE_TTL=86400

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
```

### Step 3: Generate Secure Keys

**Generate Flask Secret Key:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Generate Encryption Key:**
```python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy these keys to your `.env` file.

### Step 4: Create Required Directories

The application will create these automatically, but you can create them manually:

```bash
mkdir -p data/cache
mkdir -p data/credentials
mkdir -p configs
mkdir -p logs
```

### Step 5: Verify Configuration

```bash
# Test configuration loading
python -c "from config import DASHBOARD_CONFIG; print('Configuration loaded successfully')"
```

---

## 4. Running the Dashboard

### Development Mode

**Basic Start:**
```bash
python indian_dashboard.py
```

**With Custom Port:**
```bash
python indian_dashboard.py --port 8080
```

**With Debug Mode:**
```bash
python indian_dashboard.py --debug
```

**With Custom Host (for network access):**
```bash
python indian_dashboard.py --host 0.0.0.0 --port 8080
```

### Access the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:8080
```

Or if running on a different port:
```
http://127.0.0.1:<your-port>
```

### First-Time Setup

1. **Select Your Broker**: Choose from Kite Connect, Alice Blue, Angel One, Upstox, or Paper Trading
2. **Enter Credentials**: Provide your broker API credentials
3. **Test Connection**: Click "Test Connection" to verify
4. **Select Instruments**: Browse and select instruments to trade
5. **Configure Strategy**: Set up your trading parameters
6. **Start Trading**: Click "Start Bot" to begin

---

## 5. Production Deployment

### Option 1: Gunicorn (Linux/macOS)

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Run with Gunicorn:**
```bash
gunicorn -w 4 -b 127.0.0.1:8080 indian_dashboard:app
```

**With systemd service:**

Create `/etc/systemd/system/indian-dashboard.service`:
```ini
[Unit]
Description=Indian Market Web Dashboard
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/indian_dashboard
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8080 indian_dashboard:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable indian-dashboard
sudo systemctl start indian-dashboard
sudo systemctl status indian-dashboard
```

### Option 2: Waitress (Windows)

**Install Waitress:**
```bash
pip install waitress
```

**Run with Waitress:**
```bash
waitress-serve --host=127.0.0.1 --port=8080 indian_dashboard:app
```

**Create Windows Service:**

Use NSSM (Non-Sucking Service Manager):
```cmd
nssm install IndianDashboard "C:\path\to\venv\Scripts\waitress-serve.exe"
nssm set IndianDashboard AppParameters "--host=127.0.0.1 --port=8080 indian_dashboard:app"
nssm set IndianDashboard AppDirectory "C:\path\to\indian_dashboard"
nssm start IndianDashboard
```

### Option 3: Docker (All Platforms)

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "indian_dashboard.py", "--host", "0.0.0.0", "--port", "8080"]
```

**Build and run:**
```bash
docker build -t indian-dashboard .
docker run -d -p 8080:8080 --name dashboard indian-dashboard
```

### Reverse Proxy with Nginx (Optional)

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS Setup (Recommended for Production)

**Using Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 6. Troubleshooting

### Common Issues and Solutions

#### Issue 1: Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using the port
# Linux/macOS:
lsof -i :8080
# Windows:
netstat -ano | findstr :8080

# Kill the process or use a different port
python indian_dashboard.py --port 8081
```

#### Issue 2: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue 3: Broker Connection Failed

**Error:**
```
Connection failed: Invalid API credentials
```

**Solution:**
1. Verify API credentials are correct
2. Check if API key is active in broker portal
3. For Kite Connect: Ensure you've completed OAuth flow
4. Check network connectivity
5. Review logs in `logs/dashboard.log`

#### Issue 4: Encryption Key Error

**Error:**
```
cryptography.fernet.InvalidToken
```

**Solution:**
```bash
# Generate new encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Update .env file with new key
# Note: This will invalidate existing encrypted credentials
```

#### Issue 5: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'data/credentials'
```

**Solution:**
```bash
# Fix directory permissions
# Linux/macOS:
chmod -R 755 data configs logs

# Windows: Right-click folder → Properties → Security → Edit permissions
```

#### Issue 6: Session Expired

**Error:**
```
Session expired. Please login again.
```

**Solution:**
1. This is normal after SESSION_TIMEOUT (default 1 hour)
2. Simply reconnect to your broker
3. Adjust SESSION_TIMEOUT in .env if needed

#### Issue 7: Rate Limit Exceeded

**Error:**
```
429 Too Many Requests
```

**Solution:**
1. Wait a few seconds before retrying
2. Adjust RATE_LIMIT_PER_MINUTE in .env
3. Check if you're making too many API calls

### Checking Logs

**View recent logs:**
```bash
# Linux/macOS:
tail -f logs/dashboard.log

# Windows:
type logs\dashboard.log
```

**Search for errors:**
```bash
# Linux/macOS:
grep ERROR logs/dashboard.log

# Windows:
findstr ERROR logs\dashboard.log
```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
python indian_dashboard.py --debug
```

**Warning:** Never use debug mode in production!

---

## 7. Security Best Practices

### 1. Secure Your Environment File

```bash
# Set restrictive permissions on .env
# Linux/macOS:
chmod 600 .env

# Never commit .env to version control
echo ".env" >> .gitignore
```

### 2. Use Strong Secret Keys

- Generate random keys using cryptographically secure methods
- Never use default or example keys in production
- Rotate keys periodically (every 90 days recommended)

### 3. Enable HTTPS in Production

- Use SSL/TLS certificates (Let's Encrypt is free)
- Set `SESSION_COOKIE_SECURE=True` in Flask config
- Force HTTPS redirects in your reverse proxy

### 4. Restrict Network Access

```bash
# Bind to localhost only (default)
python indian_dashboard.py --host 127.0.0.1

# Use firewall rules to restrict access
# Linux:
sudo ufw allow from 192.168.1.0/24 to any port 8080

# Windows: Use Windows Firewall settings
```

### 5. Regular Updates

```bash
# Update dependencies regularly
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip install safety
safety check
```

### 6. Backup Credentials and Configurations

```bash
# Backup encrypted credentials
cp -r data/credentials data/credentials.backup

# Backup configurations
cp -r configs configs.backup
```

### 7. Monitor Logs

- Review logs regularly for suspicious activity
- Set up log rotation to prevent disk space issues
- Consider using log monitoring tools

### 8. API Key Security

- Never share your API keys
- Use separate API keys for testing and production
- Revoke and regenerate keys if compromised
- Enable IP whitelisting if your broker supports it

---

## 8. Maintenance

### Daily Tasks

1. **Check Bot Status**: Verify bot is running correctly
2. **Review Logs**: Check for errors or warnings
3. **Monitor Positions**: Review open positions and P&L

### Weekly Tasks

1. **Backup Data**:
   ```bash
   # Backup credentials and configs
   tar -czf backup-$(date +%Y%m%d).tar.gz data configs
   ```

2. **Review Performance**: Analyze trading results
3. **Update Instrument Cache**: Refresh if needed

### Monthly Tasks

1. **Update Dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade <package-name>
   ```

2. **Rotate Logs**:
   ```bash
   # Archive old logs
   gzip logs/dashboard.log.old
   ```

3. **Security Audit**: Review access logs and credentials

### Quarterly Tasks

1. **Rotate Secret Keys**: Generate and update encryption keys
2. **Full System Backup**: Backup entire application directory
3. **Performance Review**: Analyze system performance and optimize

### Log Rotation Setup

**Linux (logrotate):**

Create `/etc/logrotate.d/indian-dashboard`:
```
/path/to/indian_dashboard/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 your-user your-group
    sharedscripts
    postrotate
        systemctl reload indian-dashboard
    endscript
}
```

**Windows (PowerShell script):**
```powershell
# Save as rotate-logs.ps1
$logPath = "C:\path\to\logs\dashboard.log"
$archivePath = "C:\path\to\logs\archive"

if ((Get-Item $logPath).Length -gt 10MB) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Move-Item $logPath "$archivePath\dashboard-$timestamp.log"
    New-Item $logPath -ItemType File
}
```

### Monitoring Setup

**Basic health check script:**
```python
# health_check.py
import requests
import sys

try:
    response = requests.get('http://127.0.0.1:8080/', timeout=5)
    if response.status_code == 200:
        print("Dashboard is healthy")
        sys.exit(0)
    else:
        print(f"Dashboard returned status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Dashboard is down: {e}")
    sys.exit(1)
```

**Run periodically with cron (Linux) or Task Scheduler (Windows)**

---

## Quick Reference

### Start Dashboard
```bash
python indian_dashboard.py
```

### Stop Dashboard
```bash
# Press Ctrl+C in terminal
# Or kill process:
pkill -f indian_dashboard.py  # Linux/macOS
taskkill /F /IM python.exe     # Windows
```

### View Logs
```bash
tail -f logs/dashboard.log     # Linux/macOS
type logs\dashboard.log        # Windows
```

### Backup Data
```bash
tar -czf backup.tar.gz data configs  # Linux/macOS
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## Support and Resources

### Documentation
- User Guide: `USER_GUIDE.md`
- API Documentation: `API_DOCUMENTATION.md`
- FAQ: `FAQ.md`

### Getting Help
1. Check the troubleshooting section above
2. Review logs for error messages
3. Consult broker API documentation
4. Check GitHub issues (if applicable)

### Useful Links
- Kite Connect API: https://kite.trade/docs/connect/v3/
- Flask Documentation: https://flask.palletsprojects.com/
- Python Cryptography: https://cryptography.io/

---

**Version**: 1.0.0  
**Last Updated**: 2024-02-18  
**Compatibility**: Python 3.8+, Flask 3.0+
