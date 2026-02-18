"""
Diagnose TP Calculation Issue
Analyze the XPDUSD trades to understand why TP values are incorrect
"""

# Trade data from user
entry_price = 1706.024
stop_loss = 1748.748
direction = -1  # SELL
tp_values_actual = [266.636, 2.981, 185.673]

# Expected calculation (ratio-based)
tp_levels = [1.5, 2.5, 4.0]
risk = abs(entry_price - stop_loss)

print("=" * 80)
print("TP CALCULATION DIAGNOSIS - XPDUSD SELL TRADE")
print("=" * 80)
print(f"\nTrade Details:")
print(f"  Entry Price: {entry_price}")
print(f"  Stop Loss: {stop_loss}")
print(f"  Direction: SELL ({direction})")
print(f"  Risk: {risk:.3f} points")

print(f"\n{'='*80}")
print("EXPECTED TP CALCULATION (Ratio-Based):")
print(f"{'='*80}")
for i, ratio in enumerate(tp_levels, 1):
    reward = risk * ratio
    tp_expected = entry_price - reward  # SELL: subtract reward
    print(f"  TP Level {i} (R:R {ratio}): {tp_expected:.3f}")
    print(f"    Reward: {reward:.3f} points")
    print(f"    Calculation: {entry_price} - {reward:.3f} = {tp_expected:.3f}")

print(f"\n{'='*80}")
print("ACTUAL TP VALUES FROM TRADES:")
print(f"{'='*80}")
for i, tp_actual in enumerate(tp_values_actual, 1):
    print(f"  TP Level {i}: {tp_actual}")

print(f"\n{'='*80}")
print("ANALYSIS:")
print(f"{'='*80}")

# Check if actual values match expected
for i, (tp_actual, ratio) in enumerate(zip(tp_values_actual, tp_levels), 1):
    reward = risk * ratio
    tp_expected = entry_price - reward
    difference = abs(tp_actual - tp_expected)
    
    print(f"\nTP Level {i}:")
    print(f"  Expected: {tp_expected:.3f}")
    print(f"  Actual: {tp_actual}")
    print(f"  Difference: {difference:.3f}")
    
    # Try to understand what calculation could produce this
    if tp_actual < 1000:  # Suspiciously small
        # Could it be a division error?
        if abs(tp_expected / tp_actual - 1) < 0.01:
            print(f"  ⚠️  Looks like expected value was DIVIDED by something!")
        
        # Could it be entry_price - tp_expected?
        alt_calc = entry_price - tp_expected
        if abs(alt_calc - tp_actual) < 1:
            print(f"  ⚠️  Looks like: entry_price - tp_expected = {alt_calc:.3f}")
        
        # Could it be reward value itself?
        if abs(reward - tp_actual) < 1:
            print(f"  ⚠️  Looks like the REWARD value ({reward:.3f}) was used as TP!")
        
        # Could it be ratio * something?
        possible_base = tp_actual / ratio
        print(f"  🔍 If TP = ratio * X, then X = {possible_base:.3f}")

print(f"\n{'='*80}")
print("CONCLUSION:")
print(f"{'='*80}")
print("The TP values are completely incorrect!")
print("Possible causes:")
print("  1. Wrong formula used (reward instead of entry_price - reward)")
print("  2. Division error or unit conversion issue")
print("  3. Bug in calculate_multiple_take_profits method")
print("  4. TP values being overwritten by another process")
print("\nRecommendation: Check the actual code execution with logging")
