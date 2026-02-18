"""
Analyze the report to understand TP/SL calculation issues
"""

# From the report, let's analyze what might be wrong
# The report shows trades with specific TP/SL values

# Example from typical forex trading:
# EURUSD: 1 pip = 0.0001 (or 0.00001 for 5-digit brokers)
# USDJPY: 1 pip = 0.01 (or 0.001 for 3-digit brokers)
# XAUUSD: 1 pip = 0.01 (gold)

# The issue might be that the bot is calculating TP/SL in price units
# but not considering the actual pip value for the symbol

# Let's create a proper pip-based calculation

import MetaTrader5 as mt5

def calculate_pips(symbol, price_difference):
    """
    Calculate pip value for a price difference
    
    Args:
        symbol (str): Trading symbol
        price_difference (float): Difference in price units
        
    Returns:
        float: Difference in pips
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        return 0
    
    # For most forex pairs, 1 pip = 10 points (5-digit pricing)
    # For JPY pairs, 1 pip = 10 points (3-digit pricing)
    # For gold/silver, 1 pip = 1 point (2-digit pricing)
    
    # The point is the minimum price change
    point = symbol_info.point
    
    # Calculate pips
    pips = price_difference / point
    
    # For 5-digit and 3-digit brokers, divide by 10 to get actual pips
    if symbol_info.digits == 5 or symbol_info.digits == 3:
        pips = pips / 10
    
    return pips


def calculate_tp_sl_in_pips(symbol, entry_price, sl_pips, tp_pips, direction):
    """
    Calculate TP/SL based on pip values
    
    Args:
        symbol (str): Trading symbol
        entry_price (float): Entry price
        sl_pips (float): Stop loss in pips
        tp_pips (float): Take profit in pips
        direction (int): 1 for buy, -1 for sell
        
    Returns:
        tuple: (stop_loss_price, take_profit_price)
    """
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        return None, None
    
    point = symbol_info.point
    
    # For 5-digit and 3-digit brokers, multiply pips by 10 to get points
    if symbol_info.digits == 5 or symbol_info.digits == 3:
        sl_points = sl_pips * 10 * point
        tp_points = tp_pips * 10 * point
    else:
        sl_points = sl_pips * point
        tp_points = tp_pips * point
    
    if direction == 1:  # Buy
        sl_price = entry_price - sl_points
        tp_price = entry_price + tp_points
    else:  # Sell
        sl_price = entry_price + sl_points
        tp_price = entry_price - tp_points
    
    return sl_price, tp_price


# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

# Test with different symbols
symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'XAUUSD']

print("=" * 80)
print("PIP-BASED TP/SL CALCULATION TEST")
print("=" * 80)

for symbol in symbols:
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"\n{symbol}: NOT AVAILABLE")
        continue
    
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        continue
    
    entry_price = tick.ask
    
    # Example: 50 pip SL, 100 pip TP (1:2 RR)
    sl_pips = 50
    tp_pips = 100
    
    sl_price, tp_price = calculate_tp_sl_in_pips(symbol, entry_price, sl_pips, tp_pips, 1)
    
    print(f"\n{symbol}:")
    print(f"  Digits: {info.digits}")
    print(f"  Point: {info.point}")
    print(f"  Entry: {entry_price:.{info.digits}f}")
    print(f"  SL: {sl_price:.{info.digits}f} ({sl_pips} pips)")
    print(f"  TP: {tp_price:.{info.digits}f} ({tp_pips} pips)")
    print(f"  SL Distance: {abs(entry_price - sl_price):.{info.digits}f}")
    print(f"  TP Distance: {abs(tp_price - entry_price):.{info.digits}f}")
    
    # Verify pip calculation
    actual_sl_pips = calculate_pips(symbol, abs(entry_price - sl_price))
    actual_tp_pips = calculate_pips(symbol, abs(tp_price - entry_price))
    print(f"  Verified SL pips: {actual_sl_pips:.1f}")
    print(f"  Verified TP pips: {actual_tp_pips:.1f}")

mt5.shutdown()
print("\n" + "=" * 80)
