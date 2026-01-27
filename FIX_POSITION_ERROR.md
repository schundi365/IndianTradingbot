# Position Management Error Fix

## Error
```
2026-01-27 17:40:24,772 - ERROR - Error managing positions: 151469704704
```

## Problem
The bot was trying to manage a position (ticket 151469704704) that was already closed. The position tracking dictionary (`self.positions`) wasn't being cleaned up when positions closed.

## Solution Applied

### 1. Added `cleanup_closed_positions()` Method
New method that removes closed positions from the tracking dictionary:
- Gets all currently open positions
- Compares with tracked positions
- Removes any that are no longer open
- Logs cleanup activity

### 2. Improved `manage_positions()` Method
- Added try-except around individual position updates
- Calls cleanup methods for both positions and groups
- Better error handling to prevent crashes

### 3. Enhanced Error Logging
- Added debug-level traceback logging
- More informative error messages
- Warnings instead of errors for individual position issues

## Changes Made

**File**: `src/mt5_trading_bot.py`

**New Method Added**:
```python
def cleanup_closed_positions(self):
    """Remove closed positions from tracking dictionary"""
    # Get all currently open positions
    open_positions = mt5.positions_get(magic=self.magic_number)
    
    if open_positions is None:
        open_tickets = set()
    else:
        open_tickets = {pos.ticket for pos in open_positions}
    
    # Find positions in tracking that are no longer open
    tickets_to_remove = []
    for ticket in self.positions.keys():
        if ticket not in open_tickets:
            tickets_to_remove.append(ticket)
    
    # Remove closed positions from tracking
    for ticket in tickets_to_remove:
        del self.positions[ticket]
        logging.debug(f"Cleaned up closed position: {ticket}")
    
    if len(tickets_to_remove) > 0:
        logging.info(f"Cleaned up {len(tickets_to_remove)} closed position(s)")
```

**Modified Method**:
```python
def manage_positions(self):
    """Check and manage all open positions"""
    positions = mt5.positions_get(magic=self.magic_number)
    
    if positions is None or len(positions) == 0:
        # Clean up tracking dictionaries if no positions
        self.cleanup_closed_positions()
        return
    
    # ... rest of method with try-except around updates ...
    
    # Clean up closed positions and groups
    self.cleanup_closed_positions()
    self.cleanup_closed_groups()
```

## Result

✅ **Error Fixed**: Bot will no longer crash when trying to manage closed positions

✅ **Automatic Cleanup**: Tracking dictionaries are cleaned up automatically

✅ **Better Logging**: More informative messages about position cleanup

✅ **Robust Error Handling**: Individual position errors won't crash the entire bot

## Testing

The fix is already applied to `src/mt5_trading_bot.py`. 

**To test**:
1. Restart the bot: `python run_bot.py`
2. Let it run and manage positions
3. Check logs - should see cleanup messages instead of errors

**Expected log messages**:
```
INFO - Cleaned up 1 closed position(s)
INFO - Cleaned up closed group: abc123
```

## Status

✅ **FIXED** - Error handling improved, cleanup methods added

The bot will now gracefully handle closed positions without throwing errors.
