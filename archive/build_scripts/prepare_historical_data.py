"""
Prepare Historical Data for ML Training
Uses MT5 historical data to create training dataset
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_indicators(df):
    """Calculate technical indicators"""
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
    
    # ADX
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
    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()
    
    # ATR
    df['atr'] = atr
    
    # EMAs
    df['ema_fast'] = df['close'].ewm(span=20).mean()
    df['ema_slow'] = df['close'].ewm(span=50).mean()
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
    
    return df


def simulate_trades(df, symbol):
    """
    Simulate trades based on indicators to label data
    Simple strategy: Buy when RSI < 30 and MACD crosses up, Sell when RSI > 70 and MACD crosses down
    """
    trades = []
    
    for i in range(50, len(df) - 10):  # Need history and future data
        row = df.iloc[i]
        
        # Skip if indicators not available
        if pd.isna(row['rsi']) or pd.isna(row['macd']):
            continue
        
        # Simple signal logic
        signal = None
        if row['rsi'] < 35 and row['macd'] > row['macd_signal']:
            signal = 'BUY'
        elif row['rsi'] > 65 and row['macd'] < row['macd_signal']:
            signal = 'SELL'
        
        if signal:
            # Look ahead to determine if trade would be profitable
            entry_price = row['close']
            future_prices = df.iloc[i+1:i+11]['close']
            
            if signal == 'BUY':
                # Check if price went up
                max_future = future_prices.max()
                profitable = 1 if max_future > entry_price * 1.002 else 0  # 0.2% profit target
            else:  # SELL
                # Check if price went down
                min_future = future_prices.min()
                profitable = 1 if min_future < entry_price * 0.998 else 0  # 0.2% profit target
            
            trades.append({
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
                'bb_upper': row['bb_upper'],
                'bb_lower': row['bb_lower'],
                'profitable': profitable
            })
    
    return trades


def prepare_historical_data(symbols=None, timeframe=mt5.TIMEFRAME_M30, bars=1000, output_file='data/training_data.csv'):
    """
    Prepare training data from MT5 historical data
    
    Args:
        symbols: List of symbols to process
        timeframe: MT5 timeframe constant
        bars: Number of historical bars to fetch
        output_file: Path to output CSV file
    """
    if symbols is None:
        symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
    
    logger.info(f"Preparing historical data for {len(symbols)} symbols")
    
    # Initialize MT5
    if not mt5.initialize():
        logger.error("Failed to initialize MT5")
        return False
    
    # Create data directory
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    all_trades = []
    
    for symbol in symbols:
        logger.info(f"Processing {symbol}...")
        
        # Get historical data
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        
        if rates is None or len(rates) < 100:
            logger.warning(f"Insufficient data for {symbol}")
            continue
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Simulate trades
        trades = simulate_trades(df, symbol)
        all_trades.extend(trades)
        
        logger.info(f"Generated {len(trades)} samples from {symbol}")
    
    mt5.shutdown()
    
    if len(all_trades) == 0:
        logger.error("No training data generated")
        return False
    
    logger.info(f"Total samples generated: {len(all_trades)}")
    
    # Write to CSV
    fieldnames = ['timestamp', 'symbol', 'close', 'rsi', 'macd', 'macd_signal', 'adx', 'atr',
                  'ema_fast', 'ema_slow', 'volume', 'bb_upper', 'bb_lower', 'profitable']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_trades)
    
    logger.info(f"Training data saved to {output_file}")
    
    # Show statistics
    profitable_count = sum(1 for t in all_trades if t['profitable'] == 1)
    logger.info(f"Profitable: {profitable_count} ({profitable_count/len(all_trades)*100:.1f}%)")
    logger.info(f"Losing: {len(all_trades) - profitable_count} ({(len(all_trades)-profitable_count)/len(all_trades)*100:.1f}%)")
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("PREPARE HISTORICAL DATA FOR ML TRAINING")
    print("=" * 80)
    print()
    
    # Get user input
    print("This will use MT5 historical data to create training dataset")
    print()
    
    symbols_input = input("Enter symbols (comma-separated) or press Enter for defaults: ").strip()
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
    else:
        symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
    
    print(f"\nProcessing symbols: {', '.join(symbols)}")
    print("This may take a few minutes...")
    print()
    
    success = prepare_historical_data(symbols=symbols)
    
    if success:
        print()
        print("✅ Historical data prepared successfully!")
        print()
        print("Next steps:")
        print("1. Review data/training_data.csv")
        print("2. Open dashboard → ML Features")
        print("3. Click 'Train ML Model'")
        print()
    else:
        print()
        print("❌ Failed to prepare historical data")
        print()
        print("Troubleshooting:")
        print("1. Make sure MT5 is running")
        print("2. Check symbols are available in MT5")
        print("3. Ensure sufficient historical data exists")
        print()
