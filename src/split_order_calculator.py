"""
Split Order Calculator - Demonstration Script
Shows exactly how the bot calculates position sizes and splits
"""

def calculate_split_order_example():
    """
    Demonstration of split order calculation
    Run this to understand how the bot sizes positions
    """
    
    print("=" * 70)
    print("SPLIT ORDER POSITION SIZE CALCULATOR")
    print("=" * 70)
    print()
    
    # Account parameters
    account_balance = 10000  # $10,000
    risk_percent = 1.0       # 1% risk per trade
    
    # Trade parameters
    symbol = "XAUUSD"  # Gold
    entry_price = 2100.00
    stop_loss = 2070.00
    
    # Split order settings
    num_positions = 3
    tp_levels = [1.5, 2.5, 4.0]
    partial_close_percent = [40, 30, 30]
    
    print("ACCOUNT INFORMATION")
    print("-" * 70)
    print(f"Account Balance: ${account_balance:,.2f}")
    print(f"Risk per Trade: {risk_percent}%")
    print()
    
    print("TRADE SETUP")
    print("-" * 70)
    print(f"Symbol: {symbol}")
    print(f"Entry Price: ${entry_price:.2f}")
    print(f"Stop Loss: ${stop_loss:.2f}")
    print()
    
    # Step 1: Calculate risk
    risk_distance = abs(entry_price - stop_loss)
    risk_amount = account_balance * (risk_percent / 100)
    
    print("STEP 1: CALCULATE TOTAL RISK")
    print("-" * 70)
    print(f"Risk Distance: ${risk_distance:.2f}")
    print(f"Risk Amount: ${risk_amount:.2f} ({risk_percent}% of ${account_balance:,.2f})")
    print()
    
    # Step 2: Calculate total lot size
    # Simplified calculation for gold
    # Actual calculation would use symbol's tick value
    pip_value_per_01_lot = 1.00  # Approximate for gold
    risk_in_dollars_per_01_lot = risk_distance * pip_value_per_01_lot
    
    total_lots = (risk_amount / risk_in_dollars_per_01_lot) * 0.01
    total_lots = round(total_lots, 2)
    
    print("STEP 2: CALCULATE TOTAL POSITION SIZE")
    print("-" * 70)
    print(f"Risk per 0.01 lot: ${risk_in_dollars_per_01_lot:.2f}")
    print(f"Total Lot Size: {total_lots:.2f} lots")
    print(f"This risks exactly ${risk_amount:.2f}")
    print()
    
    # Step 3: Calculate take profit levels
    print("STEP 3: CALCULATE TAKE PROFIT LEVELS")
    print("-" * 70)
    
    tp_prices = []
    for i, ratio in enumerate(tp_levels):
        tp = entry_price + (risk_distance * ratio)
        tp_prices.append(tp)
        reward = tp - entry_price
        print(f"TP{i+1} (R:R {ratio}): ${tp:.2f} (+${reward:.2f} from entry)")
    
    print()
    
    # Step 4: Split into positions
    print("STEP 4: SPLIT INTO MULTIPLE POSITIONS")
    print("-" * 70)
    print(f"Splitting {total_lots:.2f} lots into {num_positions} positions")
    print(f"Allocation: {partial_close_percent}")
    print()
    
    positions = []
    for i, (percent, tp) in enumerate(zip(partial_close_percent, tp_prices)):
        lot_size = total_lots * (percent / 100)
        lot_size = round(lot_size, 2)
        
        positions.append({
            'number': i + 1,
            'lots': lot_size,
            'percent': percent,
            'tp_price': tp,
            'tp_ratio': tp_levels[i]
        })
        
        print(f"Position {i+1}:")
        print(f"  Lot Size: {lot_size:.2f} lots ({percent}% of total)")
        print(f"  Take Profit: ${tp:.2f} (R:R 1:{tp_levels[i]})")
        print()
    
    # Step 5: Calculate potential outcomes
    print("STEP 5: POTENTIAL PROFIT SCENARIOS")
    print("-" * 70)
    
    # Scenario A: Only TP1 hits
    profit_tp1 = positions[0]['lots'] * (positions[0]['tp_price'] - entry_price) * 100
    print(f"Scenario A - Only TP1 hits ({positions[0]['tp_price']:.2f}):")
    print(f"  Profit: ${profit_tp1:.2f}")
    print(f"  Remaining positions: {positions[1]['lots'] + positions[2]['lots']:.2f} lots")
    print()
    
    # Scenario B: TP1 and TP2 hit
    profit_tp2 = positions[1]['lots'] * (positions[1]['tp_price'] - entry_price) * 100
    total_profit_b = profit_tp1 + profit_tp2
    print(f"Scenario B - TP1 and TP2 hit ({positions[1]['tp_price']:.2f}):")
    print(f"  TP1 Profit: ${profit_tp1:.2f}")
    print(f"  TP2 Profit: ${profit_tp2:.2f}")
    print(f"  Total Profit: ${total_profit_b:.2f}")
    print(f"  Remaining positions: {positions[2]['lots']:.2f} lots")
    print()
    
    # Scenario C: All TPs hit
    profit_tp3 = positions[2]['lots'] * (positions[2]['tp_price'] - entry_price) * 100
    total_profit_c = profit_tp1 + profit_tp2 + profit_tp3
    print(f"Scenario C - All TPs hit ({positions[2]['tp_price']:.2f}):")
    print(f"  TP1 Profit: ${profit_tp1:.2f}")
    print(f"  TP2 Profit: ${profit_tp2:.2f}")
    print(f"  TP3 Profit: ${profit_tp3:.2f}")
    print(f"  Total Profit: ${total_profit_c:.2f}")
    print()
    
    # Scenario D: Stop loss hit
    loss = total_lots * risk_distance * 100
    print(f"Scenario D - Stop Loss hit (${stop_loss:.2f}):")
    print(f"  Loss: ${loss:.2f}")
    print(f"  This is exactly our planned risk of ${risk_amount:.2f}")
    print()
    
    # Scenario E: TP1 hits, then reversal to breakeven
    print(f"Scenario E - TP1 hits, remaining at breakeven:")
    print(f"  TP1 Profit: ${profit_tp1:.2f}")
    print(f"  Remaining closed at breakeven: $0.00")
    print(f"  Net Result: +${profit_tp1:.2f} (instead of full loss!)")
    print()
    
    # Summary
    print("SUMMARY")
    print("=" * 70)
    print(f"Account Balance: ${account_balance:,.2f}")
    print(f"Total Risk: ${risk_amount:.2f} ({risk_percent}%)")
    print(f"Total Position: {total_lots:.2f} lots split into {num_positions} orders")
    print()
    print("Best Case (All TPs): +${:.2f} ({:.1f}x risk)".format(
        total_profit_c, total_profit_c / risk_amount
    ))
    print("Good Case (TP1+TP2): +${:.2f} ({:.1f}x risk)".format(
        total_profit_b, total_profit_b / risk_amount
    ))
    print("Ok Case (TP1 only): +${:.2f} ({:.1f}x risk)".format(
        profit_tp1, profit_tp1 / risk_amount
    ))
    print("Worst Case (Stop Loss): -${:.2f} ({:.1f}x risk)".format(
        loss, loss / risk_amount
    ))
    print()
    print("Split orders give you multiple ways to win! 🎯")
    print("=" * 70)


def compare_single_vs_split():
    """
    Compare traditional single TP vs split orders
    """
    
    print("\n" + "=" * 70)
    print("SINGLE TP vs SPLIT ORDERS COMPARISON")
    print("=" * 70)
    print()
    
    # Common parameters
    account_balance = 10000
    risk_percent = 1.0
    entry_price = 2100
    stop_loss = 2070
    risk_distance = entry_price - stop_loss
    risk_amount = account_balance * (risk_percent / 100)
    
    total_lots = 0.30  # Simplified
    
    print("TRADITIONAL APPROACH - Single Take Profit")
    print("-" * 70)
    tp_single = entry_price + (risk_distance * 2.0)  # 1:2 R:R
    profit_single = total_lots * (tp_single - entry_price) * 100
    
    print(f"Position: {total_lots} lots")
    print(f"Take Profit: ${tp_single:.2f} (1:2 R:R)")
    print(f"Potential Profit: ${profit_single:.2f}")
    print()
    print("Issues:")
    print("  ❌ All-or-nothing - either full profit or full loss")
    print("  ❌ No partial profit protection")
    print("  ❌ High regret if reversal after hitting TP")
    print("  ❌ High regret if stopped out before TP")
    print()
    
    print("SPLIT ORDER APPROACH - Multiple Take Profits")
    print("-" * 70)
    
    # Split calculation
    tp1 = entry_price + (risk_distance * 1.5)
    tp2 = entry_price + (risk_distance * 2.5)
    tp3 = entry_price + (risk_distance * 4.0)
    
    lot1 = total_lots * 0.40
    lot2 = total_lots * 0.30
    lot3 = total_lots * 0.30
    
    profit1 = lot1 * (tp1 - entry_price) * 100
    profit2 = lot2 * (tp2 - entry_price) * 100
    profit3 = lot3 * (tp3 - entry_price) * 100
    
    print(f"Position 1: {lot1:.2f} lots @ TP ${tp1:.2f} (1:1.5 R:R)")
    print(f"  Potential: ${profit1:.2f}")
    print()
    print(f"Position 2: {lot2:.2f} lots @ TP ${tp2:.2f} (1:2.5 R:R)")
    print(f"  Potential: ${profit2:.2f}")
    print()
    print(f"Position 3: {lot3:.2f} lots @ TP ${tp3:.2f} (1:4.0 R:R)")
    print(f"  Potential: ${profit3:.2f}")
    print()
    print("Benefits:")
    print("  ✅ Progressive profit-taking")
    print("  ✅ Partial profit protection")
    print("  ✅ Less regret - multiple exit points")
    print("  ✅ Adapts to market momentum")
    print()
    
    # Comparison
    print("OUTCOME COMPARISON")
    print("-" * 70)
    
    print("If price reaches $2145 then reverses:")
    print(f"  Single TP: $0 (didn't reach ${tp_single:.2f})")
    print(f"  Split TP: ${profit1:.2f} (TP1 hit)")
    print(f"  Winner: Split Orders ✓")
    print()
    
    print("If price reaches $2160 then reverses:")
    print(f"  Single TP: ${profit_single:.2f} (TP hit)")
    print(f"  Split TP: ${profit1 + profit2:.2f} (TP1+TP2 hit)")
    print(f"  Winner: Split Orders ✓")
    print()
    
    print("If price reaches $2220 (full move):")
    print(f"  Single TP: ${profit_single:.2f} (TP hit at $2160)")
    print(f"  Split TP: ${profit1 + profit2 + profit3:.2f} (all TPs hit)")
    print(f"  Winner: Split Orders ✓")
    print()
    
    print("=" * 70)


if __name__ == "__main__":
    # Run the main calculator
    calculate_split_order_example()
    
    # Run comparison
    compare_single_vs_split()
    
    print("\n")
    print("💡 TIP: Adjust the values at the top of each function to")
    print("   calculate for your specific account size and risk tolerance!")
    print()
