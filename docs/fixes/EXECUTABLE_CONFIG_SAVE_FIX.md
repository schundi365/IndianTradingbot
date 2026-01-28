# Executable Configuration Save Fix

**Date:** January 28, 2026  
**Issue:** Configuration changes fail to save when running as executable

---

## Problem

When the bot is deployed as a Windows executable (.exe), users cannot save configuration changes from the dashboard.

**Error Symptoms:**
- Configuration changes don't persist
- "Failed to save configuration" error
- Settings revert to defaults after restart
- No error message but changes don't apply

**Root Cause:**
- The `src/config.py` file is bundled inside the executable
- Bundled files are read-only and cannot be modified
- The dashboard tried to modify the bundled config file
- File system permissions prevent writing to executable resources

---

## Solution

Implemented an external JSON configuration system that works with executables.

### New System Architecture

**Before (Broken):**
```
Executable
├── web_dashboard.py (bundled)
├── src/
│   └── config.py (bundled, read-only) ❌
└── [User tries to modify bundled file - FAILS]
```

**After (Fixed):**
```
Executable Directory
├── GEM_Trading_Bot.exe
├── bot_config.json (external, writable) ✅
└── config_backups/
    ├── config_backup_20260128_120000.json
    ├── config_backup_20260128_130000.json
    └── ...
```

---

## Implementation

### 1. Created Configuration Manager

**New File:** `src/config_manager.py`

**Features:**
- External JSON configuration file
- Automatic backup system (keeps last 10)
- Validation of all settings
- Import/export functionality
- Works with both executable and script modes
- Automatic directory detection

**Key Functions:**
```python
class ConfigManager:
    def __init__(self, config_file='bot_config.json')
    def get_config()  # Get current configuration
    def save_config(config)  # Save to external file
    def update_config(updates)  # Update and save
    def reset_to_default()  # Reset configuration
    def export_config(path)  # Export to file
    def import_config(path)  # Import from file
```

---

### 2. Updated Web Dashboard

**File:** `web_dashboard.py`

**Changes:**
```python
# Before
from src.config import get_config
current_config = get_config()

# After
from src.config_manager import get_config_manager, get_config
config_manager = get_config_manager()
current_config = config_manager.get_config()
```

**Configuration Save:**
```python
# Before
update_config_file(new_config)  # Tries to modify bundled file ❌

# After
config_manager.update_config(new_config)  # Saves to external JSON ✅
```

---

### 3. Updated Build Script

**File:** `build_windows.bat`

**Added Hidden Imports:**
```bat
--hidden-import=pathlib ^
--hidden-import=json ^
```

**Why:**
- Ensures pathlib and json modules are included
- Required for config manager to work
- Prevents import errors in executable

---

## How It Works

### Directory Detection

**Running as Script:**
```python
# Uses project root directory
base_dir = Path(__file__).parent.parent
config_file = base_dir / 'bot_config.json'
# Result: C:\Users\...\tradegold\bot_config.json
```

**Running as Executable:**
```python
# Uses executable directory
base_dir = Path(sys.executable).parent
config_file = base_dir / 'bot_config.json'
# Result: C:\Users\...\GEM_Trading_Bot_Windows\bot_config.json
```

---

### Configuration File Location

**When Running Executable:**
```
C:\Users\YourName\Downloads\GEM_Trading_Bot_Windows\
├── GEM_Trading_Bot.exe
├── bot_config.json  ← Configuration saved here
├── config_backups\
│   ├── config_backup_20260128_120000.json
│   └── config_backup_20260128_130000.json
├── trading_bot.log
└── [documentation files]
```

**Advantages:**
- User can see and edit configuration
- Survives executable updates
- Can be backed up easily
- Can be shared between users
- Portable configuration

---

### Automatic Backups

**When Configuration is Saved:**
1. Current config is backed up to `config_backups/`
2. Backup filename includes timestamp
3. New configuration is saved
4. Old backups are cleaned up (keeps last 10)

**Backup Naming:**
```
config_backup_20260128_120530.json
config_backup_20260128_143022.json
config_backup_20260128_165511.json
```

**Recovery:**
- If configuration gets corrupted
- User can restore from backup
- Simply copy backup to `bot_config.json`

---

## Configuration File Format

### bot_config.json Structure

```json
{
    "symbols": ["XAUUSD", "XAGUSD"],
    "timeframe": 30,
    "risk_percent": 1.0,
    "reward_ratio": 1.5,
    "min_confidence": 0.6,
    "max_daily_loss": 5,
    "fast_ma_period": 10,
    "slow_ma_period": 30,
    "rsi_period": 14,
    "rsi_overbought": 75,
    "rsi_oversold": 25,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "macd_min_histogram": 0.3,
    "atr_period": 14,
    "atr_multiplier": 1.5,
    "adx_min_strength": 20,
    "use_rsi": true,
    "use_macd": true,
    "use_adx": true,
    "use_trend_filter": false,
    "trend_ma_period": 100,
    "enable_trading_hours": false,
    "trading_start_hour": 0,
    "trading_end_hour": 23,
    "avoid_news_trading": false,
    "news_buffer_minutes": 30,
    "use_split_orders": true,
    "num_positions": 3,
    "tp_level_1": 1.0,
    "tp_level_2": 1.5,
    "tp_level_3": 2.5,
    "max_trades_total": 20,
    "max_trades_per_symbol": 5,
    "enable_trailing_stop": true,
    "trail_activation": 1.0,
    "trail_distance": 0.8,
    "use_adaptive_risk": true,
    "max_risk_multiplier": 2.0,
    "min_risk_multiplier": 0.5,
    "max_drawdown_percent": 15,
    "max_daily_trades": 50,
    "version": "2.1.0",
    "last_updated": "2026-01-28T12:05:30.123456"
}
```

**Human-Readable:**
- JSON format with indentation
- Easy to edit manually if needed
- Can be version controlled
- Can be shared with others

---

## User Experience

### First Run

1. User runs `GEM_Trading_Bot.exe`
2. No `bot_config.json` exists
3. Config manager creates default configuration
4. File saved to executable directory
5. Dashboard loads with default settings

### Changing Configuration

1. User opens dashboard (http://localhost:5000)
2. Clicks "Configuration" tab
3. Changes settings (symbols, risk, etc.)
4. Clicks "Save Configuration"
5. Configuration saved to `bot_config.json` ✅
6. Backup created automatically
7. Success message displayed
8. Bot uses new configuration

### After Restart

1. User closes and reopens executable
2. Config manager loads `bot_config.json`
3. Previous settings are restored ✅
4. No need to reconfigure

---

## Benefits

### For Users

1. **Configuration Persists**
   - Settings saved between sessions
   - No need to reconfigure
   - Reliable and predictable

2. **Easy Backup**
   - Automatic backups
   - Can manually copy config file
   - Easy to restore

3. **Portable**
   - Copy config file to new installation
   - Share settings with others
   - Version control friendly

4. **Transparent**
   - Can see configuration file
   - Can edit manually if needed
   - Understand what's saved

---

### For Developers

1. **Executable Compatible**
   - Works with PyInstaller
   - No file system restrictions
   - Clean separation

2. **Maintainable**
   - Centralized configuration logic
   - Easy to extend
   - Well documented

3. **Testable**
   - Can test configuration changes
   - Mock-friendly
   - Unit testable

---

## Migration

### From Old System

**If user has existing installation:**

1. Old config in `src/config.py` (bundled)
2. New system creates `bot_config.json`
3. Uses default values first time
4. User reconfigures once
5. Settings persist from then on

**No data loss:**
- Old trades still in MT5
- Old logs still available
- Just need to reconfigure once

---

## Troubleshooting

### Configuration Not Saving

**Symptoms:**
- Changes don't persist
- Settings revert to defaults

**Solutions:**

1. **Check File Permissions**
   ```
   - Right-click bot_config.json
   - Properties → Security
   - Ensure "Write" permission
   ```

2. **Check Disk Space**
   ```
   - Ensure sufficient disk space
   - At least 1MB free
   ```

3. **Check Antivirus**
   ```
   - Antivirus may block file writes
   - Add exception for executable directory
   ```

4. **Check File Location**
   ```
   - Should be in same directory as .exe
   - Not in Program Files (use Documents)
   ```

---

### Configuration File Missing

**Symptoms:**
- bot_config.json doesn't exist
- Settings reset every time

**Solutions:**

1. **Let It Create Automatically**
   ```
   - Delete bot_config.json if exists
   - Restart executable
   - Will create with defaults
   ```

2. **Restore from Backup**
   ```
   - Check config_backups/ folder
   - Copy latest backup
   - Rename to bot_config.json
   ```

3. **Create Manually**
   ```
   - Copy default config from docs
   - Save as bot_config.json
   - Place in executable directory
   ```

---

### Configuration Corrupted

**Symptoms:**
- Bot won't start
- Error loading configuration
- Invalid JSON error

**Solutions:**

1. **Restore from Backup**
   ```
   cd config_backups
   copy config_backup_[latest].json ..\bot_config.json
   ```

2. **Reset to Default**
   ```
   - Delete bot_config.json
   - Restart executable
   - Reconfigure settings
   ```

3. **Validate JSON**
   ```
   - Open bot_config.json in text editor
   - Check for syntax errors
   - Use JSON validator online
   ```

---

## Advanced Usage

### Manual Configuration Edit

**You can edit bot_config.json directly:**

1. Close the bot executable
2. Open `bot_config.json` in text editor
3. Make changes (be careful with JSON syntax)
4. Save file
5. Restart bot
6. Changes will be applied

**Example - Change Symbols:**
```json
{
    "symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
    ...
}
```

---

### Export/Import Configuration

**Export Configuration:**
```python
from src.config_manager import get_config_manager

manager = get_config_manager()
manager.export_config('my_config.json')
```

**Import Configuration:**
```python
manager.import_config('my_config.json')
```

**Use Cases:**
- Share configuration with team
- Backup before major changes
- Test different configurations
- Version control

---

### Configuration Profiles

**Create Multiple Profiles:**

```
GEM_Trading_Bot_Windows\
├── bot_config.json (current)
├── config_conservative.json
├── config_aggressive.json
└── config_scalping.json
```

**Switch Profiles:**
1. Copy desired profile to `bot_config.json`
2. Restart bot
3. New profile active

---

## Files Modified

1. **src/config_manager.py** (NEW)
   - Configuration manager class
   - External JSON file handling
   - Backup system
   - Validation logic

2. **web_dashboard.py**
   - Import config_manager
   - Use config_manager for saves
   - Remove old update_config_file function

3. **build_windows.bat**
   - Added pathlib hidden import
   - Added json hidden import

4. **.github/workflows/build-windows.yml**
   - No changes needed (uses build script)

---

## Testing

### Test Configuration Save

1. Run executable
2. Open dashboard
3. Change configuration
4. Click "Save Configuration"
5. Check `bot_config.json` exists
6. Check backup created
7. Restart executable
8. Verify settings persisted

### Test Backup System

1. Save configuration 5 times
2. Check `config_backups/` folder
3. Should have 5 backup files
4. Save 10 more times
5. Should have only 10 backups (oldest deleted)

### Test Recovery

1. Corrupt `bot_config.json`
2. Restart executable
3. Should show error
4. Restore from backup
5. Should work again

---

## Summary

**Problem:** Configuration couldn't be saved in executable

**Root Cause:** Bundled files are read-only

**Solution:** External JSON configuration file

**Implementation:**
1. ✅ Created ConfigManager class
2. ✅ External bot_config.json file
3. ✅ Automatic backup system
4. ✅ Updated web dashboard
5. ✅ Updated build script

**Result:**
- Configuration saves successfully ✅
- Settings persist between sessions ✅
- Automatic backups created ✅
- Works in both script and executable modes ✅
- User-friendly and transparent ✅

**Status:** ✅ Fixed and tested

---

**Configuration now saves correctly in executable deployments!** 🎉✅
