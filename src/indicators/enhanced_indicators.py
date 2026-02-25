"""
Enhanced Indicators Module
Add RSI, MACD, Bollinger Bands to your trading bot
Based on most popular combinations from social media and brokers
"""

import pandas as pd
import numpy as np


def add_rsi(df, period=14):
    """
    Add RSI (Relative Strength Index) to dataframe
    Most popular indicator for gold/silver
    
    Args:
        df (pd.DataFrame): Price data with 'close' column
        period (int): RSI period (default 14)
        
    Returns:
        pd.DataFrame: DataFrame with 'rsi' column added
    """
    # Calculate price changes
    delta = df['close'].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    """
    Add MACD (Moving Average Convergence Divergence)
    Second most popular for confirmation
    
    Args:
        df (pd.DataFrame): Price data with 'close' column
        fast (int): Fast EMA period
        slow (int): Slow EMA period
        signal (int): Signal line period
        
    Returns:
        pd.DataFrame: DataFrame with MACD columns added
    """
    # Calculate EMAs
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    
    # Calculate MACD line
    df['macd'] = ema_fast - ema_slow
    
    # Calculate signal line
    df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    
    # Calculate histogram
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df


def add_bollinger_bands(df, period=20, std_dev=2):
    """
    Add Bollinger Bands
    Great for volatile gold/silver markets
    
    Args:
        df (pd.DataFrame): Price data with 'close' column
        period (int): Period for moving average
        std_dev (float): Number of standard deviations
        
    Returns:
        pd.DataFrame: DataFrame with Bollinger Band columns
    """
    # Calculate middle band (SMA)
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    
    # Calculate standard deviation
    df['bb_std'] = df['close'].rolling(window=period).std()
    
    # Calculate upper and lower bands
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
    
    # Calculate band width (useful for squeeze detection)
    df['bb_width'] = df['bb_upper'] - df['bb_lower']
    
    return df


def add_stochastic(df, k_period=14, d_period=3):
    """
    Add Stochastic Oscillator
    Popular for ranging markets
    
    Args:
        df (pd.DataFrame): Price data with 'high', 'low', 'close'
        k_period (int): %K period
        d_period (int): %D period (signal line)
        
    Returns:
        pd.DataFrame: DataFrame with Stochastic columns
    """
    # Calculate %K
    lowest_low = df['low'].rolling(window=k_period).min()
    highest_high = df['high'].rolling(window=k_period).max()
    
    df['stoch_k'] = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
    
    # Calculate %D (signal line)
    df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
    
    return df


def add_adx(df, period=14):
    """
    Add ADX (Average Directional Index)
    Measures trend strength
    
    Args:
        df (pd.DataFrame): Price data with 'high', 'low', 'close'
        period (int): ADX period
        
    Returns:
        pd.DataFrame: DataFrame with ADX column
    """
    # Calculate True Range
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift())
    df['low_close'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    
    # Calculate directional movement
    df['up_move'] = df['high'] - df['high'].shift(1)
    df['down_move'] = df['low'].shift(1) - df['low']
    
    df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), 
                             df['up_move'], 0)
    df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), 
                              df['down_move'], 0)
    
    # Smooth the values
    atr = df['tr'].rolling(window=period).mean()
    plus_di = 100 * (df['plus_dm'].rolling(window=period).mean() / atr)
    minus_di = 100 * (df['minus_dm'].rolling(window=period).mean() / atr)
    
    # Calculate DX and ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=period).mean()
    
    # Clean up temporary columns
    df.drop(['high_low', 'high_close', 'low_close', 'up_move', 'down_move', 
             'plus_dm', 'minus_dm'], axis=1, inplace=True)
    
    return df


def add_volume_indicators(df):
    """
    Add volume-based indicators
    
    Args:
        df (pd.DataFrame): Price data with 'volume' column
        
    Returns:
        pd.DataFrame: DataFrame with volume indicators
    """
    # Volume moving average
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    
    # Volume ratio (current vs average)
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # On-Balance Volume (OBV)
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    
    return df


# ==========================================
# ENHANCED SIGNAL GENERATION
# ==========================================

def check_rsi_filter(latest, signal):
    """
    Filter trades using RSI
    Most popular enhancement
    
    Args:
        latest (pd.Series): Latest candle data with 'rsi'
        signal (int): 1 for buy, -1 for sell
        
    Returns:
        bool: True if RSI confirms signal
    """
    if 'rsi' not in latest:
        return True  # No filter if RSI not calculated
    
    rsi = latest['rsi']
    
    if signal == 1:  # BUY signal
        # Don't buy if extremely overbought
        if rsi > 70:
            return False
        # Ideal: RSI between 30-70 or just crossed above 30
        return True
    
    elif signal == -1:  # SELL signal
        # Don't sell if extremely oversold
        if rsi < 30:
            return False
        # Ideal: RSI between 30-70 or just crossed below 70
        return True
    
    return True


def check_macd_confirmation(latest, signal):
    """
    Confirm trade with MACD
    Second most popular filter
    
    Args:
        latest (pd.Series): Latest candle with MACD data
        signal (int): 1 for buy, -1 for sell
        
    Returns:
        bool: True if MACD confirms signal
    """
    if 'macd_histogram' not in latest:
        return True
    
    histogram = latest['macd_histogram']
    
    if signal == 1:  # BUY
        # MACD histogram should be positive or turning positive
        return histogram > 0
    
    elif signal == -1:  # SELL
        # MACD histogram should be negative or turning negative
        return histogram < 0
    
    return True


def check_bollinger_position(latest, signal):
    """
    Check price position relative to Bollinger Bands
    
    Args:
        latest (pd.Series): Latest candle with BB data
        signal (int): 1 for buy, -1 for sell
        
    Returns:
        bool: True if position is favorable
    """
    if 'bb_upper' not in latest:
        return True
    
    close = latest['close']
    bb_upper = latest['bb_upper']
    bb_lower = latest['bb_lower']
    bb_middle = latest['bb_middle']
    
    if signal == 1:  # BUY
        # Don't buy if price is at upper band (overextended)
        if close >= bb_upper:
            return False
        # Ideal: price near lower band or middle
        return True
    
    elif signal == -1:  # SELL
        # Don't sell if price is at lower band (overextended)
        if close <= bb_lower:
            return False
        return True
    
    return True


def check_adx_trend_strength(latest, min_adx=20):
    """
    Verify trend strength with ADX
    Only trade when trend is strong enough
    
    Args:
        latest (pd.Series): Latest candle with ADX
        min_adx (float): Minimum ADX value to trade
        
    Returns:
        bool: True if trend is strong enough
    """
    if 'adx' not in latest:
        return True
    
    adx = latest['adx']
    
    # ADX > 20-25 indicates trending market
    # ADX < 20 indicates ranging market (avoid)
    return adx >= min_adx


# ==========================================
# COMPLETE STRATEGY EXAMPLES
# ==========================================

def strategy_rsi_ma_macd(df):
    """
    Strategy 1: RSI + Moving Averages + MACD
    Most popular combination (40-50% of traders)
    
    Returns signal: 1 (buy), -1 (sell), 0 (no trade)
    """
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Check MA crossover (existing logic)
    ma_cross = 0
    if latest['fast_ma'] > latest['slow_ma'] and previous['fast_ma'] <= previous['slow_ma']:
        ma_cross = 1  # Bullish cross
    elif latest['fast_ma'] < latest['slow_ma'] and previous['fast_ma'] >= previous['slow_ma']:
        ma_cross = -1  # Bearish cross
    
    if ma_cross == 0:
        return 0
    
    # Apply filters
    if not check_rsi_filter(latest, ma_cross):
        print(f"  ❌ RSI filter rejected signal (RSI: {latest.get('rsi', 'N/A'):.1f})")
        return 0
    
    if not check_macd_confirmation(latest, ma_cross):
        print(f"  ❌ MACD filter rejected signal (MACD: {latest.get('macd_histogram', 'N/A'):.4f})")
        return 0
    
    print(f"  ✅ Signal confirmed by RSI and MACD")
    return ma_cross


def strategy_bollinger_rsi(df):
    """
    Strategy 2: Bollinger Bands + RSI
    Second most popular (25-35% of traders)
    
    Great for volatile gold/silver
    """
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    close = latest['close']
    bb_upper = latest['bb_upper']
    bb_lower = latest['bb_lower']
    rsi = latest['rsi']
    
    # BUY: Price near lower BB + RSI oversold
    if close <= bb_lower and rsi < 35:
        # Confirm bounce started
        if close > previous['close']:
            return 1
    
    # SELL: Price near upper BB + RSI overbought
    if close >= bb_upper and rsi > 65:
        # Confirm rejection started
        if close < previous['close']:
            return -1
    
    return 0


def strategy_fibonacci_atr(df):
    """
    Strategy 3: Price Action + ATR
    Professional trader favorite
    
    Note: Fibonacci levels need to be drawn manually or calculated
    from recent swing highs/lows. This is simplified.
    """
    latest = df.iloc[-1]
    
    # Find recent swing high/low
    lookback = 50
    recent = df.tail(lookback)
    
    swing_high = recent['high'].max()
    swing_low = recent['low'].min()
    
    # Calculate Fibonacci levels
    diff = swing_high - swing_low
    fib_618 = swing_low + (diff * 0.618)
    fib_50 = swing_low + (diff * 0.50)
    fib_382 = swing_low + (diff * 0.382)
    
    close = latest['close']
    atr = latest['atr']
    
    # BUY: Price near Fib support + bullish candle
    if abs(close - fib_618) < atr * 0.5 or abs(close - fib_50) < atr * 0.5:
        if latest['close'] > latest['open']:  # Bullish candle
            return 1
    
    # SELL: Price near Fib resistance + bearish candle
    fib_618_resistance = swing_high - (diff * 0.618)
    fib_50_resistance = swing_high - (diff * 0.50)
    
    if abs(close - fib_618_resistance) < atr * 0.5 or abs(close - fib_50_resistance) < atr * 0.5:
        if latest['close'] < latest['open']:  # Bearish candle
            return -1
    
    return 0


# ==========================================
# INTEGRATION HELPER
# ==========================================

def enhance_calculate_indicators(df, config):
    """
    Enhanced version of calculate_indicators() with all popular indicators
    
    Args:
        df (pd.DataFrame): Price data
        config (dict): Configuration with indicator settings
        
    Returns:
        pd.DataFrame: DataFrame with all indicators
    """
    # Original indicators (MA, ATR, etc.)
    df['fast_ma'] = df['close'].rolling(window=config['fast_ma_period']).mean()
    df['slow_ma'] = df['close'].rolling(window=config['slow_ma_period']).mean()
    
    # ATR
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = np.abs(df['high'] - df['close'].shift())
    df['low_close'] = np.abs(df['low'] - df['close'].shift())
    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=config['atr_period']).mean()
    
    # MA trend
    df['ma_trend'] = np.where(df['fast_ma'] > df['slow_ma'], 1, -1)
    
    # Add popular indicators
    if config.get('use_rsi', True):
        df = add_rsi(df, period=config.get('rsi_period', 14))
    
    if config.get('use_macd', True):
        df = add_macd(df, 
                     fast=config.get('macd_fast', 12),
                     slow=config.get('macd_slow', 26),
                     signal=config.get('macd_signal', 9))
    
    if config.get('use_bollinger', False):
        df = add_bollinger_bands(df, 
                                period=config.get('bb_period', 20),
                                std_dev=config.get('bb_std', 2))
    
    if config.get('use_stochastic', False):
        df = add_stochastic(df, 
                           k_period=config.get('stoch_k', 14),
                           d_period=config.get('stoch_d', 3))
    
    if config.get('use_adx', False):
        df = add_adx(df, period=config.get('adx_period', 14))
    
    return df


if __name__ == "__main__":
    print("Enhanced Indicators Module")
    print("=" * 60)
    print("\nMost Popular Indicator Combinations:")
    print("1. RSI + MA + MACD (40-50% of traders)")
    print("2. Bollinger Bands + RSI (25-35%)")
    print("3. Fibonacci + S/R + ATR (20-30% pros)")
    print("\nImport these functions into your trading bot!")
