"""
Analyze Trading Bot Performance
Pulls actual trade history from MT5 and provides detailed analysis
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import sys

def analyze_trades():
    """Analyze all trades from the bot"""
    
    print("=" * 80)
    print("TRADING BOT PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"❌ Failed to initialize MT5: {mt5.last_error()}")
        return
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"Account Balance: ${account_info.balance:,.2f}")
        print(f"Account Equity: ${account_info.equity:,.2f}")
        print(f"Profit/Loss: ${account_info.profit:,.2f}")
        print(f"Margin Used: ${account_info.margin:,.2f}")
        print(f"Free Margin: ${account_info.margin_free:,.2f}")
        print()
    
    # Get deals from last 7 days
    from_date = datetime.now() - timedelta(days=7)
    to_date = datetime.now()
    
    deals = mt5.history_deals_get(from_date, to_date)
    
    if deals is None or len(deals) == 0:
        print("No trades found in the last 7 days")
        mt5.shutdown()
        return
    
    print(f"Found {len(deals)} deals in the last 7 days")
    print()
    
    # Convert to DataFrame
    df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Filter only bot trades (magic number 234000)
    bot_deals = df[df['magic'] == 234000].copy()
    
    if len(bot_deals) == 0:
        print("No bot trades found (Magic Number: 234000)")
        print()
        print("All deals:")
        print(df[['time', 'symbol', 'type', 'volume', 'price', 'profit', 'comment']])
        mt5.shutdown()
        return
    
    print(f"Bot Trades (Magic: 234000): {len(bot_deals)}")
    print()
    
    # Analyze by symbol
    print("=" * 80)
    print("TRADES BY SYMBOL")
    print("=" * 80)
    
    for symbol in bot_deals['symbol'].unique():
        symbol_deals = bot_deals[bot_deals['symbol'] == symbol]
        
        print(f"\n{symbol}:")
        print("-" * 80)
        print(f"  Total Deals: {len(symbol_deals)}")
        print(f"  Total Volume: {symbol_deals['volume'].sum():.2f} lots")
        print(f"  Total Profit/Loss: ${symbol_deals['profit'].sum():,.2f}")
        print(f"  Average P/L per deal: ${symbol_deals['profit'].mean():,.2f}")
        
        # Entry vs Exit
        entries = symbol_deals[symbol_deals['entry'] == 0]  # Entry deals
        exits = symbol_deals[symbol_deals['entry'] == 1]    # Exit deals
        
        print(f"  Entries: {len(entries)}")
        print(f"  Exits: {len(exits)}")
        
        # Show individual deals
        print(f"\n  Deal Details:")
        for _, deal in symbol_deals.iterrows():
            deal_type = "BUY" if deal['type'] == 0 else "SELL"
            entry_type = "ENTRY" if deal['entry'] == 0 else "EXIT"
            print(f"    {deal['time']} | {entry_type:5} | {deal_type:4} | "
                  f"{deal['volume']:.2f} lots @ {deal['price']:.2f} | "
                  f"P/L: ${deal['profit']:,.2f} | {deal['comment']}")
    
    # Overall statistics
    print()
    print("=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)
    print(f"Total Deals: {len(bot_deals)}")
    print(f"Total Volume Traded: {bot_deals['volume'].sum():.2f} lots")
    print(f"Total Profit/Loss: ${bot_deals['profit'].sum():,.2f}")
    print(f"Average P/L per deal: ${bot_deals['profit'].mean():,.2f}")
    
    # Winning vs Losing
    winning = bot_deals[bot_deals['profit'] > 0]
    losing = bot_deals[bot_deals['profit'] < 0]
    breakeven = bot_deals[bot_deals['profit'] == 0]
    
    print()
    print(f"Winning Deals: {len(winning)} (${winning['profit'].sum():,.2f})")
    print(f"Losing Deals: {len(losing)} (${losing['profit'].sum():,.2f})")
    print(f"Breakeven Deals: {len(breakeven)}")
    
    if len(winning) + len(losing) > 0:
        win_rate = len(winning) / (len(winning) + len(losing)) * 100
        print(f"Win Rate: {win_rate:.1f}%")
    
    # Get current open positions
    print()
    print("=" * 80)
    print("CURRENT OPEN POSITIONS")
    print("=" * 80)
    
    positions = mt5.positions_get(magic=234000)
    
    if positions is None or len(positions) == 0:
        print("No open positions")
    else:
        print(f"Open Positions: {len(positions)}")
        print()
        
        for pos in positions:
            pos_type = "BUY" if pos.type == 0 else "SELL"
            print(f"  {pos.symbol} | {pos_type} | {pos.volume:.2f} lots")
            print(f"    Entry: {pos.price_open:.2f}")
            print(f"    Current: {pos.price_current:.2f}")
            print(f"    SL: {pos.sl:.2f} | TP: {pos.tp:.2f}")
            print(f"    Profit: ${pos.profit:,.2f}")
            print(f"    Comment: {pos.comment}")
            print()
    
    # Analysis and recommendations
    print("=" * 80)
    print("ANALYSIS & RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    total_profit = bot_deals['profit'].sum()
    
    if total_profit < 0:
        print("⚠️  OVERALL LOSS DETECTED")
        print()
        print("Potential Issues:")
        print("  1. M1 timeframe is EXTREMELY noisy - too many false signals")
        print("  2. Spread costs are eating into profits (M1 = many trades)")
        print("  3. Stop losses may be too tight (getting stopped out early)")
        print("  4. Market conditions may not suit the strategy")
        print()
        print("Recommendations:")
        print("  ✓ Switch to M5 or M15 timeframe (fewer, better quality signals)")
        print("  ✓ Increase ATR multiplier for SL (1.2 → 1.5 or 2.0)")
        print("  ✓ Increase minimum trade confidence (50% → 60%)")
        print("  ✓ Add time-of-day filter (avoid low liquidity hours)")
        print("  ✓ Consider trading only during major market sessions")
        print("  ✓ Reduce position size to minimize losses while testing")
    elif total_profit > 0:
        print("✅ OVERALL PROFIT!")
        print()
        print("Good signs, but consider:")
        print("  ✓ Track performance over longer period (1+ weeks)")
        print("  ✓ Monitor win rate (should be >50% ideally)")
        print("  ✓ Watch for drawdown periods")
        print("  ✓ Consider increasing position size gradually")
    else:
        print("⚠️  BREAKEVEN")
        print()
        print("Recommendations:")
        print("  ✓ Need more data to assess strategy effectiveness")
        print("  ✓ Continue monitoring for at least 50+ trades")
        print("  ✓ Consider adjusting parameters if no clear edge emerges")
    
    print()
    print("=" * 80)
    
    # Save to CSV
    bot_deals.to_csv('trade_history.csv', index=False)
    print()
    print("✅ Trade history saved to: trade_history.csv")
    
    mt5.shutdown()


if __name__ == "__main__":
    try:
        analyze_trades()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
