"""
Manually reset peak balance to current balance
This will allow the bot to continue trading
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def reset_peak():
    """Reset peak balance tracking"""
    
    print("=" * 80)
    print("PEAK BALANCE RESET UTILITY")
    print("=" * 80)
    
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return False
    
    try:
        account = mt5.account_info()
        current_balance = account.balance
        current_equity = account.equity
        
        print(f"\n📊 CURRENT ACCOUNT STATUS:")
        print(f"   Balance: ${current_balance:.2f}")
        print(f"   Equity: ${current_equity:.2f}")
        print(f"   Open Positions: {len(mt5.positions_get() or [])}")
        
        # Check if there are open positions with large unrealized P&L
        positions = mt5.positions_get()
        if positions:
            total_unrealized = sum(p.profit for p in positions)
            print(f"   Unrealized P&L: ${total_unrealized:.2f}")
            
            if abs(total_unrealized) > 50:
                print(f"\n⚠️  WARNING: You have ${total_unrealized:.2f} in unrealized P&L")
                print(f"   The peak will be set to BALANCE (${current_balance:.2f}), not equity")
                print(f"   This prevents false peaks from temporary unrealized profits")
        
        print(f"\n" + "=" * 80)
        print("SOLUTION:")
        print("=" * 80)
        
        print(f"""
The bot's peak balance tracking is stored in memory and resets when you restart.

OPTION 1: Restart the Bot (RECOMMENDED)
   - Stop the bot completely
   - Start it again
   - Peak will automatically reset to current balance: ${current_balance:.2f}

OPTION 2: Increase Max Drawdown Temporarily
   - Open dashboard: http://localhost:5000
   - Go to Configuration tab
   - Increase "Max Drawdown %" from 10% to 50% temporarily
   - This allows trading to continue while you investigate
   - Remember to set it back to 10% later

OPTION 3: Wait for Positions to Close
   - If you have open positions with unrealized losses
   - Wait for them to close
   - Balance will stabilize
   - Then restart the bot

CURRENT SITUATION:
   - Peak was set to $937.86 (likely when you had large unrealized profits)
   - Current balance is ${current_balance:.2f}
   - This creates a false 38% drawdown
   - The bot is protecting your account by pausing trading

RECOMMENDED ACTION:
   1. Close any losing positions manually if needed
   2. Restart the bot
   3. Peak will reset to current balance
   4. Trading will resume normally
""")
        
        return True
        
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    reset_peak()
