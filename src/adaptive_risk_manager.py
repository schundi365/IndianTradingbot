"""
Adaptive Risk Management Module
Dynamically adjusts Stop Loss, Trailing Stops, and Take Profit based on market trends
to minimize risk and maximize profit potential
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging


class AdaptiveRiskManager:
    """
    Dynamically adjusts risk parameters based on market conditions
    """
    
    def __init__(self, config):
        self.config = config
        self.atr_period = config.get('atr_period', 14)
        self.trend_strength_period = config.get('trend_strength_period', 50)
        self.min_trade_confidence = config.get('min_trade_confidence', 0.60)  # Use config threshold
        
    def analyze_market_condition(self, df):
        """
        Analyze overall market condition to determine risk profile
        
        Args:
            df (pd.DataFrame): Price data with indicators
            
        Returns:
            dict: Market condition analysis
        """
        if len(df) < self.trend_strength_period:
            return None
        
        latest = df.iloc[-1]
        recent = df.tail(self.trend_strength_period)
        
        # 1. Trend Strength (ADX)
        trend_strength = self.calculate_adx(df)
        
        # 2. Volatility Level
        current_atr = latest['atr']
        avg_atr = recent['atr'].mean()
        volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
        
        # 3. Trend Direction Consistency
        trend_consistency = self.calculate_trend_consistency(df)
        
        # 4. Price Position relative to MAs
        price_position = self.analyze_price_position(latest)
        
        # 5. Recent Price Action (Higher Highs/Lower Lows)
        price_action = self.analyze_price_action(recent)
        
        # 6. Support/Resistance proximity
        sr_proximity = self.check_support_resistance_proximity(df)
        
        # Classify market condition
        market_type = self.classify_market(
            trend_strength, volatility_ratio, trend_consistency
        )
        
        return {
            'market_type': market_type,  # 'strong_trend', 'weak_trend', 'ranging', 'volatile'
            'trend_strength': trend_strength,
            'trend_direction': latest['ma_trend'],  # 1 or -1
            'volatility_ratio': volatility_ratio,  # >1 = high, <1 = low
            'trend_consistency': trend_consistency,  # 0-100%
            'price_position': price_position,  # 'above_mas', 'below_mas', 'between_mas'
            'price_action': price_action,  # 'bullish', 'bearish', 'consolidating'
            'sr_proximity': sr_proximity,  # distance to nearest S/R
            'current_atr': current_atr,
            'avg_atr': avg_atr
        }
    
    def calculate_adx(self, df, period=14):
        """
        Calculate Average Directional Index (trend strength)
        
        Returns:
            float: ADX value (0-100, >25 = trending, <20 = ranging)
        """
        if len(df) < period + 1:
            return 25  # Default neutral value
        
        # Calculate +DI and -DI
        df_copy = df.copy()
        
        df_copy['up_move'] = df_copy['high'] - df_copy['high'].shift(1)
        df_copy['down_move'] = df_copy['low'].shift(1) - df_copy['low']
        
        df_copy['plus_dm'] = np.where(
            (df_copy['up_move'] > df_copy['down_move']) & (df_copy['up_move'] > 0),
            df_copy['up_move'], 0
        )
        df_copy['minus_dm'] = np.where(
            (df_copy['down_move'] > df_copy['up_move']) & (df_copy['down_move'] > 0),
            df_copy['down_move'], 0
        )
        
        # Smooth with ATR
        atr = df_copy['atr'].iloc[-1]
        plus_di = (df_copy['plus_dm'].rolling(period).mean().iloc[-1] / atr) * 100
        minus_di = (df_copy['minus_dm'].rolling(period).mean().iloc[-1] / atr) * 100
        
        # Calculate DX
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        # ADX is smoothed DX (simplified - normally uses Wilder's smoothing)
        adx = dx  # Simplified for this implementation
        
        return adx
    
    def calculate_trend_consistency(self, df, lookback=20):
        """
        Calculate how consistent the trend direction has been
        
        Returns:
            float: Consistency percentage (0-100)
        """
        if len(df) < lookback:
            return 50.0
        
        recent_trends = df['ma_trend'].tail(lookback)
        
        # Calculate what % of recent bars agree with current trend
        current_trend = df['ma_trend'].iloc[-1]
        consistency = (recent_trends == current_trend).sum() / lookback * 100
        
        return consistency
    
    def analyze_price_position(self, latest):
        """
        Determine price position relative to moving averages
        """
        price = latest['close']
        fast_ma = latest['fast_ma']
        slow_ma = latest['slow_ma']
        
        if price > fast_ma and price > slow_ma:
            return 'above_mas'
        elif price < fast_ma and price < slow_ma:
            return 'below_mas'
        else:
            return 'between_mas'
    
    def analyze_price_action(self, recent_df, lookback=10):
        """
        Analyze recent price action for higher highs/lower lows
        """
        if len(recent_df) < lookback:
            return 'consolidating'
        
        recent = recent_df.tail(lookback)
        
        # Check for higher highs and higher lows (bullish)
        highs = recent['high'].values
        lows = recent['low'].values
        
        higher_highs = sum(highs[i] > highs[i-1] for i in range(1, len(highs)))
        lower_lows = sum(lows[i] < lows[i-1] for i in range(1, len(lows)))
        
        if higher_highs > lookback * 0.6:
            return 'bullish'
        elif lower_lows > lookback * 0.6:
            return 'bearish'
        else:
            return 'consolidating'
    
    def check_support_resistance_proximity(self, df, lookback=50):
        """
        Check proximity to recent support/resistance levels
        
        Returns:
            float: Distance in ATR to nearest S/R level
        """
        if len(df) < lookback:
            return 5.0  # Default far from S/R
        
        recent = df.tail(lookback)
        current_price = df['close'].iloc[-1]
        current_atr = df['atr'].iloc[-1]
        
        # Find significant swing highs and lows
        resistance_levels = recent['high'].nlargest(5).values
        support_levels = recent['low'].nsmallest(5).values
        
        # Calculate distance to nearest level
        distances = []
        for level in np.concatenate([resistance_levels, support_levels]):
            distance = abs(current_price - level) / current_atr
            distances.append(distance)
        
        return min(distances) if distances else 5.0
    
    def classify_market(self, trend_strength, volatility_ratio, trend_consistency):
        """
        Classify market type based on indicators
        
        Returns:
            str: Market classification
        """
        # Strong trending market
        if trend_strength > 25 and trend_consistency > 70:
            return 'strong_trend'
        
        # Weak trend
        elif trend_strength > 15 and trend_consistency > 50:
            return 'weak_trend'
        
        # Volatile/choppy market
        elif volatility_ratio > 1.3:
            return 'volatile'
        
        # Ranging market
        else:
            return 'ranging'
    
    def calculate_adaptive_stop_loss(self, entry_price, direction, df, market_condition):
        """
        Calculate stop loss based on market conditions
        
        Args:
            entry_price (float): Entry price
            direction (int): 1 for buy, -1 for sell
            df (pd.DataFrame): Price data
            market_condition (dict): Market analysis
            
        Returns:
            float: Optimized stop loss price
        """
        current_atr = market_condition['current_atr']
        market_type = market_condition['market_type']
        volatility_ratio = market_condition['volatility_ratio']
        sr_proximity = market_condition['sr_proximity']
        
        # Base ATR multiplier
        if market_type == 'strong_trend':
            # Wider stops in strong trends - give trade room to breathe
            atr_multiplier = 2.5
        elif market_type == 'weak_trend':
            # Standard stops
            atr_multiplier = 2.0
        elif market_type == 'volatile':
            # Much wider stops in volatile markets
            atr_multiplier = 3.0
        else:  # ranging
            # Tighter stops in ranging markets
            atr_multiplier = 1.5
        
        # Adjust for volatility
        if volatility_ratio > 1.5:
            atr_multiplier *= 1.2  # Add 20% for high volatility
        elif volatility_ratio < 0.7:
            atr_multiplier *= 0.9  # Reduce 10% for low volatility
        
        # Check for nearby support/resistance
        if sr_proximity < 1.5:  # Very close to S/R
            # Place stop beyond the S/R level
            recent = df.tail(20)
            if direction == 1:  # Buy
                nearest_support = recent['low'].min()
                sl_sr = nearest_support - (current_atr * 0.5)
                sl_atr = entry_price - (current_atr * atr_multiplier)
                stop_loss = min(sl_sr, sl_atr)  # Use tighter of the two
            else:  # Sell
                nearest_resistance = recent['high'].max()
                sl_sr = nearest_resistance + (current_atr * 0.5)
                sl_atr = entry_price + (current_atr * atr_multiplier)
                stop_loss = max(sl_sr, sl_atr)  # Use tighter of the two
        else:
            # Standard ATR-based stop
            if direction == 1:
                stop_loss = entry_price - (current_atr * atr_multiplier)
            else:
                stop_loss = entry_price + (current_atr * atr_multiplier)
        
        logging.info(f"Adaptive SL: Market={market_type}, ATR mult={atr_multiplier:.2f}, SL={stop_loss:.2f}")
        
        return stop_loss
    
    def calculate_adaptive_take_profit(self, entry_price, stop_loss, direction, 
                                       df, market_condition):
        """
        Calculate take profit levels based on market conditions
        
        Returns:
            list: Multiple TP levels optimized for market condition
        """
        market_type = market_condition['market_type']
        trend_strength = market_condition['trend_strength']
        trend_consistency = market_condition['trend_consistency']
        price_action = market_condition['price_action']
        
        risk = abs(entry_price - stop_loss)
        
        # Adaptive R:R ratios based on market type
        if market_type == 'strong_trend':
            # Strong trends can run far - use aggressive targets
            if trend_consistency > 80:
                tp_ratios = [1.5, 3.0, 5.0]  # Very aggressive
                allocations = [30, 30, 40]   # Keep more for big move
            else:
                tp_ratios = [1.5, 2.5, 4.0]
                allocations = [35, 30, 35]
        
        elif market_type == 'weak_trend':
            # Moderate targets
            tp_ratios = [1.5, 2.0, 3.0]
            allocations = [40, 35, 25]
        
        elif market_type == 'volatile':
            # Quick profits in volatile markets
            tp_ratios = [1.0, 1.8, 3.0]
            allocations = [50, 30, 20]  # Take more profit early
        
        else:  # ranging
            # Very conservative in ranging markets
            tp_ratios = [1.0, 1.5, 2.0]
            allocations = [50, 35, 15]
        
        # Check price action alignment
        if direction == 1 and price_action == 'bullish':
            # Bullish price action supports buy - use wider targets
            tp_ratios = [r * 1.2 for r in tp_ratios]
        elif direction == -1 and price_action == 'bearish':
            # Bearish price action supports sell - use wider targets
            tp_ratios = [r * 1.2 for r in tp_ratios]
        elif (direction == 1 and price_action == 'bearish') or \
             (direction == -1 and price_action == 'bullish'):
            # Counter-trend trade - use tighter targets
            tp_ratios = [r * 0.8 for r in tp_ratios]
        
        # Calculate TP prices
        tp_prices = []
        for ratio in tp_ratios:
            if direction == 1:
                tp = entry_price + (risk * ratio)
            else:
                tp = entry_price - (risk * ratio)
            tp_prices.append(tp)
        
        logging.info(f"Adaptive TP: Market={market_type}, Ratios={tp_ratios}, Allocations={allocations}")
        
        return tp_prices, allocations
    
    def calculate_adaptive_trailing_params(self, market_condition):
        """
        Calculate optimal trailing stop parameters based on market
        
        Returns:
            dict: Trailing parameters
        """
        market_type = market_condition['market_type']
        volatility_ratio = market_condition['volatility_ratio']
        trend_consistency = market_condition['trend_consistency']
        
        if market_type == 'strong_trend':
            # In strong trends, activate earlier and trail closer
            params = {
                'activation_atr': 1.2,    # Activate sooner
                'trail_distance_atr': 1.5,  # Trail closer
                'trail_type': 'atr'
            }
            
            if trend_consistency > 85:
                # Very strong trend - even tighter trailing
                params['trail_distance_atr'] = 1.2
        
        elif market_type == 'weak_trend':
            # Standard trailing
            params = {
                'activation_atr': 1.5,
                'trail_distance_atr': 1.5,
                'trail_type': 'atr'
            }
        
        elif market_type == 'volatile':
            # Wider trailing in volatile markets
            params = {
                'activation_atr': 2.0,    # Wait for more profit
                'trail_distance_atr': 2.5,  # Trail much wider
                'trail_type': 'atr'
            }
        
        else:  # ranging
            # Quick breakeven in ranging markets
            params = {
                'activation_atr': 1.0,
                'trail_distance_atr': 1.0,
                'trail_type': 'breakeven'  # Move to BE quickly
            }
        
        # Adjust for volatility
        if volatility_ratio > 1.5:
            params['trail_distance_atr'] *= 1.3
        
        logging.info(f"Adaptive Trailing: Market={market_type}, " + 
                    f"Activation={params['activation_atr']}, " +
                    f"Distance={params['trail_distance_atr']}")
        
        return params
    
    def should_reduce_risk(self, market_condition, recent_trades_win_rate=None):
        """
        Determine if we should reduce risk based on market conditions
        
        Returns:
            float: Risk multiplier (0.5 = half risk, 1.0 = normal, 1.5 = increased)
        """
        market_type = market_condition['market_type']
        volatility_ratio = market_condition['volatility_ratio']
        sr_proximity = market_condition['sr_proximity']
        trend_consistency = market_condition['trend_consistency']
        
        risk_multiplier = 1.0  # Start with normal risk
        
        # Reduce risk in unfavorable conditions
        if market_type == 'volatile':
            risk_multiplier *= 0.7  # 30% less risk in volatile markets
        
        if market_type == 'ranging':
            risk_multiplier *= 0.8  # 20% less risk in ranging markets
        
        # Reduce risk near support/resistance (higher chance of reversal)
        if sr_proximity < 1.0:
            risk_multiplier *= 0.7
        
        # Increase risk in very favorable conditions
        if market_type == 'strong_trend' and trend_consistency > 80:
            risk_multiplier *= 1.3  # 30% more risk - high probability setup
        
        # Consider recent win rate if provided
        if recent_trades_win_rate is not None:
            if recent_trades_win_rate < 0.3:  # Losing streak
                risk_multiplier *= 0.6  # Reduce risk significantly
            elif recent_trades_win_rate > 0.7:  # Winning streak
                risk_multiplier *= 1.2  # Slightly increase risk
        
        # Cap the multiplier using config values
        max_mult = self.config.get('max_risk_multiplier', 1.5)
        min_mult = self.config.get('min_risk_multiplier', 0.5)
        risk_multiplier = max(min_mult, min(risk_multiplier, max_mult))
        
        logging.info(f"Risk Adjustment: Market={market_type}, Multiplier={risk_multiplier:.2f}")
        
        return risk_multiplier
    
    def should_take_trade(self, market_condition, signal_direction):
        """
        Determine if trade should be taken based on market alignment
        
        Returns:
            tuple: (should_trade, confidence_score)
        """
        market_type = market_condition['market_type']
        trend_direction = market_condition['trend_direction']
        price_position = market_condition['price_position']
        price_action = market_condition['price_action']
        sr_proximity = market_condition['sr_proximity']
        
        confidence = 0.5  # Start at 50%
        
        # Check trend alignment
        if signal_direction == trend_direction:
            confidence += 0.2  # Trend-aligned trade
        else:
            confidence -= 0.2  # Counter-trend trade
        
        # Check market type
        if market_type == 'strong_trend':
            confidence += 0.2  # High conviction in trending markets
        elif market_type == 'ranging':
            confidence -= 0.15  # Lower conviction in ranging
        elif market_type == 'volatile':
            confidence -= 0.1  # Slightly lower in volatile
        
        # Check price position
        if signal_direction == 1 and price_position == 'above_mas':
            confidence += 0.15  # Buy above MAs
        elif signal_direction == -1 and price_position == 'below_mas':
            confidence += 0.15  # Sell below MAs
        elif price_position == 'between_mas':
            confidence -= 0.1  # Unclear position
        
        # Check price action
        if (signal_direction == 1 and price_action == 'bullish') or \
           (signal_direction == -1 and price_action == 'bearish'):
            confidence += 0.15  # Price action confirms
        elif (signal_direction == 1 and price_action == 'bearish') or \
             (signal_direction == -1 and price_action == 'bullish'):
            confidence -= 0.15  # Price action conflicts
        
        # Check S/R proximity
        if sr_proximity < 0.8:
            confidence -= 0.2  # Too close to S/R - risky
        
        # Decision threshold (use config value)
        should_trade = confidence >= self.min_trade_confidence
        
        logging.info(f"Trade Decision: Confidence={confidence:.2f}, Take Trade={should_trade}")
        
        return should_trade, confidence


def integrate_adaptive_risk(bot, symbol, signal, df):
    """
    Integration function to use adaptive risk management in the main bot
    
    Args:
        bot: MT5TradingBot instance
        symbol (str): Trading symbol
        signal (int): Trade signal (1 or -1)
        df (pd.DataFrame): Price data with indicators
        
    Returns:
        dict: Adaptive trade parameters or None if trade rejected
    """
    # Initialize adaptive risk manager
    risk_manager = AdaptiveRiskManager(bot.config)
    
    # Analyze market condition
    market_condition = risk_manager.analyze_market_condition(df)
    
    if market_condition is None:
        logging.warning("Insufficient data for adaptive risk analysis")
        return None
    
    # Check if we should take the trade
    should_trade, confidence = risk_manager.should_take_trade(market_condition, signal)
    
    if not should_trade:
        logging.info(f"Trade rejected by adaptive risk manager (Confidence: {confidence:.2f})")
        return None
    
    # Get current prices
    tick = mt5.symbol_info_tick(symbol)
    entry_price = tick.ask if signal == 1 else tick.bid
    
    # Calculate adaptive stop loss
    stop_loss = risk_manager.calculate_adaptive_stop_loss(
        entry_price, signal, df, market_condition
    )
    
    # Calculate adaptive take profit levels
    tp_prices, allocations = risk_manager.calculate_adaptive_take_profit(
        entry_price, stop_loss, signal, df, market_condition
    )
    
    # Get adaptive trailing parameters
    trailing_params = risk_manager.calculate_adaptive_trailing_params(market_condition)
    
    # Calculate risk adjustment
    risk_multiplier = risk_manager.should_reduce_risk(market_condition)
    
    # Return all adaptive parameters
    return {
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'tp_prices': tp_prices,
        'allocations': allocations,
        'trailing_params': trailing_params,
        'risk_multiplier': risk_multiplier,
        'confidence': confidence,
        'market_condition': market_condition
    }


if __name__ == "__main__":
    print("Adaptive Risk Management Module")
    print("=" * 70)
    print("\nThis module dynamically adjusts:")
    print("  ✓ Stop Loss placement based on market volatility and structure")
    print("  ✓ Take Profit levels based on trend strength and momentum")
    print("  ✓ Trailing stop parameters based on market type")
    print("  ✓ Position size based on market favorability")
    print("  ✓ Trade filtering based on confidence scores")
    print("\nImport this module into your main bot for adaptive risk management!")
