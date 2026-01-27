"""
Dynamic Take Profit Manager
Extends take profit targets in real-time based on trend strength and momentum
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging
from datetime import datetime


class DynamicTPManager:
    """
    Manages dynamic take profit adjustments based on:
    - Trend strength (strong trends = extend TP)
    - Momentum (accelerating = extend TP)
    - Market structure (breakouts = extend TP)
    - Volatility (expansion = extend TP)
    - Price action (continuation patterns = extend TP)
    """
    
    def __init__(self, config):
        self.config = config
        self.atr_period = config.get('atr_period', 14)
        self.fast_ma_period = config.get('fast_ma_period', 10)
        self.slow_ma_period = config.get('slow_ma_period', 20)
        
        # Track TP adjustments
        self.tp_history = {}  # ticket: [list of TP adjustments]
        
    def should_extend_take_profit(self, position, df, market_condition):
        """
        Determine if take profit should be extended based on trend strength
        
        Args:
            position: MT5 position object
            df (pd.DataFrame): Current price data with indicators
            market_condition (dict): Current market analysis
            
        Returns:
            tuple: (should_extend, new_tp, reason)
        """
        ticket = position.ticket
        symbol = position.symbol
        direction = 1 if position.type == mt5.ORDER_TYPE_BUY else -1
        current_tp = position.tp
        entry_price = position.price_open
        current_price = position.price_current
        current_profit = position.profit
        
        # Get latest data
        latest = df.iloc[-1]
        current_atr = latest['atr']
        
        # Initialize tracking if needed
        if ticket not in self.tp_history:
            self.tp_history[ticket] = [{
                'time': datetime.now(),
                'tp': current_tp,
                'reason': 'initial'
            }]
        
        # Only extend TP if position is profitable
        if current_profit <= 0:
            return False, current_tp, 'Position not profitable'
        
        # Check various conditions for TP extension
        extensions = []
        
        # 1. STRONG TREND CONTINUATION
        trend_strength = self.detect_trend_strength(df, market_condition, direction)
        if trend_strength == 'very_strong':
            new_tp = self.extend_for_strong_trend(
                entry_price, current_tp, direction, current_atr, multiplier=1.5
            )
            extensions.append(('strong_trend', new_tp, 'Very strong trend continuation'))
        elif trend_strength == 'strengthening':
            new_tp = self.extend_for_strong_trend(
                entry_price, current_tp, direction, current_atr, multiplier=1.3
            )
            extensions.append(('strengthening', new_tp, 'Trend strengthening'))
        
        # 2. MOMENTUM ACCELERATION
        momentum = self.detect_momentum_acceleration(df, direction)
        if momentum == 'accelerating':
            new_tp = self.extend_for_momentum(
                entry_price, current_tp, direction, current_atr, multiplier=1.4
            )
            extensions.append(('momentum', new_tp, 'Momentum accelerating'))
        
        # 3. BREAKOUT CONFIRMATION
        breakout = self.detect_breakout(df, direction)
        if breakout:
            new_tp = self.extend_for_breakout(
                entry_price, current_tp, direction, current_atr, breakout_level=breakout
            )
            extensions.append(('breakout', new_tp, f'Breakout confirmed at {breakout:.2f}'))
        
        # 4. VOLATILITY EXPANSION (in our favor)
        volatility_change = self.detect_favorable_volatility(df, direction)
        if volatility_change == 'expanding_favorable':
            new_tp = self.extend_for_volatility(
                entry_price, current_tp, direction, current_atr, multiplier=1.3
            )
            extensions.append(('volatility', new_tp, 'Favorable volatility expansion'))
        
        # 5. PRICE ACTION CONTINUATION PATTERNS
        continuation = self.detect_continuation_pattern(df, direction)
        if continuation:
            new_tp = self.extend_for_continuation(
                entry_price, current_tp, direction, current_atr, multiplier=1.2
            )
            extensions.append(('continuation', new_tp, f'{continuation} pattern detected'))
        
        # 6. SUPPORT/RESISTANCE CLEARED
        sr_cleared = self.detect_sr_clearance(df, direction)
        if sr_cleared:
            new_tp = self.extend_beyond_sr(
                current_tp, direction, current_atr, sr_level=sr_cleared
            )
            extensions.append(('sr_cleared', new_tp, f'S/R cleared at {sr_cleared:.2f}'))
        
        # 7. TREND CONSISTENCY IMPROVEMENT
        consistency_change = self.detect_consistency_improvement(market_condition)
        if consistency_change:
            new_tp = self.extend_for_consistency(
                entry_price, current_tp, direction, current_atr, multiplier=1.2
            )
            extensions.append(('consistency', new_tp, 'Trend consistency improved'))
        
        # Select best extension (most aggressive = furthest from current price)
        if extensions:
            best_extension = self.select_best_extension(
                extensions, current_tp, current_price, direction
            )
            
            if best_extension:
                reason_type, new_tp, reason_text = best_extension
                
                # Validate the new TP
                if self.validate_tp_extension(current_tp, new_tp, current_price, direction):
                    # Log the extension
                    self.tp_history[ticket].append({
                        'time': datetime.now(),
                        'tp': new_tp,
                        'reason': reason_text
                    })
                    
                    return True, new_tp, reason_text
        
        return False, current_tp, 'No extension needed'
    
    def detect_trend_strength(self, df, market_condition, direction, lookback=20):
        """Detect if trend is very strong and continuing"""
        if not market_condition:
            return None
        
        market_type = market_condition.get('market_type', 'ranging')
        trend_direction = market_condition.get('trend_direction', 0)
        trend_consistency = market_condition.get('trend_consistency', 50)
        trend_strength = market_condition.get('trend_strength', 20)
        
        # Check if trend aligns with position
        if direction != trend_direction:
            return None
        
        # Very strong trend
        if market_type == 'strong_trend' and trend_consistency > 85 and trend_strength > 30:
            return 'very_strong'
        
        # Strengthening trend
        if market_type == 'strong_trend' and trend_consistency > 70:
            # Check if consistency is improving
            if len(df) >= lookback * 2:
                recent_consistency = self.calculate_trend_consistency(df.tail(lookback))
                older_consistency = self.calculate_trend_consistency(
                    df.tail(lookback * 2).head(lookback)
                )
                if recent_consistency > older_consistency + 10:
                    return 'strengthening'
        
        return None
    
    def calculate_trend_consistency(self, df):
        """Calculate trend consistency for a dataframe segment"""
        if len(df) < 2:
            return 50.0
        
        current_trend = df['ma_trend'].iloc[-1]
        consistency = (df['ma_trend'] == current_trend).sum() / len(df) * 100
        return consistency
    
    def detect_momentum_acceleration(self, df, direction, lookback=10):
        """Detect if momentum is accelerating in our direction"""
        if len(df) < lookback * 2:
            return None
        
        # Calculate recent price changes
        recent = df.tail(lookback)
        older = df.tail(lookback * 2).head(lookback)
        
        recent_change = abs(recent['close'].iloc[-1] - recent['close'].iloc[0])
        older_change = abs(older['close'].iloc[-1] - older['close'].iloc[0])
        
        # Check if recent movement is accelerating
        if recent_change > older_change * 1.5:  # 50% faster
            # Verify direction matches position
            if direction == 1 and recent['close'].iloc[-1] > recent['close'].iloc[0]:
                return 'accelerating'
            elif direction == -1 and recent['close'].iloc[-1] < recent['close'].iloc[0]:
                return 'accelerating'
        
        return None
    
    def detect_breakout(self, df, direction, lookback=50):
        """Detect if price has broken out of recent range"""
        if len(df) < lookback:
            return None
        
        recent = df.tail(lookback)
        current_price = df['close'].iloc[-1]
        
        if direction == 1:  # Long position
            # Check if price broke above recent resistance
            resistance = recent['high'].nlargest(5).mean()
            if current_price > resistance * 1.002:  # 0.2% above
                return resistance
        
        else:  # Short position
            # Check if price broke below recent support
            support = recent['low'].nsmallest(5).mean()
            if current_price < support * 0.998:  # 0.2% below
                return support
        
        return None
    
    def detect_favorable_volatility(self, df, direction, lookback=20):
        """Detect volatility expansion in favorable direction"""
        if len(df) < lookback:
            return None
        
        recent_atr = df['atr'].tail(lookback)
        current_atr = df['atr'].iloc[-1]
        avg_atr = recent_atr.mean()
        
        # Check if volatility is expanding
        if current_atr > avg_atr * 1.3:  # 30% increase
            # Check if price is moving in our direction
            recent_bars = df.tail(5)
            if direction == 1:
                # Check for upward movement
                if recent_bars['close'].iloc[-1] > recent_bars['close'].iloc[0]:
                    return 'expanding_favorable'
            else:
                # Check for downward movement
                if recent_bars['close'].iloc[-1] < recent_bars['close'].iloc[0]:
                    return 'expanding_favorable'
        
        return None
    
    def detect_continuation_pattern(self, df, direction, lookback=20):
        """Detect bullish/bearish continuation patterns"""
        if len(df) < lookback:
            return None
        
        recent = df.tail(lookback)
        
        if direction == 1:  # Long position
            # Look for higher highs and higher lows
            highs = recent['high'].values
            lows = recent['low'].values
            
            higher_highs = sum(highs[i] > highs[i-1] for i in range(1, min(5, len(highs))))
            higher_lows = sum(lows[i] > lows[i-1] for i in range(1, min(5, len(lows))))
            
            if higher_highs >= 3 and higher_lows >= 3:
                return 'bullish_continuation'
        
        else:  # Short position
            # Look for lower highs and lower lows
            highs = recent['high'].values
            lows = recent['low'].values
            
            lower_highs = sum(highs[i] < highs[i-1] for i in range(1, min(5, len(highs))))
            lower_lows = sum(lows[i] < lows[i-1] for i in range(1, min(5, len(lows))))
            
            if lower_highs >= 3 and lower_lows >= 3:
                return 'bearish_continuation'
        
        return None
    
    def detect_sr_clearance(self, df, direction, lookback=50):
        """Detect if price has cleared significant S/R level"""
        if len(df) < lookback:
            return None
        
        recent = df.tail(lookback)
        current_price = df['close'].iloc[-1]
        
        if direction == 1:  # Long position
            # Find resistance levels
            resistance_levels = recent['high'].nlargest(10).values
            
            # Check if we've cleared any resistance
            for resistance in resistance_levels:
                if current_price > resistance * 1.001:  # 0.1% above
                    # Verify it was a significant level (price tested it multiple times)
                    tests = sum(abs(recent['high'] - resistance) / resistance < 0.002)
                    if tests >= 2:
                        return resistance
        
        else:  # Short position
            # Find support levels
            support_levels = recent['low'].nsmallest(10).values
            
            # Check if we've cleared any support
            for support in support_levels:
                if current_price < support * 0.999:  # 0.1% below
                    # Verify it was a significant level
                    tests = sum(abs(recent['low'] - support) / support < 0.002)
                    if tests >= 2:
                        return support
        
        return None
    
    def detect_consistency_improvement(self, market_condition):
        """Detect if trend consistency has improved significantly"""
        if not market_condition:
            return False
        
        trend_consistency = market_condition.get('trend_consistency', 50)
        
        # Very high consistency suggests strong trend continuation
        if trend_consistency > 80:
            return True
        
        return False
    
    def extend_for_strong_trend(self, entry_price, current_tp, direction, atr, multiplier=1.5):
        """Extend TP for strong trend continuation"""
        risk = abs(entry_price - (entry_price - (atr * 2.0)))  # Assume 2.0 ATR SL
        current_reward = abs(current_tp - entry_price)
        
        # Extend by multiplier
        new_reward = current_reward * multiplier
        
        if direction == 1:  # Long
            return entry_price + new_reward
        else:  # Short
            return entry_price - new_reward
    
    def extend_for_momentum(self, entry_price, current_tp, direction, atr, multiplier=1.4):
        """Extend TP for momentum acceleration"""
        current_reward = abs(current_tp - entry_price)
        new_reward = current_reward * multiplier
        
        if direction == 1:
            return entry_price + new_reward
        else:
            return entry_price - new_reward
    
    def extend_for_breakout(self, entry_price, current_tp, direction, atr, breakout_level):
        """Extend TP beyond breakout level"""
        # Extend TP to breakout level + 2× ATR
        if direction == 1:  # Long
            return max(current_tp, breakout_level + (atr * 2.0))
        else:  # Short
            return min(current_tp, breakout_level - (atr * 2.0))
    
    def extend_for_volatility(self, entry_price, current_tp, direction, atr, multiplier=1.3):
        """Extend TP for favorable volatility expansion"""
        current_reward = abs(current_tp - entry_price)
        new_reward = current_reward * multiplier
        
        if direction == 1:
            return entry_price + new_reward
        else:
            return entry_price - new_reward
    
    def extend_for_continuation(self, entry_price, current_tp, direction, atr, multiplier=1.2):
        """Extend TP for continuation pattern"""
        current_reward = abs(current_tp - entry_price)
        new_reward = current_reward * multiplier
        
        if direction == 1:
            return entry_price + new_reward
        else:
            return entry_price - new_reward
    
    def extend_beyond_sr(self, current_tp, direction, atr, sr_level):
        """Extend TP beyond cleared S/R level"""
        if direction == 1:  # Long
            # Extend to S/R + 1.5× ATR
            return max(current_tp, sr_level + (atr * 1.5))
        else:  # Short
            # Extend to S/R - 1.5× ATR
            return min(current_tp, sr_level - (atr * 1.5))
    
    def extend_for_consistency(self, entry_price, current_tp, direction, atr, multiplier=1.2):
        """Extend TP for improved trend consistency"""
        current_reward = abs(current_tp - entry_price)
        new_reward = current_reward * multiplier
        
        if direction == 1:
            return entry_price + new_reward
        else:
            return entry_price - new_reward
    
    def select_best_extension(self, extensions, current_tp, current_price, direction):
        """Select the most appropriate TP extension"""
        if not extensions:
            return None
        
        # Priority order for extensions
        priority = {
            'breakout': 1,           # Highest priority
            'strong_trend': 2,
            'momentum': 3,
            'sr_cleared': 4,
            'strengthening': 5,
            'volatility': 6,
            'continuation': 7,
            'consistency': 8         # Lowest priority
        }
        
        # Sort by priority
        sorted_extensions = sorted(
            extensions,
            key=lambda x: priority.get(x[0], 99)
        )
        
        # Return highest priority extension that extends TP furthest
        best = sorted_extensions[0]
        
        # Check if any other high-priority extension goes further
        for ext in sorted_extensions[1:3]:  # Check top 3
            if direction == 1:  # Long
                if ext[1] > best[1]:
                    best = ext
            else:  # Short
                if ext[1] < best[1]:
                    best = ext
        
        return best
    
    def validate_tp_extension(self, current_tp, new_tp, current_price, direction):
        """Validate that the new TP makes sense"""
        # TP should only move further away (extend), never closer
        if direction == 1:  # Long
            # New TP should be higher than current TP
            if new_tp <= current_tp:
                return False
            # New TP should be above current price
            if new_tp <= current_price:
                return False
        else:  # Short
            # New TP should be lower than current TP
            if new_tp >= current_tp:
                return False
            # New TP should be below current price
            if new_tp >= current_price:
                return False
        
        # Don't make tiny extensions (less than 0.5%)
        change_pct = abs(new_tp - current_tp) / current_tp * 100
        if change_pct < 0.5:
            return False
        
        # Don't extend too aggressively (max 100% extension at once)
        if change_pct > 100:
            return False
        
        return True
    
    def apply_dynamic_tp(self, position, new_tp, reason):
        """Apply the new take profit to the position"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position.ticket,
            "sl": position.sl,
            "tp": new_tp,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Dynamic TP extended for {position.symbol} (Ticket: {position.ticket})")
            logging.info(f"  Old TP: {position.tp:.2f} → New TP: {new_tp:.2f}")
            logging.info(f"  Extension: {abs(new_tp - position.tp):.2f} points")
            logging.info(f"  Reason: {reason}")
            return True
        else:
            logging.warning(f"Failed to extend dynamic TP: {result.comment}")
            return False


def integrate_dynamic_tp(bot, position, df, market_condition):
    """
    Integration function to use dynamic TP management in the main bot
    
    Args:
        bot: MT5TradingBot instance
        position: MT5 position object
        df (pd.DataFrame): Current price data
        market_condition (dict): Market analysis
        
    Returns:
        bool: True if TP was extended
    """
    # Initialize dynamic TP manager
    tp_manager = DynamicTPManager(bot.config)
    
    # Check if TP should be extended
    should_extend, new_tp, reason = tp_manager.should_extend_take_profit(
        position, df, market_condition
    )
    
    if should_extend:
        # Apply the extension
        success = tp_manager.apply_dynamic_tp(position, new_tp, reason)
        return success
    
    return False


if __name__ == "__main__":
    print("Dynamic Take Profit Manager")
    print("=" * 70)
    print("\nThis module dynamically extends take profit based on:")
    print("  ✓ Strong trend continuation")
    print("  ✓ Momentum acceleration")
    print("  ✓ Breakout confirmations")
    print("  ✓ Favorable volatility expansion")
    print("  ✓ Continuation patterns")
    print("  ✓ Support/Resistance clearance")
    print("  ✓ Trend consistency improvement")
    print("\nImport this module into your main bot for dynamic TP management!")
