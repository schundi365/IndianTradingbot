"""
Dynamic Stop Loss Manager
Updates stop loss in real-time based on trend changes and market structure
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging
from datetime import datetime


class DynamicSLManager:
    """
    Manages dynamic stop loss adjustments based on:
    - Trend changes (MA crossovers, trend reversals)
    - Market structure (swing highs/lows, support/resistance)
    - Volatility changes (ATR expansion/contraction)
    - Price action (breakouts, consolidations)
    """
    
    def __init__(self, config):
        self.config = config
        self.atr_period = config.get('atr_period', 14)
        self.fast_ma_period = config.get('fast_ma_period', 10)
        self.slow_ma_period = config.get('slow_ma_period', 20)
        
        # Track SL adjustments
        self.sl_history = {}  # ticket: [list of SL adjustments]
        
    def should_adjust_stop_loss(self, position, df, market_condition):
        """
        Determine if stop loss should be adjusted based on trend changes
        
        Args:
            position: MT5 position object
            df (pd.DataFrame): Current price data with indicators
            market_condition (dict): Current market analysis
            
        Returns:
            tuple: (should_adjust, new_sl, reason)
        """
        ticket = position.ticket
        symbol = position.symbol
        direction = 1 if position.type == mt5.ORDER_TYPE_BUY else -1
        current_sl = position.sl
        entry_price = position.price_open
        current_price = position.price_current
        
        # Get latest data
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest
        current_atr = latest['atr']
        
        # Initialize tracking if needed
        if ticket not in self.sl_history:
            self.sl_history[ticket] = [{
                'time': datetime.now(),
                'sl': current_sl,
                'reason': 'initial'
            }]
        
        # Check various conditions for SL adjustment
        adjustments = []
        
        # 1. TREND REVERSAL DETECTION
        trend_reversal = self.detect_trend_reversal(df, direction)
        if trend_reversal:
            new_sl = self.calculate_reversal_stop(
                entry_price, current_price, direction, current_atr
            )
            adjustments.append(('trend_reversal', new_sl, 'Trend reversal detected'))
        
        # 2. MA CROSSOVER (against position)
        ma_cross_against = self.detect_ma_crossover_against(latest, previous, direction)
        if ma_cross_against:
            new_sl = self.calculate_crossover_stop(
                entry_price, current_price, direction, current_atr
            )
            adjustments.append(('ma_crossover', new_sl, 'MA crossover against position'))
        
        # 3. VOLATILITY EXPANSION
        volatility_change = self.detect_volatility_change(df)
        if volatility_change == 'expansion':
            new_sl = self.widen_stop_for_volatility(
                current_sl, current_atr, direction
            )
            adjustments.append(('volatility_expansion', new_sl, 'Volatility expanding'))
        elif volatility_change == 'contraction':
            new_sl = self.tighten_stop_for_volatility(
                current_sl, current_price, current_atr, direction
            )
            adjustments.append(('volatility_contraction', new_sl, 'Volatility contracting'))
        
        # 4. SWING HIGH/LOW FORMATION
        swing_level = self.detect_swing_level(df, direction)
        if swing_level:
            new_sl = self.adjust_to_swing_level(
                swing_level, current_atr, direction
            )
            adjustments.append(('swing_level', new_sl, f'New swing level at {swing_level:.2f}'))
        
        # 5. SUPPORT/RESISTANCE BREAK
        sr_break = self.detect_sr_break(df, direction)
        if sr_break:
            new_sl = self.adjust_for_sr_break(
                sr_break, current_atr, direction
            )
            adjustments.append(('sr_break', new_sl, f'S/R break at {sr_break:.2f}'))
        
        # 6. TREND STRENGTH CHANGE
        trend_strength_change = self.detect_trend_strength_change(
            market_condition, direction
        )
        if trend_strength_change == 'strengthening':
            new_sl = self.widen_stop_for_strong_trend(
                current_sl, current_price, current_atr, direction
            )
            adjustments.append(('trend_strengthening', new_sl, 'Trend strengthening'))
        elif trend_strength_change == 'weakening':
            new_sl = self.tighten_stop_for_weak_trend(
                current_sl, current_price, current_atr, direction
            )
            adjustments.append(('trend_weakening', new_sl, 'Trend weakening'))
        
        # Select best adjustment (most conservative = closest to current price)
        if adjustments:
            best_adjustment = self.select_best_adjustment(
                adjustments, current_sl, current_price, direction
            )
            
            if best_adjustment:
                reason_type, new_sl, reason_text = best_adjustment
                
                # Validate the new SL
                if self.validate_sl_adjustment(current_sl, new_sl, current_price, direction):
                    # Log the adjustment
                    self.sl_history[ticket].append({
                        'time': datetime.now(),
                        'sl': new_sl,
                        'reason': reason_text
                    })
                    
                    return True, new_sl, reason_text
        
        return False, current_sl, 'No adjustment needed'
    
    def detect_trend_reversal(self, df, direction, lookback=10):
        """Detect if trend is reversing against the position"""
        if len(df) < lookback:
            return False
        
        recent = df.tail(lookback)
        
        # Check for trend reversal pattern
        if direction == 1:  # Long position
            # Look for lower highs and lower lows
            highs = recent['high'].values
            lower_highs = sum(highs[i] < highs[i-1] for i in range(1, len(highs)))
            
            # Also check MA trend
            ma_bearish = recent['ma_trend'].iloc[-1] == -1
            
            return lower_highs > lookback * 0.6 and ma_bearish
        
        else:  # Short position
            # Look for higher highs and higher lows
            lows = recent['low'].values
            higher_lows = sum(lows[i] > lows[i-1] for i in range(1, len(lows)))
            
            # Also check MA trend
            ma_bullish = recent['ma_trend'].iloc[-1] == 1
            
            return higher_lows > lookback * 0.6 and ma_bullish
    
    def detect_ma_crossover_against(self, latest, previous, direction):
        """Detect MA crossover against the position"""
        if direction == 1:  # Long position
            # Bearish crossover
            return (latest['fast_ma'] < latest['slow_ma'] and 
                    previous['fast_ma'] >= previous['slow_ma'])
        else:  # Short position
            # Bullish crossover
            return (latest['fast_ma'] > latest['slow_ma'] and 
                    previous['fast_ma'] <= previous['slow_ma'])
    
    def detect_volatility_change(self, df, lookback=20):
        """Detect significant volatility changes"""
        if len(df) < lookback:
            return None
        
        recent_atr = df['atr'].tail(lookback)
        current_atr = df['atr'].iloc[-1]
        avg_atr = recent_atr.mean()
        
        ratio = current_atr / avg_atr
        
        if ratio > 1.3:  # 30% increase
            return 'expansion'
        elif ratio < 0.7:  # 30% decrease
            return 'contraction'
        
        return None
    
    def detect_swing_level(self, df, direction, lookback=20):
        """Detect new swing high/low formation"""
        if len(df) < lookback:
            return None
        
        recent = df.tail(lookback)
        
        if direction == 1:  # Long position - look for swing lows
            # Find recent swing low
            swing_low = recent['low'].min()
            # Check if it's a significant level
            if swing_low < recent['low'].iloc[-1]:
                return swing_low
        
        else:  # Short position - look for swing highs
            # Find recent swing high
            swing_high = recent['high'].max()
            # Check if it's a significant level
            if swing_high > recent['high'].iloc[-1]:
                return swing_high
        
        return None
    
    def detect_sr_break(self, df, direction, lookback=50):
        """Detect support/resistance break"""
        if len(df) < lookback:
            return None
        
        recent = df.tail(lookback)
        current_price = df['close'].iloc[-1]
        
        if direction == 1:  # Long position
            # Look for support break (price breaking below support)
            support_levels = recent['low'].nsmallest(5).values
            for support in support_levels:
                if current_price < support * 0.999:  # 0.1% below support
                    return support
        
        else:  # Short position
            # Look for resistance break (price breaking above resistance)
            resistance_levels = recent['high'].nlargest(5).values
            for resistance in resistance_levels:
                if current_price > resistance * 1.001:  # 0.1% above resistance
                    return resistance
        
        return None
    
    def detect_trend_strength_change(self, market_condition, direction):
        """Detect if trend is strengthening or weakening"""
        if not market_condition:
            return None
        
        trend_direction = market_condition.get('trend_direction', 0)
        trend_consistency = market_condition.get('trend_consistency', 50)
        market_type = market_condition.get('market_type', 'ranging')
        
        # Check if trend aligns with position
        if direction == trend_direction:
            # Trend with us
            if market_type == 'strong_trend' and trend_consistency > 75:
                return 'strengthening'
            elif market_type in ['ranging', 'volatile']:
                return 'weakening'
        else:
            # Trend against us
            return 'weakening'
        
        return None
    
    def calculate_reversal_stop(self, entry_price, current_price, direction, atr):
        """Calculate stop loss for trend reversal - tighten significantly"""
        if direction == 1:  # Long
            # Move SL to just below current price
            return current_price - (atr * 0.5)
        else:  # Short
            return current_price + (atr * 0.5)
    
    def calculate_crossover_stop(self, entry_price, current_price, direction, atr):
        """Calculate stop loss for MA crossover - tighten moderately"""
        if direction == 1:  # Long
            return current_price - (atr * 1.0)
        else:  # Short
            return current_price + (atr * 1.0)
    
    def widen_stop_for_volatility(self, current_sl, atr, direction):
        """Widen stop loss when volatility expands"""
        if direction == 1:  # Long
            return current_sl - (atr * 0.5)  # Move SL further down
        else:  # Short
            return current_sl + (atr * 0.5)  # Move SL further up
    
    def tighten_stop_for_volatility(self, current_sl, current_price, atr, direction):
        """Tighten stop loss when volatility contracts"""
        if direction == 1:  # Long
            new_sl = current_price - (atr * 1.5)
            return max(new_sl, current_sl)  # Only move up
        else:  # Short
            new_sl = current_price + (atr * 1.5)
            return min(new_sl, current_sl)  # Only move down
    
    def adjust_to_swing_level(self, swing_level, atr, direction):
        """Adjust stop loss to swing level"""
        if direction == 1:  # Long
            return swing_level - (atr * 0.3)  # Just below swing low
        else:  # Short
            return swing_level + (atr * 0.3)  # Just above swing high
    
    def adjust_for_sr_break(self, sr_level, atr, direction):
        """Adjust stop loss when S/R breaks"""
        if direction == 1:  # Long - support broke
            return sr_level - (atr * 0.5)  # Below broken support
        else:  # Short - resistance broke
            return sr_level + (atr * 0.5)  # Above broken resistance
    
    def widen_stop_for_strong_trend(self, current_sl, current_price, atr, direction):
        """Widen stop when trend strengthens (give trade more room)"""
        if direction == 1:  # Long
            new_sl = current_price - (atr * 2.5)
            return min(new_sl, current_sl)  # Only move down (wider)
        else:  # Short
            new_sl = current_price + (atr * 2.5)
            return max(new_sl, current_sl)  # Only move up (wider)
    
    def tighten_stop_for_weak_trend(self, current_sl, current_price, atr, direction):
        """Tighten stop when trend weakens"""
        if direction == 1:  # Long
            new_sl = current_price - (atr * 1.0)
            return max(new_sl, current_sl)  # Only move up (tighter)
        else:  # Short
            new_sl = current_price + (atr * 1.0)
            return min(new_sl, current_sl)  # Only move down (tighter)
    
    def select_best_adjustment(self, adjustments, current_sl, current_price, direction):
        """Select the most appropriate SL adjustment"""
        if not adjustments:
            return None
        
        # Priority order for adjustments
        priority = {
            'trend_reversal': 1,      # Highest priority
            'ma_crossover': 2,
            'sr_break': 3,
            'swing_level': 4,
            'trend_weakening': 5,
            'volatility_contraction': 6,
            'trend_strengthening': 7,
            'volatility_expansion': 8  # Lowest priority
        }
        
        # Sort by priority
        sorted_adjustments = sorted(
            adjustments,
            key=lambda x: priority.get(x[0], 99)
        )
        
        # Return highest priority adjustment
        return sorted_adjustments[0]
    
    def validate_sl_adjustment(self, current_sl, new_sl, current_price, direction):
        """Validate that the new SL makes sense"""
        # Don't move SL in wrong direction
        if direction == 1:  # Long
            # SL should only move up (tighter) or stay same
            if new_sl < current_sl:
                return False  # Don't widen SL for long
            # Don't move SL above current price
            if new_sl >= current_price:
                return False
        else:  # Short
            # SL should only move down (tighter) or stay same
            if new_sl > current_sl:
                return False  # Don't widen SL for short
            # Don't move SL below current price
            if new_sl <= current_price:
                return False
        
        # Don't make tiny adjustments (less than 0.1%)
        change_pct = abs(new_sl - current_sl) / current_sl * 100
        if change_pct < 0.1:
            return False
        
        return True
    
    def apply_dynamic_sl(self, position, new_sl, reason):
        """Apply the new stop loss to the position"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position.ticket,
            "sl": new_sl,
            "tp": position.tp,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Dynamic SL updated for {position.symbol} (Ticket: {position.ticket})")
            logging.info(f"  Old SL: {position.sl:.2f} → New SL: {new_sl:.2f}")
            logging.info(f"  Reason: {reason}")
            return True
        else:
            logging.warning(f"Failed to update dynamic SL: {result.comment}")
            return False


def integrate_dynamic_sl(bot, position, df, market_condition):
    """
    Integration function to use dynamic SL management in the main bot
    
    Args:
        bot: MT5TradingBot instance
        position: MT5 position object
        df (pd.DataFrame): Current price data
        market_condition (dict): Market analysis
        
    Returns:
        bool: True if SL was adjusted
    """
    # Initialize dynamic SL manager
    sl_manager = DynamicSLManager(bot.config)
    
    # Check if SL should be adjusted
    should_adjust, new_sl, reason = sl_manager.should_adjust_stop_loss(
        position, df, market_condition
    )
    
    if should_adjust:
        # Apply the adjustment
        success = sl_manager.apply_dynamic_sl(position, new_sl, reason)
        return success
    
    return False


if __name__ == "__main__":
    print("Dynamic Stop Loss Manager")
    print("=" * 70)
    print("\nThis module dynamically adjusts stop loss based on:")
    print("  ✓ Trend reversals (MA crossovers, price action)")
    print("  ✓ Market structure (swing highs/lows)")
    print("  ✓ Support/Resistance breaks")
    print("  ✓ Volatility changes (ATR expansion/contraction)")
    print("  ✓ Trend strength changes")
    print("\nImport this module into your main bot for dynamic SL management!")
