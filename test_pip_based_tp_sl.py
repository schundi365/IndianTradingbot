"""
Test pip-based TP/SL calculations
"""
import sys
sys.path.insert(0, 'src')

from mt5_trading_bot import MT5TradingBot
import MetaTrader5 as mt5

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

# Test configuration with pip-based TP/SL
config = {
    'symbols': ['EURUSD', 'USDJPY', 'GBPUSD', 'XAUUSD'],
    'timeframe': mt5.TIMEFRAME_H1,
    'magic_number': 234000,
    'lot_size': 0.01,
    'risk_percent': 1.0,
    'reward_ratio': 2.0,
    
    # Pip-based TP/SL settings
    'use_pip_based_sl': True,
    'use_pip_based_tp': True,
    'sl_pips': 50,
    'tp_pips': 100,
    
    # Other settings
    'fast_ma_period': 20,
    'slow_ma_period': 50,
    'atr_period': 14,
    'atr_multiplier': 2.0,
}

# Create bot instance
bot = MT5TradingBot(config)

print("=" * 80)
print("PIP-BASED TP/SL CALCULATION TEST")
print("=" * 80)

for symbol in config['symbols']:
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"\n{symbol}: NOT AVAILABLE")
        continue
    
    symbol_info = mt5.symbol_info(symbol)
    entry_price = tick.ask
    direction = 1  # Buy
    
    # Calculate SL and TP using pip-based method
    sl_price = bot.calculate_price_from_pips(symbol, entry_price, 50, direction, is_sl=True)
    tp_price = bot.calculate_price_from_pips(symbol, entry_price, 100, direction, is_sl=False)
    
    # Verify pip calculations
    sl_pips = bot.calculate_pips_from_price(symbol, abs(entry_price - sl_price))
    tp_pips = bot.calculate_pips_from_price(symbol, abs(tp_price - entry_price))
    
    print(f"\n{symbol}:")
    print(f"  Digits: {symbol_info.digits}")
    print(f"  Point: {symbol_info.point}")
    print(f"  Entry: {entry_price:.{symbol_info.digits}f}")
    print(f"  SL: {sl_price:.{symbol_info.digits}f} (Target: 50 pips, Actual: {sl_pips:.1f} pips)")
    print(f"  TP: {tp_price:.{symbol_info.digits}f} (Target: 100 pips, Actual: {tp_pips:.1f} pips)")
    print(f"  Risk:Reward: 1:{tp_pips/sl_pips:.1f}")
    
    # Verify the calculations are correct
    if abs(sl_pips - 50) < 0.1 and abs(tp_pips - 100) < 0.1:
        print(f"  ✅ PASSED - Pip calculations are correct!")
    else:
        print(f"  ❌ FAILED - Pip calculations are incorrect!")
        print(f"     Expected: SL=50 pips, TP=100 pips")
        print(f"     Got: SL={sl_pips:.1f} pips, TP={tp_pips:.1f} pips")

# Test with bot's calculate_stop_loss and calculate_take_profit methods
print("\n" + "=" * 80)
print("TESTING BOT METHODS")
print("=" * 80)

for symbol in config['symbols']:
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        continue
    
    symbol_info = mt5.symbol_info(symbol)
    entry_price = tick.ask
    direction = 1  # Buy
    atr = 0.001  # Dummy ATR value (not used in pip-based mode)
    
    # Calculate using bot methods
    sl_price = bot.calculate_stop_loss(entry_price, direction, atr, symbol)
    tp_price = bot.calculate_take_profit(entry_price, sl_price, direction, symbol)
    
    # Verify
    sl_pips = bot.calculate_pips_from_price(symbol, abs(entry_price - sl_price))
    tp_pips = bot.calculate_pips_from_price(symbol, abs(tp_price - entry_price))
    
    print(f"\n{symbol}:")
    print(f"  Entry: {entry_price:.{symbol_info.digits}f}")
    print(f"  SL: {sl_price:.{symbol_info.digits}f} ({sl_pips:.1f} pips)")
    print(f"  TP: {tp_price:.{symbol_info.digits}f} ({tp_pips:.1f} pips)")
    
    if abs(sl_pips - 50) < 0.1 and abs(tp_pips - 100) < 0.1:
        print(f"  ✅ Bot methods working correctly!")
    else:
        print(f"  ❌ Bot methods not working as expected!")

mt5.shutdown()
print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
