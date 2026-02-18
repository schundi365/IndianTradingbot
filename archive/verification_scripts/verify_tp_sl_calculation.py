"""
Verify TP/SL calculation with symbol pip units
"""
import MetaTrader5 as mt5

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

# Test symbols
symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'XAUUSD']

print("=" * 80)
print("SYMBOL INFORMATION FOR TP/SL CALCULATION")
print("=" * 80)

for symbol in symbols:
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"\n{symbol}: NOT AVAILABLE")
        continue
    
    print(f"\n{symbol}:")
    print(f"  Point: {info.point}")
    print(f"  Digits: {info.digits}")
    print(f"  Trade Tick Value: {info.trade_tick_value}")
    print(f"  Trade Tick Size: {info.trade_tick_size}")
    print(f"  Trade Contract Size: {info.trade_contract_size}")
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        print(f"  Current Bid: {tick.bid}")
        print(f"  Current Ask: {tick.ask}")
        
        # Example calculation
        entry_price = tick.ask
        atr = 0.001 if 'USD' in symbol and 'JPY' not in symbol else 0.1  # Example ATR
        atr_multiplier = 2.0
        
        # Current method (direct price calculation)
        sl = entry_price - (atr_multiplier * atr)
        risk = abs(entry_price - sl)
        tp = entry_price + (risk * 2.0)  # 1:2 RR
        
        print(f"\n  Example Trade (ATR={atr}):")
        print(f"    Entry: {entry_price:.{info.digits}f}")
        print(f"    SL: {sl:.{info.digits}f}")
        print(f"    TP: {tp:.{info.digits}f}")
        print(f"    Risk in price units: {risk:.{info.digits}f}")
        print(f"    Risk in pips: {risk / info.point:.1f}")
        print(f"    Reward in pips: {(tp - entry_price) / info.point:.1f}")

mt5.shutdown()
print("\n" + "=" * 80)
