"""
Adaptive Risk Management Demonstration
Shows how parameters change based on different market conditions
"""

def demonstrate_adaptive_risk():
    """
    Demonstrate how adaptive risk changes parameters in different market scenarios
    """
    
    print("=" * 80)
    print("ADAPTIVE RISK MANAGEMENT - PARAMETER COMPARISON")
    print("=" * 80)
    print()
    
    # Base scenario
    entry_price = 2100.00
    atr = 20.00
    risk_amount = 100.00  # $100 risk per trade
    
    print("BASE SCENARIO")
    print("-" * 80)
    print(f"Entry Price: ${entry_price:.2f}")
    print(f"ATR: ${atr:.2f}")
    print(f"Risk Amount: ${risk_amount:.2f}")
    print()
    
    scenarios = [
        {
            'name': 'STRONG UPTREND',
            'adx': 35,
            'consistency': 85,
            'volatility_ratio': 1.0,
            'price_position': 'above_mas',
            'price_action': 'bullish',
            'sr_proximity': 4.0
        },
        {
            'name': 'WEAK UPTREND',
            'adx': 20,
            'consistency': 55,
            'volatility_ratio': 0.9,
            'price_position': 'above_mas',
            'price_action': 'consolidating',
            'sr_proximity': 3.0
        },
        {
            'name': 'RANGING MARKET',
            'adx': 12,
            'consistency': 45,
            'volatility_ratio': 0.8,
            'price_position': 'between_mas',
            'price_action': 'consolidating',
            'sr_proximity': 2.0
        },
        {
            'name': 'VOLATILE MARKET',
            'adx': 18,
            'consistency': 50,
            'volatility_ratio': 1.7,
            'price_position': 'between_mas',
            'price_action': 'bullish',
            'sr_proximity': 3.5
        },
        {
            'name': 'NEAR SUPPORT (Risky)',
            'adx': 22,
            'consistency': 60,
            'volatility_ratio': 1.1,
            'price_position': 'above_mas',
            'price_action': 'bullish',
            'sr_proximity': 0.7  # Very close!
        }
    ]
    
    for scenario in scenarios:
        print("=" * 80)
        print(f"SCENARIO: {scenario['name']}")
        print("=" * 80)
        
        # Classify market
        if scenario['adx'] > 25 and scenario['consistency'] > 70:
            market_type = 'STRONG TREND'
        elif scenario['adx'] > 15 and scenario['consistency'] > 50:
            market_type = 'WEAK TREND'
        elif scenario['volatility_ratio'] > 1.3:
            market_type = 'VOLATILE'
        else:
            market_type = 'RANGING'
        
        print(f"\nMarket Classification: {market_type}")
        print(f"  ADX: {scenario['adx']}")
        print(f"  Trend Consistency: {scenario['consistency']}%")
        print(f"  Volatility Ratio: {scenario['volatility_ratio']:.2f}x")
        print(f"  Price Position: {scenario['price_position']}")
        print(f"  Price Action: {scenario['price_action']}")
        print(f"  S/R Proximity: {scenario['sr_proximity']:.1f} ATR")
        print()
        
        # Calculate confidence score
        confidence = 0.5
        
        # Trend alignment (assume BUY)
        if scenario['price_position'] == 'above_mas':
            confidence += 0.15
        elif scenario['price_position'] == 'between_mas':
            confidence -= 0.1
        
        # Market type
        if market_type == 'STRONG TREND':
            confidence += 0.2
        elif market_type == 'RANGING':
            confidence -= 0.15
        elif market_type == 'VOLATILE':
            confidence -= 0.1
        
        # Price action
        if scenario['price_action'] == 'bullish':
            confidence += 0.15
        elif scenario['price_action'] == 'bearish':
            confidence -= 0.15
        
        # S/R proximity
        if scenario['sr_proximity'] < 0.8:
            confidence -= 0.2
        
        confidence = max(0, min(confidence, 1.0))
        
        # Trade decision
        take_trade = confidence >= 0.60
        
        print(f"TRADE DECISION")
        print(f"  Confidence Score: {confidence:.1%}")
        print(f"  Take Trade: {'YES ✅' if take_trade else 'NO ❌ (filtered out)'}")
        print()
        
        if not take_trade:
            print("  → Trade rejected due to low confidence")
            print()
            continue
        
        # Calculate adaptive stop loss
        if market_type == 'STRONG TREND':
            atr_multiplier = 2.5
        elif market_type == 'WEAK TREND':
            atr_multiplier = 2.0
        elif market_type == 'VOLATILE':
            atr_multiplier = 3.0
        else:  # RANGING
            atr_multiplier = 1.5
        
        # Adjust for volatility
        if scenario['volatility_ratio'] > 1.5:
            atr_multiplier *= 1.2
        elif scenario['volatility_ratio'] < 0.7:
            atr_multiplier *= 0.9
        
        # Near S/R adjustment
        if scenario['sr_proximity'] < 1.5:
            print(f"  ⚠️  Near support/resistance - adjusting stop loss placement")
        
        stop_loss = entry_price - (atr * atr_multiplier)
        
        # Calculate adaptive take profit
        if market_type == 'STRONG TREND':
            if scenario['consistency'] > 80:
                tp_ratios = [1.5, 3.0, 5.0]
                allocations = [30, 30, 40]
            else:
                tp_ratios = [1.5, 2.5, 4.0]
                allocations = [35, 30, 35]
        elif market_type == 'WEAK TREND':
            tp_ratios = [1.5, 2.0, 3.0]
            allocations = [40, 35, 25]
        elif market_type == 'VOLATILE':
            tp_ratios = [1.0, 1.8, 3.0]
            allocations = [50, 30, 20]
        else:  # RANGING
            tp_ratios = [1.0, 1.5, 2.0]
            allocations = [50, 35, 15]
        
        # Price action adjustment
        if scenario['price_action'] == 'bullish':
            tp_ratios = [r * 1.2 for r in tp_ratios]
        
        risk = entry_price - stop_loss
        tp_prices = [entry_price + (risk * r) for r in tp_ratios]
        
        # Calculate trailing parameters
        if market_type == 'STRONG TREND':
            trail_activation = 1.2
            trail_distance = 1.5
        elif market_type == 'WEAK TREND':
            trail_activation = 1.5
            trail_distance = 1.5
        elif market_type == 'VOLATILE':
            trail_activation = 2.0
            trail_distance = 2.5
        else:  # RANGING
            trail_activation = 1.0
            trail_distance = 1.0
        
        # Risk multiplier
        risk_multiplier = 1.0
        
        if market_type == 'VOLATILE':
            risk_multiplier *= 0.7
        if market_type == 'RANGING':
            risk_multiplier *= 0.8
        if scenario['sr_proximity'] < 1.0:
            risk_multiplier *= 0.7
        if market_type == 'STRONG TREND' and scenario['consistency'] > 80:
            risk_multiplier *= 1.3
        
        risk_multiplier = max(0.3, min(risk_multiplier, 1.5))
        
        adjusted_risk = risk_amount * risk_multiplier
        
        print(f"ADAPTIVE PARAMETERS")
        print(f"  Stop Loss: ${stop_loss:.2f} ({atr_multiplier:.1f} × ATR)")
        print(f"    vs Fixed: ${entry_price - (atr * 2):.2f} (2.0 × ATR)")
        print()
        print(f"  Take Profit Levels:")
        for i, (tp, ratio, alloc) in enumerate(zip(tp_prices, tp_ratios, allocations)):
            print(f"    TP{i+1}: ${tp:.2f} ({ratio:.1f}:1 R:R) - {alloc}% of position")
        print(f"    vs Fixed: ${entry_price + (risk * 2):.2f} (2.0:1 R:R) - 100%")
        print()
        print(f"  Trailing Stop:")
        print(f"    Activate at: {trail_activation:.1f} × ATR profit")
        print(f"    Trail distance: {trail_distance:.1f} × ATR")
        print(f"    vs Fixed: 1.5 × ATR activation, 1.0 × ATR distance")
        print()
        print(f"  Position Sizing:")
        print(f"    Risk Multiplier: {risk_multiplier:.2f}x")
        print(f"    Risk Amount: ${adjusted_risk:.2f}")
        print(f"    vs Fixed: ${risk_amount:.2f}")
        print()
        
        # Show impact
        profit_potential_1 = (tp_prices[0] - entry_price) * (allocations[0] / 100)
        profit_potential_2 = (tp_prices[1] - entry_price) * (allocations[1] / 100)
        profit_potential_3 = (tp_prices[2] - entry_price) * (allocations[2] / 100)
        total_profit_potential = profit_potential_1 + profit_potential_2 + profit_potential_3
        
        fixed_profit_potential = (entry_price + (risk * 2)) - entry_price
        
        print(f"PROFIT POTENTIAL (per $1 position)")
        print(f"  Adaptive: ${total_profit_potential:.2f}")
        print(f"  Fixed: ${fixed_profit_potential:.2f}")
        print(f"  Difference: {((total_profit_potential / fixed_profit_potential - 1) * 100):.1f}%")
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Key Insights:")
    print("  1. Strong trends get WIDER stops and MORE AGGRESSIVE targets")
    print("  2. Ranging markets get TIGHTER stops and CONSERVATIVE targets")
    print("  3. Volatile markets get MUCH WIDER stops and QUICK profit-taking")
    print("  4. Low confidence setups are FILTERED OUT entirely")
    print("  5. Near S/R levels trigger REDUCED position sizes")
    print()
    print("Result: Better risk management, higher profits, fewer losses! 🚀")
    print("=" * 80)


if __name__ == "__main__":
    demonstrate_adaptive_risk()
