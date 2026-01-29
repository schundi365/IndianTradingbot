"""
Live Crossover Monitor
Watches XAUUSD and XAGUSD for imminent crossovers
Updates every 10 seconds
"""
import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def calculate_mas(df, fast=20, slow=50):
    """Calculate moving averages"""
    df['fast_ma'] = df['close'].rolling(window=fast).mean()
    df['slow_ma'] = df['close'].rolling(window=slow).mean()
    return df

def check_crossover_status(symbol):
    """Check how close symbol is to crossover"""
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 60)
    if rates is None or len(rates) == 0:
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = calculate_mas(df)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    fast_ma = latest['fast_ma']
    slow_ma = latest['slow_ma']
    close = latest['close']
    distance = abs(fast_ma - slow_ma)
    
    # Determine trend
    if fast_ma > slow_ma:
        trend = "BULLISH"
        trend_emoji = "📈"
    else:
        trend = "BEARISH"
        trend_emoji = "📉"
    
    # Check if crossover happened
    prev_fast = prev['fast_ma']
    prev_slow = prev['slow_ma']
    
    crossover = None
    if prev_fast <= prev_slow and fast_ma > slow_ma:
        crossover = "BULLISH CROSSOVER! 🚀"
    elif prev_fast >= prev_slow and fast_ma < slow_ma:
        crossover = "BEARISH CROSSOVER! 📉"
    
    # Calculate convergence speed
    prev_distance = abs(prev_fast - prev_slow)
    convergence_speed = prev_distance - distance
    
    return {
        'symbol': symbol,
        'close': close,
        'fast_ma': fast_ma,
        'slow_ma': slow_ma,
        'distance': distance,
        'trend': trend,
        'trend_emoji': trend_emoji,
        'crossover': crossover,
        'convergence_speed': convergence_speed,
        'time': latest['time']
    }

def main():
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
    
    print("Starting live crossover monitor...")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            print("="*80)
            print("LIVE CROSSOVER MONITOR - M1 TIMEFRAME")
            print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            print()
            
            for symbol in ["XAUUSD", "XAGUSD"]:
                status = check_crossover_status(symbol)
                
                if status is None:
                    print(f"{symbol}: Failed to get data")
                    continue
                
                print(f"{'='*80}")
                print(f"{symbol} {status['trend_emoji']}")
                print(f"{'='*80}")
                print(f"Current Price:  {status['close']:.2f}")
                print(f"Fast MA (20):   {status['fast_ma']:.2f}")
                print(f"Slow MA (50):   {status['slow_ma']:.2f}")
                print(f"Distance:       {status['distance']:.2f} points")
                print(f"Trend:          {status['trend']}")
                
                if status['crossover']:
                    print(f"\n🎯 {status['crossover']}")
                else:
                    # Show proximity warning
                    if status['distance'] < 1:
                        print(f"\n⚠️  EXTREMELY CLOSE! Crossover imminent!")
                    elif status['distance'] < 5:
                        print(f"\n⚡ VERY CLOSE! Watch closely!")
                    elif status['distance'] < 20:
                        print(f"\n👀 Getting close... converging")
                    else:
                        print(f"\n   Converging at {status['convergence_speed']:.2f} points/min")
                
                print()
            
            print("="*80)
            print("Refreshing in 10 seconds... (Ctrl+C to stop)")
            print("="*80)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
