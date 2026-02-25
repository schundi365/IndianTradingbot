# Monitor Tab 404 Error Fix

## Problem
When connected to Paper Trading and viewing the Monitor tab, getting:
```
GET http://127.0.0.1:8080/api/bot/account 404 (NOT FOUND)
Error: Account information not available
```

## Investigation Results

✅ **Endpoint exists**: `/api/bot/account` in `indian_dashboard/api/bot.py`  
✅ **Controller method exists**: `get_account_info()` in `bot_controller.py`  
✅ **Adapter method exists**: `get_account_info()` in `paper_trading_adapter.py`  

## Root Cause

The 404 error with "Account information not available" suggests the endpoint is returning 404 status when `account_info` is None.

Looking at `indian_dashboard/api/bot.py` line 210-218:
```python
if account_info:
    return jsonify({'success': True, 'account': account_info}), 200
else:
    return jsonify({'success': False, 'error': 'Account information not available'}), 404
```

The issue is likely:
1. Bot is not started (bot_controller.broker_adapter is None)
2. Broker adapter is not connected
3. Paper Trading engine not initialized

## Solution

The Monitor tab should work even when the bot is NOT running, as long as the broker is connected. The issue is that `bot_controller.get_account_info()` checks if the bot is running, but it should check the broker_manager instead.

### Fix Required

Modify `indian_dashboard/api/bot.py` to get account info directly from broker_manager when bot is not running:

```python
@bot_bp.route('/account', methods=['GET'])
def get_account_info():
    """Get account information"""
    try:
        # Try to get from bot controller first (if bot is running)
        account_info = bot_bp.bot_controller.get_account_info()
        
        # If bot not running, get directly from broker
        if not account_info and bot_bp.broker_manager.is_connected():
            adapter = bot_bp.broker_manager.get_adapter()
            if adapter and hasattr(adapter, 'get_account_info'):
                account_info = adapter.get_account_info()
        
        if account_info:
            return jsonify({'success': True, 'account': account_info}), 200
        else:
            return jsonify({'success': False, 'error': 'Account information not available'}), 404
            
    except Exception as e:
        logger.error(f"Error getting account info: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
```

This allows the Monitor tab to show account info even when the bot is not actively trading.

## Testing

After applying the fix:
1. Connect to Paper Trading
2. Go to Monitor tab
3. Should see account balance, equity, margin info
4. No 404 errors in console

## Files to Modify

1. `indian_dashboard/api/bot.py` - Update `/account` endpoint
2. Similar fix may be needed for `/positions` endpoint
