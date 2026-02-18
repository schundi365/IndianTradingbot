"""
Check what trades caused the recent losses
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta

def check_losses():
    if not mt5.initialize():
        print("Failed to initialize MT5")
        return
    
    try:
        # Get deals from 13:42 onwards (when peak was set)
        from_time = datetime.now().replace(hour=13, minute=42, second=0)
        deals = mt5.history_deals_get(from_time, datetime.now())
        
        print("=" * 80)
        print("TRADES SINCE PEAK BALANCE (13:42)")
        print("=" * 80)
        
        if deals:
            total_profit = 0
            losing_trades = []
            winning_trades = []
            
            for deal in deals:
                if deal.entry == 1 and deal.profit != 0:  # Exit deals with P&L
                    deal_time = datetime.fromtimestamp(deal.time)
                    total_profit += deal.profit
                    
                    trade_info = {
                        'time': deal_time,
                        'symbol': deal.symbol,
                        'profit': deal.profit,
                        'volume': deal.volume
                    }
                    
                    if deal.profit < 0:
                        losing_trades.append(trade_info)
                    else:
                        winning_trades.append(trade_info)
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total Trades: {len(losing_trades) + len(winning_trades)}")
            print(f"   Winning Trades: {len(winning_trades)}")
            print(f"   Losing Trades: {len(losing_trades)}")
            print(f"   Net P&L: ${total_profit:.2f}")
            
            if losing_trades:
                print(f"\n❌ LOSING TRADES ({len(losing_trades)}):")
                losing_trades.sort(key=lambda x: x['profit'])
                for trade in losing_trades:
                    print(f"   {trade['time'].strftime('%H:%M:%S')} - {trade['symbol']}: "
                          f"${trade['profit']:.2f} (Vol: {trade['volume']})")
                
                total_loss = sum(t['profit'] for t in losing_trades)
                print(f"   Total Losses: ${total_loss:.2f}")
            
            if winning_trades:
                print(f"\n✅ WINNING TRADES ({len(winning_trades)}):")
                for trade in winning_trades[:5]:  # Show first 5
                    print(f"   {trade['time'].strftime('%H:%M:%S')} - {trade['symbol']}: "
                          f"${trade['profit']:.2f} (Vol: {trade['volume']})")
                
                if len(winning_trades) > 5:
                    print(f"   ... and {len(winning_trades) - 5} more")
                
                total_win = sum(t['profit'] for t in winning_trades)
                print(f"   Total Wins: ${total_win:.2f}")
            
            # Check account info
            account = mt5.account_info()
            print(f"\n📈 CURRENT ACCOUNT:")
            print(f"   Balance: ${account.balance:.2f}")
            print(f"   Equity: ${account.equity:.2f}")
            print(f"   Open Positions: {len(mt5.positions_get() or [])}")
            
            print(f"\n" + "=" * 80)
            print("ANALYSIS:")
            print("=" * 80)
            
            if total_profit < -300:
                print(f"\n⚠️  SIGNIFICANT LOSSES DETECTED!")
                print(f"   You lost ${abs(total_profit):.2f} since 13:42")
                print(f"   This is a REAL drawdown, not a false alarm")
                print(f"\n   The bot correctly paused trading to protect your account.")
                print(f"\n   RECOMMENDED ACTIONS:")
                print(f"   1. Review your trading strategy")
                print(f"   2. Check if market conditions changed")
                print(f"   3. Consider adjusting risk parameters")
                print(f"   4. Verify TP/SL settings are appropriate")
            else:
                print(f"\n   Net P&L since peak: ${total_profit:.2f}")
                print(f"   This doesn't match the reported $360 loss")
                print(f"   There may be other factors (swaps, commissions, etc.)")
        
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    check_losses()
