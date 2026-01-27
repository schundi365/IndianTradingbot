"""
Scalping Manager for M1 Timeframe
Dynamic exit logic instead of fixed take profit levels
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging
import time


class ScalpingManager:
    """
    Manages scalping exits for M1 timeframe
    Uses dynamic logic instead of fixed TP levels
    """
    
    def __init__(self, config):
        self.config = config
        
        # Scalping parameters
        self.min_profit_pips = config.get('scalp_min_profit_pips', 20)  # Minimum 20 pips profit
        self.max_hold_time = config.get('scalp_max_hold_minutes', 30)  # Max 30 minutes
        self.trail_after_pips = config.get('scalp_trail_after_pips', 30)  # Trail after 30 pips
        self.trail_distance_pips = config.get('scalp_trail_distance_pips', 15)  # Trail 15 pips behind
        
        # Exit triggers
        self.use_momentum_exit = config.get('scalp_momentum_exit', True)
        self.use_reversal_exit = config.get('scalp_reversal_exit', True)
        self.use_time_exit = config.get('scalp_time_exit', True)
        
        # Track position entry times
        self.position_entry_times = {}
    
    def should_exit_position(self, position, df, current_price):
        """
        Determine if position should be closed based on scalping logic
        
        Args:
            position: MT5 position object
            df: Price data with indicators
            current_price: Current market price
            
        Returns:
            tuple: (should_exit, reason, exit_type)
        """
        if len(df) < 20:
            return False, None, None
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Calculate current profit in pips
        if position.type == mt5.ORDER_TYPE_BUY:
            profit_pips = (current_price - position.price_open) / 0.01  # Adjust for symbol
        else:  # SELL
            profit_pips = (position.price_open - current_price) / 0.01
        
        # Track entry time
        if position.ticket not in self.position_entry_times:
            self.position_entry_times[position.ticket] = time.time()
        
        hold_time_minutes = (time.time() - self.position_entry_times[position.ticket]) / 60
        
        # 1. MINIMUM PROFIT EXIT (Quick scalp)
        if profit_pips >= self.min_profit_pips:
            # Check for momentum weakening
            if self.use_momentum_exit and self._is_momentum_weakening(df, position.type):
                return True, f"Momentum weakening at +{profit_pips:.1f} pips", "momentum_exit"
            
            # Check for reversal signals
            if self.use_reversal_exit and self._is_reversal_signal(df, position.type):
                return True, f"Reversal signal at +{profit_pips:.1f} pips", "reversal_exit"
        
        # 2. TIME-BASED EXIT (Don't hold too long on M1)
        if self.use_time_exit and hold_time_minutes >= self.max_hold_time:
            if profit_pips > 0:
                return True, f"Time exit at +{profit_pips:.1f} pips ({hold_time_minutes:.1f}m)", "time_exit"
            elif profit_pips > -self.min_profit_pips:  # Small loss, cut it
                return True, f"Time exit at {profit_pips:.1f} pips ({hold_time_minutes:.1f}m)", "time_exit_loss"
        
        # 3. BREAKEVEN EXIT (Price returned to entry)
        if profit_pips < 5 and profit_pips > -5 and hold_time_minutes > 10:
            # Been in trade for 10+ minutes and back at breakeven - exit
            if self._is_momentum_weakening(df, position.type):
                return True, f"Breakeven exit after {hold_time_minutes:.1f}m", "breakeven_exit"
        
        # 4. STOP LOSS HIT (Let MT5 handle this, but log it)
        if position.type == mt5.ORDER_TYPE_BUY:
            if current_price <= position.sl:
                return False, None, None  # MT5 will close it
        else:
            if current_price >= position.sl:
                return False, None, None  # MT5 will close it
        
        return False, None, None
    
    def _is_momentum_weakening(self, df, position_type):
        """Check if momentum is weakening (MACD histogram declining)"""
        if 'macd_histogram' not in df.columns:
            return False
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        prev2 = df.iloc[-3]
        
        if position_type == mt5.ORDER_TYPE_BUY:
            # For BUY: Check if MACD histogram is declining
            if latest['macd_histogram'] < previous['macd_histogram'] < prev2['macd_histogram']:
                return True
            # Or if histogram turned negative
            if latest['macd_histogram'] < 0 and previous['macd_histogram'] > 0:
                return True
        else:  # SELL
            # For SELL: Check if MACD histogram is rising (less negative)
            if latest['macd_histogram'] > previous['macd_histogram'] > prev2['macd_histogram']:
                return True
            # Or if histogram turned positive
            if latest['macd_histogram'] > 0 and previous['macd_histogram'] < 0:
                return True
        
        return False
    
    def _is_reversal_signal(self, df, position_type):
        """Check for reversal signals (MA crossover against position)"""
        if 'fast_ma' not in df.columns or 'slow_ma' not in df.columns:
            return False
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        if position_type == mt5.ORDER_TYPE_BUY:
            # For BUY: Check if fast MA crossed below slow MA (bearish)
            if latest['fast_ma'] < latest['slow_ma'] and previous['fast_ma'] >= previous['slow_ma']:
                return True
            # Or if RSI turned overbought
            if 'rsi' in df.columns:
                if latest['rsi'] > 75:
                    return True
        else:  # SELL
            # For SELL: Check if fast MA crossed above slow MA (bullish)
            if latest['fast_ma'] > latest['slow_ma'] and previous['fast_ma'] <= previous['slow_ma']:
                return True
            # Or if RSI turned oversold
            if 'rsi' in df.columns:
                if latest['rsi'] < 25:
                    return True
        
        return False
    
    def calculate_trailing_stop(self, position, current_price, profit_pips):
        """
        Calculate trailing stop for scalping
        Only trail after minimum profit reached
        """
        if profit_pips < self.trail_after_pips:
            return position.sl  # Don't trail yet
        
        # Calculate trailing stop
        if position.type == mt5.ORDER_TYPE_BUY:
            # Trail below current price
            new_sl = current_price - (self.trail_distance_pips * 0.01)
            # Only move SL up, never down
            if new_sl > position.sl:
                return new_sl
        else:  # SELL
            # Trail above current price
            new_sl = current_price + (self.trail_distance_pips * 0.01)
            # Only move SL down, never up
            if new_sl < position.sl or position.sl == 0:
                return new_sl
        
        return position.sl
    
    def close_position(self, position, reason):
        """Close position with market order"""
        # Determine order type (opposite of position)
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
        else:
            order_type = mt5.ORDER_TYPE_BUY
        
        # Get current price
        tick = mt5.symbol_info_tick(position.symbol)
        if tick is None:
            logging.error(f"Failed to get tick for {position.symbol}")
            return False
        
        price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask
        
        # Create close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": position.magic,
            "comment": f"Scalp exit: {reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            profit = position.profit
            logging.info(f"Scalp exit: {position.symbol} (Ticket: {position.ticket})")
            logging.info(f"  Reason: {reason}")
            logging.info(f"  Profit: ${profit:.2f}")
            
            # Clean up entry time tracking
            if position.ticket in self.position_entry_times:
                del self.position_entry_times[position.ticket]
            
            return True
        else:
            logging.warning(f"Failed to close position: {result.comment}")
            return False


def integrate_scalping(bot, position, df):
    """
    Integration function to use scalping manager in main bot
    
    Args:
        bot: MT5TradingBot instance
        position: MT5 position object
        df: Price data with indicators
        
    Returns:
        bool: True if position was closed
    """
    # Only use scalping on M1 timeframe
    if bot.timeframe != mt5.TIMEFRAME_M1:
        return False
    
    # Initialize scalping manager if not exists
    if not hasattr(bot, 'scalping_manager'):
        bot.scalping_manager = ScalpingManager(bot.config)
    
    scalper = bot.scalping_manager
    
    # Get current price
    tick = mt5.symbol_info_tick(position.symbol)
    if tick is None:
        return False
    
    current_price = tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask
    
    # Check if should exit
    should_exit, reason, exit_type = scalper.should_exit_position(position, df, current_price)
    
    if should_exit:
        logging.info(f"Scalping exit triggered for {position.symbol}")
        logging.info(f"  Type: {exit_type}")
        return scalper.close_position(position, reason)
    
    # Update trailing stop if in profit
    if position.type == mt5.ORDER_TYPE_BUY:
        profit_pips = (current_price - position.price_open) / 0.01
    else:
        profit_pips = (position.price_open - current_price) / 0.01
    
    if profit_pips > scalper.trail_after_pips:
        new_sl = scalper.calculate_trailing_stop(position, current_price, profit_pips)
        
        if new_sl != position.sl:
            # Update stop loss
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position.ticket,
                "sl": new_sl,
                "tp": position.tp,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logging.info(f"Scalping trail updated for {position.symbol}")
                logging.info(f"  New SL: {new_sl:.2f} (trailing {scalper.trail_distance_pips} pips)")
    
    return False


# Example usage in main bot
if __name__ == "__main__":
    print("Scalping Manager for M1 Timeframe")
    print("=" * 60)
    print("\nScalping Exit Logic:")
    print("1. Momentum Exit - Close when momentum weakens after min profit")
    print("2. Reversal Exit - Close on MA crossover against position")
    print("3. Time Exit - Close after max hold time (30 min default)")
    print("4. Breakeven Exit - Close at breakeven if momentum weak")
    print("5. Trailing Stop - Trail after min profit reached")
    print("\nAdvantages over Fixed TP:")
    print("- Adapts to market conditions")
    print("- Captures more profit in strong trends")
    print("- Exits quickly when momentum fades")
    print("- Better for M1 scalping")
