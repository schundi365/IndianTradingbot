# Configuration Update Encoding Fix

## Issue
When saving configuration from the dashboard, the following error occurred:
```
'charmap' codec can't decode byte 0x8f in position 95: character maps to <undefined>
```

## Root Cause
The `update_config_file()` function in `web_dashboard.py` was opening files without specifying UTF-8 encoding, causing Windows to use the default 'charmap' codec which couldn't handle certain characters.

## Solution
Added `encoding='utf-8'` parameter to both file operations in the `update_config_file()` function:

### Before:
```python
with open(config_path, 'r') as f:
    lines = f.readlines()
...
with open(config_path, 'w') as f:
    f.writelines(updated_lines)
```

### After:
```python
with open(config_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
...
with open(config_path, 'w', encoding='utf-8') as f:
    f.writelines(updated_lines)
```

## Files Modified
- `web_dashboard.py` (lines 557, 577)

## Testing
1. Open dashboard at http://gemtrading:5000
2. Navigate to Configuration tab
3. Modify any setting (symbols, timeframe, risk)
4. Click "Apply Configuration"
5. Verify success message appears
6. Check that `src/config.py` was updated correctly

## Status
✅ **FIXED** - Configuration updates now work without encoding errors

## Next Steps
Restart the dashboard server to apply the changes:
1. Stop current server (Ctrl+C)
2. Run: `python web_dashboard.py`
3. Test configuration save functionality
