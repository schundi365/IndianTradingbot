"""
Diagnostic script to investigate the drawdown calculation issue
"""

import MetaTrader5 as mt5
from datetime import datetime

def diagnose_drawdown():
    """Check current account status and identify the issue"""
    
    print("=" * 80)
    print("DRAWDOWN ISSUE DIAGNOSTIC")
    print("=" * 80)
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return
    
    try:
        # Get account info
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ Failed to get account info")
            return
        
        print("\n📊 CURRENT ACCOUNT STATUS:")
        print(f"   Balance: ${account_info.balance:.2f}")
        print(f"   Equity: ${account_info.equity:.2f}")
        print(f"   Margin: ${account_info.margin:.2f}")
        print(f"   Free Margin: ${account_info.margin_free:.2f}")
        print(f"   Profit: ${account_info.profit:.2f}")
        
        # Check open positions
        positions = mt5.positions_get()
        print(f"\n📈 OPEN POSITIONS: {len(positions) if positions else 0}")
        
        if positions:
            total_unrealized = 0
            for pos in positions:
                print(f"   {pos.symbol}: {pos.type_str} | Volume: {pos.volume} | Profit: ${pos.profit:.2f}")
                total_unrealized += pos.profit
            print(f"   Total Unrealized P&L: ${total_unrealized:.2f}")
        
        # Get today's deals (closed trades)
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        deals = mt5.history_deals_get(from_date, datetime.now())
        
        print(f"\n💰 TODAY'S CLOSED TRADES: {len(deals) if deals else 0}")
        
        if deals:
            total_realized_today = 0
            for deal in deals:
                if deal.entry == 1:  # Entry (OUT) deals show profit
                    total_realized_today += deal.profit
                    if deal.profit != 0:
                        print(f"   {deal.symbol}: ${deal.profit:.2f} at {datetime.fromtimestamp(deal.time)}")
            print(f"   Total Realized P&L Today: ${total_realized_today:.2f}")
        
        # Calculate what the peak should be
        print("\n" + "=" * 80)
        print("ANALYSIS:")
        print("=" * 80)
        
        reported_peak = 99911.93
        current_balance = account_info.balance
        reported_drawdown = reported_peak - current_balance
        
        print(f"\n❌ REPORTED ISSUE:")
        print(f"   Peak Balance: ${reported_peak:.2f}")
        print(f"   Current Balance: ${current_balance:.2f}")
        print(f"   Reported Drawdown: ${reported_drawdown:.2f} ({reported_drawdown/reported_peak*100:.2f}%)")
        
        print(f"\n🔍 LIKELY CAUSE:")
        
        # Check if peak was set from equity instead of balance
        if account_info.equity > account_info.balance:
            print(f"   ⚠️  Current equity (${account_info.equity:.2f}) > balance (${account_info.balance:.2f})")
            print(f"   ⚠️  Unrealized profit: ${account_info.profit:.2f}")
            print(f"   ⚠️  Peak may have been set when there were large unrealized profits")
        
        # Check if there was a large loss today
        if deals:
            if total_realized_today < -1000:
                print(f"   ⚠️  Large realized loss today: ${total_realized_today:.2f}")
                print(f"   ⚠️  This would explain the balance drop")
            else:
                print(f"   ✅ No large realized losses today (${total_realized_today:.2f})")
                print(f"   ❌ The peak balance of ${reported_peak:.2f} seems incorrect!")
                print(f"   ❌ Current balance ${current_balance:.2f} suggests peak was set incorrectly")
        
        # Suggest solution
        print("\n" + "=" * 80)
        print("RECOMMENDED SOLUTION:")
        print("=" * 80)
        
        print(f"""
The peak balance of ${reported_peak:.2f} appears to be incorrect.

OPTION 1: Reset Peak Balance to Current Balance
   - This will reset the drawdown tracking to start fresh
   - Add this to your bot initialization or config:
     self.peak_balance = account_info.balance
     self.peak_balance_date = datetime.now()

OPTION 2: Persist Peak Balance Across Restarts
   - Save peak_balance to a file or database
   - Load it when the bot starts
   - This prevents losing peak tracking on restart

OPTION 3: Use Daily Peak Reset
   - Reset peak balance at the start of each trading day
   - This prevents accumulation of incorrect peaks

IMMEDIATE FIX:
   1. Stop the bot
   2. Check your actual account history in MT5
   3. Verify if you actually had $99,911 balance at 13:02 today
   4. If not, the peak was set incorrectly (likely from equity with unrealized profits)
   5. Restart the bot - it will reset peak to current balance
""")
        
        # Check if we can find when the peak was set
        print("\n" + "=" * 80)
        print("CHECKING RECENT HISTORY:")
        print("=" * 80)
        
        # Get deals from the last hour
        from_time = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
        recent_deals = mt5.history_deals_get(from_time, datetime.now())
        
        if recent_deals:
            print(f"\nDeals since 13:00 today:")
            for deal in recent_deals:
                deal_time = datetime.fromtimestamp(deal.time)
                deal_type = "BUY" if deal.type == 0 else "SELL" if deal.type == 1 else "BALANCE"
                print(f"   {deal_time.strftime('%H:%M:%S')} - {deal.symbol}: "
                      f"{deal_type} | Volume: {deal.volume} | Profit: ${deal.profit:.2f}")
        
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    diagnose_drawdown()
