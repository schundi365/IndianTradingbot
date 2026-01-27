"""
Advanced Trailing Strategies for MT5 Trading Bot
Different trailing stop and take profit methods
"""

import MetaTrader5 as mt5
import numpy as np


class TrailingStrategies:
    """Advanced trailing stop and take profit strategies"""
    
    @staticmethod
    def atr_trailing_stop(entry_price, current_price, atr, direction, multiplier=1.0):
        """
        ATR-based trailing stop
        
        Args:
            entry_price (float): Original entry price
            current_price (float): Current market price
            atr (float): Current ATR value
            direction (int): 1 for buy, -1 for sell
            multiplier (float): ATR multiplier for distance
            
        Returns:
            float: New stop loss price
        """
        if direction == 1:  # Buy
            new_sl = current_price - (multiplier * atr)
        else:  # Sell
            new_sl = current_price + (multiplier * atr)
        
        return new_sl
    
    @staticmethod
    def percentage_trailing_stop(entry_price, current_price, direction, trail_percent=2.0):
        """
        Percentage-based trailing stop
        
        Args:
            entry_price (float): Original entry price
            current_price (float): Current market price
            direction (int): 1 for buy, -1 for sell
            trail_percent (float): Percentage distance for trailing
            
        Returns:
            float: New stop loss price
        """
        trail_distance = current_price * (trail_percent / 100)
        
        if direction == 1:  # Buy
            new_sl = current_price - trail_distance
        else:  # Sell
            new_sl = current_price + trail_distance
        
        return new_sl
    
    @staticmethod
    def swing_high_low_trailing(df, direction, lookback=10):
        """
        Trail based on swing highs/lows
        
        Args:
            df (pd.DataFrame): Price data
            direction (int): 1 for buy, -1 for sell
            lookback (int): Number of bars to look back for swing points
            
        Returns:
            float: New stop loss based on swing points
        """
        if len(df) < lookback:
            return None
        
        recent_data = df.tail(lookback)
        
        if direction == 1:  # Buy - trail below swing low
            new_sl = recent_data['low'].min()
        else:  # Sell - trail above swing high
            new_sl = recent_data['high'].max()
        
        return new_sl
    
    @staticmethod
    def parabolic_sar_trailing(df):
        """
        Parabolic SAR-based trailing stop
        
        Args:
            df (pd.DataFrame): Price data with 'high', 'low', 'close'
            
        Returns:
            float: SAR value for trailing stop
        """
        # Simplified Parabolic SAR calculation
        af_start = 0.02
        af_increment = 0.02
        af_max = 0.2
        
        if len(df) < 2:
            return None
        
        # This is a simplified version - for production use a proper SAR library
        sar = df.iloc[-1]['low'] if df.iloc[-1]['close'] > df.iloc[-2]['close'] else df.iloc[-1]['high']
        
        return sar
    
    @staticmethod
    def step_trailing_stop(entry_price, current_price, direction, step_size=50, trail_distance=30):
        """
        Step-based trailing (moves in fixed pip increments)
        
        Args:
            entry_price (float): Original entry price
            current_price (float): Current market price
            direction (int): 1 for buy, -1 for sell
            step_size (float): Price movement required to adjust SL (in pips)
            trail_distance (float): Distance of SL from price (in pips)
            
        Returns:
            float: New stop loss price
        """
        pip_size = 0.0001  # For forex pairs, adjust for gold/silver
        
        profit = (current_price - entry_price) * direction
        steps = int(profit / (step_size * pip_size))
        
        if steps <= 0:
            return None
        
        if direction == 1:  # Buy
            new_sl = entry_price + (steps * step_size * pip_size) - (trail_distance * pip_size)
        else:  # Sell
            new_sl = entry_price - (steps * step_size * pip_size) + (trail_distance * pip_size)
        
        return new_sl
    
    @staticmethod
    def breakeven_plus_trailing(entry_price, current_price, direction, activation_pips=100, 
                                be_plus_pips=10, trail_start_pips=150):
        """
        Move to breakeven+, then start trailing
        
        Args:
            entry_price (float): Original entry price
            current_price (float): Current market price
            direction (int): 1 for buy, -1 for sell
            activation_pips (float): Pips profit to move to breakeven
            be_plus_pips (float): Pips beyond breakeven to set SL
            trail_start_pips (float): Pips profit to start normal trailing
            
        Returns:
            tuple: (new_sl, stage) - stage: 'initial', 'breakeven', 'trailing'
        """
        pip_size = 0.0001
        
        profit_pips = ((current_price - entry_price) * direction) / pip_size
        
        if profit_pips < activation_pips:
            return None, 'initial'
        elif profit_pips < trail_start_pips:
            # Move to breakeven + X pips
            if direction == 1:
                new_sl = entry_price + (be_plus_pips * pip_size)
            else:
                new_sl = entry_price - (be_plus_pips * pip_size)
            return new_sl, 'breakeven'
        else:
            # Start normal trailing
            return None, 'trailing'
    
    @staticmethod
    def chandelier_exit(df, atr_period=14, multiplier=3.0):
        """
        Chandelier Exit trailing stop
        
        Args:
            df (pd.DataFrame): Price data
            atr_period (int): ATR calculation period
            multiplier (float): ATR multiplier
            
        Returns:
            tuple: (long_stop, short_stop)
        """
        if len(df) < atr_period:
            return None, None
        
        # Calculate ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(atr_period).mean()
        
        # Chandelier Exit calculation
        highest_high = df['high'].rolling(atr_period).max()
        lowest_low = df['low'].rolling(atr_period).min()
        
        long_stop = highest_high.iloc[-1] - (multiplier * atr.iloc[-1])
        short_stop = lowest_low.iloc[-1] + (multiplier * atr.iloc[-1])
        
        return long_stop, short_stop


class DynamicTakeProfit:
    """Dynamic take profit strategies"""
    
    @staticmethod
    def scaling_out(entry_price, current_price, direction, targets=[1.5, 2.0, 3.0]):
        """
        Calculate multiple TP levels for scaling out
        
        Args:
            entry_price (float): Entry price
            current_price (float): Current price
            direction (int): 1 for buy, -1 for sell
            targets (list): List of risk:reward ratios
            
        Returns:
            list: List of TP prices
        """
        # This would be used with partial position closing
        # Returns multiple TP levels
        
        base_risk = abs(current_price - entry_price)
        tp_levels = []
        
        for ratio in targets:
            if direction == 1:
                tp = entry_price + (base_risk * ratio)
            else:
                tp = entry_price - (base_risk * ratio)
            tp_levels.append(tp)
        
        return tp_levels
    
    @staticmethod
    def resistance_support_tp(df, entry_price, direction, lookback=50):
        """
        Set TP at nearest significant resistance/support
        
        Args:
            df (pd.DataFrame): Price data
            entry_price (float): Entry price
            direction (int): 1 for buy, -1 for sell
            lookback (int): Bars to analyze
            
        Returns:
            float: Take profit level
        """
        if len(df) < lookback:
            return None
        
        recent = df.tail(lookback)
        
        if direction == 1:  # Buy - find resistance
            # Find swing highs
            resistance_levels = recent[recent['high'] > recent['high'].shift(1)]['high'].values
            resistance_levels = resistance_levels[resistance_levels > entry_price]
            
            if len(resistance_levels) > 0:
                return min(resistance_levels)  # Nearest resistance
        else:  # Sell - find support
            # Find swing lows
            support_levels = recent[recent['low'] < recent['low'].shift(1)]['low'].values
            support_levels = support_levels[support_levels < entry_price]
            
            if len(support_levels) > 0:
                return max(support_levels)  # Nearest support
        
        return None
    
    @staticmethod
    def trailing_take_profit(entry_price, highest_price, direction, trail_ratio=0.5, atr=None):
        """
        Trailing take profit (locks in profit as price moves favorably)
        
        Args:
            entry_price (float): Entry price
            highest_price (float): Highest favorable price reached
            direction (int): 1 for buy, -1 for sell
            trail_ratio (float): Percentage of profit to give back
            atr (float): Optional ATR for dynamic trailing
            
        Returns:
            float: New TP level
        """
        if atr:
            # ATR-based trailing TP
            if direction == 1:
                new_tp = highest_price - atr
            else:
                new_tp = highest_price + atr
        else:
            # Percentage-based trailing TP
            max_profit = abs(highest_price - entry_price)
            giveback = max_profit * trail_ratio
            
            if direction == 1:
                new_tp = highest_price - giveback
            else:
                new_tp = highest_price + giveback
        
        return new_tp


# Example usage functions
def apply_advanced_trailing(bot, position, strategy='atr'):
    """
    Apply advanced trailing strategy to a position
    
    Args:
        bot: MT5TradingBot instance
        position: Position object from MT5
        strategy (str): 'atr', 'percentage', 'swing', 'chandelier', 'breakeven'
    """
    symbol = position.symbol
    direction = 1 if position.type == mt5.ORDER_TYPE_BUY else -1
    
    # Get data
    df = bot.get_historical_data(symbol, bot.timeframe, 50)
    df = bot.calculate_indicators(df)
    
    current_price = mt5.symbol_info_tick(symbol).bid if direction == 1 else mt5.symbol_info_tick(symbol).ask
    atr = df.iloc[-1]['atr']
    
    new_sl = None
    
    if strategy == 'atr':
        new_sl = TrailingStrategies.atr_trailing_stop(
            position.price_open, current_price, atr, direction, multiplier=1.0
        )
    elif strategy == 'percentage':
        new_sl = TrailingStrategies.percentage_trailing_stop(
            position.price_open, current_price, direction, trail_percent=2.0
        )
    elif strategy == 'swing':
        new_sl = TrailingStrategies.swing_high_low_trailing(df, direction, lookback=10)
    elif strategy == 'chandelier':
        long_stop, short_stop = TrailingStrategies.chandelier_exit(df)
        new_sl = long_stop if direction == 1 else short_stop
    elif strategy == 'breakeven':
        new_sl, stage = TrailingStrategies.breakeven_plus_trailing(
            position.price_open, current_price, direction
        )
    
    return new_sl


if __name__ == "__main__":
    print("Advanced Trailing Strategies Module")
    print("Import this module into your main trading bot")
    print("\nAvailable strategies:")
    print("- ATR Trailing Stop")
    print("- Percentage Trailing Stop")
    print("- Swing High/Low Trailing")
    print("- Parabolic SAR Trailing")
    print("- Step Trailing")
    print("- Breakeven Plus Trailing")
    print("- Chandelier Exit")
    print("- Dynamic Take Profit with Scaling")
    print("- Resistance/Support TP")
    print("- Trailing Take Profit")
