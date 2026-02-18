# Quick Deployment Guide

This is a quick reference for deploying the Indian Market Web Dashboard. For detailed instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate secret keys
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))" >> .env
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env
```

### 3. Run Troubleshooting

```bash
python troubleshoot.py
```

Fix any issues reported by the troubleshooting script.

### 4. Start Dashboard

**Linux/macOS:**
```bash
./start_dashboard.sh
```

**Windows:**
```cmd
start_dashboard.bat
```

**Or manually:**
```bash
python indian_dashboard.py
```

### 5. Access Dashboard

Open your browser and go to:
```
http://127.0.0.1:8080
```

## Using Startup Scripts

### Linux/macOS

```bash
# Make script executable
chmod +x start_dashboard.sh

# Run with default settings
./start_dashboard.sh

# Run with custom port
./start_dashboard.sh --port 8081

# Run in debug mode
./start_dashboard.sh --debug
```

### Windows

```cmd
# Run with default settings
start_dashboard.bat

# Run with custom port
start_dashboard.bat --port 8081

# Run in debug mode
start_dashboard.bat --debug
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Create .env file first
cp .env.example .env
# Edit .env and set your keys

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Docker Directly

```bash
# Build image
docker build -t indian-dashboard .

# Run container
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/configs:/app/configs \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  --name dashboard \
  indian-dashboard

# View logs
docker logs -f dashboard

# Stop container
docker stop dashboard
```

## Production Deployment

### Using Gunicorn (Linux/macOS)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 127.0.0.1:8080 indian_dashboard:app

# Or use systemd service
sudo cp indian-dashboard.service /etc/systemd/system/
sudo systemctl enable indian-dashboard
sudo systemctl start indian-dashboard
```

### Using Waitress (Windows)

```bash
# Install Waitress
pip install waitress

# Run server
waitress-serve --host=127.0.0.1 --port=8080 indian_dashboard:app
```

## Common Issues

### Port Already in Use

```bash
# Use different port
python indian_dashboard.py --port 8081
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Denied

```bash
# Fix permissions (Linux/macOS)
chmod -R 755 data configs logs

# Windows: Right-click folder → Properties → Security
```

### Broker Connection Failed

1. Verify API credentials are correct
2. Check broker API status
3. Review logs: `tail -f logs/dashboard.log`
4. Try paper trading mode first

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with secret keys
- [ ] Troubleshooting script passes (`python troubleshoot.py`)
- [ ] Dashboard starts without errors
- [ ] Can access dashboard at http://127.0.0.1:8080
- [ ] Can connect to broker (or paper trading)
- [ ] Can select instruments
- [ ] Can save configuration

## Next Steps

1. **First Time Setup**: Follow the on-screen wizard to configure your broker
2. **Read Documentation**: See [USER_GUIDE.md](USER_GUIDE.md) for detailed usage
3. **Configure Strategy**: Set up your trading parameters
4. **Test with Paper Trading**: Always test with paper trading first
5. **Monitor Performance**: Use the Monitor tab to track your bot

## Getting Help

- **Troubleshooting**: Run `python troubleshoot.py`
- **Logs**: Check `logs/dashboard.log`
- **Documentation**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **FAQ**: See [FAQ.md](FAQ.md)

## Security Reminders

- ✓ Never commit `.env` file to version control
- ✓ Use strong, random secret keys
- ✓ Keep API credentials secure
- ✓ Enable HTTPS in production
- ✓ Regularly update dependencies
- ✓ Backup your data and configurations

---

**Ready to deploy?** Run `python troubleshoot.py` to verify your setup!
