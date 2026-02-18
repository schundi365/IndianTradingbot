"""
Check if there were MA crossovers in the last 15 minutes
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def check_signals(symbol, timeframe_minutes=30, fast_ma=10, slow_ma=30):
    """Check for MA crossovers in recent data"""
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"Failed to initialize MT5: {mt5.last_error()}")
        return
    
    # Get timeframe constant
    if timeframe_minutes == 1:
        timeframe = mt5.TIMEFRAME_M1
    elif timeframe_minutes == 5:
        timeframe = mt5.TIMEFRAME_M5
    elif timeframe_minutes == 15:
        timeframe = mt5.TIMEFRAME_M15
    elif timeframe_minutes == 30:
        timeframe = mt5.TIMEFRAME_M30
    elif timeframe_minutes == 60:
        timeframe = mt5.TIMEFRAME_H1
    else:
        timeframe = mt5.TIMEFRAME_M30
    
    # Get recent data (last 100 bars to calculate MAs properly)
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    
    if rates is None or len(rates) == 0:
        print(f"❌ No data for {symbol}")
        mt5.shutdown()
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Calculate MAs
    df['fast_ma'] = df['close'].rolling(window=fast_ma).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_ma).mean()
    
    # Calculate MA crossovers
    df['ma_cross'] = 0
    df.loc[(df['fast_ma'] > df['slow_ma']) & 
           (df['fast_ma'].shift(1) <= df['slow_ma'].shift(1)), 'ma_cross'] = 1  # Bullish
    df.loc[(df['fast_ma'] < df['slow_ma']) & 
           (df['fast_ma'].shift(1) >= df['slow_ma'].shift(1)), 'ma_cross'] = -1  # Bearish
    
    # Get last 15 minutes of data
    now = datetime.now()
    fifteen_min_ago = now - timedelta(minutes=15)
    
    recent_df = df[df['time'] >= fifteen_min_ago]
    
    print(f"\n{'='*80}")
    print(f"SIGNAL CHECK: {symbol} (M{timeframe_minutes})")
    print(f"{'='*80}")
    print(f"Fast MA: {fast_ma}, Slow MA: {slow_ma}")
    print(f"Checking last 15 minutes: {fifteen_min_ago.strftime('%H:%M')} - {now.strftime('%H:%M')}")
    print(f"Bars in last 15 min: {len(recent_df)}")
    
    # Check for crossovers in last 15 minutes
    crossovers = recent_df[recent_df['ma_cross'] != 0]
    
    if len(crossovers) > 0:
        print(f"\n✅ CROSSOVERS DETECTED:")
        for idx, row in crossovers.iterrows():
            signal_type = "BULLISH (BUY)" if row['ma_cross'] == 1 else "BEARISH (SELL)"
            print(f"\n  Time: {row['time'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Signal: {signal_type}")
            print(f"  Close: {row['close']:.5f}")
            print(f"  Fast MA: {row['fast_ma']:.5f}")
            print(f"  Slow MA: {row['slow_ma']:.5f}")
    else:
        print(f"\n❌ NO CROSSOVERS in last 15 minutes")
    
    # Show latest bar info
    latest = df.iloc[-1]
    print(f"\n📊 LATEST BAR ({latest['time'].strftime('%Y-%m-%d %H:%M:%S')}):")
    print(f"  Close: {latest['close']:.5f}")
    print(f"  Fast MA: {latest['fast_ma']:.5f}")
    print(f"  Slow MA: {latest['slow_ma']:.5f}")
    print(f"  Fast > Slow: {'YES (Bullish trend)' if latest['fast_ma'] > latest['slow_ma'] else 'NO (Bearish trend)'}")
    
    # Check if close to crossover
    ma_diff = abs(latest['fast_ma'] - latest['slow_ma'])
    ma_diff_pct = (ma_diff / latest['close']) * 100
    
    if ma_diff_pct < 0.1:  # Less than 0.1% difference
        print(f"\n⚠️  MAs are VERY CLOSE (diff: {ma_diff:.5f} = {ma_diff_pct:.3f}%)")
        print(f"  Crossover may be imminent!")
    
    mt5.shutdown()

if __name__ == "__main__":
    print("="*80)
    print("CHECKING FOR RECENT MA CROSSOVERS")
    print("="*80)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check XAUUSD
    check_signals("XAUUSD", timeframe_minutes=30, fast_ma=10, slow_ma=30)
    
    # Check XAGUSD
    check_signals("XAGUSD", timeframe_minutes=30, fast_ma=10, slow_ma=30)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nIf crossovers were detected above, the bot should have traded them.")
    print("If bot was running and didn't trade, check:")
    print("  1. RSI filter (may have rejected if RSI > 75 or < 25)")
    print("  2. MACD filter (histogram must match direction)")
    print("  3. Volume filter (if enabled)")
    print("  4. Min confidence threshold")
    print("\nIf NO crossovers detected, the 'signals' you saw may have been:")
    print("  - Price movement without MA crossover")
    print("  - Signals on different timeframe")
    print("  - Signals from different indicator")
