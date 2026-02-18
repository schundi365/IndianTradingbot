"""
Analyze Losing Trades to Find Improvement Opportunities
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def analyze_losing_trades(days=7):
    """Analyze losing trades from the last N days"""
    
    if not mt5.initialize():
        print("Failed to initialize MT5")
        return
    
    # Get account info
    account_info = mt5.account_info()
    print("=" * 80)
    print("LOSING TRADES ANALYSIS")
    print("=" * 80)
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print(f"Equity: ${account_info.equity:.2f}")
    print()
    
    # Get deals from last N days
    from_date = datetime.now() - timedelta(days=days)
    deals = mt5.history_deals_get(from_date, datetime.now())
    
    if deals is None or len(deals) == 0:
        print("No deals found")
        mt5.shutdown()
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    
    # Filter only closed positions (entry + exit)
    df = df[df['entry'].isin([mt5.DEAL_ENTRY_IN, mt5.DEAL_ENTRY_OUT])]
    
    # Group by position_id to match entry/exit
    positions = {}
    for _, deal in df.iterrows():
        pos_id = deal['position_id']
        if pos_id not in positions:
            positions[pos_id] = {'entry': None, 'exit': None}
        
        if deal['entry'] == mt5.DEAL_ENTRY_IN:
            positions[pos_id]['entry'] = deal
        elif deal['entry'] == mt5.DEAL_ENTRY_OUT:
            positions[pos_id]['exit'] = deal
    
    # Analyze completed positions
    losing_trades = []
    winning_trades = []
    
    for pos_id, pos in positions.items():
        if pos['entry'] is not None and pos['exit'] is not None:
            entry = pos['entry']
            exit_deal = pos['exit']
            
            # Calculate profit
            profit = exit_deal['profit']
            
            # Get trade details
            trade = {
                'position_id': pos_id,
                'symbol': entry['symbol'],
                'type': 'BUY' if entry['type'] == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': entry['volume'],
                'entry_price': entry['price'],
                'exit_price': exit_deal['price'],
                'entry_time': datetime.fromtimestamp(entry['time']),
                'exit_time': datetime.fromtimestamp(exit_deal['time']),
                'profit': profit,
                'commission': entry['commission'] + exit_deal['commission'],
                'swap': entry['swap'] + exit_deal['swap'],
            }
            
            # Calculate duration
            trade['duration_minutes'] = (trade['exit_time'] - trade['entry_time']).total_seconds() / 60
            
            # Calculate pips
            if trade['type'] == 'BUY':
                trade['pips'] = (trade['exit_price'] - trade['entry_price']) / 0.01
            else:
                trade['pips'] = (trade['entry_price'] - trade['exit_price']) / 0.01
            
            if profit < 0:
                losing_trades.append(trade)
            else:
                winning_trades.append(trade)
    
    # Analysis
    print(f"Analysis Period: Last {days} days")
    print(f"Total Closed Trades: {len(losing_trades) + len(winning_trades)}")
    print(f"Winning Trades: {len(winning_trades)}")
    print(f"Losing Trades: {len(losing_trades)}")
    print()
    
    if len(losing_trades) == 0:
        print("No losing trades found!")
        mt5.shutdown()
        return
    
    # Convert to DataFrame for analysis
    losses_df = pd.DataFrame(losing_trades)
    
    print("=" * 80)
    print("LOSING TRADES BREAKDOWN")
    print("=" * 80)
    print()
    
    # 1. Total Loss
    total_loss = losses_df['profit'].sum()
    avg_loss = losses_df['profit'].mean()
    max_loss = losses_df['profit'].min()
    
    print(f"Total Loss: ${total_loss:.2f}")
    print(f"Average Loss: ${avg_loss:.2f}")
    print(f"Largest Loss: ${max_loss:.2f}")
    print()
    
    # 2. Loss by Symbol
    print("=" * 80)
    print("LOSSES BY SYMBOL")
    print("=" * 80)
    symbol_losses = losses_df.groupby('symbol').agg({
        'profit': ['count', 'sum', 'mean'],
        'pips': 'mean',
        'duration_minutes': 'mean'
    }).round(2)
    print(symbol_losses)
    print()
    
    # 3. Loss by Direction
    print("=" * 80)
    print("LOSSES BY DIRECTION")
    print("=" * 80)
    direction_losses = losses_df.groupby('type').agg({
        'profit': ['count', 'sum', 'mean'],
        'pips': 'mean',
        'duration_minutes': 'mean'
    }).round(2)
    print(direction_losses)
    print()
    
    # 4. Duration Analysis
    print("=" * 80)
    print("DURATION ANALYSIS")
    print("=" * 80)
    print(f"Average Hold Time: {losses_df['duration_minutes'].mean():.1f} minutes")
    print(f"Shortest Loss: {losses_df['duration_minutes'].min():.1f} minutes")
    print(f"Longest Loss: {losses_df['duration_minutes'].max():.1f} minutes")
    print()
    
    # Quick losses (< 5 minutes) - likely stop loss hits
    quick_losses = losses_df[losses_df['duration_minutes'] < 5]
    if len(quick_losses) > 0:
        print(f"Quick Losses (< 5 min): {len(quick_losses)} trades")
        print(f"  Total: ${quick_losses['profit'].sum():.2f}")
        print(f"  Average: ${quick_losses['profit'].mean():.2f}")
        print()
    
    # Long losses (> 20 minutes) - held too long
    long_losses = losses_df[losses_df['duration_minutes'] > 20]
    if len(long_losses) > 0:
        print(f"Long Losses (> 20 min): {len(long_losses)} trades")
        print(f"  Total: ${long_losses['profit'].sum():.2f}")
        print(f"  Average: ${long_losses['profit'].mean():.2f}")
        print()
    
    # 5. Pips Analysis
    print("=" * 80)
    print("PIPS ANALYSIS")
    print("=" * 80)
    print(f"Average Loss: {losses_df['pips'].mean():.1f} pips")
    print(f"Smallest Loss: {losses_df['pips'].min():.1f} pips")
    print(f"Largest Loss: {losses_df['pips'].max():.1f} pips")
    print()
    
    # 6. Time of Day Analysis
    print("=" * 80)
    print("TIME OF DAY ANALYSIS")
    print("=" * 80)
    losses_df['hour'] = losses_df['entry_time'].dt.hour
    hourly_losses = losses_df.groupby('hour').agg({
        'profit': ['count', 'sum', 'mean']
    }).round(2)
    print("Losses by Hour:")
    print(hourly_losses)
    print()
    
    # 7. Detailed Trade List
    print("=" * 80)
    print("TOP 10 LARGEST LOSSES")
    print("=" * 80)
    top_losses = losses_df.nlargest(10, 'profit', keep='first')[
        ['symbol', 'type', 'entry_time', 'pips', 'duration_minutes', 'profit']
    ]
    print(top_losses.to_string(index=False))
    print()
    
    # 8. Pattern Detection
    print("=" * 80)
    print("PATTERN DETECTION")
    print("=" * 80)
    
    # Check if losses are concentrated
    worst_symbol = losses_df.groupby('symbol')['profit'].sum().idxmin()
    worst_symbol_loss = losses_df.groupby('symbol')['profit'].sum().min()
    worst_symbol_pct = (worst_symbol_loss / total_loss) * 100
    
    print(f"Worst Symbol: {worst_symbol}")
    print(f"  Loss: ${worst_symbol_loss:.2f} ({worst_symbol_pct:.1f}% of total)")
    print()
    
    worst_direction = losses_df.groupby('type')['profit'].sum().idxmin()
    worst_direction_loss = losses_df.groupby('type')['profit'].sum().min()
    worst_direction_pct = (worst_direction_loss / total_loss) * 100
    
    print(f"Worst Direction: {worst_direction}")
    print(f"  Loss: ${worst_direction_loss:.2f} ({worst_direction_pct:.1f}% of total)")
    print()
    
    # 9. Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    # Check stop loss size
    avg_loss_pips = abs(losses_df['pips'].mean())
    if avg_loss_pips > 30:
        recommendations.append(f"⚠️  Stop losses too wide ({avg_loss_pips:.1f} pips avg)")
        recommendations.append(f"   → Reduce ATR_MULTIPLIER_SL from 1.2 to 1.0")
    elif avg_loss_pips < 10:
        recommendations.append(f"⚠️  Stop losses too tight ({avg_loss_pips:.1f} pips avg)")
        recommendations.append(f"   → Increase ATR_MULTIPLIER_SL from 1.2 to 1.5")
    
    # Check hold time
    avg_hold = losses_df['duration_minutes'].mean()
    if avg_hold > 25:
        recommendations.append(f"⚠️  Holding losers too long ({avg_hold:.1f} min avg)")
        recommendations.append(f"   → Enable scalping time exit (SCALP_MAX_HOLD_MINUTES = 20)")
    
    # Check quick losses
    quick_loss_pct = (len(quick_losses) / len(losses_df)) * 100
    if quick_loss_pct > 50:
        recommendations.append(f"⚠️  Too many quick losses ({quick_loss_pct:.1f}%)")
        recommendations.append(f"   → Stop losses being hit too fast")
        recommendations.append(f"   → Consider wider stops or better entry timing")
    
    # Check symbol concentration
    if worst_symbol_pct > 60:
        recommendations.append(f"⚠️  Losses concentrated in {worst_symbol} ({worst_symbol_pct:.1f}%)")
        recommendations.append(f"   → Consider removing {worst_symbol} from trading")
        recommendations.append(f"   → Or reduce position size for {worst_symbol}")
    
    # Check direction bias
    if worst_direction_pct > 70:
        recommendations.append(f"⚠️  Losses concentrated in {worst_direction} trades ({worst_direction_pct:.1f}%)")
        recommendations.append(f"   → Market may be trending opposite direction")
        recommendations.append(f"   → Check trend filter settings")
    
    # Check time of day
    worst_hour = losses_df.groupby('hour')['profit'].sum().idxmin()
    worst_hour_loss = losses_df.groupby('hour')['profit'].sum().min()
    worst_hour_pct = (worst_hour_loss / total_loss) * 100
    
    if worst_hour_pct > 40:
        recommendations.append(f"⚠️  Losses concentrated at {worst_hour}:00 hour ({worst_hour_pct:.1f}%)")
        recommendations.append(f"   → Avoid trading during this hour")
        recommendations.append(f"   → Enable ENABLE_TRADING_HOURS and exclude {worst_hour}:00")
    
    if len(recommendations) == 0:
        print("✅ No major issues detected")
        print("   Losses appear normal for M1 scalping")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    print()
    print("=" * 80)
    
    mt5.shutdown()


if __name__ == "__main__":
    print("\nAnalyzing losing trades...")
    print("This will help identify patterns and improvement opportunities\n")
    
    # Analyze last 7 days
    analyze_losing_trades(days=7)
    
    print("\nAnalysis complete!")
    print("Review recommendations above to improve performance")
