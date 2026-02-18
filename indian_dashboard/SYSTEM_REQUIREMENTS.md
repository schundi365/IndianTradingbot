# System Requirements

## Hardware Requirements

### Minimum Configuration
- **CPU:** 2 cores, 2.0 GHz
- **RAM:** 2 GB
- **Storage:** 500 MB free space
- **Network:** Stable internet connection (minimum 1 Mbps)

### Recommended Configuration
- **CPU:** 4 cores, 2.5 GHz or higher
- **RAM:** 4 GB or more
- **Storage:** 1 GB free space
- **Network:** High-speed internet (5+ Mbps, low latency preferred)

### Optimal Configuration (for production)
- **CPU:** 6+ cores, 3.0 GHz or higher
- **RAM:** 8 GB or more
- **Storage:** 2 GB free space (SSD recommended)
- **Network:** Dedicated high-speed connection (10+ Mbps)

---

## Software Requirements

### Operating System

**Supported:**
- Windows 10 (64-bit) or Windows 11
- Ubuntu 20.04 LTS or later
- Debian 10 or later
- CentOS 8 or later
- macOS 10.15 (Catalina) or later

**Not Supported:**
- Windows 7, 8, 8.1
- 32-bit operating systems
- Windows Server (untested)

### Python

**Required:**
- Python 3.8 or higher

**Recommended:**
- Python 3.9 or Python 3.10

**Not Supported:**
- Python 2.x
- Python 3.7 or earlier

**Verification:**
```bash
python --version
# Should show: Python 3.8.x or higher
```

### Python Packages

**Core Dependencies:**
- Flask >= 2.0.0 (web framework)
- cryptography >= 3.4.0 (credential encryption)
- requests >= 2.25.0 (HTTP client)
- python-dotenv >= 0.19.0 (environment variables)

**Broker-Specific:**
- kiteconnect >= 4.0.0 (for Kite Connect)
- Additional broker SDKs as needed

**All dependencies listed in:** `requirements.txt`

### Web Browser

**Supported:**
- Google Chrome 90+ (recommended)
- Mozilla Firefox 88+
- Microsoft Edge 90+
- Safari 14+ (macOS only)

**Features Required:**
- JavaScript enabled
- Cookies enabled
- LocalStorage support
- Modern CSS support (Flexbox, Grid)

**Not Supported:**
- Internet Explorer (any version)
- Very old browser versions

---

## Network Requirements

### Internet Connectivity

**Required:**
- Stable internet connection
- Minimum bandwidth: 1 Mbps
- Recommended bandwidth: 5+ Mbps
- Low latency preferred (<100ms to broker APIs)

### Firewall Configuration

**Outbound Access Required:**
- HTTPS (port 443) to broker APIs
- HTTP (port 80) for redirects

**Inbound Access (optional):**
- Port 8080 (or configured port) for dashboard access
- Only needed if accessing from other devices

### Broker API Endpoints

**Must be accessible:**
- Kite Connect: `api.kite.trade`
- Alice Blue: `ant.aliceblueonline.com`
- Angel One: `apiconnect.angelbroking.com`
- Upstox: `api.upstox.com`

**Verification:**
```bash
# Test connectivity
ping api.kite.trade
curl https://api.kite.trade
```

### Proxy Configuration

If behind corporate proxy:
- Configure proxy in environment variables
- Ensure HTTPS traffic is allowed
- May need to whitelist broker domains

---

## Storage Requirements

### Disk Space

**Minimum:** 500 MB
- Application: ~50 MB
- Python packages: ~200 MB
- Data and cache: ~100 MB
- Logs: ~50 MB
- Buffer: ~100 MB

**Recommended:** 1 GB
- Allows for growth
- Multiple configurations
- Extended log history
- Instrument cache

### File System

**Supported:**
- NTFS (Windows)
- ext4, ext3 (Linux)
- APFS, HFS+ (macOS)

**Permissions Required:**
- Read/write access to application directory
- Ability to create subdirectories
- Ability to create and modify files

---

## Performance Considerations

### CPU Usage

**Typical:**
- Idle: 1-2% CPU
- Active trading: 5-10% CPU
- Peak (data refresh): 15-20% CPU

**Factors affecting CPU:**
- Number of instruments monitored
- Auto-refresh frequency
- Number of concurrent positions
- Indicator calculations

### Memory Usage

**Typical:**
- Base application: ~100 MB
- With data cache: ~200-300 MB
- Peak usage: ~500 MB

**Factors affecting memory:**
- Number of instruments cached
- Cache expiry settings
- Number of open positions
- Browser memory usage

### Network Usage

**Typical:**
- Idle: <1 KB/s
- Active monitoring: 5-10 KB/s
- Data refresh: 50-100 KB/s
- Peak (instrument fetch): 500 KB/s

**Factors affecting network:**
- Auto-refresh frequency
- Number of instruments
- Market data subscriptions
- Order placement frequency

---

## Compatibility Matrix

### Python Version Compatibility

| Python Version | Status | Notes |
|---------------|--------|-------|
| 3.11 | ✅ Supported | Latest, recommended |
| 3.10 | ✅ Supported | Recommended |
| 3.9 | ✅ Supported | Recommended |
| 3.8 | ✅ Supported | Minimum version |
| 3.7 | ❌ Not Supported | EOL |
| 2.7 | ❌ Not Supported | EOL |

### Operating System Compatibility

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| Windows | 11 | ✅ Fully Supported | Recommended |
| Windows | 10 (64-bit) | ✅ Fully Supported | |
| Windows | 10 (32-bit) | ❌ Not Supported | |
| Ubuntu | 22.04 LTS | ✅ Fully Supported | Recommended |
| Ubuntu | 20.04 LTS | ✅ Fully Supported | |
| Ubuntu | 18.04 LTS | ⚠️ Limited Support | EOL soon |
| Debian | 11 | ✅ Fully Supported | |
| Debian | 10 | ✅ Fully Supported | |
| CentOS | 8 | ✅ Fully Supported | |
| macOS | 13 (Ventura) | ✅ Fully Supported | |
| macOS | 12 (Monterey) | ✅ Fully Supported | |
| macOS | 11 (Big Sur) | ✅ Fully Supported | |
| macOS | 10.15 (Catalina) | ✅ Supported | Minimum |

### Browser Compatibility

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | 100+ | ✅ Fully Supported | Recommended |
| Chrome | 90-99 | ✅ Supported | |
| Firefox | 100+ | ✅ Fully Supported | |
| Firefox | 88-99 | ✅ Supported | |
| Edge | 100+ | ✅ Fully Supported | |
| Edge | 90-99 | ✅ Supported | |
| Safari | 15+ | ✅ Fully Supported | macOS only |
| Safari | 14 | ✅ Supported | macOS only |
| IE | Any | ❌ Not Supported | |

---

## Deployment Environment Requirements

### Development Environment

**Minimum:**
- Python 3.8+
- 2 GB RAM
- Text editor
- Terminal/Command Prompt

**Recommended:**
- Python 3.9+
- 4 GB RAM
- IDE (VS Code, PyCharm)
- Git

### Production Environment

**Minimum:**
- Python 3.8+
- 4 GB RAM
- Stable internet
- Process manager (systemd, NSSM)

**Recommended:**
- Python 3.9+
- 8 GB RAM
- Dedicated server/VPS
- Monitoring tools
- Backup system

### Testing Environment

**Requirements:**
- Same as development
- Paper trading account
- Test broker credentials
- Separate configuration

---

## Security Requirements

### System Security

**Required:**
- Firewall enabled
- Antivirus/antimalware (recommended)
- Regular OS updates
- Strong user passwords

**Recommended:**
- Disk encryption
- VPN for remote access
- Intrusion detection
- Regular security audits

### Application Security

**Required:**
- Strong encryption keys
- Secure credential storage
- HTTPS for remote access
- Regular updates

**Recommended:**
- IP whitelisting
- 2FA on broker accounts
- Rate limiting enabled
- Security monitoring

---

## Scalability Considerations

### Single User Setup
- Default configuration sufficient
- Localhost access only
- Minimal resources

### Multi-Device Access
- Bind to 0.0.0.0
- Firewall configuration
- Increased memory recommended

### Production Deployment
- Dedicated server
- Process manager
- Monitoring and logging
- Backup strategy
- High availability setup (optional)

---

## Verification Checklist

Use this checklist to verify your system meets requirements:

### Hardware
- [ ] CPU: 2+ cores, 2.0+ GHz
- [ ] RAM: 2+ GB available
- [ ] Storage: 500+ MB free
- [ ] Network: Stable internet

### Software
- [ ] Python 3.8+ installed
- [ ] pip installed and working
- [ ] Virtual environment support
- [ ] Modern web browser

### Network
- [ ] Internet connectivity
- [ ] Broker API accessible
- [ ] Firewall configured
- [ ] Port 8080 available

### Permissions
- [ ] Read/write access to app directory
- [ ] Can create files and folders
- [ ] Can install Python packages
- [ ] Can bind to network port

### Optional
- [ ] Git installed
- [ ] Text editor/IDE
- [ ] Process manager
- [ ] Monitoring tools

---

## Automated Verification

Run the system check script:

```bash
python troubleshoot.py --check-requirements
```

This will verify:
- Python version
- Required packages
- Disk space
- Network connectivity
- File permissions
- Port availability

---

## Upgrade Path

### From Older Python Versions

If running Python 3.7 or earlier:

1. Install Python 3.8+
2. Create new virtual environment
3. Reinstall dependencies
4. Test thoroughly

### From 32-bit to 64-bit

1. Install 64-bit Python
2. Recreate virtual environment
3. Reinstall all packages
4. Migrate configurations

### Hardware Upgrades

**Priority order:**
1. RAM (most impact)
2. CPU (moderate impact)
3. Storage (SSD for better performance)
4. Network (stable connection critical)

---

## Known Limitations

### Platform-Specific

**Windows:**
- PowerShell execution policy may need adjustment
- Some Linux-specific features unavailable

**Linux:**
- May need additional system packages
- Permissions more strict

**macOS:**
- Some broker SDKs may have limited support
- Gatekeeper may block unsigned packages

### Resource Limitations

**Low RAM (<2GB):**
- Reduce cache size
- Lower auto-refresh frequency
- Monitor fewer instruments

**Slow CPU:**
- Increase refresh intervals
- Reduce concurrent operations
- Simplify indicator calculations

**Slow Network:**
- Increase timeouts
- Reduce API calls
- Use cached data when possible

---

## Support and Updates

### Checking for Updates

```bash
# Check current version
python indian_dashboard.py --version

# Update to latest
git pull origin main
pip install -r requirements.txt --upgrade
```

### Compatibility Updates

- Monitor release notes
- Test in development first
- Backup before upgrading
- Review breaking changes

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-02-18  
**Next Review:** 2024-05-18

For the latest requirements, check the repository documentation.
