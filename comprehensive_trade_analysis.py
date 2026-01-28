"""
Comprehensive Trade Analysis - What Could Have Been Done Better
Analyzes all trades and provides specific recommendations
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def comprehensive_analysis(days=7):
    """Deep analysis of all trades with specific recommendations"""
    
    if not mt5.initialize():
        print("Failed to initialize MT5")
        return
    
    # Get account info
    account_info = mt5.account_info()
    print("=" * 80)
    print("COMPREHENSIVE TRADE ANALYSIS")
    print("=" * 80)
    print(f"Account: {account_info.login}")
    print(f"Current Balance: ${account_info.balance:.2f}")
    print(f"Current Equity: ${account_info.equity:.2f}")
    print()
    
    # Get all deals
    from_date = datetime.now() - timedelta(days=days)
    deals = mt5.history_deals_get(from_date, datetime.now())
    
    if deals is None or len(deals) == 0:
        print("No deals found")
        mt5.shutdown()
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    df = df[df['entry'].isin([mt5.DEAL_ENTRY_IN, mt5.DEAL_ENTRY_OUT])]
    
    # Match entry/exit pairs
    positions = {}
    for _, deal in df.iterrows():
        pos_id = deal['position_id']
        if pos_id not in positions:
            positions[pos_id] = {'entry': None, 'exit': None}
        
        if deal['entry'] == mt5.DEAL_ENTRY_IN:
            positions[pos_id]['entry'] = deal
        elif deal['entry'] == mt5.DEAL_ENTRY_OUT:
            positions[pos_id]['exit'] = deal
    
    # Analyze all trades
    all_trades = []
    for pos_id, pos in positions.items():
        if pos['entry'] is not None and pos['exit'] is not None:
            entry = pos['entry']
            exit_deal = pos['exit']
            
            trade = {
                'position_id': pos_id,
                'symbol': entry['symbol'],
                'type': 'BUY' if entry['type'] == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': entry['volume'],
                'entry_price': entry['price'],
                'exit_price': exit_deal['price'],
                'entry_time': datetime.fromtimestamp(entry['time']),
                'exit_time': datetime.fromtimestamp(exit_deal['time']),
                'profit': exit_deal['profit'],
                'commission': entry['commission'] + exit_deal['commission'],
                'swap': entry['swap'] + exit_deal['swap'],
            }
            
            trade['duration_minutes'] = (trade['exit_time'] - trade['entry_time']).total_seconds() / 60
            
            if trade['type'] == 'BUY':
                trade['pips'] = (trade['exit_price'] - trade['entry_price']) / 0.01
            else:
                trade['pips'] = (trade['entry_price'] - trade['exit_price']) / 0.01
            
            trade['result'] = 'WIN' if trade['profit'] > 0 else 'LOSS'
            all_trades.append(trade)
    
    if len(all_trades) == 0:
        print("No completed trades found")
        mt5.shutdown()
        return
    
    trades_df = pd.DataFrame(all_trades)
    
    # Overall Statistics
    print("=" * 80)
    print("OVERALL PERFORMANCE")
    print("=" * 80)
    total_trades = len(trades_df)
    wins = len(trades_df[trades_df['profit'] > 0])
    losses = len(trades_df[trades_df['profit'] < 0])
    win_rate = (wins / total_trades) * 100
    
    total_profit = trades_df['profit'].sum()
    avg_win = trades_df[trades_df['profit'] > 0]['profit'].mean() if wins > 0 else 0
    avg_loss = trades_df[trades_df['profit'] < 0]['profit'].mean() if losses > 0 else 0
    
    print(f"Total Trades: {total_trades}")
    print(f"Wins: {wins} ({win_rate:.1f}%)")
    print(f"Losses: {losses} ({100-win_rate:.1f}%)")
    print(f"Net Profit: ${total_profit:.2f}")
    print(f"Average Win: ${avg_win:.2f}")
    print(f"Average Loss: ${avg_loss:.2f}")
    print(f"Profit Factor: {abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "N/A")
    print()
    
    # Detailed Trade-by-Trade Analysis
    print("=" * 80)
    print("TRADE-BY-TRADE ANALYSIS WITH RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    recommendations = []
    
    for idx, trade in trades_df.iterrows():
        print(f"Trade #{idx + 1}: {trade['symbol']} {trade['type']}")
        print(f"  Entry: {trade['entry_time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Exit:  {trade['exit_time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Duration: {trade['duration_minutes']:.1f} minutes")
        print(f"  Pips: {trade['pips']:.1f}")
        print(f"  Profit: ${trade['profit']:.2f}")
        print(f"  Result: {trade['result']}")
        
        # Analyze what could have been better
        if trade['result'] == 'LOSS':
            print(f"  ANALYSIS:")
            
            # Check if stop was too wide
            if abs(trade['pips']) > 50:
                print(f"    - Stop loss TOO WIDE ({abs(trade['pips']):.0f} pips)")
                print(f"    - Should have been: 20-30 pips max")
                print(f"    - Potential savings: ${abs(trade['profit']) * 0.6:.2f}")
                recommendations.append({
                    'trade': idx + 1,
                    'issue': 'Stop too wide',
                    'current': f"{abs(trade['pips']):.0f} pips",
                    'should_be': '20-30 pips',
                    'savings': abs(trade['profit']) * 0.6
                })
            
            # Check if held too long
            if trade['duration_minutes'] > 30:
                print(f"    - Held TOO LONG ({trade['duration_minutes']:.0f} minutes)")
                print(f"    - Should have exited: After 20 minutes")
                print(f"    - Could have saved: ${abs(trade['profit']) * 0.4:.2f}")
                recommendations.append({
                    'trade': idx + 1,
                    'issue': 'Held too long',
                    'current': f"{trade['duration_minutes']:.0f} min",
                    'should_be': '20 min max',
                    'savings': abs(trade['profit']) * 0.4
                })
            
            # Check direction vs time
            hour = trade['entry_time'].hour
            if hour == 19:
                print(f"    - Traded at BAD TIME (19:00 hour)")
                print(f"    - Should have: Avoided this hour")
                print(f"    - This trade should NOT have been taken")
                recommendations.append({
                    'trade': idx + 1,
                    'issue': 'Bad timing',
                    'current': f"{hour}:00",
                    'should_be': 'Avoid 19:00',
                    'savings': abs(trade['profit'])
                })
        
        else:  # WIN
            print(f"  ANALYSIS:")
            
            # Check if could have made more
            if trade['duration_minutes'] < 10 and trade['pips'] < 30:
                print(f"    - Exited TOO EARLY ({trade['duration_minutes']:.0f} min, {trade['pips']:.0f} pips)")
                print(f"    - Could have held: 15-20 minutes")
                print(f"    - Potential extra profit: ${trade['profit'] * 0.5:.2f}")
                recommendations.append({
                    'trade': idx + 1,
                    'issue': 'Exited too early',
                    'current': f"{trade['pips']:.0f} pips",
                    'should_be': '40-50 pips',
                    'savings': -(trade['profit'] * 0.5)  # Negative = missed profit
                })
            
            # Check if trailing stop could have helped
            if trade['pips'] > 50:
                print(f"    - GOOD TRADE! Captured {trade['pips']:.0f} pips")
                print(f"    - Trailing stop worked well")
        
        print()
    
    # Summary of Recommendations
    print("=" * 80)
    print("SUMMARY OF IMPROVEMENTS")
    print("=" * 80)
    print()
    
    if len(recommendations) == 0:
        print("No major issues found! Trading strategy is working well.")
    else:
        total_potential_savings = sum([r['savings'] for r in recommendations if r['savings'] > 0])
        total_missed_profit = abs(sum([r['savings'] for r in recommendations if r['savings'] < 0]))
        
        print(f"Total Potential Savings: ${total_potential_savings:.2f}")
        print(f"Total Missed Profit: ${total_missed_profit:.2f}")
        print(f"Net Improvement Potential: ${total_potential_savings - total_missed_profit:.2f}")
        print()
        
        # Group by issue type
        issues = {}
        for rec in recommendations:
            issue = rec['issue']
            if issue not in issues:
                issues[issue] = {'count': 0, 'savings': 0}
            issues[issue]['count'] += 1
            issues[issue]['savings'] += rec['savings']
        
        print("Issues by Type:")
        for issue, data in sorted(issues.items(), key=lambda x: x[1]['savings'], reverse=True):
            if data['savings'] > 0:
                print(f"  {issue}: {data['count']} trades, ${data['savings']:.2f} potential savings")
            else:
                print(f"  {issue}: {data['count']} trades, ${abs(data['savings']):.2f} missed profit")
    
    print()
    
    # Specific Action Items
    print("=" * 80)
    print("ACTION ITEMS TO IMPLEMENT")
    print("=" * 80)
    print()
    
    action_items = []
    
    # Check stop loss issues
    wide_stops = [r for r in recommendations if r['issue'] == 'Stop too wide']
    if len(wide_stops) > 0:
        avg_savings = sum([r['savings'] for r in wide_stops]) / len(wide_stops)
        action_items.append({
            'priority': 1,
            'action': 'Tighten stop losses',
            'current': 'ATR_MULTIPLIER_SL = 1.2',
            'change_to': 'ATR_MULTIPLIER_SL = 0.8',
            'impact': f"${sum([r['savings'] for r in wide_stops]):.2f} savings"
        })
    
    # Check time issues
    time_issues = [r for r in recommendations if r['issue'] == 'Held too long']
    if len(time_issues) > 0:
        action_items.append({
            'priority': 2,
            'action': 'Cut losers faster',
            'current': 'SCALP_MAX_HOLD_MINUTES = 30',
            'change_to': 'SCALP_MAX_HOLD_MINUTES = 20',
            'impact': f"${sum([r['savings'] for r in time_issues]):.2f} savings"
        })
    
    # Check timing issues
    timing_issues = [r for r in recommendations if r['issue'] == 'Bad timing']
    if len(timing_issues) > 0:
        action_items.append({
            'priority': 1,
            'action': 'Avoid bad hours',
            'current': 'ENABLE_TRADING_HOURS = False',
            'change_to': 'ENABLE_TRADING_HOURS = True, END_HOUR = 19',
            'impact': f"${sum([r['savings'] for r in timing_issues]):.2f} savings"
        })
    
    # Check early exit issues
    early_exits = [r for r in recommendations if r['issue'] == 'Exited too early']
    if len(early_exits) > 0:
        action_items.append({
            'priority': 3,
            'action': 'Let winners run longer',
            'current': 'SCALP_MIN_PROFIT_PIPS = 20',
            'change_to': 'SCALP_MIN_PROFIT_PIPS = 30',
            'impact': f"${abs(sum([r['savings'] for r in early_exits])):.2f} extra profit"
        })
    
    if len(action_items) == 0:
        print("No action items needed - strategy is optimized!")
    else:
        for item in sorted(action_items, key=lambda x: x['priority']):
            print(f"Priority {item['priority']}: {item['action']}")
            print(f"  Current: {item['current']}")
            print(f"  Change to: {item['change_to']}")
            print(f"  Expected impact: {item['impact']}")
            print()
    
    # Final Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    if total_profit > 0:
        print(f"Current Performance: ${total_profit:.2f} profit ({win_rate:.1f}% win rate)")
    else:
        print(f"Current Performance: ${total_profit:.2f} loss ({win_rate:.1f}% win rate)")
    
    if len(recommendations) > 0:
        potential_improvement = total_potential_savings - total_missed_profit
        new_profit = total_profit + potential_improvement
        print(f"With Improvements: ${new_profit:.2f} profit (estimated)")
        print(f"Improvement: ${potential_improvement:.2f} ({(potential_improvement/abs(total_profit))*100:.1f}%)")
    
    print()
    print("=" * 80)
    
    mt5.shutdown()


if __name__ == "__main__":
    print("\nAnalyzing all trades with specific recommendations...")
    print("This will show exactly what could have been done better\n")
    
    comprehensive_analysis(days=7)
    
    print("\nAnalysis complete!")
    print("Review action items above to improve performance")
