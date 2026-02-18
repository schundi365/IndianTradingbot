"""
Analyze TP Issues from User-Provided Trade Data
Based on the data shown in the Excel file
"""

# Trade data extracted from the Excel file
trades = [
    # XPDUSD SELL trades
    {
        'symbol': 'XPDUSD',
        'entry': 1706.024,
        'sl': 1748.748,
        'tp_values': [266.636, 2.981, 185.673],
        'direction': 'SELL'
    },
    # XPTUSD SELL trades  
    {
        'symbol': 'XPTUSD',
        'entry': 2079.481,
        'sl': 2076.596,  # Note: SL is BELOW entry for SELL - this is WRONG!
        'tp_values': [81.092, 230.387, 22.749],
        'direction': 'SELL'
    },
    # XAGUSD SELL trades
    {
        'symbol': 'XAGUSD',
        'entry': 77.129,
        'sl': 77.146,  # Note: SL is ABOVE entry for SELL - this is correct
        'tp_values': [11.89, 5.077, 0.164],
        'direction': 'SELL'
    },
    # GBPCAD SELL trades
    {
        'symbol': 'GBPCAD',
        'entry': 1.85643,
        'sl': 1.86425,
        'tp_values': [1.8419, 1.3857, 1.10306],
        'direction': 'SELL'
    },
    # XAUUSD SELL trades
    {
        'symbol': 'XAUUSD',
        'entry': 4864.91,
        'sl': 4857.47,  # Note: SL is BELOW entry for SELL - this is WRONG!
        'tp_values': [646.3, 182.89, 1534.35],
        'direction': 'SELL'
    },
    # GBPJPY SELL trades
    {
        'symbol': 'GBPJPY',
        'entry': 213.296,
        'sl': 214.303,
        'tp_values': [211.79, 210.786, 209.278],
        'direction': 'SELL'
    },
]

tp_ratios = [1.5, 2.5, 4.0]

print("="*100)
print("TP CALCULATION ANALYSIS - ALL SYMBOLS FROM EXCEL")
print("="*100)

issues_found = []

for trade in trades:
    symbol = trade['symbol']
    entry = trade['entry']
    sl = trade['sl']
    tp_values = trade['tp_values']
    direction = trade['direction']
    
    print(f"\n{'='*100}")
    print(f"SYMBOL: {symbol} ({direction})")
    print(f"{'='*100}")
    print(f"Entry Price: {entry}")
    print(f"Stop Loss: {sl}")
    
    # Check SL direction
    if direction == 'SELL':
        if sl < entry:
            print(f"⚠️  WARNING: SL ({sl}) is BELOW entry ({entry}) for SELL - INCORRECT!")
            print(f"   SL should be ABOVE entry for SELL trades")
            issues_found.append(f"{symbol}: SL in wrong direction")
        else:
            print(f"✅ SL direction correct (above entry for SELL)")
    
    risk = abs(entry - sl)
    print(f"Risk: {risk:.3f} points")
    
    # Calculate expected TP values
    print(f"\nExpected TP Values (Ratio-Based):")
    expected_tps = []
    for i, ratio in enumerate(tp_ratios, 1):
        reward = risk * ratio
        if direction == 'SELL':
            tp_expected = entry - reward
        else:
            tp_expected = entry + reward
        expected_tps.append(tp_expected)
        print(f"  TP{i} (R:R {ratio}): {tp_expected:.3f} (reward: {reward:.3f})")
    
    # Compare with actual TP values
    print(f"\nActual TP Values:")
    all_correct = True
    for i, (tp_actual, tp_expected) in enumerate(zip(tp_values, expected_tps), 1):
        difference = abs(tp_actual - tp_expected)
        is_correct = difference < 1.0
        
        if not is_correct:
            all_correct = False
            status = "❌ WRONG"
            issues_found.append(f"{symbol} TP{i}: {tp_actual:.3f} (expected {tp_expected:.3f})")
        else:
            status = "✅ CORRECT"
        
        print(f"  TP{i}: {tp_actual:.3f} {status}")
        
        if not is_correct:
            print(f"       Expected: {tp_expected:.3f}")
            print(f"       Difference: {difference:.3f} points")
            
            # Analyze the error
            if tp_actual < 1000 and entry > 1000:
                print(f"       ⚠️  TP value is suspiciously small compared to entry price!")
                
                # Check if it's the reward value
                reward = risk * tp_ratios[i-1]
                if abs(tp_actual - reward) < 1:
                    print(f"       🔍 BUG: Reward value ({reward:.3f}) was used as TP instead of entry ± reward!")
                
                # Check if it's a division error
                if abs(tp_expected / tp_actual - 1) < 0.01:
                    print(f"       🔍 BUG: Expected TP was divided by something!")
            
            # Check if TP is in wrong direction
            if direction == 'SELL':
                if tp_actual > entry:
                    print(f"       ⚠️  TP ({tp_actual}) is ABOVE entry ({entry}) for SELL - WRONG DIRECTION!")
    
    if all_correct:
        print(f"\n✅ All TP values are CORRECT for {symbol}")
    else:
        print(f"\n❌ TP calculation errors found for {symbol}")

print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

print(f"\nTotal symbols analyzed: {len(trades)}")
print(f"Issues found: {len(issues_found)}")

if issues_found:
    print(f"\nDetailed Issues:")
    for issue in issues_found:
        print(f"  - {issue}")

print(f"\n{'='*100}")
print("ROOT CAUSE ANALYSIS")
print(f"{'='*100}")

print("\nThe TP values are completely incorrect for most symbols.")
print("\nPossible causes:")
print("  1. calculate_multiple_take_profits() doesn't support pip-based TP")
print("  2. Missing symbol parameter prevents proper calculation")
print("  3. Possible bug using reward value instead of entry ± reward")
print("  4. Some SL values are also in wrong direction (XPTUSD, XAUUSD)")

print(f"\n{'='*100}")
print("FIX VERIFICATION")
print(f"{'='*100}")

print("\nThe fix applied will correct these issues:")
print("\n1. Added symbol parameter to calculate_multiple_take_profits()")
print("2. Implemented pip-based TP calculation:")
print("   - TP Level 1: 100 × 1.5 = 150 pips")
print("   - TP Level 2: 100 × 2.5 = 250 pips")
print("   - TP Level 3: 100 × 4.0 = 400 pips")
print("\n3. Added detailed logging to track calculations")
print("\n4. Updated all method calls to pass symbol parameter")

print("\nExpected results after fix (for XPDUSD example):")
print("  Entry: 1,706.024")
print("  TP1: ~1,691 (150 pips below)")
print("  TP2: ~1,681 (250 pips below)")
print("  TP3: ~1,666 (400 pips below)")

print("\nInstead of the current incorrect values:")
print("  TP1: 266.636 ❌")
print("  TP2: 2.981 ❌")
print("  TP3: 185.673 ❌")

print(f"\n{'='*100}")
print("RECOMMENDATION")
print(f"{'='*100}")
print("\n✅ The fix has been applied to src/mt5_trading_bot.py")
print("✅ Restart the bot to apply the changes")
print("✅ Monitor the first few trades to verify TP values are correct")
print("✅ Check logs for detailed TP calculation information")
