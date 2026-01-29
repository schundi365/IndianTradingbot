"""
MT5 Gold & Silver Trading Bot
Automated trading with dynamic stop loss, trailing stops, and take profit
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

# Import adaptive risk management
try:
    from adaptive_risk_manager import AdaptiveRiskManager, integrate_adaptive_risk
    ADAPTIVE_RISK_AVAILABLE = True
except ImportError:
    ADAPTIVE_RISK_AVAILABLE = False
    logging.warning("Adaptive Risk Manager not available")

# Import volume analyzer
try:
    from volume_analyzer import VolumeAnalyzer
    VOLUME_ANALYZER_AVAILABLE = True
except ImportError:
    VOLUME_ANALYZER_AVAILABLE = False
    logging.warning("Volume Analyzer not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

class MT5TradingBot:
    def __init__(self, config):
        """
        Initialize the MT5 Trading Bot
        
        Args:
            config (dict): Configuration dictionary with trading parameters
        """
        self.config = config
        self.symbols = config['symbols']  # e.g., ['XAUUSD', 'XAGUSD']
        self.timeframe = config['timeframe']  # e.g., mt5.TIMEFRAME_H1
        self.magic_number = config['magic_number']
        self.lot_size = config['lot_size']
        
        # Risk management parameters
        self.risk_percent = config.get('risk_percent', 1.0)  # % of account to risk
        self.reward_ratio = config.get('reward_ratio', 2.0)  # Risk:Reward ratio
        
        # Moving average parameters
        self.fast_ma_period = config.get('fast_ma_period', 20)
        self.slow_ma_period = config.get('slow_ma_period', 50)
        self.atr_period = config.get('atr_period', 14)
        self.atr_multiplier = config.get('atr_multiplier', 2.0)
        
        # MACD parameters
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        
        # Trailing parameters
        self.trail_activation = config.get('trail_activation', 1.5)  # ATR multiplier to activate
        self.trail_distance = config.get('trail_distance', 1.0)  # ATR multiplier for trail distance
        
        # Split orders configuration
        self.use_split_orders = config.get('use_split_orders', True)
        self.num_positions = config.get('num_positions', 3)  # Split into 3 positions
        self.tp_levels = config.get('tp_levels', [1.5, 2.5, 4.0])  # R:R ratios for each TP
        self.partial_close_percent = config.get('partial_close_percent', [40, 30, 30])  # % of total for each level
        
        # Max lots per order
        self.max_lot_per_order = config.get('max_lot_per_order', 0.5)
        
        # Adaptive risk management
        self.use_adaptive_risk = config.get('use_adaptive_risk', True)
        if self.use_adaptive_risk and ADAPTIVE_RISK_AVAILABLE:
            self.adaptive_risk_manager = AdaptiveRiskManager(config)
            logging.info("Adaptive Risk Management enabled")
        else:
            self.adaptive_risk_manager = None
            if self.use_adaptive_risk and not ADAPTIVE_RISK_AVAILABLE:
                logging.warning("Adaptive Risk requested but module not available")
        
        # Volume analyzer
        self.use_volume_filter = config.get('use_volume_filter', True)
        if self.use_volume_filter and VOLUME_ANALYZER_AVAILABLE:
            self.volume_analyzer = VolumeAnalyzer(config)
            logging.info("Volume Analysis enabled")
        else:
            self.volume_analyzer = None
            if self.use_volume_filter and not VOLUME_ANALYZER_AVAILABLE:
                logging.warning("Volume filter requested but module not available")
        
        self.positions = {}
        self.split_position_groups = {}  # Track groups of split positions
        
    def connect(self):
        """Connect to MetaTrader5 with build 5549+ compatibility"""
        import os
        import platform
        
        # Try standard initialization first
        if not mt5.initialize():
            # Try alternative initialization for build 5549+
            if platform.system() == 'Windows':
                logging.info("Standard MT5 initialization failed, trying with path parameter...")
                
                # Try common MT5 installation paths
                username = os.environ.get('USERNAME', '')
                mt5_paths = [
                    r"C:\Program Files\MetaTrader 5\terminal64.exe",
                    r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
                ]
                
                # Try to find MT5 in user's AppData
                appdata = os.environ.get('APPDATA', '')
                if appdata:
                    import glob
                    terminal_paths = glob.glob(os.path.join(appdata, 'MetaQuotes', 'Terminal', '*', 'terminal64.exe'))
                    mt5_paths.extend(terminal_paths)
                
                initialized = False
                for path in mt5_paths:
                    if os.path.exists(path):
                        logging.info(f"Trying MT5 path: {path}")
                        if mt5.initialize(path=path):
                            logging.info(f"MT5 initialized successfully with path: {path}")
                            initialized = True
                            break
                
                if not initialized:
                    logging.error(f"MT5 initialization failed: {mt5.last_error()}")
                    logging.error("Tried paths: " + ", ".join(mt5_paths))
                    return False
            else:
                logging.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
        
        logging.info(f"MT5 initialized successfully")
        
        # Get version info
        version_info = mt5.version()
        if version_info:
            logging.info(f"MT5 version: {version_info}")
        
        # Get terminal info including build number
        terminal_info = mt5.terminal_info()
        if terminal_info:
            logging.info(f"MT5 build: {terminal_info.build}")
            logging.info(f"MT5 company: {terminal_info.company}")
            if terminal_info.build >= 5549:
                logging.info("MT5 build 5549+ detected - enhanced compatibility mode active")
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            logging.info(f"Account balance: {account_info.balance}")
            logging.info(f"Account equity: {account_info.equity}")
            logging.info(f"Account server: {account_info.server}")
        
        return True
    
    def disconnect(self):
        """Disconnect from MetaTrader5"""
        mt5.shutdown()
        logging.info("MT5 connection closed")
    
    def get_historical_data(self, symbol, timeframe, bars=200):
        """
        Fetch historical price data from MT5 with improved error handling
        
        Args:
            symbol (str): Trading symbol
            timeframe: MT5 timeframe constant
            bars (int): Number of bars to fetch
            
        Returns:
            pd.DataFrame: Historical price data
        """
        # Try up to 3 times with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            
            # Check error type
            error = mt5.last_error()
            error_code = error[0] if error else 0
            
            # If IPC error, try to reconnect
            if error_code == -10001:
                logging.warning(f"IPC error for {symbol}, attempting to reconnect MT5...")
                mt5.shutdown()
                time.sleep(2)
                if mt5.initialize():
                    logging.info("MT5 reconnected successfully")
                else:
                    logging.error("Failed to reconnect MT5")
            
            # If failed, log and retry
            if attempt < max_retries - 1:
                logging.warning(f"Failed to get data for {symbol} (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(2)  # Wait 2 seconds before retry (increased from 1)
            else:
                logging.error(f"Failed to get data for {symbol} after {max_retries} attempts. Error: {error}")
        
        return None
    
    def calculate_indicators(self, df):
        """
        Calculate technical indicators (Enhanced with RSI)
        
        Args:
            df (pd.DataFrame): Price data
            
        Returns:
            pd.DataFrame: Data with calculated indicators
        """
        # Moving Averages
        df['fast_ma'] = df['close'].rolling(window=self.fast_ma_period).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_ma_period).mean()
        
        # ATR (Average True Range) for volatility-based stops
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=self.atr_period).mean()
        
        # RSI (Relative Strength Index) - Popular filter for gold/silver
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Enhanced MACD (already configured in config, but calculate properly)
        ema_fast = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Trend direction
        df['ma_trend'] = np.where(df['fast_ma'] > df['slow_ma'], 1, -1)
        
        # MA crossover signals
        df['ma_cross'] = 0
        df.loc[(df['fast_ma'] > df['slow_ma']) & 
               (df['fast_ma'].shift(1) <= df['slow_ma'].shift(1)), 'ma_cross'] = 1  # Bullish cross
        df.loc[(df['fast_ma'] < df['slow_ma']) & 
               (df['fast_ma'].shift(1) >= df['slow_ma'].shift(1)), 'ma_cross'] = -1  # Bearish cross
        
        return df
    
    def calculate_stop_loss(self, entry_price, direction, atr):
        """
        Calculate stop loss based on ATR
        
        Args:
            entry_price (float): Entry price
            direction (int): 1 for buy, -1 for sell
            atr (float): Average True Range value
            
        Returns:
            float: Stop loss price
        """
        if direction == 1:  # Buy
            sl = entry_price - (self.atr_multiplier * atr)
        else:  # Sell
            sl = entry_price + (self.atr_multiplier * atr)
        
        return sl
    
    def calculate_take_profit(self, entry_price, stop_loss, direction):
        """
        Calculate take profit based on risk:reward ratio
        
        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            
        Returns:
            float: Take profit price
        """
        risk = abs(entry_price - stop_loss)
        reward = risk * self.reward_ratio
        
        if direction == 1:  # Buy
            tp = entry_price + reward
        else:  # Sell
            tp = entry_price - reward
        
        return tp
    
    def calculate_multiple_take_profits(self, entry_price, stop_loss, direction, ratios=None):
        """
        Calculate multiple take profit levels for partial closing
        
        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            ratios (list): List of risk:reward ratios (uses self.tp_levels if None)
            
        Returns:
            list: List of take profit prices
        """
        if ratios is None:
            ratios = self.tp_levels
        
        risk = abs(entry_price - stop_loss)
        tp_prices = []
        
        for ratio in ratios:
            reward = risk * ratio
            
            if direction == 1:  # Buy
                tp = entry_price + reward
            else:  # Sell
                tp = entry_price - reward
            
            tp_prices.append(tp)
        
        return tp_prices
    
    def calculate_position_size(self, symbol, entry_price, stop_loss):
        """
        Calculate position size based on risk percentage and available funds
        
        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            
        Returns:
            float: Total position size in lots
        """
        account_info = mt5.account_info()
        if not account_info:
            return self.lot_size
        
        # Use free margin instead of balance for more accurate available funds
        account_balance = account_info.balance
        free_margin = account_info.margin_free
        
        # Calculate based on risk percentage of balance
        risk_amount = account_balance * (self.risk_percent / 100)
        
        # Get symbol info for pip value calculation
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return self.lot_size
        
        pip_value = symbol_info.trade_tick_value
        stop_loss_pips = abs(entry_price - stop_loss) / symbol_info.point
        
        if stop_loss_pips == 0:
            return self.lot_size
        
        # Calculate lot size based on risk
        lot_size = risk_amount / (stop_loss_pips * pip_value)
        
        # Check if we have enough margin for this lot size
        # Estimate required margin
        leverage = account_info.leverage if account_info.leverage > 0 else 100
        contract_size = symbol_info.trade_contract_size
        estimated_margin = (lot_size * contract_size * entry_price) / leverage
        
        # If not enough margin, reduce lot size
        if estimated_margin > free_margin * 0.8:  # Use max 80% of free margin
            lot_size = (free_margin * 0.8 * leverage) / (contract_size * entry_price)
            logging.warning(f"Lot size reduced due to margin constraints: {lot_size:.2f}")
        
        # Round to symbol's volume step
        lot_size = round(lot_size / symbol_info.volume_step) * symbol_info.volume_step
        
        # Ensure within min/max limits
        lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        
        logging.info(f"Calculated lot size: {lot_size} (Balance: {account_balance}, Free Margin: {free_margin})")
        
        return lot_size
    
    def split_lot_size(self, total_lot_size, num_splits=None, percentages=None):
        """
        Split total lot size into smaller orders
        
        Args:
            total_lot_size (float): Total lot size to split
            num_splits (int): Number of splits (uses self.num_positions if None)
            percentages (list): Percentage allocation for each split (uses self.partial_close_percent if None)
            
        Returns:
            list: List of lot sizes for each split
        """
        if num_splits is None:
            num_splits = self.num_positions
        
        if percentages is None:
            percentages = self.partial_close_percent
        
        # Ensure percentages sum to 100
        if sum(percentages) != 100:
            # Normalize
            total = sum(percentages)
            percentages = [p / total * 100 for p in percentages]
        
        lot_sizes = []
        for i, percent in enumerate(percentages[:num_splits]):
            lot = total_lot_size * (percent / 100)
            
            # Ensure each lot doesn't exceed max per order
            if lot > self.max_lot_per_order:
                lot = self.max_lot_per_order
            
            # Round to volume step
            lot_sizes.append(lot)
        
        return lot_sizes
    
    def check_entry_signal(self, df):
        """
        Check for entry signals with RSI and MACD filtering
        
        Args:
            df (pd.DataFrame): Price data with indicators
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for no signal
        """
        if len(df) < 2:
            logging.debug("Not enough data for signal check (need at least 2 bars)")
            return 0
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        logging.debug(f"Signal Check - Close: {latest['close']:.5f}, Fast MA: {latest['fast_ma']:.5f}, Slow MA: {latest['slow_ma']:.5f}")
        
        # Check for MA crossover
        signal = 0
        if latest['ma_cross'] == 1:
            logging.info(f"✓ Bullish MA crossover detected")
            signal = 1
        elif latest['ma_cross'] == -1:
            logging.info(f"✓ Bearish MA crossover detected")
            signal = -1
        
        # Additional confirmation: price above/below both MAs
        if signal == 0:
            if (latest['close'] > latest['fast_ma'] and 
                latest['close'] > latest['slow_ma'] and 
                latest['ma_trend'] == 1 and previous['ma_trend'] == -1):
                logging.info(f"✓ Bullish trend confirmation (price above both MAs)")
                signal = 1
            elif (latest['close'] < latest['fast_ma'] and 
                  latest['close'] < latest['slow_ma'] and 
                  latest['ma_trend'] == -1 and previous['ma_trend'] == 1):
                logging.info(f"✓ Bearish trend confirmation (price below both MAs)")
                signal = -1
            else:
                logging.debug(f"No signal: Price={latest['close']:.5f}, Fast MA={latest['fast_ma']:.5f}, Slow MA={latest['slow_ma']:.5f}, Trend={latest['ma_trend']}")
        
        # Apply RSI filter (most popular enhancement)
        if signal != 0 and not pd.isna(latest['rsi']):
            rsi = latest['rsi']
            if signal == 1:  # BUY
                if rsi > 70:
                    logging.info(f"  ✗ RSI filter: Too overbought (RSI: {rsi:.1f}) - TRADE REJECTED")
                    return 0
                else:
                    logging.info(f"  ✓ RSI filter: OK (RSI: {rsi:.1f})")
            elif signal == -1:  # SELL
                if rsi < 30:
                    logging.info(f"  ✗ RSI filter: Too oversold (RSI: {rsi:.1f}) - TRADE REJECTED")
                    return 0
                else:
                    logging.info(f"  ✓ RSI filter: OK (RSI: {rsi:.1f})")
        
        # Apply MACD confirmation (second most popular)
        if signal != 0 and not pd.isna(latest['macd_histogram']):
            histogram = latest['macd_histogram']
            if signal == 1:  # BUY
                if histogram <= 0:
                    logging.info(f"  ✗ MACD filter: Histogram not positive ({histogram:.6f}) - TRADE REJECTED")
                    return 0
                else:
                    logging.info(f"  ✓ MACD filter: Confirmed ({histogram:.6f})")
            elif signal == -1:  # SELL
                if histogram >= 0:
                    logging.info(f"  ✗ MACD filter: Histogram not negative ({histogram:.6f}) - TRADE REJECTED")
                    return 0
                else:
                    logging.info(f"  ✓ MACD filter: Confirmed ({histogram:.6f})")
        
        if signal != 0:
            logging.info(f"{'BUY' if signal == 1 else 'SELL'} signal confirmed - All filters passed!")
        
        return signal
    
    def open_position(self, symbol, direction, entry_price, stop_loss, take_profit, lot_size):
        """
        Open a position in MT5 (single order - legacy method)
        
        Args:
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            take_profit (float): Take profit price
            lot_size (float): Position size
            
        Returns:
            bool: True if successful
        """
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logging.error(f"Symbol {symbol} not found")
            return False
        
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logging.error(f"Failed to select {symbol}")
                return False
        
        # Prepare request
        order_type = mt5.ORDER_TYPE_BUY if direction == 1 else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).ask if direction == 1 else mt5.symbol_info_tick(symbol).bid
        
        # Get correct filling mode for this symbol
        filling_mode = self.get_filling_mode(symbol)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,
            "magic": self.magic_number,
            "comment": f"MT5Bot_{direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Order failed: {result.retcode}, {result.comment}")
            return False
        
        logging.info(f"Position opened: {symbol} {direction} at {price}, SL: {stop_loss}, TP: {take_profit}")
        
        # Store position info for trailing
        self.positions[result.order] = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': price,
            'initial_sl': stop_loss,
            'initial_tp': take_profit,
            'ticket': result.order
        }
        
        return True
    
    def get_filling_mode(self, symbol):
        """
        Get the appropriate filling mode for the symbol
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            int: MT5 filling mode constant
        """
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return mt5.ORDER_FILLING_FOK
        
        # Check which filling modes are supported
        filling_mode = symbol_info.filling_mode
        
        # Try filling modes in order of preference
        if filling_mode & 1:  # FOK (Fill or Kill)
            return mt5.ORDER_FILLING_FOK
        elif filling_mode & 2:  # IOC (Immediate or Cancel)
            return mt5.ORDER_FILLING_IOC
        else:  # Return (market execution)
            return mt5.ORDER_FILLING_RETURN
    
    def open_split_positions(self, symbol, direction, entry_price, stop_loss, total_lot_size):
        """
        Open multiple positions with different take profit levels
        
        Args:
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            total_lot_size (float): Total lot size to split
            
        Returns:
            tuple: (success, group_id, tickets)
        """
        import uuid
        import time
        
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logging.error(f"Symbol {symbol} not found")
            return False, None, []
        
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logging.error(f"Failed to select {symbol}")
                return False, None, []
        
        # Calculate split lot sizes
        lot_sizes = self.split_lot_size(total_lot_size)
        
        # Calculate multiple TP levels
        tp_prices = self.calculate_multiple_take_profits(entry_price, stop_loss, direction)
        
        # Round prices
        digits = symbol_info.digits
        stop_loss = round(stop_loss, digits)
        tp_prices = [round(tp, digits) for tp in tp_prices]
        
        # Generate unique group ID for this set of positions
        group_id = str(uuid.uuid4())[:8]
        
        logging.info(f"Opening split positions for {symbol}:")
        logging.info(f"  Group ID: {group_id}")
        logging.info(f"  Total lots: {total_lot_size}, Split into: {lot_sizes}")
        logging.info(f"  TP levels: {tp_prices}")
        
        tickets = []
        order_type = mt5.ORDER_TYPE_BUY if direction == 1 else mt5.ORDER_TYPE_SELL
        
        # Get correct filling mode for this symbol
        filling_mode = self.get_filling_mode(symbol)
        
        # Open each position with its respective TP level
        for i, (lot, tp) in enumerate(zip(lot_sizes, tp_prices)):
            # Round lot size to volume step
            lot = round(lot / symbol_info.volume_step) * symbol_info.volume_step
            
            # Ensure within limits
            lot = max(symbol_info.volume_min, min(lot, symbol_info.volume_max))
            
            if lot < symbol_info.volume_min:
                logging.warning(f"Lot size {lot} too small for position {i+1}, skipping")
                continue
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            price = tick.ask if direction == 1 else tick.bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": order_type,
                "price": price,
                "sl": stop_loss,
                "tp": tp,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"MT5Bot_Split_{group_id}_{i+1}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Order {i+1} failed: {result.retcode}, {result.comment}")
                continue
            
            logging.info(f"  Position {i+1}: {lot} lots at {price}, TP: {tp} (Ticket: {result.order})")
            
            tickets.append(result.order)
            
            # Store position info
            self.positions[result.order] = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': price,
                'initial_sl': stop_loss,
                'initial_tp': tp,
                'ticket': result.order,
                'group_id': group_id,
                'position_number': i + 1,
                'total_positions': len(lot_sizes)
            }
            
            # Small delay between orders
            time.sleep(0.5)
        
        if len(tickets) == 0:
            logging.error("Failed to open any split positions")
            return False, None, []
        
        # Store group info
        self.split_position_groups[group_id] = {
            'symbol': symbol,
            'direction': direction,
            'tickets': tickets,
            'entry_price': entry_price,
            'initial_sl': stop_loss,
            'created_at': datetime.now()
        }
        
        logging.info(f"Successfully opened {len(tickets)} split positions (Group: {group_id})")
        return True, group_id, tickets
    
    def update_trailing_stop(self, position_ticket, symbol, direction):
        """
        Update trailing stop loss for an open position
        
        Args:
            position_ticket (int): Position ticket number
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            
        Returns:
            bool: True if updated
        """
        # Get current position
        positions = mt5.positions_get(ticket=position_ticket)
        if not positions or len(positions) == 0:
            return False
        
        position = positions[0]
        current_price = mt5.symbol_info_tick(symbol).bid if direction == 1 else mt5.symbol_info_tick(symbol).ask
        
        # Get current ATR
        df = self.get_historical_data(symbol, self.timeframe, 50)
        if df is None:
            return False
        
        df = self.calculate_indicators(df)
        current_atr = df.iloc[-1]['atr']
        
        entry_price = self.positions[position_ticket]['entry_price']
        initial_sl = self.positions[position_ticket]['initial_sl']
        
        # Check if trailing should be activated
        profit_in_atr = abs(current_price - entry_price) / current_atr
        
        if profit_in_atr < self.trail_activation:
            return False  # Not enough profit to activate trailing
        
        # Calculate new trailing stop
        if direction == 1:  # Buy position
            new_sl = current_price - (self.trail_distance * current_atr)
            if new_sl > position.sl:  # Only move SL up
                new_sl = round(new_sl, mt5.symbol_info(symbol).digits)
            else:
                return False
        else:  # Sell position
            new_sl = current_price + (self.trail_distance * current_atr)
            if new_sl < position.sl:  # Only move SL down
                new_sl = round(new_sl, mt5.symbol_info(symbol).digits)
            else:
                return False
        
        # Modify position
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position_ticket,
            "sl": new_sl,
            "tp": position.tp,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Trailing stop updated for {symbol}: New SL = {new_sl}")
            return True
        else:
            logging.warning(f"Failed to update trailing stop: {result.comment}")
            return False
    
    def update_group_trailing_stop(self, group_id):
        """
        Update trailing stop for all positions in a split position group
        Updates all positions together to maintain consistency
        
        Args:
            group_id (str): Group ID for split positions
            
        Returns:
            int: Number of positions updated
        """
        if group_id not in self.split_position_groups:
            return 0
        
        group = self.split_position_groups[group_id]
        symbol = group['symbol']
        direction = group['direction']
        tickets = group['tickets']
        
        # Get current data
        df = self.get_historical_data(symbol, self.timeframe, 50)
        if df is None:
            return 0
        
        df = self.calculate_indicators(df)
        current_atr = df.iloc[-1]['atr']
        
        tick = mt5.symbol_info_tick(symbol)
        current_price = tick.bid if direction == 1 else tick.ask
        entry_price = group['entry_price']
        
        # Check if trailing should activate
        profit_in_atr = abs(current_price - entry_price) / current_atr
        
        if profit_in_atr < self.trail_activation:
            return 0
        
        # Calculate new trailing stop (same for all positions in group)
        if direction == 1:  # Buy
            new_sl = current_price - (self.trail_distance * current_atr)
        else:  # Sell
            new_sl = current_price + (self.trail_distance * current_atr)
        
        new_sl = round(new_sl, mt5.symbol_info(symbol).digits)
        
        updated_count = 0
        
        # Update all positions in the group
        for ticket in tickets:
            positions = mt5.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                continue
            
            position = positions[0]
            
            # Only move SL in profitable direction
            should_update = False
            if direction == 1 and new_sl > position.sl:
                should_update = True
            elif direction == -1 and new_sl < position.sl:
                should_update = True
            
            if not should_update:
                continue
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "sl": new_sl,
                "tp": position.tp,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                updated_count += 1
        
        if updated_count > 0:
            logging.info(f"Group {group_id}: Updated trailing stop for {updated_count} positions to {new_sl}")
        
        return updated_count
    
    def manage_positions(self):
        """Check and manage all open positions with dynamic SL/TP"""
        positions = mt5.positions_get(magic=self.magic_number)
        
        if positions is None or len(positions) == 0:
            # Clean up tracking dictionaries if no positions
            self.cleanup_closed_positions()
            return
        
        # Track which groups we've already processed
        processed_groups = set()
        
        # Get list of open ticket numbers
        open_tickets = {pos.ticket for pos in positions}
        
        for position in positions:
            ticket = position.ticket
            symbol = position.symbol
            direction = 1 if position.type == mt5.ORDER_TYPE_BUY else -1
            
            try:
                # Verify position still exists before processing
                verify_position = mt5.positions_get(ticket=ticket)
                if not verify_position or len(verify_position) == 0:
                    logging.debug(f"Position {ticket} already closed, skipping update")
                    continue
                
                # Get current data and market condition for dynamic adjustments
                df = self.get_historical_data(symbol, self.timeframe, 100)
                if df is not None:
                    df = self.calculate_indicators(df)
                    
                    # Get market condition if adaptive risk is enabled
                    market_condition = None
                    if self.use_adaptive_risk and self.adaptive_risk_manager:
                        market_condition = self.adaptive_risk_manager.analyze_market_condition(df)
                    
                    # Dynamic Stop Loss adjustment
                    if self.config.get('use_dynamic_sl', False):
                        try:
                            from src.dynamic_sl_manager import integrate_dynamic_sl
                            integrate_dynamic_sl(self, position, df, market_condition)
                        except Exception as e:
                            logging.debug(f"Dynamic SL not available: {str(e)}")
                    
                    # Dynamic Take Profit extension
                    if self.config.get('use_dynamic_tp', False) and position.profit > 0:
                        try:
                            from src.dynamic_tp_manager import integrate_dynamic_tp
                            integrate_dynamic_tp(self, position, df, market_condition)
                        except Exception as e:
                            logging.debug(f"Dynamic TP not available: {str(e)}")
                    
                    # Scalping Mode (M1 only) - Dynamic exits instead of fixed TP
                    if self.config.get('use_scalping_mode', False) and self.timeframe == mt5.TIMEFRAME_M1:
                        try:
                            from scalping_manager import integrate_scalping
                            # Returns True if position was closed
                            if integrate_scalping(self, position, df):
                                continue  # Position closed, skip trailing stop logic
                        except Exception as e:
                            logging.debug(f"Scalping mode not available: {str(e)}")
                
                # Standard trailing stop logic
                # Check if this is part of a split position group
                if ticket in self.positions and 'group_id' in self.positions[ticket]:
                    group_id = self.positions[ticket]['group_id']
                    
                    # Update entire group together (only once)
                    if group_id not in processed_groups:
                        self.update_group_trailing_stop(group_id)
                        processed_groups.add(group_id)
                else:
                    # Single position, update individually
                    self.update_trailing_stop(ticket, symbol, direction)
            except Exception as e:
                # More informative error message
                error_msg = str(e)
                if "not found" in error_msg.lower() or ticket == int(error_msg):
                    logging.debug(f"Position {ticket} closed during update, will clean up")
                else:
                    logging.warning(f"Error updating position {ticket} ({symbol}): {error_msg}")
                continue
        
        # Clean up closed positions and groups
        self.cleanup_closed_positions()
        self.cleanup_closed_groups()
    
    def cleanup_closed_groups(self):
        """Remove groups where all positions are closed"""
        groups_to_remove = []
        
        for group_id, group in self.split_position_groups.items():
            all_closed = True
            for ticket in group['tickets']:
                positions = mt5.positions_get(ticket=ticket)
                if positions and len(positions) > 0:
                    all_closed = False
                    break
            
            if all_closed:
                groups_to_remove.append(group_id)
        
        for group_id in groups_to_remove:
            del self.split_position_groups[group_id]
            logging.info(f"Cleaned up closed group: {group_id}")
    
    def cleanup_closed_positions(self):
        """Remove closed positions from tracking dictionary"""
        # Get all currently open positions
        open_positions = mt5.positions_get(magic=self.magic_number)
        
        if open_positions is None:
            open_tickets = set()
        else:
            open_tickets = {pos.ticket for pos in open_positions}
        
        # Find positions in tracking that are no longer open
        tickets_to_remove = []
        for ticket in self.positions.keys():
            if ticket not in open_tickets:
                tickets_to_remove.append(ticket)
        
        # Remove closed positions from tracking
        for ticket in tickets_to_remove:
            del self.positions[ticket]
            logging.debug(f"Cleaned up closed position: {ticket}")
        
        if len(tickets_to_remove) > 0:
            logging.info(f"Cleaned up {len(tickets_to_remove)} closed position(s)")
    
    def check_daily_loss_limit(self):
        """
        Check if daily loss limit has been exceeded
        
        Returns:
            bool: True if can continue trading, False if limit exceeded
        """
        from datetime import datetime, timedelta
        
        # Get account info
        account_info = mt5.account_info()
        if not account_info:
            return True  # Can't check, allow trading
        
        current_equity = account_info.equity
        
        # Get today's deals
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        deals = mt5.history_deals_get(today_start, datetime.now())
        
        if deals is None or len(deals) == 0:
            return True  # No deals today, can trade
        
        # Calculate today's profit/loss for bot trades only
        daily_pnl = 0.0
        for deal in deals:
            if deal.magic == self.magic_number:
                daily_pnl += deal.profit
        
        # Calculate loss percentage of current equity
        if daily_pnl < 0:
            loss_percent = abs(daily_pnl) / current_equity * 100
            
            max_loss_percent = self.config.get('max_daily_loss_percent', 5.0)
            
            if loss_percent >= max_loss_percent:
                logging.warning(f"Daily loss limit reached: {loss_percent:.2f}% (Max: {max_loss_percent}%)")
                logging.warning(f"Daily P/L: ${daily_pnl:.2f}, Equity: ${current_equity:.2f}")
                logging.warning(f"Trading paused for today. Will resume tomorrow.")
                return False
            
            # Log warning when approaching limit (at 80%)
            if loss_percent >= max_loss_percent * 0.8:
                logging.warning(f"Approaching daily loss limit: {loss_percent:.2f}% of {max_loss_percent}%")
                logging.warning(f"Daily P/L: ${daily_pnl:.2f}, Remaining: ${(max_loss_percent * current_equity / 100) - abs(daily_pnl):.2f}")
        
        return True
    
    def run_strategy(self, symbol):
        """
        Execute trading strategy for a symbol
        
        Args:
            symbol (str): Trading symbol
        """
        logging.debug(f"=" * 60)
        logging.debug(f"ANALYZING {symbol}")
        logging.debug(f"=" * 60)
        
        # Check daily loss limit before trading
        if not self.check_daily_loss_limit():
            logging.warning(f"Daily loss limit reached - skipping {symbol}")
            return
        
        # Check if already have maximum positions for this symbol
        positions = mt5.positions_get(symbol=symbol, magic=self.magic_number)
        max_per_symbol = self.config.get('max_trades_per_symbol', 1)
        
        if positions and len(positions) >= max_per_symbol:
            logging.debug(f"Already have {len(positions)} position(s) for {symbol} (Max: {max_per_symbol}) - skipping")
            return
        
        # Get data and calculate indicators
        logging.debug(f"Fetching historical data for {symbol}...")
        df = self.get_historical_data(symbol, self.timeframe)
        if df is None:
            logging.error(f"Failed to get data for {symbol}")
            return
        
        logging.debug(f"Calculating indicators for {symbol}...")
        df = self.calculate_indicators(df)
        
        # Check for entry signal
        logging.debug(f"Checking entry signals for {symbol}...")
        signal = self.check_entry_signal(df)
        
        if signal == 0:
            logging.debug(f"No entry signal for {symbol}")
            return  # No signal
        
        logging.info(f"{'BUY' if signal == 1 else 'SELL'} signal detected for {symbol}!")
        
        # === VOLUME ANALYSIS ===
        confidence_adjustment = 0.0
        if self.use_volume_filter and self.volume_analyzer:
            logging.info(f"Applying Volume Analysis for {symbol}")
            
            # Check if trade should be taken based on volume
            should_trade, volume_confidence = self.volume_analyzer.should_trade(
                df, 'buy' if signal == 1 else 'sell'
            )
            
            if not should_trade:
                logging.warning(f"✗ Trade REJECTED by volume filter for {symbol}")
                return
            
            # Apply confidence boost from volume analysis
            confidence_adjustment = volume_confidence
            logging.info(f"✓ Volume analysis passed - Confidence boost: {confidence_adjustment:+.2%}")
        
        # === ADAPTIVE RISK MANAGEMENT ===
        if self.use_adaptive_risk and self.adaptive_risk_manager:
            logging.info(f"Using Adaptive Risk Management for {symbol}")
            
            # Get adaptive parameters
            adaptive_params = integrate_adaptive_risk(self, symbol, signal, df)
            
            if adaptive_params is None:
                logging.info(f"Trade rejected by adaptive risk manager for {symbol}")
                return
            
            # Extract adaptive parameters
            entry_price = adaptive_params['entry_price']
            stop_loss = adaptive_params['stop_loss']
            tp_prices = adaptive_params['tp_prices']
            allocations = adaptive_params['allocations']
            trailing_params = adaptive_params['trailing_params']
            risk_multiplier = adaptive_params['risk_multiplier']
            confidence = adaptive_params['confidence']
            market_condition = adaptive_params['market_condition']
            
            # Apply volume confidence adjustment
            confidence += confidence_adjustment
            confidence = min(1.0, max(0.0, confidence))  # Clamp between 0 and 1
            
            # Adjust risk multiplier based on updated confidence
            if confidence >= 0.8:
                risk_multiplier = min(risk_multiplier * 1.1, self.config.get('max_risk_multiplier', 2.0))
            elif confidence < 0.5:
                risk_multiplier = max(risk_multiplier * 0.9, self.config.get('min_risk_multiplier', 0.5))
            
            logging.info(f"Adaptive Analysis:")
            logging.info(f"  Market Type: {market_condition['market_type']}")
            logging.info(f"  Trend Strength: {market_condition['trend_strength']:.1f}")
            logging.info(f"  Volatility Ratio: {market_condition['volatility_ratio']:.2f}")
            logging.info(f"  Trade Confidence: {confidence:.1%} (Volume boost: {confidence_adjustment:+.1%})")
            logging.info(f"  Risk Multiplier: {risk_multiplier:.2f}x")
            
            # Calculate position size with risk adjustment
            base_lot_size = self.calculate_position_size(symbol, entry_price, stop_loss)
            total_lot_size = base_lot_size * risk_multiplier
            
            # Update trailing parameters dynamically
            self.trail_activation = trailing_params['activation_atr']
            self.trail_distance = trailing_params['trail_distance_atr']
            
        else:
            # === STANDARD RISK MANAGEMENT ===
            logging.info(f"Using Standard Risk Management for {symbol}")
            
            # Get current price and ATR
            latest = df.iloc[-1]
            current_atr = latest['atr']
            tick = mt5.symbol_info_tick(symbol)
            entry_price = tick.ask if signal == 1 else tick.bid
            
            # Calculate SL
            stop_loss = self.calculate_stop_loss(entry_price, signal, current_atr)
            
            # Calculate position size
            total_lot_size = self.calculate_position_size(symbol, entry_price, stop_loss)
            
            # Use configured TP levels
            tp_prices = self.calculate_multiple_take_profits(entry_price, stop_loss, signal)
            allocations = self.partial_close_percent
        
        # Round prices
        digits = mt5.symbol_info(symbol).digits
        stop_loss = round(stop_loss, digits)
        
        logging.info(f"Signal for {symbol}: {'BUY' if signal == 1 else 'SELL'}")
        logging.info(f"Entry: {entry_price}, SL: {stop_loss}, Total Lots: {total_lot_size:.2f}")
        
        # Decide whether to use split orders
        if self.use_split_orders:
            # Round TP prices
            tp_prices_rounded = [round(tp, digits) for tp in tp_prices]
            
            logging.info(f"Using split orders strategy:")
            logging.info(f"  Take Profit levels: {tp_prices_rounded}")
            logging.info(f"  Allocations: {allocations}%")
            
            # Open split positions
            success, group_id, tickets = self.open_split_positions(
                symbol, signal, entry_price, stop_loss, total_lot_size
            )
            
            if success:
                logging.info(f"Split positions opened successfully (Group: {group_id})")
            else:
                logging.error(f"Failed to open split positions for {symbol}")
        else:
            # Use single position with one TP
            take_profit = self.calculate_take_profit(entry_price, stop_loss, signal)
            take_profit = round(take_profit, digits)
            
            logging.info(f"Using single position strategy")
            logging.info(f"  TP: {take_profit}")
            
            # Open single position
            self.open_position(symbol, signal, entry_price, stop_loss, take_profit, total_lot_size)
    
    def run(self):
        """Main bot loop"""
        if not self.connect():
            return
        
        logging.info("Trading bot started")
        logging.info(f"Trading symbols: {self.symbols}")
        logging.info(f"Timeframe: {self.timeframe}")
        
        try:
            while True:
                # Run strategy for each symbol
                for symbol in self.symbols:
                    try:
                        self.run_strategy(symbol)
                    except Exception as e:
                        logging.error(f"Error processing {symbol}: {str(e)}")
                        logging.debug(f"Traceback:", exc_info=True)
                
                # Manage existing positions (trailing stops)
                try:
                    self.manage_positions()
                except Exception as e:
                    logging.error(f"Error managing positions: {str(e)}")
                    logging.debug(f"Traceback:", exc_info=True)
                
                # Wait before next iteration
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        finally:
            self.disconnect()


if __name__ == "__main__":
    # Configuration
    config = {
        'symbols': ['XAUUSD', 'XAGUSD'],  # Gold and Silver
        'timeframe': mt5.TIMEFRAME_H1,  # 1-hour timeframe
        'magic_number': 234000,  # Unique identifier for bot's trades
        'lot_size': 0.01,  # Default lot size
        'risk_percent': 1.0,  # Risk 1% per trade
        'reward_ratio': 2.0,  # 1:2 risk/reward
        
        # Moving average parameters
        'fast_ma_period': 20,
        'slow_ma_period': 50,
        
        # ATR-based stops
        'atr_period': 14,
        'atr_multiplier': 2.0,  # SL = Entry ± 2*ATR
        
        # Trailing parameters
        'trail_activation': 1.5,  # Activate trailing after 1.5*ATR profit
        'trail_distance': 1.0,  # Trail at 1*ATR distance
    }
    
    # Create and run bot
    bot = MT5TradingBot(config)
    bot.run()
