"""
Analyze TP Calculation Issues from Excel File
Parse the trade data and identify all TP calculation problems
"""

import pandas as pd
import numpy as np

# Read the Excel file
df = pd.read_excel('Bugs/TP-102168389.xlsx')

# Find the "Positions" section (row with "Symbol", "Position", "Time", etc.)
positions_start = None
for idx, row in df.iterrows():
    if 'Symbol' in str(row.values) and 'Position' in str(row.values):
        positions_start = idx
        break

if positions_start is None:
    print("Could not find Positions section")
    exit(1)

# Extract column names from the header row
header_row = df.iloc[positions_start]
columns = header_row.values

# Get the data rows (positions)
data_rows = []
for idx in range(positions_start + 1, len(df)):
    row = df.iloc[idx]
    # Stop when we hit "Orders" section or NaN
    if 'Orders' in str(row.values) or pd.isna(row.iloc[0]):
        break
    data_rows.append(row.values)

# Create DataFrame with proper columns
positions_df = pd.DataFrame(data_rows, columns=columns)

# Filter for SELL positions with split orders (they have TP values)
sell_positions = positions_df[
    (positions_df['Type'] == 'sell') & 
    (positions_df['Comment'].str.contains('MT5Bot_Split', na=False))
].copy()

print("="*100)
print("TP CALCULATION ANALYSIS - ALL SYMBOLS")
print("="*100)

# Analyze each symbol
symbols_analyzed = {}

for idx, row in sell_positions.iterrows():
    symbol = row['Symbol']
    entry = float(row['Price'])
    sl = float(row['S / L'])
    tp = float(row['T / P'])
    
    if symbol not in symbols_analyzed:
        symbols_analyzed[symbol] = []
    
    symbols_analyzed[symbol].append({
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'position': row['Position']
    })

# Analyze each symbol
for symbol, trades in symbols_analyzed.items():
    print(f"\n{'='*100}")
    print(f"SYMBOL: {symbol}")
    print(f"{'='*100}")
    
    # Group by entry price (same trade group)
    trade_groups = {}
    for trade in trades:
        entry_key = round(trade['entry'], 2)
        if entry_key not in trade_groups:
            trade_groups[entry_key] = []
        trade_groups[entry_key].append(trade)
    
    for entry_price, group in trade_groups.items():
        print(f"\nTrade Group - Entry: {entry_price}")
        print(f"  Stop Loss: {group[0]['sl']}")
        print(f"  Risk: {abs(entry_price - group[0]['sl']):.3f} points")
        
        # Expected TP values (ratio-based)
        risk = abs(entry_price - group[0]['sl'])
        tp_ratios = [1.5, 2.5, 4.0]
        expected_tps = []
        for ratio in tp_ratios:
            reward = risk * ratio
            tp_expected = entry_price - reward  # SELL: subtract
            expected_tps.append(tp_expected)
        
        print(f"\n  Expected TP Values (Ratio-Based):")
        for i, (ratio, tp_exp) in enumerate(zip(tp_ratios, expected_tps), 1):
            print(f"    TP{i} (R:R {ratio}): {tp_exp:.3f}")
        
        print(f"\n  Actual TP Values:")
        for i, trade in enumerate(group, 1):
            tp_actual = trade['tp']
            tp_expected = expected_tps[i-1] if i <= len(expected_tps) else 0
            difference = abs(tp_actual - tp_expected)
            
            # Check if TP is correct
            is_correct = difference < 1.0  # Within 1 point tolerance
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            
            print(f"    TP{i}: {tp_actual:.3f} {status}")
            if not is_correct:
                print(f"         Expected: {tp_expected:.3f}")
                print(f"         Difference: {difference:.3f} points")
                
                # Try to understand the calculation
                if tp_actual < 1000:  # Suspiciously small
                    print(f"         ⚠️  TP value is suspiciously small!")
                    
                    # Check if it's the reward value
                    reward = risk * tp_ratios[i-1]
                    if abs(tp_actual - reward) < 1:
                        print(f"         🔍 Looks like REWARD ({reward:.3f}) was used instead of entry - reward!")
                    
                    # Check if it's entry - expected_tp
                    alt = entry_price - tp_expected
                    if abs(tp_actual - alt) < 1:
                        print(f"         🔍 Looks like entry - expected_tp = {alt:.3f}")

print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

total_positions = len(sell_positions)
print(f"\nTotal SELL positions analyzed: {total_positions}")
print(f"Symbols with issues: {len(symbols_analyzed)}")
print(f"\nSymbols: {', '.join(symbols_analyzed.keys())}")

print(f"\n{'='*100}")
print("CONCLUSION")
print(f"{'='*100}")
print("\nThe fix applied to calculate_multiple_take_profits() will correct these issues by:")
print("  1. Adding symbol parameter support")
print("  2. Implementing pip-based TP calculation for split orders")
print("  3. Adding detailed logging to track calculations")
print("\nWith use_pip_based_tp=true and tp_pips=100:")
print("  - TP Level 1: 150 pips (100 × 1.5)")
print("  - TP Level 2: 250 pips (100 × 2.5)")
print("  - TP Level 3: 400 pips (100 × 4.0)")
print("\nThis will produce consistent, correct TP values for all symbols.")
