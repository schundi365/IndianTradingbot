"""
Quick Test Script
Run a single iteration of the bot to test functionality
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_config
from mt5_trading_bot import MT5TradingBot
import MetaTrader5 as mt5


def quick_test():
    """Run one iteration of the bot"""
    print("=" * 60)
    print("QUICK TEST - Single Iteration")
    print("=" * 60)
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return
    
    print("✅ MT5 connected")
    print()
    
    # Load config
    config = get_config()
    print(f"Testing with: {config['symbols']}")
    print(f"Timeframe: {config['timeframe']}")
    print()
    
    # Create bot
    bot = MT5TradingBot(config)
    
    # Run one check
    print("Checking for signals...")
    for symbol in config['symbols']:
        try:
            # Get historical data
            rates = mt5.copy_rates_from_pos(symbol, config['timeframe'], 0, 100)
            if rates is None or len(rates) == 0:
                print(f"⚠️  Could not get data for {symbol}")
                continue
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Calculate simple moving averages
            df['fast_ma'] = df['close'].rolling(window=config['fast_ma_period']).mean()
            df['slow_ma'] = df['close'].rolling(window=config['slow_ma_period']).mean()
            
            # Check last values
            if len(df) < 2:
                print(f"⏸️  Not enough data for {symbol}")
                continue
                
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Simple crossover check
            if pd.notna(last['fast_ma']) and pd.notna(last['slow_ma']):
                if prev['fast_ma'] <= prev['slow_ma'] and last['fast_ma'] > last['slow_ma']:
                    print(f"📈 BUY signal detected for {symbol}")
                    print(f"   Price: {last['close']:.2f}, Fast MA: {last['fast_ma']:.2f}, Slow MA: {last['slow_ma']:.2f}")
                elif prev['fast_ma'] >= prev['slow_ma'] and last['fast_ma'] < last['slow_ma']:
                    print(f"📉 SELL signal detected for {symbol}")
                    print(f"   Price: {last['close']:.2f}, Fast MA: {last['fast_ma']:.2f}, Slow MA: {last['slow_ma']:.2f}")
                else:
                    print(f"⏸️  No signal for {symbol}")
                    print(f"   Price: {last['close']:.2f}, Fast MA: {last['fast_ma']:.2f}, Slow MA: {last['slow_ma']:.2f}")
            else:
                print(f"⏸️  Indicators not ready for {symbol}")
                
        except Exception as e:
            print(f"❌ Error checking {symbol}: {str(e)}")
    
    print()
    print("Test complete!")
    
    mt5.shutdown()


if __name__ == "__main__":
    try:
        quick_test()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
