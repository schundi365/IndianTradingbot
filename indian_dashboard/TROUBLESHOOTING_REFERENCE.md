# Troubleshooting Reference Guide

## Quick Diagnostics

Run the automated troubleshooting script:
```bash
python troubleshoot.py
```

## Common Issues and Solutions

### Installation Issues

#### Issue: Python not found
**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. Reinstall Python with "Add to PATH" checked
2. Use full path: `C:\Python39\python.exe`
3. On Linux/macOS, use `python3` instead of `python`

**Verification:**
```bash
python --version
# Should show: Python 3.8.x or higher
```

---

#### Issue: pip install fails
**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solutions:**
```bash
# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. Install with verbose output
pip install -r requirements.txt -v

# 3. Install packages individually
pip install Flask
pip install cryptography
pip install requests
pip install python-dotenv

# 4. Use --user flag if permission issues
pip install --user -r requirements.txt
```

---

#### Issue: Virtual environment activation fails
**Symptoms:**
```
venv\Scripts\activate : File cannot be loaded because running scripts is disabled
```

**Solution (Windows PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Alternative:**
```cmd
# Use Command Prompt instead
venv\Scripts\activate.bat
```

---

### Runtime Issues

#### Issue: Port already in use
**Symptoms:**
```
OSError: [Errno 98] Address already in use
OSError: [WinError 10048] Only one usage of each socket address
```

**Solutions:**

**Windows:**
```cmd
# Find process using port 8080
netstat -ano | findstr :8080

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
python run_dashboard.py --port 8081
```

**Linux/macOS:**
```bash
# Find process
lsof -i :8080
# or
netstat -tulpn | grep 8080

# Kill process
kill -9 <PID>

# Or use different port
python run_dashboard.py --port 8081
```

---

#### Issue: Module not found
**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'cryptography'
```

**Solutions:**
```bash
# 1. Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# 2. Verify activation (should show venv path)
which python  # Linux/macOS
where python  # Windows

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Check if package is installed
pip list | grep flask
```

---

#### Issue: Permission denied
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

**For files:**
```bash
# Linux/macOS
chmod 755 indian_dashboard/
chmod 644 *.py
chmod 700 data/
chmod 600 .env

# Windows
# Right-click folder → Properties → Security → Edit permissions
```

**For pip install:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

---

### Configuration Issues

#### Issue: Encryption key error
**Symptoms:**
```
cryptography.fernet.InvalidToken
ValueError: Fernet key must be 32 url-safe base64-encoded bytes
```

**Solutions:**
```bash
# 1. Generate new encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Update .env file with new key
ENCRYPTION_KEY=<generated-key>

# 3. Delete old encrypted credentials
rm data/credentials.enc  # Linux/macOS
del data\credentials.enc  # Windows

# 4. Re-enter broker credentials in dashboard
```

---

#### Issue: Environment variables not loaded
**Symptoms:**
```
KeyError: 'FLASK_SECRET_KEY'
Configuration error: Missing required environment variable
```

**Solutions:**
```bash
# 1. Verify .env file exists
ls -la .env  # Linux/macOS
dir .env     # Windows

# 2. Check .env file format (no spaces around =)
FLASK_SECRET_KEY=your-key-here
# NOT: FLASK_SECRET_KEY = your-key-here

# 3. Verify python-dotenv is installed
pip install python-dotenv

# 4. Load environment manually
export $(cat .env | xargs)  # Linux/macOS
# Windows: Set variables in System Properties
```

---

### Broker Connection Issues

#### Issue: Kite Connect authentication fails
**Symptoms:**
```
TokenException: Invalid API credentials
InputException: Invalid API key
```

**Solutions:**
1. Verify API Key and Secret are correct (no extra spaces)
2. Check if Kite Connect subscription is active
3. Ensure request token is fresh (expires in 2-3 minutes)
4. Try OAuth flow instead of manual token
5. Check if API key is enabled in Kite developer console

**Verification:**
```python
# Test credentials
from kiteconnect import KiteConnect
kite = KiteConnect(api_key="your_api_key")
print(kite.login_url())
```

---

#### Issue: Rate limit exceeded
**Symptoms:**
```
HTTPError: 429 Too Many Requests
Rate limit exceeded
```

**Solutions:**
1. Wait 1-2 minutes before retrying
2. Reduce auto-refresh frequency in dashboard
3. Check broker's rate limit policy
4. Implement request throttling

**Rate Limits (typical):**
- Kite Connect: 3 requests/second
- Alice Blue: 10 requests/second
- Angel One: 5 requests/second

---

#### Issue: Network timeout
**Symptoms:**
```
requests.exceptions.ConnectionError: Connection timeout
requests.exceptions.ReadTimeout: Read timed out
```

**Solutions:**
```bash
# 1. Check internet connection
ping api.kite.trade

# 2. Check firewall settings
# Allow outbound HTTPS (443)

# 3. Increase timeout in config.py
TIMEOUT = 30  # seconds

# 4. Check broker API status
# Visit broker's status page

# 5. Try different network
# Mobile hotspot, different WiFi
```

---

### Dashboard Access Issues

#### Issue: Cannot access dashboard
**Symptoms:**
```
This site can't be reached
ERR_CONNECTION_REFUSED
```

**Solutions:**
1. Verify dashboard is running
   ```bash
   # Look for: "Running on http://127.0.0.1:8080"
   ```

2. Try different URLs:
   ```
   http://localhost:8080
   http://127.0.0.1:8080
   http://0.0.0.0:8080
   ```

3. Check firewall:
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="Dashboard" dir=in action=allow protocol=TCP localport=8080
   
   # Linux
   sudo ufw allow 8080/tcp
   ```

4. Check if port is listening:
   ```bash
   # Windows
   netstat -an | findstr :8080
   
   # Linux/macOS
   netstat -an | grep 8080
   ```

---

#### Issue: Blank page or JavaScript errors
**Symptoms:**
- White/blank page
- Console errors (F12)
- Failed to load resource

**Solutions:**
```bash
# 1. Clear browser cache
# Ctrl+Shift+Delete → Clear cache

# 2. Hard refresh
# Ctrl+F5 or Ctrl+Shift+R

# 3. Try different browser
# Chrome, Firefox, Edge

# 4. Check browser console (F12)
# Look for specific error messages

# 5. Verify static files exist
ls static/css/dashboard.css
ls static/js/app.js

# 6. Check Flask static file serving
# In indian_dashboard.py, verify:
# app = Flask(__name__, static_folder='static')
```

---

### Data and File Issues

#### Issue: Configuration not saving
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'configs/config.json'
Failed to save configuration
```

**Solutions:**
```bash
# 1. Check directory exists
mkdir -p configs  # Linux/macOS
mkdir configs     # Windows

# 2. Check permissions
# Linux/macOS
chmod 755 configs
chmod 644 configs/*.json

# Windows
# Right-click → Properties → Security → Full Control

# 3. Check disk space
df -h  # Linux/macOS
dir    # Windows

# 4. Check if file is locked
# Close any programs that might have file open
```

---

#### Issue: Instruments not loading
**Symptoms:**
```
Failed to fetch instruments
Instrument list is empty
```

**Solutions:**
```bash
# 1. Check broker connection
# Verify broker is connected in dashboard

# 2. Clear cache
rm data/instruments_cache.json  # Linux/macOS
del data\instruments_cache.json  # Windows

# 3. Refresh instruments
# Click "Refresh Instruments" button in dashboard

# 4. Check broker API
# Verify broker's instrument API is working

# 5. Check logs
tail -f logs/dashboard.log  # Linux/macOS
type logs\dashboard.log     # Windows
```

---

### Performance Issues

#### Issue: Dashboard slow or unresponsive
**Symptoms:**
- Slow page loads
- Delayed responses
- Browser freezing

**Solutions:**
1. Reduce auto-refresh frequency
   - Change from 5s to 10s or 30s

2. Clear browser cache
   - Ctrl+Shift+Delete

3. Reduce selected instruments
   - Select fewer instruments

4. Check system resources
   ```bash
   # Linux
   top
   htop
   
   # Windows
   # Task Manager (Ctrl+Shift+Esc)
   
   # macOS
   top
   Activity Monitor
   ```

5. Restart dashboard
   ```bash
   # Stop (Ctrl+C) and restart
   python run_dashboard.py
   ```

---

#### Issue: High memory usage
**Symptoms:**
- Dashboard using >500MB RAM
- System slowdown
- Out of memory errors

**Solutions:**
```bash
# 1. Restart dashboard
# Stop (Ctrl+C) and restart

# 2. Clear cache
rm -rf data/cache/*  # Linux/macOS
del /Q data\cache\*  # Windows

# 3. Reduce cache expiry
# In .env:
CACHE_EXPIRY=3600  # 1 hour instead of 24

# 4. Check for memory leaks
# Monitor memory over time
# Report if continuously increasing

# 5. Limit concurrent requests
# Reduce auto-refresh frequency
```

---

### Logging and Debugging

#### Enable Debug Mode
```bash
# In .env file
FLASK_DEBUG=True
LOG_LEVEL=DEBUG

# Restart dashboard
python run_dashboard.py
```

#### View Logs

**Real-time:**
```bash
# Linux/macOS
tail -f logs/dashboard.log

# Windows (PowerShell)
Get-Content logs\dashboard.log -Wait

# Windows (Command Prompt)
# Use a text editor or PowerShell
```

**Search logs:**
```bash
# Linux/macOS
grep "ERROR" logs/dashboard.log
grep "broker" logs/dashboard.log

# Windows (PowerShell)
Select-String -Path logs\dashboard.log -Pattern "ERROR"
```

#### Log Locations
- Application logs: `logs/dashboard.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

---

## Diagnostic Commands

### System Check
```bash
# Python version
python --version

# Pip version
pip --version

# Installed packages
pip list

# Virtual environment
which python  # Linux/macOS
where python  # Windows

# Disk space
df -h  # Linux/macOS
dir    # Windows

# Memory
free -h  # Linux
vm_stat  # macOS
# Task Manager on Windows
```

### Network Check
```bash
# Internet connectivity
ping 8.8.8.8

# Broker API connectivity
ping api.kite.trade
curl https://api.kite.trade

# Port availability
netstat -an | grep 8080  # Linux/macOS
netstat -an | findstr :8080  # Windows
```

### Application Check
```bash
# Run troubleshoot script
python troubleshoot.py

# Check configuration
python -c "from config import DASHBOARD_CONFIG; print(DASHBOARD_CONFIG)"

# Test imports
python -c "import flask; import cryptography; print('OK')"

# Check file permissions
ls -la  # Linux/macOS
dir     # Windows
```

---

## Getting Help

### Before Asking for Help

1. Run troubleshoot.py
2. Check logs for errors
3. Review this guide
4. Check FAQ.md

### When Reporting Issues

Include:
- Error message (full text)
- Steps to reproduce
- Log entries (relevant sections)
- System information:
  ```bash
  python --version
  pip list
  # OS version
  ```
- Configuration (sanitized, no credentials)

### Useful Information to Collect

```bash
# System info
python --version
pip list
uname -a  # Linux/macOS
systeminfo  # Windows

# Application info
cat .env  # Remove sensitive data!
ls -la
cat logs/dashboard.log | tail -50

# Network info
ifconfig  # Linux/macOS
ipconfig  # Windows
netstat -an | grep 8080
```

---

## Emergency Recovery

### Complete Reset

**Warning:** This will delete all data and configurations!

```bash
# 1. Stop dashboard (Ctrl+C)

# 2. Backup important data
cp -r configs configs_backup
cp -r data data_backup

# 3. Delete data and configs
rm -rf data/*
rm -rf configs/*

# 4. Regenerate keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 5. Update .env with new key

# 6. Restart dashboard
python run_dashboard.py

# 7. Reconfigure from scratch
```

### Restore from Backup

```bash
# 1. Stop dashboard

# 2. Restore files
cp -r configs_backup/* configs/
cp -r data_backup/* data/

# 3. Restart dashboard
python run_dashboard.py
```

---

## Additional Resources

- Full Documentation: `DEPLOYMENT_DOCUMENTATION.md`
- User Guide: `USER_GUIDE.md`
- FAQ: `FAQ.md`
- Quick Reference: `QUICK_REFERENCE.md`

---

**Last Updated:** 2024-02-18  
**Version:** 1.0.0
