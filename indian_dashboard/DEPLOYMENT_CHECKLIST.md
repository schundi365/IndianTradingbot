# Deployment Checklist

Use this checklist to ensure proper deployment of the Indian Market Web Dashboard.

## Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] 4GB+ RAM available
- [ ] 500MB+ disk space available
- [ ] Stable internet connection
- [ ] Modern web browser installed

### Software Setup
- [ ] Repository cloned or downloaded
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All dependencies verified (`python verify_installation.py`)

### Configuration
- [ ] `.env.example` copied to `.env`
- [ ] `FLASK_SECRET_KEY` generated and set
- [ ] `ENCRYPTION_KEY` generated and set
- [ ] Port configuration reviewed (default: 8080)
- [ ] Session timeout configured (default: 3600 seconds)
- [ ] Log level set appropriately (INFO for production)

### Directory Structure
- [ ] `data/cache` directory exists
- [ ] `data/credentials` directory exists
- [ ] `configs` directory exists
- [ ] `logs` directory exists
- [ ] All directories have proper permissions

### Security
- [ ] Secret keys are strong and random (not defaults)
- [ ] `.env` file has restrictive permissions (600 on Linux/macOS)
- [ ] `.env` added to `.gitignore`
- [ ] Credentials will be encrypted before storage
- [ ] HTTPS configured (for production deployments)

## Deployment Checklist

### Development Deployment
- [ ] Troubleshooting script passes (`python troubleshoot.py`)
- [ ] Dashboard starts without errors
- [ ] Can access dashboard at http://127.0.0.1:8080
- [ ] All tabs load correctly
- [ ] No console errors in browser

### Production Deployment (Additional)
- [ ] Debug mode disabled (`DASHBOARD_DEBUG=False`)
- [ ] Production WSGI server installed (Gunicorn/Waitress)
- [ ] Systemd service configured (Linux) or Windows Service (Windows)
- [ ] Service starts automatically on boot
- [ ] Reverse proxy configured (Nginx/Apache) - optional
- [ ] HTTPS/SSL certificates installed
- [ ] Firewall rules configured
- [ ] Log rotation configured
- [ ] Backup strategy in place

### Docker Deployment (If Using Docker)
- [ ] Docker installed and running
- [ ] Dockerfile reviewed
- [ ] docker-compose.yml configured
- [ ] `.env` file created with secrets
- [ ] Volumes configured for data persistence
- [ ] Container builds successfully
- [ ] Container starts and runs
- [ ] Can access dashboard through Docker port mapping
- [ ] Logs accessible via `docker logs`

## Post-Deployment Checklist

### Initial Testing
- [ ] Dashboard accessible via browser
- [ ] Can select broker
- [ ] Can enter credentials (test with paper trading first)
- [ ] Broker connection successful
- [ ] Can fetch instruments list
- [ ] Can search and filter instruments
- [ ] Can select instruments
- [ ] Can configure trading parameters
- [ ] Configuration validation works
- [ ] Can save configuration
- [ ] Can load saved configuration
- [ ] Can export/import configuration

### Bot Testing (Paper Trading)
- [ ] Paper trading mode enabled
- [ ] Bot starts successfully
- [ ] Bot status updates correctly
- [ ] Account info displays
- [ ] Can view positions (if any)
- [ ] Can view trade history
- [ ] Auto-refresh works
- [ ] Can stop bot successfully

### Security Verification
- [ ] Credentials encrypted in storage
- [ ] Session expires after timeout
- [ ] Cannot access API without session
- [ ] Rate limiting works
- [ ] Input validation prevents invalid data
- [ ] Error messages don't leak sensitive info
- [ ] HTTPS enforced (production only)

### Performance Testing
- [ ] Dashboard loads within 2 seconds
- [ ] Instrument list loads within 2 seconds
- [ ] Configuration saves instantly
- [ ] API responses within acceptable time
- [ ] Auto-refresh doesn't cause lag
- [ ] No memory leaks over time

### Monitoring Setup
- [ ] Log files being created
- [ ] Log rotation configured
- [ ] Can view logs easily
- [ ] Error logging works
- [ ] Access logging works (if enabled)
- [ ] Health check endpoint works (if configured)

## Production Readiness Checklist

### Documentation
- [ ] Deployment guide reviewed
- [ ] User guide available
- [ ] API documentation available
- [ ] Troubleshooting guide accessible
- [ ] FAQ document available

### Backup and Recovery
- [ ] Backup strategy documented
- [ ] Credentials backed up securely
- [ ] Configurations backed up
- [ ] Restore procedure tested
- [ ] Backup schedule established

### Maintenance Plan
- [ ] Update procedure documented
- [ ] Dependency update schedule
- [ ] Log rotation schedule
- [ ] Backup schedule
- [ ] Security audit schedule
- [ ] Performance review schedule

### Support
- [ ] Support contact information documented
- [ ] Issue reporting process established
- [ ] Emergency procedures documented
- [ ] Escalation path defined

## Go-Live Checklist

### Final Verification
- [ ] All above checklists completed
- [ ] Tested with real broker credentials (in test mode)
- [ ] Verified with small position sizes
- [ ] Monitored for at least 1 hour
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Users trained on dashboard usage

### Launch
- [ ] Announce to users
- [ ] Monitor closely for first 24 hours
- [ ] Be available for support
- [ ] Document any issues encountered
- [ ] Collect user feedback

### Post-Launch
- [ ] Review logs daily for first week
- [ ] Monitor performance metrics
- [ ] Address any issues promptly
- [ ] Update documentation based on feedback
- [ ] Plan for improvements

## Rollback Plan

If issues occur:
- [ ] Stop the dashboard service
- [ ] Restore from backup if needed
- [ ] Review logs to identify issue
- [ ] Fix issue in development environment
- [ ] Test fix thoroughly
- [ ] Redeploy with fix

## Sign-Off

- [ ] System Administrator: _________________ Date: _______
- [ ] Security Review: _________________ Date: _______
- [ ] User Acceptance: _________________ Date: _______
- [ ] Production Approval: _________________ Date: _______

---

**Notes:**
- Check off items as you complete them
- Document any deviations from standard procedure
- Keep this checklist for audit purposes
- Update checklist based on lessons learned
