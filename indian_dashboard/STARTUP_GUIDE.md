# Dashboard Startup Guide

This guide explains how to start the Indian Market Web Dashboard using the provided startup scripts.

## Quick Start

### Windows
```cmd
cd indian_dashboard
start_dashboard.bat
```

### Linux/macOS
```bash
cd indian_dashboard
chmod +x start_dashboard.sh
./start_dashboard.sh
```

### Python Script (Cross-platform)
```bash
cd indian_dashboard
python run_dashboard.py
```

## Startup Scripts Overview

### 1. `run_dashboard.py` (Recommended)
The main Python startup script with comprehensive features:

- **Pre-flight checks**: Validates Python version, dependencies, directories, and configuration
- **Command-line arguments**: Flexible configuration options
- **Key generation**: Built-in secure key generator
- **Cross-platform**: Works on Windows, Linux, and macOS

#### Basic Usage
```bash
# Start with default settings (127.0.0.1:8080)
python run_dashboard.py

# Start on custom host and port
python run_dashboard.py --host 0.0.0.0 --port 5000

# Start in debug mode
python run_dashboard.py --debug

# Enable auto-reload (development)
python run_dashboard.py --debug --reload
```

#### Advanced Options
```bash
# Generate secure keys for .env file
python run_dashboard.py --generate-keys

# Run startup checks only (don't start dashboard)
python run_dashboard.py --check-only

# Skip startup checks (not recommended)
python run_dashboard.py --skip-checks

# Set custom log level
python run_dashboard.py --log-level DEBUG
```

#### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--host` | Host to bind to | 127.0.0.1 |
| `--port` | Port to bind to | 8080 |
| `--debug` | Enable debug mode | False |
| `--reload` | Enable auto-reload | False |
| `--generate-keys` | Generate secure keys | - |
| `--skip-checks` | Skip startup checks | False |
| `--check-only` | Run checks only | False |
| `--log-level` | Set logging level | INFO |

### 2. `start_dashboard.bat` (Windows)
Batch script for Windows users:

- Automatically creates virtual environment if missing
- Installs dependencies if needed
- Creates .env from .env.example if missing
- Creates required directories
- Starts the dashboard

#### Usage
```cmd
cd indian_dashboard
start_dashboard.bat

# With custom arguments
start_dashboard.bat --port 5000 --debug
```

### 3. `start_dashboard.sh` (Linux/macOS)
Shell script for Unix-based systems:

- Checks Python version
- Creates virtual environment if missing
- Installs dependencies if needed
- Creates .env from .env.example if missing
- Creates required directories
- Starts the dashboard

#### Usage
```bash
cd indian_dashboard
chmod +x start_dashboard.sh  # Make executable (first time only)
./start_dashboard.sh

# With custom arguments
./start_dashboard.sh --port 5000 --debug
```

## Startup Checks

The `run_dashboard.py` script performs the following checks:

### 1. Python Version Check
- **Requirement**: Python 3.8 or higher
- **Action**: Verifies installed Python version

### 2. Dependencies Check
- **Requirement**: Flask, Flask-CORS, cryptography, and other packages
- **Action**: Checks if required packages are installed
- **Fix**: Run `pip install -r requirements.txt`

### 3. Directories Check
- **Requirement**: data/cache, data/credentials, configs, logs directories
- **Action**: Creates directories if missing

### 4. Environment File Check
- **Requirement**: .env file with configuration
- **Action**: Warns if .env is missing
- **Fix**: Copy .env.example to .env and configure

### 5. Secret Keys Check
- **Requirement**: FLASK_SECRET_KEY and ENCRYPTION_KEY
- **Action**: Warns if using default or missing keys
- **Fix**: Generate keys with `python run_dashboard.py --generate-keys`

### 6. Broker Adapters Check
- **Requirement**: Broker adapter files in src/ directory
- **Action**: Warns if adapters are missing
- **Fix**: Ensure broker adapter files exist

## Configuration

### Environment Variables

Create a `.env` file in the `indian_dashboard` directory:

```bash
# Server Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8080
DASHBOARD_DEBUG=False

# Security (IMPORTANT: Change these!)
FLASK_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Session
SESSION_TIMEOUT=3600

# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60

# Instrument Cache
INSTRUMENT_CACHE_TTL=86400

# Auto-refresh
AUTO_REFRESH_INTERVAL=5
```

### Generating Secure Keys

Use the built-in key generator:

```bash
python run_dashboard.py --generate-keys
```

This will output:
```
Flask Secret Key:
  FLASK_SECRET_KEY=a1b2c3d4e5f6...

Encryption Key:
  ENCRYPTION_KEY=gAAAAABf...
```

Copy these values to your `.env` file.

## Troubleshooting

### Issue: "Python 3.8+ required"
**Solution**: Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

### Issue: "Missing required packages"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Issue: "Permission denied" (Linux/macOS)
**Solution**: Make the script executable:
```bash
chmod +x start_dashboard.sh
```

### Issue: "Port already in use"
**Solution**: Use a different port:
```bash
python run_dashboard.py --port 8081
```

### Issue: "Module not found" errors
**Solution**: Ensure you're in the correct directory and virtual environment is activated:
```bash
cd indian_dashboard
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows
```

### Issue: Dashboard starts but can't connect to broker
**Solution**: 
1. Check broker adapter files exist in `src/` directory
2. Verify broker credentials are correct
3. Check broker API status

## Production Deployment

For production deployment:

1. **Set secure keys**:
   ```bash
   python run_dashboard.py --generate-keys
   ```
   Add generated keys to `.env`

2. **Disable debug mode**:
   ```bash
   DASHBOARD_DEBUG=False
   ```

3. **Use production server**:
   Consider using Gunicorn or uWSGI instead of Flask's built-in server:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8080 indian_dashboard:app
   ```

4. **Enable HTTPS**:
   Use a reverse proxy (nginx, Apache) with SSL certificate

5. **Set proper host**:
   ```bash
   DASHBOARD_HOST=0.0.0.0  # Listen on all interfaces
   ```

6. **Configure firewall**:
   Allow incoming connections on your chosen port

## Systemd Service (Linux)

For automatic startup on Linux, use the provided systemd service file:

```bash
# Copy service file
sudo cp indian-dashboard.service /etc/systemd/system/

# Edit service file with your paths
sudo nano /etc/systemd/system/indian-dashboard.service

# Enable and start service
sudo systemctl enable indian-dashboard
sudo systemctl start indian-dashboard

# Check status
sudo systemctl status indian-dashboard
```

## Docker Deployment

Use the provided Dockerfile:

```bash
# Build image
docker build -t indian-dashboard .

# Run container
docker run -d -p 8080:8080 \
  -e FLASK_SECRET_KEY=your-key \
  -e ENCRYPTION_KEY=your-key \
  --name dashboard \
  indian-dashboard
```

## Development Mode

For development with auto-reload:

```bash
python run_dashboard.py --debug --reload
```

This enables:
- Debug mode with detailed error pages
- Auto-reload on code changes
- Interactive debugger

**Warning**: Never use debug mode in production!

## Accessing the Dashboard

Once started, access the dashboard at:

- Local: http://127.0.0.1:8080
- Network: http://YOUR_IP:8080 (if host is 0.0.0.0)

Default credentials: None (no authentication by default)

## Stopping the Dashboard

- **Interactive mode**: Press `Ctrl+C`
- **Systemd service**: `sudo systemctl stop indian-dashboard`
- **Docker**: `docker stop dashboard`

## Logs

Logs are stored in:
- File: `../logs/dashboard.log`
- Console: Standard output

View logs:
```bash
# Tail log file
tail -f ../logs/dashboard.log

# Systemd logs
sudo journalctl -u indian-dashboard -f

# Docker logs
docker logs -f dashboard
```

## Support

For issues or questions:
1. Check this guide
2. Review logs for error messages
3. Verify all startup checks pass
4. Check broker adapter compatibility
5. Consult the main documentation

## Next Steps

After starting the dashboard:
1. Connect to a broker (Broker tab)
2. Select instruments (Instruments tab)
3. Configure strategy (Configuration tab)
4. Start bot (Monitor tab)
5. View trades (Trades tab)

Refer to the User Guide for detailed usage instructions.
