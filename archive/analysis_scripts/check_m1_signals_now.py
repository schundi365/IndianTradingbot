"""
Real-time M1 Signal Diagnostic Tool
Checks current M1 data to see why no signals are being generated
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_indicators(df, fast_period=20, slow_period=50, rsi_period=14):
    """Calculate indicators"""
    # Moving averages
    df['fast_ma'] = df['close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_period).mean()
    
    # MA crossover detection
    df['ma_cross'] = 0
    df['ma_trend'] = 0
    
    for i in range(1, len(df)):
        prev_fast = df['fast_ma'].iloc[i-1]
        prev_slow = df['slow_ma'].iloc[i-1]
        curr_fast = df['fast_ma'].iloc[i]
        curr_slow = df['slow_ma'].iloc[i]
        
        # Detect crossover
        if pd.notna(prev_fast) and pd.notna(curr_fast):
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                df.loc[df.index[i], 'ma_cross'] = 1  # Bullish crossover
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                df.loc[df.index[i], 'ma_cross'] = -1  # Bearish crossover
        
        # Track trend
        if pd.notna(curr_fast) and pd.notna(curr_slow):
            if curr_fast > curr_slow:
                df.loc[df.index[i], 'ma_trend'] = 1
            elif curr_fast < curr_slow:
                df.loc[df.index[i], 'ma_trend'] = -1
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

def check_signal_conditions(df):
    """Check what conditions are preventing signals"""
    if len(df) < 2:
        return "Not enough data"
    
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    print("\n" + "="*80)
    print("CURRENT MARKET CONDITIONS")
    print("="*80)
    print(f"Time: {latest.name}")
    print(f"Close: {latest['close']:.2f}")
    print(f"Fast MA (20): {latest['fast_ma']:.2f}")
    print(f"Slow MA (50): {latest['slow_ma']:.2f}")
    print(f"MA Distance: {abs(latest['fast_ma'] - latest['slow_ma']):.2f} points")
    print(f"MA Trend: {latest['ma_trend']} (1=bullish, -1=bearish)")
    print(f"MA Cross: {latest['ma_cross']} (1=bullish cross, -1=bearish cross)")
    print(f"RSI: {latest['rsi']:.1f}")
    print(f"MACD Histogram: {latest['macd_histogram']:.6f}")
    
    print("\n" + "-"*80)
    print("SIGNAL ANALYSIS")
    print("-"*80)
    
    # Check for crossover
    has_crossover = latest['ma_cross'] != 0
    print(f"✓ MA Crossover: {'YES' if has_crossover else 'NO'}")
    
    if not has_crossover:
        # Check for trend confirmation
        price_above_both = latest['close'] > latest['fast_ma'] and latest['close'] > latest['slow_ma']
        price_below_both = latest['close'] < latest['fast_ma'] and latest['close'] < latest['slow_ma']
        trend_changed_bullish = latest['ma_trend'] == 1 and previous['ma_trend'] == -1
        trend_changed_bearish = latest['ma_trend'] == -1 and previous['ma_trend'] == 1
        
        print(f"  Price above both MAs: {price_above_both}")
        print(f"  Price below both MAs: {price_below_both}")
        print(f"  Trend changed to bullish: {trend_changed_bullish}")
        print(f"  Trend changed to bearish: {trend_changed_bearish}")
        
        if price_above_both and trend_changed_bullish:
            print("  → Would generate BUY signal (trend confirmation)")
        elif price_below_both and trend_changed_bearish:
            print("  → Would generate SELL signal (trend confirmation)")
        else:
            print("  → No trend confirmation signal")
    else:
        signal_type = "BUY" if latest['ma_cross'] == 1 else "SELL"
        print(f"  → {signal_type} signal detected!")
        
        # Check filters
        print("\nFILTER CHECKS:")
        
        # RSI filter
        if signal_type == "BUY":
            if latest['rsi'] > 70:
                print(f"  ✗ RSI filter: REJECTED (RSI {latest['rsi']:.1f} > 70 - overbought)")
            else:
                print(f"  ✓ RSI filter: PASSED (RSI {latest['rsi']:.1f})")
        else:
            if latest['rsi'] < 30:
                print(f"  ✗ RSI filter: REJECTED (RSI {latest['rsi']:.1f} < 30 - oversold)")
            else:
                print(f"  ✓ RSI filter: PASSED (RSI {latest['rsi']:.1f})")
        
        # MACD filter
        if signal_type == "BUY":
            if latest['macd_histogram'] <= 0:
                print(f"  ✗ MACD filter: REJECTED (Histogram {latest['macd_histogram']:.6f} <= 0)")
            else:
                print(f"  ✓ MACD filter: PASSED (Histogram {latest['macd_histogram']:.6f})")
        else:
            if latest['macd_histogram'] >= 0:
                print(f"  ✗ MACD filter: REJECTED (Histogram {latest['macd_histogram']:.6f} >= 0)")
            else:
                print(f"  ✓ MACD filter: PASSED (Histogram {latest['macd_histogram']:.6f})")
    
    # Show recent crossovers
    print("\n" + "-"*80)
    print("RECENT CROSSOVERS (Last 60 minutes)")
    print("-"*80)
    recent_crosses = df[df['ma_cross'] != 0].tail(10)
    if len(recent_crosses) > 0:
        for idx, row in recent_crosses.iterrows():
            signal_type = "BUY" if row['ma_cross'] == 1 else "SELL"
            print(f"{idx} - {signal_type}: Close={row['close']:.2f}, RSI={row['rsi']:.1f}, MACD={row['macd_histogram']:.6f}")
    else:
        print("No crossovers in last 60 minutes")
    
    print("\n" + "="*80)

def main():
    # Initialize MT5
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
    
    print("MT5 Connected Successfully")
    print(f"MT5 Version: {mt5.version()}")
    
    symbols = ["XAUUSD", "XAGUSD"]
    
    for symbol in symbols:
        print(f"\n{'='*80}")
        print(f"ANALYZING {symbol} - M1 TIMEFRAME")
        print(f"{'='*80}")
        
        # Get M1 data (last 100 bars to calculate indicators properly)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
        
        if rates is None or len(rates) == 0:
            print(f"Failed to get data for {symbol}")
            continue
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Check conditions
        check_signal_conditions(df)
        
        # Show MA convergence/divergence
        print("\nMA CONVERGENCE ANALYSIS (Last 10 bars):")
        print("-"*80)
        recent = df.tail(10)
        for idx, row in recent.iterrows():
            distance = abs(row['fast_ma'] - row['slow_ma'])
            direction = "↑" if row['fast_ma'] > row['slow_ma'] else "↓"
            print(f"{idx.strftime('%H:%M')} - Distance: {distance:.2f} {direction} | Close: {row['close']:.2f}")
    
    mt5.shutdown()
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)

if __name__ == "__main__":
    main()
