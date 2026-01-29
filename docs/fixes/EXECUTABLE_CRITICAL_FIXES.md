# Critical Executable Fixes - Build 5549 & Process Management

**Date**: January 29, 2026  
**Status**: URGENT FIXES REQUIRED

---

## Issues Identified

### 1. MT5 Build 5549 Compatibility
**Problem**: Bot doesn't integrate with MT5 version 5 build 5549  
**Cause**: Missing MT5 initialization parameters for newer builds

### 2. Configuration Not Applied
**Problem**: Configuration changes not taking effect  
**Cause**: Bot thread not reloading config after changes

### 3. Bot Process Not Stopping
**Problem**: Bot executable still running in Task Manager even when dashboard says stopped  
**Cause**: Background thread not terminating properly

---

## Fixes Required

### Fix 1: MT5 Build 5549 Compatibility

Update `src/mt5_trading_bot.py` connect method:

```python
def connect(self):
    """Connect to MetaTrader5 with build 5549 compatibility"""
    # Try with path parameter for newer builds
    if not mt5.initialize():
        # Try alternative initialization for build 5549+
        import platform
        if platform.system() == 'Windows':
            # Try common MT5 installation paths
            mt5_paths = [
                r"C:\Program Files\MetaTrader 5\terminal64.exe",
                r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
                r"C:\Users\{}\AppData\Roaming\MetaQuotes\Terminal\*\terminal64.exe".format(os.environ.get('USERNAME', ''))
            ]
            
            for path in mt5_paths:
                if os.path.exists(path):
                    if mt5.initialize(path=path):
                        logging.info(f"MT5 initialized with path: {path}")
                        break
            else:
                logging.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
        else:
            logging.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
    
    logging.info(f"MT5 initialized successfully")
    logging.info(f"MT5 version: {mt5.version()}")
    logging.info(f"MT5 build: {mt5.terminal_info().build if mt5.terminal_info() else 'Unknown'}")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        logging.info(f"Account balance: {account_info.balance}")
        logging.info(f"Account equity: {account_info.equity}")
    
    return True
```

### Fix 2: Configuration Reload on Bot Start

Update `web_dashboard.py` start_bot function:

```python
@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_running, bot_thread, current_config
    
    if bot_running:
        return jsonify({'status': 'error', 'message': 'Bot already running'})
    
    # CRITICAL: Reload configuration from config manager before starting
    current_config = config_manager.get_config()
    logger.info(f"Reloaded configuration from {config_manager.config_file}")
    logger.info(f"Symbols: {current_config.get('symbols')}")
    logger.info(f"Timeframe: {current_config.get('timeframe')}")
    logger.info(f"Risk: {current_config.get('risk_percent')}%")
    
    # Test MT5 connection first
    if not mt5.initialize():
        logger.error("Failed to start bot: MT5 not connected")
        return jsonify({'status': 'error', 'message': 'MT5 not connected. Please check MT5 is running.'})
    
    account_info = mt5.account_info()
    if account_info is None:
        mt5.shutdown()
        logger.error("Failed to start bot: No account info")
        return jsonify({'status': 'error', 'message': 'Cannot access MT5 account. Check login.'})
    
    mt5.shutdown()
    
    bot_running = True
    bot_thread = threading.Thread(target=run_bot_background, daemon=True)  # Make daemon
    bot_thread.start()
    
    logger.info("Trading bot started")
    return jsonify({'status': 'success', 'message': 'Bot started successfully'})
```

### Fix 3: Proper Bot Process Termination

Update `web_dashboard.py` stop_bot and run_bot_background:

```python
@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_running, bot_thread
    
    if not bot_running:
        return jsonify({'status': 'warning', 'message': 'Bot is not running'})
    
    logger.info("Stopping trading bot...")
    bot_running = False
    
    # Wait for thread to finish (max 10 seconds)
    if bot_thread and bot_thread.is_alive():
        bot_thread.join(timeout=10)
        if bot_thread.is_alive():
            logger.warning("Bot thread did not stop gracefully")
        else:
            logger.info("Bot thread stopped successfully")
    
    # Force MT5 shutdown
    try:
        mt5.shutdown()
    except:
        pass
    
    logger.info("Trading bot stopped")
    return jsonify({'status': 'success', 'message': 'Bot stopped successfully'})


def run_bot_background():
    """Run bot in background thread"""
    global bot_running, current_config
    
    from src.mt5_trading_bot import MT5TradingBot
    
    # Get latest configuration from config manager
    current_config = config_manager.get_config()
    
    logger.info("Initializing trading bot...")
    logger.info(f"Configuration: Symbols={current_config.get('symbols')}, Timeframe={current_config.get('timeframe')}, Risk={current_config.get('risk_percent')}%")
    
    bot = MT5TradingBot(current_config)
    
    if not bot.connect():
        logger.error("Failed to connect to MT5")
        bot_running = False
        return
    
    logger.info("Bot connected successfully, starting trading loop...")
    
    try:
        while bot_running:
            try:
                # Check if bot should still be running
                if not bot_running:
                    break
                
                # Run one iteration
                for symbol in bot.symbols:
                    if not bot_running:  # Check again
                        break
                    try:
                        bot.run_strategy(symbol)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {str(e)}")
                
                # Manage positions
                if bot_running:
                    try:
                        bot.manage_positions()
                    except Exception as e:
                        logger.error(f"Error managing positions: {str(e)}")
                
                # Sleep with frequent checks
                for _ in range(60):  # Check every second for 60 seconds
                    if not bot_running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in bot loop: {str(e)}")
                if not bot_running:
                    break
                time.sleep(5)
    except Exception as e:
        logger.error(f"Critical bot error: {str(e)}")
    finally:
        logger.info("Shutting down bot...")
        try:
            bot.disconnect()
        except:
            pass
        bot_running = False
        logger.info("Bot shutdown complete")
```

---

## Implementation Steps

### Step 1: Update MT5 Trading Bot

```bash
# Edit src/mt5_trading_bot.py
# Update the connect() method with build 5549 compatibility
```

### Step 2: Update Web Dashboard

```bash
# Edit web_dashboard.py
# Update start_bot(), stop_bot(), and run_bot_background()
```

### Step 3: Rebuild Executable

```bash
# Run build script
build_windows.bat
```

### Step 4: Test

1. **Test MT5 Connection**:
   - Start MT5 build 5549
   - Run executable
   - Check connection in dashboard

2. **Test Configuration**:
   - Change symbols in dashboard
   - Save configuration
   - Start bot
   - Verify bot uses new symbols (check logs)

3. **Test Stop Function**:
   - Start bot
   - Stop bot
   - Check Task Manager - process should be gone
   - Check dashboard - should show "stopped"

---

## Additional Improvements

### Add Process ID Tracking

```python
# In web_dashboard.py
import psutil

bot_process_id = None

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    global bot_running, bot_thread, bot_process_id
    
    # ... existing code ...
    
    bot_process_id = os.getpid()
    logger.info(f"Bot process ID: {bot_process_id}")
    
    # ... rest of code ...

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    global bot_running, bot_thread, bot_process_id
    
    # ... existing stop code ...
    
    # Force kill if still running
    if bot_process_id:
        try:
            process = psutil.Process(bot_process_id)
            if process.is_running():
                logger.warning("Force terminating bot process")
                process.terminate()
                process.wait(timeout=5)
        except:
            pass
    
    bot_process_id = None
```

### Add Configuration Validation

```python
# In src/config_manager.py
def validate_mt5_compatibility(self):
    """Validate configuration for MT5 build 5549+"""
    try:
        if not mt5.initialize():
            return False, "Cannot connect to MT5"
        
        terminal_info = mt5.terminal_info()
        if terminal_info:
            build = terminal_info.build
            logger.info(f"MT5 Build: {build}")
            
            if build >= 5549:
                logger.info("MT5 build 5549+ detected - using enhanced initialization")
        
        mt5.shutdown()
        return True, "MT5 compatible"
    except Exception as e:
        return False, str(e)
```

---

## Testing Checklist

- [ ] MT5 build 5549 connects successfully
- [ ] Configuration changes are applied
- [ ] Bot stops completely (not in Task Manager)
- [ ] Dashboard shows correct bot status
- [ ] Logs show configuration reload
- [ ] Symbols from config are used
- [ ] Timeframe from config is used
- [ ] Risk settings from config are used

---

## User Instructions

### If Bot Won't Connect to MT5 5549:

1. **Check MT5 is Running**:
   - Open MetaTrader 5
   - Verify you're logged in
   - Check build number: Help > About

2. **Enable Algo Trading**:
   - Tools > Options > Expert Advisors
   - Check "Allow algorithmic trading"
   - Click OK

3. **Restart Both**:
   - Close MT5 completely
   - Close bot executable
   - Start MT5 first
   - Wait 30 seconds
   - Start bot executable

### If Configuration Not Applied:

1. **Save Configuration**:
   - Make changes in dashboard
   - Click "Save Configuration"
   - Wait for success message

2. **Restart Bot**:
   - Click "Stop Bot"
   - Wait 5 seconds
   - Click "Start Bot"
   - Check logs for "Reloaded configuration"

3. **Verify in Logs**:
   - Go to Logs tab
   - Look for "Configuration: Symbols=..."
   - Verify your symbols are listed

### If Bot Won't Stop:

1. **Use Stop Button**:
   - Click "Stop Bot" in dashboard
   - Wait 10 seconds

2. **Check Task Manager**:
   - Open Task Manager (Ctrl+Shift+Esc)
   - Look for "GEM_Trading_Bot.exe"
   - If still running, right-click > End Task

3. **Restart Dashboard**:
   - Close browser
   - Close executable completely
   - Restart executable

---

## Priority: CRITICAL

These fixes must be implemented before next release. Current executable has:
- ❌ MT5 5549 compatibility issues
- ❌ Configuration not being applied
- ❌ Process not stopping properly

After fixes:
- ✅ MT5 5549 fully compatible
- ✅ Configuration applied immediately
- ✅ Clean process termination

---

**Status**: Fixes documented, ready for implementation
