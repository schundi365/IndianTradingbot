"""
Prepare Training Data for ML Model
Cleans, validates, and prepares data for training
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_training_data(input_file='data/training_data.csv', 
                          output_file='data/training_data_prepared.csv'):
    """
    Prepare training data for ML model
    
    Args:
        input_file: Path to raw training data CSV
        output_file: Path to save prepared data
    
    Returns:
        bool: Success status
    """
    logger.info(f"Preparing training data from {input_file}")
    
    # Check if input file exists
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.error("Run 1_extract_training_data.py first!")
        return False
    
    # Load data
    try:
        df = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df)} samples")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False
    
    # Check minimum samples
    if len(df) < 50:
        logger.error(f"Insufficient data: {len(df)} samples (minimum 50 required)")
        logger.error("Collect more trading data before training")
        return False
    
    # Show initial statistics
    logger.info(f"Initial data shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Remove rows with missing critical values
    critical_columns = ['rsi', 'macd', 'adx', 'atr', 'profitable']
    initial_count = len(df)
    df = df.dropna(subset=critical_columns)
    removed_count = initial_count - len(df)
    
    if removed_count > 0:
        logger.warning(f"Removed {removed_count} rows with missing critical values")
    
    # Fill missing optional values with defaults
    if 'ema_fast' in df.columns:
        df['ema_fast'].fillna(df['close'], inplace=True)
    if 'ema_slow' in df.columns:
        df['ema_slow'].fillna(df['close'], inplace=True)
    if 'volume' in df.columns:
        df['volume'].fillna(df['volume'].median(), inplace=True)
    
    # Remove outliers (values beyond 3 standard deviations)
    numeric_columns = ['rsi', 'macd', 'macd_signal', 'adx', 'atr']
    for col in numeric_columns:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            df = df[np.abs(df[col] - mean) <= (3 * std)]
    
    logger.info(f"After cleaning: {len(df)} samples")
    
    # Check if we still have enough data
    if len(df) < 50:
        logger.error(f"After cleaning, only {len(df)} samples remain (minimum 50 required)")
        return False
    
    # Create additional features
    logger.info("Creating additional features...")
    
    # RSI features
    if 'rsi' in df.columns:
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_neutral'] = ((df['rsi'] >= 30) & (df['rsi'] <= 70)).astype(int)
    
    # MACD features
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        df['macd_bullish'] = (df['macd'] > df['macd_signal']).astype(int)
        df['macd_bearish'] = (df['macd'] < df['macd_signal']).astype(int)
    
    # ADX features
    if 'adx' in df.columns:
        df['adx_strong'] = (df['adx'] > 25).astype(int)
        df['adx_weak'] = (df['adx'] <= 25).astype(int)
    
    # EMA features
    if 'ema_fast' in df.columns and 'ema_slow' in df.columns:
        df['ema_bullish'] = (df['ema_fast'] > df['ema_slow']).astype(int)
        df['ema_bearish'] = (df['ema_fast'] < df['ema_slow']).astype(int)
    
    # Volatility features
    if 'atr' in df.columns and 'close' in df.columns:
        df['volatility_ratio'] = df['atr'] / df['close']
    
    logger.info(f"Final data shape: {df.shape}")
    logger.info(f"Features created: {len(df.columns)} columns")
    
    # Show class distribution
    if 'profitable' in df.columns:
        profitable_count = df['profitable'].sum()
        losing_count = len(df) - profitable_count
        logger.info(f"Class distribution:")
        logger.info(f"  Profitable: {profitable_count} ({profitable_count/len(df)*100:.1f}%)")
        logger.info(f"  Losing: {losing_count} ({losing_count/len(df)*100:.1f}%)")
        
        # Check for class imbalance
        if profitable_count / len(df) < 0.3 or profitable_count / len(df) > 0.7:
            logger.warning("⚠️  Class imbalance detected!")
            logger.warning("   Consider collecting more balanced data")
    
    # Save prepared data
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    df.to_csv(output_file, index=False)
    logger.info(f"Prepared data saved to {output_file}")
    
    # Show summary statistics
    logger.info("\nSummary Statistics:")
    logger.info(df.describe())
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("PREPARE TRAINING DATA")
    print("=" * 80)
    print()
    
    success = prepare_training_data()
    
    if success:
        print()
        print("✅ Training data prepared successfully!")
        print()
        print("Next steps:")
        print("1. Review data/training_data_prepared.csv")
        print("2. Run: python ml_training/3_train_ml_model.py")
        print()
    else:
        print()
        print("❌ Failed to prepare training data")
        print()
        print("Troubleshooting:")
        print("1. Make sure data/training_data.csv exists")
        print("2. Run: python ml_training/1_extract_training_data.py")
        print("3. Ensure you have at least 50 trades")
        print()
