#!/usr/bin/env python3
"""
Restore complete detailed logging to calculate_indicators method
"""

import sys
import os
from pathlib import Path

def restore_detailed_logging():
    """Restore complete detailed logging to the calculate_indicators method"""
    
    bot_file = Path("src/mt5_trading_bot.py")
    
    if not bot_file.exists():
        print("❌ Bot file not found!")
        return False
    
    print("📖 Reading current bot file...")
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the calculate_indicators method
    method_start = 'def calculate_indicators(self, df):'
    method_end = 'def calculate_stop_loss(self, entry_price, direction, atr):'
    
    if method_start not in content or method_end not in content:
        print("❌ Method boundaries not found!")
        return False
    
    # Extract the parts before and after the method
    start_index = content.find(method_start)
    end_index = content.find(method_end)
    
    before_method = content[:start_index]
    after_method = content[end_index:]
    
    # Create the new method with complete detailed logging
    new_method = '''def calculate_indicators(self, df):
        """
        Calculate technical indicators (Enhanced with RSI)
        WITH DETAILED CALCULATION LOGGING
        
        Args:
            df (pd.DataFrame): Price data
            
        Returns:
            pd.DataFrame: Data with calculated indicators
        """
        # FORCE DETAILED LOGGING TO APPEAR
        logging.info("🔥🔥🔥 DETAILED INDICATOR CALCULATION STARTING 🔥🔥🔥")
        logging.info("="*80)
        
        # Log raw data summary
        logging.info(f"📊 Raw Data Summary:")
        logging.info(f"   Data Points: {len(df)} bars")
        logging.info(f"   Date Range: {df.index[0]} to {df.index[-1]}")
        logging.info(f"   Price Range: {df['low'].min():.5f} - {df['high'].max():.5f}")
        logging.info(f"   Latest OHLC: O={df['open'].iloc[-1]:.5f}, H={df['high'].iloc[-1]:.5f}, L={df['low'].iloc[-1]:.5f}, C={df['close'].iloc[-1]:.5f}")
        if 'volume' in df.columns:
            logging.info(f"   Volume Range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
            logging.info(f"   Latest Volume: {df['volume'].iloc[-1]:.0f}")
        
        # Moving Averages
        logging.info(f"\\n📈 MOVING AVERAGES:")
        df['fast_ma'] = df['close'].rolling(window=self.fast_ma_period).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_ma_period).mean()
        
        # Log MA calculations
        latest_fast_ma = df['fast_ma'].iloc[-1]
        latest_slow_ma = df['slow_ma'].iloc[-1]
        latest_close = df['close'].iloc[-1]
        
        logging.info(f"   Fast MA ({self.fast_ma_period} periods): {latest_fast_ma:.5f}")
        logging.info(f"   Slow MA ({self.slow_ma_period} periods): {latest_slow_ma:.5f}")
        logging.info(f"   MA Spread: {abs(latest_fast_ma - latest_slow_ma):.5f} points")
        logging.info(f"   MA Spread %: {abs(latest_fast_ma - latest_slow_ma) / latest_close * 100:.3f}%")
        logging.info(f"   Price vs Fast MA: {latest_close - latest_fast_ma:+.5f} ({(latest_close - latest_fast_ma) / latest_close * 100:+.3f}%)")
        logging.info(f"   Price vs Slow MA: {latest_close - latest_slow_ma:+.5f} ({(latest_close - latest_slow_ma) / latest_close * 100:+.3f}%)")
        
        # ATR (Average True Range) for volatility-based stops
        logging.info(f"\\n📊 AVERAGE TRUE RANGE (ATR):")
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=self.atr_period).mean()
        
        # Log ATR calculations
        latest_atr = df['atr'].iloc[-1]
        latest_tr = df['tr'].iloc[-1]
        atr_avg_5 = df['atr'].tail(5).mean()
        atr_avg_20 = df['atr'].tail(20).mean()
        
        logging.info(f"   ATR Period: {self.atr_period}")
        logging.info(f"   Current True Range: {latest_tr:.5f}")
        logging.info(f"   Current ATR: {latest_atr:.5f}")
        logging.info(f"   ATR (5-bar avg): {atr_avg_5:.5f}")
        logging.info(f"   ATR (20-bar avg): {atr_avg_20:.5f}")
        logging.info(f"   ATR as % of price: {latest_atr / latest_close * 100:.3f}%")
        logging.info(f"   ATR Multiplier (SL): {self.atr_multiplier}x = {latest_atr * self.atr_multiplier:.5f} points")
        
        # Volatility analysis
        if latest_atr > atr_avg_20 * 1.5:
            logging.info(f"   🔥 HIGH VOLATILITY: ATR {latest_atr:.5f} > 20-bar avg {atr_avg_20:.5f} * 1.5")
        elif latest_atr < atr_avg_20 * 0.7:
            logging.info(f"   😴 LOW VOLATILITY: ATR {latest_atr:.5f} < 20-bar avg {atr_avg_20:.5f} * 0.7")
        else:
            logging.info(f"   📊 NORMAL VOLATILITY: ATR within normal range")
        
        # RSI (Relative Strength Index) - Popular filter for gold/silver
        logging.info(f"\\n📈 RELATIVE STRENGTH INDEX (RSI):")
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Log RSI calculations
        latest_rsi = df['rsi'].iloc[-1]
        rsi_avg_5 = df['rsi'].tail(5).mean()
        rsi_change = df['rsi'].iloc[-1] - df['rsi'].iloc[-2]
        
        logging.info(f"   RSI Period: 14")
        logging.info(f"   Current RSI: {latest_rsi:.2f}")
        logging.info(f"   RSI (5-bar avg): {rsi_avg_5:.2f}")
        logging.info(f"   RSI Change: {rsi_change:+.2f}")
        logging.info(f"   Latest Gain: {gain.iloc[-1]:.5f}")
        logging.info(f"   Latest Loss: {loss.iloc[-1]:.5f}")
        logging.info(f"   Avg Gain (14): {avg_gain.iloc[-1]:.5f}")
        logging.info(f"   Avg Loss (14): {avg_loss.iloc[-1]:.5f}")
        logging.info(f"   RS Ratio: {rs.iloc[-1]:.3f}")
        
        # RSI interpretation
        if latest_rsi > 70:
            logging.info(f"   🔴 OVERBOUGHT: RSI {latest_rsi:.2f} > 70")
        elif latest_rsi < 30:
            logging.info(f"   🟢 OVERSOLD: RSI {latest_rsi:.2f} < 30")
        elif latest_rsi > 50:
            logging.info(f"   📈 BULLISH ZONE: RSI {latest_rsi:.2f} > 50")
        else:
            logging.info(f"   📉 BEARISH ZONE: RSI {latest_rsi:.2f} < 50")
        
        # Enhanced MACD (already configured in config, but calculate properly)
        logging.info(f"\\n📊 MACD (Moving Average Convergence Divergence):")
        ema_fast = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Log MACD calculations
        latest_macd = df['macd'].iloc[-1]
        latest_signal = df['macd_signal'].iloc[-1]
        latest_histogram = df['macd_histogram'].iloc[-1]
        macd_change = df['macd'].iloc[-1] - df['macd'].iloc[-2]
        histogram_change = df['macd_histogram'].iloc[-1] - df['macd_histogram'].iloc[-2]
        
        logging.info(f"   MACD Fast EMA: {self.macd_fast} periods")
        logging.info(f"   MACD Slow EMA: {self.macd_slow} periods")
        logging.info(f"   MACD Signal: {self.macd_signal} periods")
        logging.info(f"   Fast EMA: {ema_fast.iloc[-1]:.5f}")
        logging.info(f"   Slow EMA: {ema_slow.iloc[-1]:.5f}")
        logging.info(f"   MACD Line: {latest_macd:.6f}")
        logging.info(f"   Signal Line: {latest_signal:.6f}")
        logging.info(f"   Histogram: {latest_histogram:.6f}")
        logging.info(f"   MACD Change: {macd_change:+.6f}")
        logging.info(f"   Histogram Change: {histogram_change:+.6f}")
        
        # MACD interpretation
        if latest_histogram > 0:
            logging.info(f"   📈 BULLISH: Histogram {latest_histogram:.6f} > 0 (MACD above Signal)")
        else:
            logging.info(f"   📉 BEARISH: Histogram {latest_histogram:.6f} < 0 (MACD below Signal)")
        
        if histogram_change > 0:
            logging.info(f"   🚀 STRENGTHENING: Histogram increasing ({histogram_change:+.6f})")
        else:
            logging.info(f"   📉 WEAKENING: Histogram decreasing ({histogram_change:+.6f})")
        
        # Trend direction
        logging.info(f"\\n🎯 TREND ANALYSIS:")
        df['ma_trend'] = np.where(df['fast_ma'] > df['slow_ma'], 1, -1)
        
        # MA crossover signals
        df['ma_cross'] = 0
        df.loc[(df['fast_ma'] > df['slow_ma']) & 
               (df['fast_ma'].shift(1) <= df['slow_ma'].shift(1)), 'ma_cross'] = 1  # Bullish cross
        df.loc[(df['fast_ma'] < df['slow_ma']) & 
               (df['fast_ma'].shift(1) >= df['slow_ma'].shift(1)), 'ma_cross'] = -1  # Bearish cross
        
        # Log trend analysis
        current_trend = df['ma_trend'].iloc[-1]
        previous_trend = df['ma_trend'].iloc[-2]
        crossover = df['ma_cross'].iloc[-1]
        
        logging.info(f"   Current Trend: {current_trend} ({'BULLISH' if current_trend == 1 else 'BEARISH'})")
        logging.info(f"   Previous Trend: {previous_trend} ({'BULLISH' if previous_trend == 1 else 'BEARISH'})")
        logging.info(f"   Trend Change: {'YES' if current_trend != previous_trend else 'NO'}")
        logging.info(f"   MA Crossover: {crossover} ({'BULLISH' if crossover == 1 else 'BEARISH' if crossover == -1 else 'NONE'})")
        
        # Calculate trend strength
        ma_separation = abs(latest_fast_ma - latest_slow_ma) / latest_close * 100
        if ma_separation > 0.5:
            logging.info(f"   💪 STRONG TREND: MA separation {ma_separation:.3f}% > 0.5%")
        elif ma_separation > 0.2:
            logging.info(f"   📊 MODERATE TREND: MA separation {ma_separation:.3f}% (0.2-0.5%)")
        else:
            logging.info(f"   😐 WEAK TREND: MA separation {ma_separation:.3f}% < 0.2%")
        
        # Price action analysis
        logging.info(f"\\n📊 PRICE ACTION ANALYSIS:")
        price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
        price_change_pct = price_change / df['close'].iloc[-2] * 100
        candle_body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        candle_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        body_ratio = candle_body / candle_range if candle_range > 0 else 0
        
        logging.info(f"   Price Change: {price_change:+.5f} ({price_change_pct:+.3f}%)")
        logging.info(f"   Candle Body: {candle_body:.5f}")
        logging.info(f"   Candle Range: {candle_range:.5f}")
        logging.info(f"   Body/Range Ratio: {body_ratio:.3f} ({body_ratio*100:.1f}%)")
        
        if body_ratio > 0.7:
            logging.info(f"   💪 STRONG CANDLE: Body ratio {body_ratio:.3f} > 0.7")
        elif body_ratio > 0.4:
            logging.info(f"   📊 MODERATE CANDLE: Body ratio {body_ratio:.3f} (0.4-0.7)")
        else:
            logging.info(f"   😐 WEAK CANDLE: Body ratio {body_ratio:.3f} < 0.4 (indecision)")
        
        # Market structure analysis
        logging.info(f"\\n🏗️ MARKET STRUCTURE:")
        recent_highs = df['high'].tail(5)
        recent_lows = df['low'].tail(5)
        higher_highs = (recent_highs.iloc[-1] > recent_highs.iloc[-2] > recent_highs.iloc[-3])
        lower_lows = (recent_lows.iloc[-1] < recent_lows.iloc[-2] < recent_lows.iloc[-3])
        
        logging.info(f"   Recent 5-bar High: {recent_highs.max():.5f}")
        logging.info(f"   Recent 5-bar Low: {recent_lows.min():.5f}")
        logging.info(f"   Higher Highs Pattern: {'YES' if higher_highs else 'NO'}")
        logging.info(f"   Lower Lows Pattern: {'YES' if lower_lows else 'NO'}")
        
        if higher_highs and not lower_lows:
            logging.info(f"   📈 UPTREND STRUCTURE: Higher highs forming")
        elif lower_lows and not higher_highs:
            logging.info(f"   📉 DOWNTREND STRUCTURE: Lower lows forming")
        else:
            logging.info(f"   📊 SIDEWAYS STRUCTURE: Mixed signals")
        
        logging.info(f"\\n🔥🔥🔥 DETAILED INDICATOR CALCULATION COMPLETE 🔥🔥🔥")
        logging.info("="*80)
        
        return df

    '''
    
    # Combine the parts
    new_content = before_method + new_method + after_method
    
    # Create backup
    import time
    backup_file = f"src/mt5_trading_bot_backup_restore_{int(time.time())}.py"
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write the new file
    print("💾 Writing restored bot file...")
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Detailed logging restored successfully!")
    return True

if __name__ == "__main__":
    print("🔧 RESTORE DETAILED LOGGING")
    print("=" * 50)
    
    success = restore_detailed_logging()
    
    if success:
        print("\n✅ DETAILED LOGGING RESTORED!")
        print("📝 Complete detailed logging is now in the calculate_indicators method")
        print("🔄 Restart the bot to see full detailed indicator calculations")
    else:
        print("\n❌ RESTORE FAILED!")
        print("   Please check the file manually")