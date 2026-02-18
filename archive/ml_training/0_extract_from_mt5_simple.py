"""
Extract Training Data from MT5 - Simplified Version
More robust error handling and clearer output
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import csv
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_from_mt5(symbols=None, bars=1000):
    """
    Extract training data from MT5
    
    Args:
        symbols: List of symbols (default: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY'])
        bars: Number of bars to fetch per symbol
    """
    if symbols is None:
        symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
    
    logger.info("=" * 80)
    logger.info("EXTRACT TRAINING DATA FROM MT5")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize MT5
    logger.info("Step 1: Connecting to MT5...")
    if not mt5.initialize():
        logger.error("❌ Failed to initialize MT5")
        logger.error("   Make sure MT5 is running and you're logged in")
        return False
    
    logger.info("✅ Connected to MT5")
    account_info = mt5.account_info()
    if account_info:
        logger.info(f"   Account: {account_info.login}")
        logger.info(f"   Server: {account_info.server}")
    logger.info("")
    
    # Process each symbol
    all_samples = []
    
    for symbol in symbols:
        logger.info(f"Step 2: Processing {symbol}...")
        
        # Check symbol availability
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.warning(f"⚠️  {symbol} not available, skipping")
            continue
        
        # Fetch historical data
        logger.info(f"   Fetching {bars} bars...")
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M30, 0, bars)
        
        if rates is None or len(rates) < 100:
            logger.warning(f"⚠️  Insufficient data for {symbol}, skipping")
            continue
        
        logger.info(f"   ✅ Got {len(rates)} bars")
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate indicators
        logger.info(f"   Calculating indicators...")
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # ADX (simplified)
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        tr = pd.concat([
            df['high'] - df['low'],
            abs(df['high'] - df['close'].shift()),
            abs(df['low'] - df['close'].shift())
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        df['atr'] = atr
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.rolling(window=14).mean()
        
        # EMAs
        df['ema_fast'] = df['close'].ewm(span=20).mean()
        df['ema_slow'] = df['close'].ewm(span=50).mean()
        
        logger.info(f"   ✅ Indicators calculated")
        
        # Generate samples
        logger.info(f"   Generating training samples...")
        samples = 0
        
        for i in range(50, len(df) - 10):
            row = df.iloc[i]
            
            # Skip if indicators not available
            if pd.isna(row['rsi']) or pd.isna(row['macd']) or pd.isna(row['adx']):
                continue
            
            # Simple signal logic
            signal = None
            if row['rsi'] < 35 and row['macd'] > row['macd_signal']:
                signal = 'BUY'
            elif row['rsi'] > 65 and row['macd'] < row['macd_signal']:
                signal = 'SELL'
            
            if signal:
                # Look ahead to determine outcome
                entry_price = row['close']
                future_prices = df.iloc[i+1:i+11]['close']
                
                if signal == 'BUY':
                    max_future = future_prices.max()
                    profitable = 1 if max_future > entry_price * 1.002 else 0
                else:  # SELL
                    min_future = future_prices.min()
                    profitable = 1 if min_future < entry_price * 0.998 else 0
                
                all_samples.append({
                    'timestamp': row['time'],
                    'symbol': symbol,
                    'close': row['close'],
                    'rsi': row['rsi'],
                    'macd': row['macd'],
                    'macd_signal': row['macd_signal'],
                    'adx': row['adx'],
                    'atr': row['atr'],
                    'ema_fast': row['ema_fast'],
                    'ema_slow': row['ema_slow'],
                    'volume': row['tick_volume'],
                    'profitable': profitable
                })
                samples += 1
        
        logger.info(f"   ✅ Generated {samples} samples")
        logger.info("")
    
    mt5.shutdown()
    
    if len(all_samples) == 0:
        logger.error("❌ No training samples generated")
        logger.error("   Try different symbols or check data availability")
        return False
    
    # Save to CSV
    logger.info(f"Step 3: Saving data...")
    output_file = 'data/training_data.csv'
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    fieldnames = ['timestamp', 'symbol', 'close', 'rsi', 'macd', 'macd_signal', 
                  'adx', 'atr', 'ema_fast', 'ema_slow', 'volume', 'profitable']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_samples)
    
    logger.info(f"✅ Saved to {output_file}")
    logger.info("")
    
    # Statistics
    logger.info("=" * 80)
    logger.info("EXTRACTION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total samples: {len(all_samples)}")
    
    profitable_count = sum(1 for s in all_samples if s['profitable'] == 1)
    logger.info(f"Profitable: {profitable_count} ({profitable_count/len(all_samples)*100:.1f}%)")
    logger.info(f"Losing: {len(all_samples) - profitable_count} ({(len(all_samples)-profitable_count)/len(all_samples)*100:.1f}%)")
    logger.info("")
    
    return True


if __name__ == '__main__':
    print()
    print("This will extract training data from MT5 historical data")
    print()
    
    # Get symbols
    symbols_input = input("Enter symbols (comma-separated) or press Enter for defaults: ").strip()
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
    else:
        symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
    
    print()
    success = extract_from_mt5(symbols=symbols)
    
    if success:
        print()
        print("✅ SUCCESS!")
        print()
        print("Next steps:")
        print("1. Review data/training_data.csv")
        print("2. Run: python ml_training/2_prepare_training_data.py")
        print()
    else:
        print()
        print("❌ FAILED")
        print()
        print("Troubleshooting:")
        print("1. Make sure MT5 is running")
        print("2. Check you're logged in to MT5")
        print("3. Verify symbols are in Market Watch")
        print("4. Try with default symbols first")
        print()
