# Executable Update Guide - Critical Fixes

**Version**: 2.1.1  
**Date**: January 29, 2026  
**Priority**: CRITICAL UPDATE REQUIRED

---

## What's Fixed

### ✅ MT5 Build 5549 Compatibility
- Bot now works with MT5 version 5 build 5549 and newer
- Enhanced initialization with automatic path detection
- Better error messages for connection issues

### ✅ Configuration Changes Applied
- Configuration changes now take effect immediately
- Bot reloads config from `bot_config.json` on every start
- Detailed logging shows which config is being used

### ✅ Bot Process Stops Properly
- Bot now stops completely when "Stop Bot" is clicked
- No more zombie processes in Task Manager
- Clean MT5 connection shutdown

---

## For Users: How to Update

### Step 1: Download New Executable

1. Download the latest `GEM_Trading_Bot_v2.1.1_Windows.zip`
2. Extract to a new folder (don't overwrite old version yet)

### Step 2: Backup Your Configuration

1. Find your old installation folder
2. Copy `bot_config.json` (if it exists)
3. Save it somewhere safe

### Step 3: Install New Version

1. Close the old bot completely
2. Check Task Manager - make sure no `GEM_Trading_Bot.exe` is running
3. Delete or rename old installation folder
4. Extract new version to desired location
5. Copy your `bot_config.json` back (if you had one)

### Step 4: Test

1. Make sure MT5 is running and logged in
2. Double-click `GEM_Trading_Bot.exe`
3. Wait for dashboard to open
4. Click "Test MT5" - should show "Connected"
5. Check logs for "MT5 build: 5549" (or your build number)

---

## For Developers: How to Rebuild

### Step 1: Pull Latest Changes

```bash
git pull origin main
```

### Step 2: Verify Changes

Check these files were updated:
- `src/mt5_trading_bot.py` - Enhanced connect() method
- `web_dashboard.py` - Fixed start_bot(), stop_bot(), run_bot_background()

### Step 3: Rebuild Executable

```bash
# Windows
build_windows.bat

# This will:
# 1. Install dependencies
# 2. Build executable with PyInstaller
# 3. Create distribution package
# 4. Include all documentation
```

### Step 4: Test Executable

```bash
cd dist
GEM_Trading_Bot.exe
```

**Test Checklist**:
- [ ] Dashboard opens at http://localhost:5000
- [ ] "Test MT5" shows connected
- [ ] Logs show MT5 build number
- [ ] Can change configuration
- [ ] Configuration changes are applied
- [ ] Bot starts successfully
- [ ] Bot stops completely (check Task Manager)
- [ ] No zombie processes

### Step 5: Create Release

```bash
# Create ZIP for distribution
cd dist
# Right-click GEM_Trading_Bot_Windows folder
# Send to > Compressed (zipped) folder
# Rename to: GEM_Trading_Bot_v2.1.1_Windows.zip
```

---

## What Changed (Technical Details)

### 1. MT5 Connection Enhancement

**File**: `src/mt5_trading_bot.py`

**Before**:
```python
def connect(self):
    if not mt5.initialize():
        logging.error(f"MT5 initialization failed: {mt5.last_error()}")
        return False
```

**After**:
```python
def connect(self):
    # Try standard initialization
    if not mt5.initialize():
        # Try with path parameter for build 5549+
        if platform.system() == 'Windows':
            # Try common MT5 paths
            mt5_paths = [
                r"C:\Program Files\MetaTrader 5\terminal64.exe",
                r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
                # + AppData paths
            ]
            for path in mt5_paths:
                if os.path.exists(path):
                    if mt5.initialize(path=path):
                        logging.info(f"MT5 initialized with path: {path}")
                        break
    
    # Log build number
    terminal_info = mt5.terminal_info()
    if terminal_info:
        logging.info(f"MT5 build: {terminal_info.build}")
```

### 2. Configuration Reload

**File**: `web_dashboard.py`

**Before**:
```python
@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    # ... existing code ...
    bot_thread = threading.Thread(target=run_bot_background)
    bot_thread.start()
```

**After**:
```python
@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    # CRITICAL: Reload configuration
    current_config = config_manager.get_config()
    logger.info("=" * 80)
    logger.info("STARTING BOT WITH CONFIGURATION:")
    logger.info(f"Symbols: {current_config.get('symbols')}")
    logger.info(f"Timeframe: {current_config.get('timeframe')}")
    logger.info("=" * 80)
    
    # Make daemon thread
    bot_thread = threading.Thread(target=run_bot_background, daemon=True)
    bot_thread.start()
```

### 3. Proper Bot Termination

**File**: `web_dashboard.py`

**Before**:
```python
@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    global bot_running
    bot_running = False
    return jsonify({'status': 'success'})
```

**After**:
```python
@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    global bot_running, bot_thread
    
    bot_running = False
    
    # Wait for thread to finish
    if bot_thread and bot_thread.is_alive():
        bot_thread.join(timeout=10)
        if bot_thread.is_alive():
            logger.warning("Thread did not stop gracefully")
    
    # Force MT5 shutdown
    try:
        mt5.shutdown()
    except:
        pass
    
    return jsonify({'status': 'success'})
```

### 4. Enhanced Bot Loop

**File**: `web_dashboard.py`

**Before**:
```python
def run_bot_background():
    while bot_running:
        bot.run()
        time.sleep(60)
```

**After**:
```python
def run_bot_background():
    while bot_running:
        # Run strategy for each symbol
        for symbol in bot.symbols:
            if not bot_running:  # Check stop signal
                break
            bot.run_strategy(symbol)
        
        # Manage positions
        if bot_running:
            bot.manage_positions()
        
        # Sleep with frequent checks
        for _ in range(60):
            if not bot_running:  # Check every second
                break
            time.sleep(1)
```

---

## Verification Steps

### For Users

1. **Check MT5 Connection**:
   ```
   Dashboard > Test MT5 > Should show "Connected"
   Logs should show: "MT5 build: 5549" (or your build)
   ```

2. **Verify Configuration**:
   ```
   Dashboard > Configuration > Change symbols
   Click "Save Configuration"
   Dashboard > Logs > Should show "STARTING BOT WITH CONFIGURATION"
   Verify your symbols are listed
   ```

3. **Test Stop Function**:
   ```
   Dashboard > Start Bot
   Wait 10 seconds
   Dashboard > Stop Bot
   Open Task Manager (Ctrl+Shift+Esc)
   Look for "GEM_Trading_Bot.exe" - should NOT be there
   ```

### For Developers

1. **Test MT5 Initialization**:
   ```python
   python -c "import MetaTrader5 as mt5; print('Init:', mt5.initialize()); print('Build:', mt5.terminal_info().build if mt5.terminal_info() else 'N/A'); mt5.shutdown()"
   ```

2. **Test Configuration Manager**:
   ```python
   python -c "from src.config_manager import get_config; c = get_config(); print('Symbols:', c['symbols']); print('Timeframe:', c['timeframe'])"
   ```

3. **Test Bot Import**:
   ```python
   python -c "from src.mt5_trading_bot import MT5TradingBot; print('Bot imported successfully')"
   ```

---

## Troubleshooting

### Issue: "MT5 initialization failed"

**Solution**:
1. Make sure MT5 is running
2. Check you're logged into an account
3. Enable algo trading: Tools > Options > Expert Advisors
4. Check MT5 installation path in logs
5. Try running as Administrator

### Issue: "Configuration not applied"

**Solution**:
1. Check `bot_config.json` exists in bot folder
2. Open file - verify your changes are there
3. Restart bot completely (stop, wait 5 seconds, start)
4. Check logs for "STARTING BOT WITH CONFIGURATION"
5. Verify symbols/timeframe in logs match your config

### Issue: "Bot won't stop"

**Solution**:
1. Click "Stop Bot" and wait 10 seconds
2. Check Task Manager for `GEM_Trading_Bot.exe`
3. If still running, right-click > End Task
4. Close browser
5. Restart executable

### Issue: "Zombie process in Task Manager"

**Solution**:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find `GEM_Trading_Bot.exe`
3. Right-click > End Task
4. If multiple instances, end all
5. Restart executable
6. If problem persists, update to latest version

---

## Release Notes

### Version 2.1.1 (January 29, 2026)

**Critical Fixes**:
- ✅ MT5 build 5549+ compatibility
- ✅ Configuration changes now applied immediately
- ✅ Bot process stops completely
- ✅ Enhanced logging for debugging
- ✅ Daemon threads for clean shutdown

**Improvements**:
- Better error messages
- Detailed configuration logging
- MT5 build number detection
- Automatic path detection for MT5
- Graceful thread termination

**Files Changed**:
- `src/mt5_trading_bot.py` - Enhanced connect() method
- `web_dashboard.py` - Fixed bot lifecycle management
- `docs/fixes/EXECUTABLE_CRITICAL_FIXES.md` - Documentation

---

## Support

### For Users

If you encounter issues:
1. Check `trading_bot.log` in bot folder
2. Look for error messages
3. Try solutions in Troubleshooting section
4. Read `TROUBLESHOOTING.md` for more help

### For Developers

If you need to debug:
1. Run bot from source (not executable)
2. Check logs with `tail -f trading_bot.log`
3. Use Python debugger
4. Check MT5 terminal logs
5. Review `docs/fixes/EXECUTABLE_CRITICAL_FIXES.md`

---

## Next Steps

1. **Rebuild executable** with `build_windows.bat`
2. **Test thoroughly** with checklist above
3. **Create release** ZIP file
4. **Update users** with new version
5. **Monitor feedback** for any remaining issues

---

**Status**: Ready for rebuild and distribution  
**Priority**: CRITICAL - Update all users ASAP  
**Compatibility**: Windows 10/11, MT5 build 5549+
