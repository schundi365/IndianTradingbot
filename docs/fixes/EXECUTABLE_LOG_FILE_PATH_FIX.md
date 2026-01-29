# Executable Log File Path Fix

**Date**: January 29, 2026  
**Issue**: Log file not found when running as executable  
**Status**: ✅ FIXED

---

## Problem

When running the bot as an executable, the dashboard was showing an error:

```json
{
  "message": "[WinError 2] The system cannot find the file specified: 
  'C:\\Users\\...\\AppData\\Local\\Temp\\_MEI49802\\trading_bot.log'",
  "status": "error"
}
```

### Root Cause

The log file path was hardcoded as `'trading_bot.log'`, which works fine when running as a Python script (uses current directory), but fails when running as a PyInstaller executable because:

1. PyInstaller extracts files to a temporary directory (`_MEI*`)
2. The temp directory is read-only and gets deleted
3. The bot can't create log files in the temp directory
4. The log file needs to be in the executable's directory, not the temp directory

---

## Solution

Updated both `web_dashboard.py` and `src/mt5_trading_bot.py` to dynamically determine the correct base directory and log file path:

### Changes Made

#### 1. web_dashboard.py

**Before**:
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
```

**After**:
```python
import logging
import sys
from pathlib import Path

# Determine base directory (works for both script and executable)
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Ensure logs directory exists
LOG_FILE = BASE_DIR / 'trading_bot.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

Also updated log reading functions to use `LOG_FILE` instead of hardcoded string.

#### 2. src/mt5_trading_bot.py

**Before**:
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
```

**After**:
```python
import logging
import sys
from pathlib import Path

# Determine base directory (works for both script and executable)
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent.parent

# Log file path
LOG_FILE = BASE_DIR / 'trading_bot.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

---

## How It Works

### Detection Logic

```python
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
```

- `sys.frozen` is set by PyInstaller when running as executable
- If frozen: Use the directory where the .exe is located
- If not frozen: Use the script's directory

### Log File Location

**When running as script**:
```
C:\path\to\project\trading_bot.log
```

**When running as executable**:
```
C:\path\to\GEM_Trading_Bot.exe
C:\path\to\trading_bot.log  ← Log file here
```

The log file is created in the same directory as the executable, where the user has write permissions.

---

## Benefits

1. **Works in both modes** - Script and executable
2. **Persistent logs** - Not in temp directory
3. **User accessible** - In executable's directory
4. **No permissions issues** - User's directory has write access
5. **UTF-8 encoding** - Proper character support

---

## Testing

### Test as Script

```cmd
python web_dashboard.py
```

Log file should be created at: `project_root/trading_bot.log`

### Test as Executable

```cmd
cd dist
GEM_Trading_Bot.exe
```

Log file should be created at: `dist/trading_bot.log`

### Verify in Dashboard

1. Open dashboard: http://localhost:5000
2. Go to System Logs tab
3. Should see logs without errors
4. Click "Download Logs" - should download successfully

---

## Files Modified

- ✅ `web_dashboard.py` - Dynamic log file path
- ✅ `src/mt5_trading_bot.py` - Dynamic log file path

---

## Related Issues

This fix is part of the executable deployment fixes:

1. ✅ MT5 Build 5549 Compatibility
2. ✅ Configuration Not Applied
3. ✅ Bot Process Not Stopping
4. ✅ TensorBoard Build Error
5. ✅ Log File Path (this fix)

---

## Rebuild Required

After this fix, you need to rebuild the executable:

```cmd
rmdir /s /q build
rmdir /s /q dist
del GEM_Trading_Bot.spec
build_windows.bat
```

---

## Verification Checklist

After rebuilding:

- [ ] Executable starts without errors
- [ ] Dashboard loads at http://localhost:5000
- [ ] System Logs tab shows logs
- [ ] No "file not found" errors
- [ ] Log file exists in executable's directory
- [ ] Download logs button works
- [ ] Logs persist after restart

---

**Status**: Ready for rebuild and testing
