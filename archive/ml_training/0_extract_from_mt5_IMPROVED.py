"""
IMPROVED ML Training Data Extractor
Generates high-quality labeled data from MT5 historical prices
Uses multiple signal methods and proper labeling
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
    """Calculate comprehensive technical indicators"""
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
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
    df['atr'] = atr
    
    # EMAs - Multiple periods for better context
    df['ema6'] = df['close'].ewm(span=6, adjust=False).mean()
    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
    
    # Price momentum
    df['roc3'] = df['close'].pct_change(3) * 100  # 3-bar rate of change
    df['roc10'] = df['close'].pct_change(10) * 100  # 10-bar rate of change
    
    # Volume
    df['volume_sma'] = df['tick_volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['tick_volume'] / df['volume_sma']
    
    # Recent high/low (for breakout detection)
    df['high_10'] = df['high'].rolling(window=10).max()
    df['low_10'] = df['low'].rolling(window=10).min()
    
    # Trend detection
    df['trend_ema'] = np.where(df['ema20'] > df['ema50'], 1, -1)
    
    # Price position relative to BB
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    return df


def generate_training_samples(df, symbol):
    """
    Generate training samples with multiple signal types
    Better than old script - generates samples for EVERY bar with proper labeling
    """
    samples = []
    
    # Need 50 bars history for indicators, 20 bars forward to check profit/loss
    for i in range(50, len(df) - 20):
        row = df.iloc[i]
        
        # Skip if indicators not available
        if pd.isna(row['rsi']) or pd.isna(row['atr']):
            continue
        
        # ========================================================================
        # LABEL CALCULATION: Look 20 bars forward, measure max/min price movement
        # ========================================================================
        entry_price = row['close']
        atr_current = row['atr']
        
        # Get next 20 bars
        future_bars = df.iloc[i+1:i+21]
        max_future = future_bars['high'].max()
        min_future = future_bars['low'].min()
        
        # Calculate potential profit/loss in ATR units
        max_move_up = (max_future - entry_price) / atr_current
        max_move_down = (entry_price - min_future) / atr_current
        
        # LABEL LOGIC (this is what ML will learn to predict):
        # 1 = BUY signal (price went up more than down)
        # 0 = SELL signal (price went down more than up)
        # We use a threshold: if move > 0.3 ATR, it's a signal
        
        if max_move_up > 0.3 and max_move_up > max_move_down:
            signal_type = 1  # BUY
            profitable = 1 if max_move_up > 0.5 else 0
        elif max_move_down > 0.3 and max_move_down > max_move_up:
            signal_type = 0  # SELL
            profitable = 1 if max_move_down > 0.5 else 0
        else:
            # No clear direction, skip
            continue
        
        # ========================================================================
        # FEATURES: All the indicators ML will use to make predictions
        # ========================================================================
        sample = {
            'timestamp': row['time'],
            'symbol': symbol,
            
            # Price data
            'close': row['close'],
            'high': row['high'],
            'low': row['low'],
            'open': row['open'],
            
            # Oscillators
            'rsi': row['rsi'],
            'macd': row['macd'],
            'macd_signal': row['macd_signal'],
            'macd_hist': row['macd_hist'],
            
            # Trend
            'adx': row['adx'],
            'ema6': row['ema6'],
            'ema12': row['ema12'],
            'ema20': row['ema20'],
            'ema50': row['ema50'],
            'trend_ema': row['trend_ema'],
            
            # Volatility
            'atr': row['atr'],
            'bb_upper': row['bb_upper'],
            'bb_lower': row['bb_lower'],
            'bb_position': row['bb_position'],
            
            # Momentum
            'roc3': row['roc3'],
            'roc10': row['roc10'],
            
            # Volume
            'volume': row['tick_volume'],
            'volume_ratio': row['volume_ratio'],
            
            # Support/Resistance
            'high_10': row['high_10'],
            'low_10': row['low_10'],
            
            # LABEL
            'signal_type': signal_type,  # 1=BUY, 0=SELL
            'profitable': profitable,  # Did this signal make money?
            'max_move_up_atr': max_move_up,
            'max_move_down_atr': max_move_down
        }
        
        samples.append(sample)
    
    return samples


def prepare_ml_training_data(
    symbols=None,
    timeframe=mt5.TIMEFRAME_M30,
    bars=5000,
    output_file='data/ml_training_data.csv'
):
    """
    Prepare comprehensive ML training data from MT5
    
    Args:
        symbols: List of symbols to process
        timeframe: MT5 timeframe constant
        bars: Number of historical bars to fetch
        output_file: Path to output CSV file
    """
    if symbols is None:
        symbols = ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 
                   'EURJPY', 'GBPJPY', 'AUDUSD', 'NZDUSD', 'USDCAD']
    
    logger.info(f"="*80)
    logger.info(f"ML TRAINING DATA GENERATOR")
    logger.info(f"="*80)
    logger.info(f"Symbols: {len(symbols)}")
    logger.info(f"Bars per symbol: {bars}")
    logger.info(f"Timeframe: M30")
    
    # Initialize MT5
    if not mt5.initialize():
        logger.error("Failed to initialize MT5")
        return False
    
    # Create data directory
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    all_samples = []
    
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
        
        # Generate training samples
        samples = generate_training_samples(df, symbol)
        all_samples.extend(samples)
        
        logger.info(f"  Generated {len(samples)} samples from {symbol}")
    
    mt5.shutdown()
    
    if len(all_samples) == 0:
        logger.error("No training data generated")
        return False
    
    logger.info(f"\n{'='*80}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Total samples: {len(all_samples)}")
    
    # Convert to DataFrame for analysis
    df_samples = pd.DataFrame(all_samples)
    
    # Statistics
    buy_signals = (df_samples['signal_type'] == 1).sum()
    sell_signals = (df_samples['signal_type'] == 0).sum()
    profitable_trades = (df_samples['profitable'] == 1).sum()
    
    logger.info(f"BUY signals: {buy_signals} ({buy_signals/len(all_samples)*100:.1f}%)")
    logger.info(f"SELL signals: {sell_signals} ({sell_signals/len(all_samples)*100:.1f}%)")
    logger.info(f"Profitable: {profitable_trades} ({profitable_trades/len(all_samples)*100:.1f}%)")
    
    # Write to CSV
    df_samples.to_csv(output_file, index=False)
    
    logger.info(f"\nTraining data saved to {output_file}")
    logger.info(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return True


if __name__ == '__main__':
    print("="*80)
    print("IMPROVED ML TRAINING DATA EXTRACTOR")
    print("="*80)
    print()
    print("This will generate labeled training data for ML from MT5 historical prices")
    print()
    
    symbols_input = input("Enter symbols (comma-separated) or press Enter for defaults: ").strip()
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
    else:
        symbols = None  # Use defaults
    
    bars_input = input("Enter number of bars per symbol (default 5000): ").strip()
    bars = int(bars_input) if bars_input else 5000
    
    print()
    print("Processing...")
    print()
    
    success = prepare_ml_training_data(symbols=symbols, bars=bars)
    
    if success:
        print()
        print("✅ ML training data generated successfully!")
        print()
        print("Next steps:")
        print("1. The file 'data/ml_training_data.csv' contains labeled samples")
        print("2. Features include: RSI, MACD, EMAs, ADX, ATR, BB, ROC, Volume")
        print("3. Labels: signal_type (1=BUY, 0=SELL), profitable (1/0)")
        print("4. Ready to train ML models (Random Forest, XGBoost, Neural Nets)")
        print()
    else:
        print()
        print("❌ Failed to generate training data")
        print("Make sure MT5 is running and symbols are available")
        print()
