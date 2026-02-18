"""
Check actual ATR values for different symbols
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

def calculate_atr(df, period=14):
    """Calculate ATR"""
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = np.abs(df['high'] - df['close'].shift())
    df['low_close'] = np.abs(df['low'] - df['close'].shift())
    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=period).mean()
    return df

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

# Test symbols
symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'XAUUSD', 'EURJPY']
timeframe = mt5.TIMEFRAME_M30

print("=" * 80)
print("ACTUAL ATR VALUES AND TP/SL CALCULATIONS")
print("=" * 80)

for symbol in symbols:
    # Get historical data
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    if rates is None:
        print(f"\n{symbol}: NO DATA AVAILABLE")
        continue
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = calculate_atr(df)
    
    # Get symbol info
    info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    
    if info and tick:
        current_atr = df.iloc[-1]['atr']
        entry_price = tick.ask
        atr_multiplier = 2.0
        
        # Calculate SL and TP
        sl = entry_price - (atr_multiplier * current_atr)
        risk = abs(entry_price - sl)
        tp = entry_price + (risk * 2.0)  # 1:2 RR
        
        print(f"\n{symbol}:")
        print(f"  Point size: {info.point}")
        print(f"  Current price: {entry_price:.{info.digits}f}")
        print(f"  Current ATR: {current_atr:.{info.digits}f}")
        print(f"  ATR in pips: {current_atr / info.point:.1f}")
        print(f"\n  BUY Trade Example:")
        print(f"    Entry: {entry_price:.{info.digits}f}")
        print(f"    SL: {sl:.{info.digits}f} (distance: {risk:.{info.digits}f} = {risk/info.point:.1f} pips)")
        print(f"    TP: {tp:.{info.digits}f} (distance: {(tp-entry_price):.{info.digits}f} = {(tp-entry_price)/info.point:.1f} pips)")
        print(f"    Risk:Reward = 1:{(tp-entry_price)/risk:.1f}")

mt5.shutdown()
print("\n" + "=" * 80)
