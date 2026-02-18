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
import sys
from pathlib import Path

# Determine base directory (works for both script and executable)
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent.parent

# Log file path
LOG_FILE = BASE_DIR / 'trading_bot.log'

# Import adaptive risk management
try:
    from src.adaptive_risk_manager import AdaptiveRiskManager, integrate_adaptive_risk
    ADAPTIVE_RISK_AVAILABLE = True
except ImportError:
    ADAPTIVE_RISK_AVAILABLE = False
    logging.warning("Adaptive Risk Manager not available")

# Import volume analyzer
try:
    from src.volume_analyzer import VolumeAnalyzer
    VOLUME_ANALYZER_AVAILABLE = True
except ImportError:
    VOLUME_ANALYZER_AVAILABLE = False
    logging.warning("Volume Analyzer not available")

# Import trend detection engine
try:
    from src.trend_detection_engine import TrendDetectionEngine
    TREND_DETECTION_AVAILABLE = True
except ImportError:
    TREND_DETECTION_AVAILABLE = False
    logging.warning("Trend Detection Engine not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
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
        
        # Trend detection engine
        self.use_trend_detection = config.get('use_trend_detection', True)
        if self.use_trend_detection and TREND_DETECTION_AVAILABLE:
            self.trend_detection_engine = TrendDetectionEngine(config)
            logging.info("Advanced Trend Detection enabled")
        else:
            self.trend_detection_engine = None
            if self.use_trend_detection and not TREND_DETECTION_AVAILABLE:
                logging.warning("Trend detection requested but module not available")
        
        self.positions = {}
        self.split_position_groups = {}  # Track groups of split positions
        
        # Price level protection
        self.prevent_worse_entries = config.get('prevent_worse_entries', True)
        
    def check_existing_position_prices(self, symbol, signal):
        """
        Check existing position prices to prevent placing orders at worse levels
        
        Args:
            symbol (str): Trading symbol
            signal (int): 1 for BUY, -1 for SELL
            
        Returns:
            tuple: (can_trade, limit_price, reason)
                can_trade (bool): Whether new position can be placed
                limit_price (float): Price limit (highest buy or lowest sell)
                reason (str): Explanation message
        """
        if not self.prevent_worse_entries:
            return True, None, "Price level protection disabled"
        
        # Get existing positions for this symbol with our magic number
        positions = mt5.positions_get(symbol=symbol, magic=self.magic_number)
        
        if not positions or len(positions) == 0:
            return True, None, "No existing positions"
        
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return True, None, "Cannot get current price"
        
        current_price = tick.ask if signal == 1 else tick.bid
        
        if signal == 1:  # BUY signal
            # Find highest existing BUY position price
            buy_positions = [p for p in positions if p.type == mt5.POSITION_TYPE_BUY]
            
            if not buy_positions:
                return True, None, "No existing BUY positions"
            
            highest_buy_price = max(p.price_open for p in buy_positions)
            
            # Don't place BUY if current price is higher than highest existing BUY
            if current_price > highest_buy_price:
                reason = (f"Cannot place BUY at {current_price:.5f} - "
                         f"higher than highest existing BUY at {highest_buy_price:.5f}")
                logging.warning(f"🚫 PRICE LEVEL PROTECTION: {reason}")
                logging.info(f"   Existing BUY positions: {len(buy_positions)}")
                logging.info(f"   Highest BUY price: {highest_buy_price:.5f}")
                logging.info(f"   Current price: {current_price:.5f}")
                logging.info(f"   Difference: {(current_price - highest_buy_price):.5f} ({((current_price - highest_buy_price) / highest_buy_price * 100):.2f}%)")
                return False, highest_buy_price, reason
            else:
                return True, highest_buy_price, f"BUY allowed - below highest existing BUY at {highest_buy_price:.5f}"
        
        else:  # SELL signal
            # Find lowest existing SELL position price
            sell_positions = [p for p in positions if p.type == mt5.POSITION_TYPE_SELL]
            
            if not sell_positions:
                return True, None, "No existing SELL positions"
            
            lowest_sell_price = min(p.price_open for p in sell_positions)
            
            # Don't place SELL if current price is lower than lowest existing SELL
            if current_price < lowest_sell_price:
                reason = (f"Cannot place SELL at {current_price:.5f} - "
                         f"lower than lowest existing SELL at {lowest_sell_price:.5f}")
                logging.warning(f"🚫 PRICE LEVEL PROTECTION: {reason}")
                logging.info(f"   Existing SELL positions: {len(sell_positions)}")
                logging.info(f"   Lowest SELL price: {lowest_sell_price:.5f}")
                logging.info(f"   Current price: {current_price:.5f}")
                logging.info(f"   Difference: {(lowest_sell_price - current_price):.5f} ({((lowest_sell_price - current_price) / lowest_sell_price * 100):.2f}%)")
                return False, lowest_sell_price, reason
            else:
                return True, lowest_sell_price, f"SELL allowed - above lowest existing SELL at {lowest_sell_price:.5f}"
        
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
            
            # If IPC error (-10004 or -10001), try to reconnect
            if error_code in [-10004, -10001]:
                logging.warning(f"IPC connection error for {symbol} (code: {error_code}), attempting to reconnect MT5...")
                mt5.shutdown()
                time.sleep(2)
                if mt5.initialize():
                    logging.info("MT5 reconnected successfully")
                    continue  # Retry immediately after reconnect
                else:
                    logging.error("Failed to reconnect MT5")
                    return None
            
            # If failed, log and retry
            if attempt < max_retries - 1:
                logging.warning(f"Failed to get data for {symbol} (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(2)  # Wait 2 seconds before retry
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
    
    def calculate_price_from_pips(self, symbol, entry_price, pips, direction, is_sl=True):
        """
        Calculate price from pip value
        
        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price
            pips (float): Number of pips
            direction (int): 1 for buy, -1 for sell
            is_sl (bool): True for stop loss, False for take profit
            
        Returns:
            float: Calculated price
        """
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logging.error(f"Cannot get symbol info for {symbol}")
            return entry_price
        
        point = symbol_info.point
        digits = symbol_info.digits
        
        # For 5-digit and 3-digit brokers, multiply pips by 10 to get points
        # For 2-digit brokers (like gold), pips = points
        if digits == 5 or digits == 3:
            price_distance = pips * 10 * point
        else:
            price_distance = pips * point
        
        # Calculate price based on direction and whether it's SL or TP
        if direction == 1:  # Buy
            if is_sl:
                price = entry_price - price_distance
            else:  # TP
                price = entry_price + price_distance
        else:  # Sell
            if is_sl:
                price = entry_price + price_distance
            else:  # TP
                price = entry_price - price_distance
        
        return price
    
    def calculate_pips_from_price(self, symbol, price_difference):
        """
        Calculate pip value from price difference
        
        Args:
            symbol (str): Trading symbol
            price_difference (float): Difference in price units
            
        Returns:
            float: Difference in pips
        """
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return 0
        
        point = symbol_info.point
        digits = symbol_info.digits
        
        # Calculate points
        points = price_difference / point
        
        # For 5-digit and 3-digit brokers, divide by 10 to get actual pips
        if digits == 5 or digits == 3:
            pips = points / 10
        else:
            pips = points
        
        return pips
    
    def calculate_stop_loss(self, entry_price, direction, atr, symbol=None):
        """
        Calculate stop loss based on ATR or fixed pips
        
        Args:
            entry_price (float): Entry price
            direction (int): 1 for buy, -1 for sell
            atr (float): Average True Range value (in symbol's price units)
            symbol (str): Trading symbol (required for pip-based calculation)
            
        Returns:
            float: Stop loss price
        """
        # Check if using pip-based SL
        if self.config.get('use_pip_based_sl', False) and symbol:
            sl_pips = self.config.get('sl_pips', 50)
            return self.calculate_price_from_pips(symbol, entry_price, sl_pips, direction, is_sl=True)
        
        # Default: ATR-based SL
        if direction == 1:  # Buy
            sl = entry_price - (self.atr_multiplier * atr)
        else:  # Sell
            sl = entry_price + (self.atr_multiplier * atr)
        
        return sl
    
    def calculate_take_profit(self, entry_price, stop_loss, direction, symbol=None):
        """
        Calculate take profit based on risk:reward ratio or fixed pips
        
        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            symbol (str): Trading symbol (required for pip-based calculation)
            
        Returns:
            float: Take profit price
        """
        # Check if using pip-based TP
        if self.config.get('use_pip_based_tp', False) and symbol:
            tp_pips = self.config.get('tp_pips', 100)
            return self.calculate_price_from_pips(symbol, entry_price, tp_pips, direction, is_sl=False)
        
        # Default: Risk:reward ratio based TP
        risk = abs(entry_price - stop_loss)
        reward = risk * self.reward_ratio
        
        if direction == 1:  # Buy
            tp = entry_price + reward
        else:  # Sell
            tp = entry_price - reward
        
        return tp
    
    def calculate_multiple_take_profits(self, entry_price, stop_loss, direction, ratios=None, symbol=None):
        """
        Calculate multiple take profit levels for partial closing
        
        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            ratios (list): List of risk:reward ratios (uses self.tp_levels if None)
            symbol (str): Trading symbol (required for pip-based calculation)
            
        Returns:
            list: List of take profit prices
        """
        if ratios is None:
            ratios = self.tp_levels
        
        # Check if using pip-based TP
        if self.config.get('use_pip_based_tp', False) and symbol:
            tp_pips_base = self.config.get('tp_pips', 100)
            tp_prices = []
            
            # Calculate TP for each level using pip multipliers
            for i, ratio in enumerate(ratios):
                # Multiply base pips by the ratio
                tp_pips = tp_pips_base * ratio
                tp = self.calculate_price_from_pips(symbol, entry_price, tp_pips, direction, is_sl=False)
                tp_prices.append(tp)
                
                logging.info(f"  TP Level {i+1}: {tp_pips:.1f} pips (ratio {ratio}) = {tp:.5f}")
            
            return tp_prices
        
        # Default: Risk:reward ratio based TP
        risk = abs(entry_price - stop_loss)
        tp_prices = []
        
        logging.info(f"  Using ratio-based TP calculation:")
        logging.info(f"    Entry: {entry_price}, SL: {stop_loss}, Risk: {risk:.5f}")
        
        for i, ratio in enumerate(ratios):
            reward = risk * ratio
            
            if direction == 1:  # Buy
                tp = entry_price + reward
            else:  # Sell
                tp = entry_price - reward
            
            tp_prices.append(tp)
            logging.info(f"    TP Level {i+1}: ratio {ratio}, reward {reward:.5f} = {tp:.5f}")
        
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
    
    def get_trend_analysis(self, symbol, df=None):
        """
        Get comprehensive trend analysis for a symbol
        
        Args:
            symbol (str): Trading symbol
            df (pd.DataFrame, optional): Price data (will fetch if not provided)
            
        Returns:
            dict: Trend analysis results or None if trend detection disabled
        """
        if not self.trend_detection_engine:
            return None
        
        try:
            # Get price data if not provided
            if df is None:
                df = self.get_historical_data(symbol, self.timeframe, 200)
                if df is None or len(df) < 50:
                    logging.warning(f"Insufficient data for trend analysis of {symbol}")
                    return None
                
                # Calculate indicators
                df = self.calculate_indicators(df)
            
            # Get comprehensive trend analysis
            analysis_result = self.trend_detection_engine.analyze_trend_change(df, symbol)
            
            # Convert to dictionary for easier consumption
            trend_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'overall_confidence': analysis_result.confidence,
                'signals_count': len(analysis_result.signals),
                'signals': [],
                'market_structure': None,
                'divergences': [],
                'aroon_signal': None,
                'ema_signal': None,
                'trendline_breaks': [],
                'timeframe_alignment': None,
                'volume_confirmation': None,
                'early_warnings': []
            }
            
            # Process signals
            for signal in analysis_result.signals:
                trend_data['signals'].append({
                    'type': signal.signal_type,
                    'source': signal.source,
                    'confidence': signal.confidence,
                    'strength': signal.strength,
                    'price_level': signal.price_level,
                    'supporting_factors': signal.supporting_factors,
                    'timestamp': signal.timestamp.isoformat()
                })
            
            # Process market structure
            if analysis_result.market_structure:
                ms = analysis_result.market_structure
                trend_data['market_structure'] = {
                    'break_type': ms.break_type,
                    'break_level': ms.break_level,
                    'previous_level': ms.previous_level,
                    'volume_confirmation': ms.volume_confirmation,
                    'strength': ms.strength,
                    'confirmed': ms.confirmed
                }
            
            # Process divergences
            for div in analysis_result.divergences:
                trend_data['divergences'].append({
                    'type': div.divergence_type,
                    'indicator': div.indicator,
                    'strength': div.strength,
                    'validated': div.validated,
                    'price_points_count': len(div.price_points),
                    'indicator_points_count': len(div.indicator_points)
                })
            
            # Process Aroon signal
            if analysis_result.aroon_signal:
                aroon = analysis_result.aroon_signal
                trend_data['aroon_signal'] = {
                    'aroon_up': aroon.aroon_up,
                    'aroon_down': aroon.aroon_down,
                    'oscillator': aroon.oscillator,
                    'signal_type': aroon.signal_type,
                    'trend_strength': aroon.trend_strength
                }
            
            # Process EMA signal
            if analysis_result.ema_signal:
                ema = analysis_result.ema_signal
                trend_data['ema_signal'] = {
                    'signal_type': ema.signal_type,
                    'fast_ema': ema.fast_ema,
                    'slow_ema': ema.slow_ema,
                    'separation': ema.separation,
                    'momentum_strength': ema.momentum_strength,
                    'crossover_confirmed': ema.crossover_confirmed
                }
            
            # Process trendline breaks
            for tl_break in analysis_result.trendline_breaks:
                trend_data['trendline_breaks'].append({
                    'line_type': tl_break.trendline.line_type,
                    'break_point_price': tl_break.break_point[1],
                    'volume_confirmation': tl_break.volume_confirmation,
                    'retest_confirmed': tl_break.retest_confirmed,
                    'break_strength': tl_break.break_strength,
                    'trendline_strength': tl_break.trendline.strength,
                    'touch_points': tl_break.trendline.touch_points
                })
            
            # Process timeframe alignment
            if analysis_result.timeframe_alignment:
                mta = analysis_result.timeframe_alignment
                trend_data['timeframe_alignment'] = {
                    'primary_timeframe': mta.primary_timeframe,
                    'higher_timeframe': mta.higher_timeframe,
                    'alignment_score': mta.alignment_score,
                    'confirmation_level': mta.confirmation_level
                }
            
            # Process volume confirmation
            if analysis_result.volume_confirmation:
                vc = analysis_result.volume_confirmation
                trend_data['volume_confirmation'] = {
                    'volume_spike': vc.volume_spike,
                    'volume_ratio': vc.volume_ratio,
                    'strength': vc.strength
                }
            
            # Process early warnings
            for warning in analysis_result.early_warnings:
                trend_data['early_warnings'].append({
                    'warning_type': warning.warning_type,
                    'confidence': warning.confidence,
                    'probability_score': warning.probability_score,
                    'price_level': warning.price_level,
                    'current_price': warning.current_price,
                    'factors': warning.factors,
                    'strength': warning.strength,
                    'description': warning.description,
                    'timestamp': warning.timestamp.isoformat()
                })
            
            return trend_data
            
        except Exception as e:
            logging.error(f"Error getting trend analysis for {symbol}: {e}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def get_trend_summary(self, symbol, df=None):
        """
        Get a simplified trend summary for quick assessment
        
        Args:
            symbol (str): Trading symbol
            df (pd.DataFrame, optional): Price data (will fetch if not provided)
            
        Returns:
            dict: Simplified trend summary
        """
        trend_analysis = self.get_trend_analysis(symbol, df)
        
        if not trend_analysis:
            return {
                'symbol': symbol,
                'trend_available': False,
                'message': 'Trend detection not available'
            }
        
        # Determine overall trend direction
        bullish_signals = [s for s in trend_analysis['signals'] if 'bullish' in s['type']]
        bearish_signals = [s for s in trend_analysis['signals'] if 'bearish' in s['type']]
        
        if len(bullish_signals) > len(bearish_signals):
            trend_direction = 'bullish'
            signal_strength = sum(s['confidence'] * s['strength'] for s in bullish_signals) / len(bullish_signals) if bullish_signals else 0
        elif len(bearish_signals) > len(bullish_signals):
            trend_direction = 'bearish'
            signal_strength = sum(s['confidence'] * s['strength'] for s in bearish_signals) / len(bearish_signals) if bearish_signals else 0
        else:
            trend_direction = 'neutral'
            signal_strength = 0.5
        
        # Determine confidence level
        confidence = trend_analysis['overall_confidence']
        if confidence >= 0.8:
            confidence_level = 'high'
        elif confidence >= 0.6:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'
        
        # Key factors
        key_factors = []
        if trend_analysis['market_structure'] and trend_analysis['market_structure']['confirmed']:
            key_factors.append('structure_break')
        if trend_analysis['divergences']:
            key_factors.append('divergence')
        if trend_analysis['trendline_breaks']:
            key_factors.append('trendline_break')
        if trend_analysis['timeframe_alignment'] and trend_analysis['timeframe_alignment']['confirmation_level'] in ['strong', 'moderate']:
            key_factors.append('mtf_confirmation')
        
        return {
            'symbol': symbol,
            'trend_available': True,
            'trend_direction': trend_direction,
            'confidence': confidence,
            'confidence_level': confidence_level,
            'signal_strength': signal_strength,
            'signals_count': trend_analysis['signals_count'],
            'key_factors': key_factors,
            'early_warnings_count': len(trend_analysis['early_warnings']),
            'timestamp': trend_analysis['timestamp']
        }

    def check_entry_signal(self, df, symbol="unknown"):
        """
        Check for entry signals with RSI and MACD filtering
        WITH DETAILED CALCULATION LOGGING
        
        Args:
            df (pd.DataFrame): Price data with indicators
            symbol (str): Trading symbol for logging and trend detection
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for no signal
        """
        if len(df) < 2:
            logging.info("❌ Not enough data for signal check (need at least 2 bars)")
            return 0
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Log detailed market data
        logging.info("="*80)
        logging.info("📊 SIGNAL ANALYSIS - DETAILED CALCULATIONS")
        logging.info("="*80)
        logging.info(f"Current Price:     {latest['close']:.5f}")
        logging.info(f"Fast MA ({self.fast_ma_period}):      {latest['fast_ma']:.5f}")
        logging.info(f"Slow MA ({self.slow_ma_period}):      {latest['slow_ma']:.5f}")
        logging.info(f"MA Distance:       {abs(latest['fast_ma'] - latest['slow_ma']):.5f} points")
        logging.info(f"MA Position:       Fast {'ABOVE' if latest['fast_ma'] > latest['slow_ma'] else 'BELOW'} Slow")
        logging.info(f"Price vs Fast MA:  {latest['close'] - latest['fast_ma']:+.5f} ({'above' if latest['close'] > latest['fast_ma'] else 'below'})")
        logging.info(f"Price vs Slow MA:  {latest['close'] - latest['slow_ma']:+.5f} ({'above' if latest['close'] > latest['slow_ma'] else 'below'})")
        logging.info("-"*80)
        
        # ENHANCED SIGNAL GENERATION - Multiple Signal Types
        signal = 0
        signal_reason = ""
        
        # METHOD 1: MA CROSSOVER (Original - High Confidence)
        logging.info("🔍 METHOD 1: CHECKING MA CROSSOVER:")
        logging.info(f"  Previous: Fast MA={previous['fast_ma']:.5f}, Slow MA={previous['slow_ma']:.5f}")
        logging.info(f"  Current:  Fast MA={latest['fast_ma']:.5f}, Slow MA={latest['slow_ma']:.5f}")
        
        if latest['ma_cross'] == 1:
            logging.info(f"  ✅ BULLISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed ABOVE Slow MA")
            logging.info(f"     Previous: Fast {previous['fast_ma']:.5f} <= Slow {previous['slow_ma']:.5f}")
            logging.info(f"     Current:  Fast {latest['fast_ma']:.5f} > Slow {latest['slow_ma']:.5f}")
            signal = 1
            signal_reason = "MA Bullish Crossover"
        elif latest['ma_cross'] == -1:
            logging.info(f"  ✅ BEARISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed BELOW Slow MA")
            logging.info(f"     Previous: Fast {previous['fast_ma']:.5f} >= Slow {previous['slow_ma']:.5f}")
            logging.info(f"     Current:  Fast {latest['fast_ma']:.5f} < Slow {latest['slow_ma']:.5f}")
            signal = -1
            signal_reason = "MA Bearish Crossover"
        else:
            logging.info(f"  ❌ No crossover detected")
            logging.info(f"     MA Cross value: {latest['ma_cross']}")
        
        # METHOD 2: TREND CONFIRMATION (Original - High Confidence)
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 METHOD 2: CHECKING TREND CONFIRMATION:")
            logging.info(f"  Current MA Trend:  {latest['ma_trend']} (1=bullish, -1=bearish)")
            logging.info(f"  Previous MA Trend: {previous['ma_trend']}")
            logging.info(f"  Price > Fast MA:   {latest['close'] > latest['fast_ma']}")
            logging.info(f"  Price > Slow MA:   {latest['close'] > latest['slow_ma']}")
            logging.info(f"  Price < Fast MA:   {latest['close'] < latest['fast_ma']}")
            logging.info(f"  Price < Slow MA:   {latest['close'] < latest['slow_ma']}")
            
            if (latest['close'] > latest['fast_ma'] and 
                latest['close'] > latest['slow_ma'] and 
                latest['ma_trend'] == 1 and previous['ma_trend'] == -1):
                logging.info(f"  ✅ BULLISH TREND CONFIRMATION!")
                logging.info(f"     Price above both MAs AND trend changed to bullish")
                signal = 1
                signal_reason = "Bullish Trend Confirmation"
            elif (latest['close'] < latest['fast_ma'] and 
                  latest['close'] < latest['slow_ma'] and 
                  latest['ma_trend'] == -1 and previous['ma_trend'] == 1):
                logging.info(f"  ✅ BEARISH TREND CONFIRMATION!")
                logging.info(f"     Price below both MAs AND trend changed to bearish")
                signal = -1
                signal_reason = "Bearish Trend Confirmation"
            else:
                logging.info(f"  ❌ No trend confirmation")
                logging.info(f"     Conditions not met for trend-based signal")
        
        # METHOD 3: MOMENTUM SIGNALS (New - Medium Confidence)
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 METHOD 3: CHECKING MOMENTUM SIGNALS:")
            
            # Check if we have RSI and MACD data for momentum analysis
            if not pd.isna(latest['rsi']) and not pd.isna(latest['macd_histogram']):
                rsi = latest['rsi']
                macd_hist = latest['macd_histogram']
                macd_hist_prev = previous['macd_histogram'] if not pd.isna(previous['macd_histogram']) else 0
                
                logging.info(f"  RSI: {rsi:.2f}")
                logging.info(f"  MACD Histogram: {macd_hist:.6f}")
                logging.info(f"  MACD Hist Previous: {macd_hist_prev:.6f}")
                
                # BULLISH MOMENTUM: RSI oversold recovery + MACD turning positive
                if (rsi > 30 and rsi < 60 and  # RSI recovering from oversold
                    macd_hist > 0 and macd_hist > macd_hist_prev and  # MACD histogram improving
                    latest['close'] > latest['fast_ma'] and  # Price above fast MA
                    latest['fast_ma'] > latest['slow_ma']):  # Bullish MA alignment
                    
                    logging.info(f"  ✅ BULLISH MOMENTUM SIGNAL!")
                    logging.info(f"     RSI {rsi:.2f} recovering from oversold")
                    logging.info(f"     MACD histogram improving: {macd_hist:.6f} > {macd_hist_prev:.6f}")
                    logging.info(f"     Price above fast MA in bullish trend")
                    signal = 1
                    signal_reason = "Bullish Momentum Recovery"
                
                # BEARISH MOMENTUM: RSI overbought decline + MACD turning negative
                elif (rsi < 70 and rsi > 40 and  # RSI declining from overbought
                      macd_hist < 0 and macd_hist < macd_hist_prev and  # MACD histogram declining
                      latest['close'] < latest['fast_ma'] and  # Price below fast MA
                      latest['fast_ma'] < latest['slow_ma']):  # Bearish MA alignment
                    
                    logging.info(f"  ✅ BEARISH MOMENTUM SIGNAL!")
                    logging.info(f"     RSI {rsi:.2f} declining from overbought")
                    logging.info(f"     MACD histogram declining: {macd_hist:.6f} < {macd_hist_prev:.6f}")
                    logging.info(f"     Price below fast MA in bearish trend")
                    signal = -1
                    signal_reason = "Bearish Momentum Decline"
                else:
                    logging.info(f"  ❌ No momentum signal")
                    logging.info(f"     Momentum conditions not aligned")
            else:
                logging.info(f"  ⚠️  Insufficient data for momentum analysis")
        
        # METHOD 4: PULLBACK SIGNALS (New - Medium Confidence)
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 METHOD 4: CHECKING PULLBACK SIGNALS:")
            
            # Calculate price distance from MAs
            fast_ma_distance = (latest['close'] - latest['fast_ma']) / latest['fast_ma'] * 100
            slow_ma_distance = (latest['close'] - latest['slow_ma']) / latest['slow_ma'] * 100
            
            logging.info(f"  Price distance from Fast MA: {fast_ma_distance:+.3f}%")
            logging.info(f"  Price distance from Slow MA: {slow_ma_distance:+.3f}%")
            
            # BULLISH PULLBACK: Price near fast MA in uptrend
            if (latest['fast_ma'] > latest['slow_ma'] and  # Uptrend
                abs(fast_ma_distance) < 0.1 and  # Price very close to fast MA
                fast_ma_distance > -0.05 and  # Price not too far below
                slow_ma_distance > 0.05):  # Price still above slow MA
                
                logging.info(f"  ✅ BULLISH PULLBACK SIGNAL!")
                logging.info(f"     Price pulled back to fast MA in uptrend")
                logging.info(f"     Good entry point for trend continuation")
                signal = 1
                signal_reason = "Bullish Pullback to MA"
            
            # BEARISH PULLBACK: Price near fast MA in downtrend
            elif (latest['fast_ma'] < latest['slow_ma'] and  # Downtrend
                  abs(fast_ma_distance) < 0.1 and  # Price very close to fast MA
                  fast_ma_distance < 0.05 and  # Price not too far above
                  slow_ma_distance < -0.05):  # Price still below slow MA
                
                logging.info(f"  ✅ BEARISH PULLBACK SIGNAL!")
                logging.info(f"     Price pulled back to fast MA in downtrend")
                logging.info(f"     Good entry point for trend continuation")
                signal = -1
                signal_reason = "Bearish Pullback to MA"
            else:
                logging.info(f"  ❌ No pullback signal")
                logging.info(f"     Pullback conditions not met")
        
        # METHOD 5: BREAKOUT SIGNALS (New - High Confidence)
        if signal == 0 and len(df) >= 20:
            logging.info("-"*80)
            logging.info("🔍 METHOD 5: CHECKING BREAKOUT SIGNALS:")
            
            # Calculate recent high/low (last 10 bars)
            recent_bars = df.tail(10)
            recent_high = recent_bars['high'].max()
            recent_low = recent_bars['low'].min()
            current_price = latest['close']
            
            logging.info(f"  Recent High (10 bars): {recent_high:.5f}")
            logging.info(f"  Recent Low (10 bars):  {recent_low:.5f}")
            logging.info(f"  Current Price:         {current_price:.5f}")
            
            # BULLISH BREAKOUT: Price breaks above recent high
            if (current_price > recent_high and
                latest['fast_ma'] > latest['slow_ma'] and  # Bullish MA alignment
                current_price > latest['fast_ma']):  # Price above fast MA
                
                breakout_strength = (current_price - recent_high) / recent_high * 100
                logging.info(f"  ✅ BULLISH BREAKOUT SIGNAL!")
                logging.info(f"     Price broke above recent high")
                logging.info(f"     Breakout strength: {breakout_strength:+.3f}%")
                signal = 1
                signal_reason = "Bullish Breakout"
            
            # BEARISH BREAKOUT: Price breaks below recent low
            elif (current_price < recent_low and
                  latest['fast_ma'] < latest['slow_ma'] and  # Bearish MA alignment
                  current_price < latest['fast_ma']):  # Price below fast MA
                
                breakout_strength = (recent_low - current_price) / recent_low * 100
                logging.info(f"  ✅ BEARISH BREAKOUT SIGNAL!")
                logging.info(f"     Price broke below recent low")
                logging.info(f"     Breakout strength: {breakout_strength:+.3f}%")
                signal = -1
                signal_reason = "Bearish Breakout"
            else:
                logging.info(f"  ❌ No breakout signal")
                logging.info(f"     No significant breakout detected")
        
        # Final check - if still no signal
        if signal == 0:
            logging.info("-"*80)
            logging.info("❌ NO SIGNAL GENERATED")
            logging.info("   Checked 5 signal methods:")
            logging.info("   1. MA Crossover - No crossover")
            logging.info("   2. Trend Confirmation - No trend change")
            logging.info("   3. Momentum Signals - No momentum alignment")
            logging.info("   4. Pullback Signals - No pullback opportunity")
            logging.info("   5. Breakout Signals - No breakout detected")
            logging.info("   Market conditions not favorable for entry")
            logging.info("="*80)
            return 0
        
        # Log the successful signal
        logging.info("-"*80)
        logging.info(f"✅ SIGNAL GENERATED: {signal_reason}")
        logging.info("="*80)
        
        # Log signal detected
        signal_type = "BUY" if signal == 1 else "SELL"
        logging.info("-"*80)
        logging.info(f"🎯 {signal_type} SIGNAL DETECTED - Now checking filters...")
        logging.info("-"*80)
        
        # Apply RSI filter (most popular enhancement)
        logging.info("🔍 RSI FILTER CHECK:")
        if not pd.isna(latest['rsi']):
            rsi = latest['rsi']
            rsi_overbought = self.config.get('rsi_overbought', 70)
            rsi_oversold = self.config.get('rsi_oversold', 30)
            
            logging.info(f"  Current RSI: {rsi:.2f}")
            logging.info(f"  RSI Overbought threshold: {rsi_overbought}")
            logging.info(f"  RSI Oversold threshold: {rsi_oversold}")
            
            if signal == 1:  # BUY
                logging.info(f"  Checking BUY: RSI range 50-{rsi_overbought}")
                
                # Check if overbought (too high)
                if rsi > rsi_overbought:
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     RSI {rsi:.2f} is too overbought (>{rsi_overbought})")
                    logging.info(f"     Market may be overextended - skipping trade")
                    logging.info("="*80)
                    return 0
                
                # NEW: Check for minimum bullish strength (momentum confirmation)
                if rsi < 50:
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     RSI {rsi:.2f} is too weak for BUY (<50)")
                    logging.info(f"     Not enough bullish momentum - skipping trade")
                    logging.info("="*80)
                    return 0
                
                # RSI is in the sweet spot: 50-70 (or whatever overbought is set to)
                logging.info(f"  ✅ RSI FILTER PASSED!")
                logging.info(f"     RSI {rsi:.2f} shows good bullish momentum (50-{rsi_overbought})")
            elif signal == -1:  # SELL
                logging.info(f"  Checking SELL: RSI range {rsi_oversold}-50")
                
                # Check if oversold (too low)
                if rsi < rsi_oversold:
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     RSI {rsi:.2f} is too oversold (<{rsi_oversold})")
                    logging.info(f"     Market may be overextended - skipping trade")
                    logging.info("="*80)
                    return 0
                
                # NEW: Check for maximum bearish strength (momentum confirmation)
                if rsi > 50:
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     RSI {rsi:.2f} is too strong for SELL (>50)")
                    logging.info(f"     Not enough bearish momentum - skipping trade")
                    logging.info("="*80)
                    return 0
                
                # RSI is in the sweet spot: 30-50 (or whatever oversold is set to)
                logging.info(f"  ✅ RSI FILTER PASSED!")
                logging.info(f"     RSI {rsi:.2f} shows good bearish momentum ({rsi_oversold}-50)")
        else:
            logging.info(f"  ⚠️  RSI data not available - skipping RSI filter")
        
        # Apply MACD confirmation (second most popular) - ENHANCED WITH THRESHOLD
        logging.info("-"*80)
        logging.info("🔍 MACD FILTER CHECK:")
        
        # Check if MACD filter is enabled
        if not self.config.get('use_macd', True):
            logging.info("  ⚪ MACD filter: DISABLED (skipping check)")
        elif not pd.isna(latest['macd_histogram']):
            histogram = latest['macd_histogram']
            macd = latest['macd']
            macd_signal = latest['macd_signal']
            
            # Enhanced MACD with meaningful threshold
            MACD_THRESHOLD = self.config.get('macd_min_histogram', 0.0005)
            
            logging.info(f"  MACD Line:         {macd:.6f}")
            logging.info(f"  MACD Signal Line:  {macd_signal:.6f}")
            logging.info(f"  MACD Histogram:    {histogram:.6f}")
            logging.info(f"  MACD Threshold:    ±{MACD_THRESHOLD:.6f}")
            logging.info(f"  Histogram Position: {'POSITIVE' if histogram > 0 else 'NEGATIVE' if histogram < 0 else 'ZERO'}")
            
            if signal == 1:  # BUY
                logging.info(f"  Checking: Histogram {histogram:.6f} > {MACD_THRESHOLD:.6f}?")
                if histogram <= MACD_THRESHOLD:
                    logging.info(f"  ❌ MACD FILTER REJECTED!")
                    if histogram <= 0:
                        logging.info(f"     Histogram {histogram:.6f} is negative - contradicts BUY signal")
                    else:
                        logging.info(f"     Histogram {histogram:.6f} is too weak (≤{MACD_THRESHOLD:.6f})")
                        logging.info(f"     MACD momentum insufficient for reliable entry")
                    logging.info("="*80)
                    return 0
                else:
                    logging.info(f"  ✅ MACD FILTER PASSED!")
                    logging.info(f"     Histogram {histogram:.6f} shows strong bullish momentum")
                    logging.info(f"     MACD confirms BUY signal with sufficient strength")
            elif signal == -1:  # SELL
                logging.info(f"  Checking: Histogram {histogram:.6f} < -{MACD_THRESHOLD:.6f}?")
                if histogram >= -MACD_THRESHOLD:
                    logging.info(f"  ❌ MACD FILTER REJECTED!")
                    if histogram >= 0:
                        logging.info(f"     Histogram {histogram:.6f} is positive - contradicts SELL signal")
                    else:
                        logging.info(f"     Histogram {histogram:.6f} is too weak (≥-{MACD_THRESHOLD:.6f})")
                        logging.info(f"     MACD momentum insufficient for reliable entry")
                    logging.info("="*80)
                    return 0
                else:
                    logging.info(f"  ✅ MACD FILTER PASSED!")
                    logging.info(f"     Histogram {histogram:.6f} shows strong bearish momentum")
                    logging.info(f"     MACD confirms SELL signal with sufficient strength")
        else:
            logging.info(f"  ⚠️  MACD data not available - skipping MACD filter")
        
        # Apply ADX trend direction filter (MISSING FROM ORIGINAL - NOW ADDED)
        logging.info("-"*80)
        logging.info("🔍 ADX TREND DIRECTION FILTER:")
        if self.config.get('use_adx', True):
            # Calculate ADX and directional indicators if not already present
            if 'adx' not in df.columns:
                # Calculate ADX components
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                tr = df[['high_low', 'high_close', 'low_close']].max(axis=1)
                
                # Directional Movement
                plus_dm = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']), 
                                 np.maximum(df['high'] - df['high'].shift(), 0), 0)
                minus_dm = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()), 
                                  np.maximum(df['low'].shift() - df['low'], 0), 0)
                
                # Smooth the values
                adx_period = self.config.get('adx_period', 14)
                tr_smooth = pd.Series(tr).rolling(window=adx_period).mean()
                plus_dm_smooth = pd.Series(plus_dm).rolling(window=adx_period).mean()
                minus_dm_smooth = pd.Series(minus_dm).rolling(window=adx_period).mean()
                
                # Calculate DI
                df['plus_di'] = 100 * (plus_dm_smooth / tr_smooth)
                df['minus_di'] = 100 * (minus_dm_smooth / tr_smooth)
                
                # Calculate DX and ADX
                dx = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
                df['adx'] = dx.rolling(window=adx_period).mean()
            
            if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest.get('adx', 0)):
                adx = latest.get('adx', 0)
                plus_di = latest.get('plus_di', 0) if 'plus_di' in df.columns else 0 if 'plus_di' in df.columns else 0
                minus_di = latest.get('minus_di', 0) if 'minus_di' in df.columns else 0 if 'minus_di' in df.columns else 0
                
                ADX_THRESHOLD = self.config.get('adx_min_strength', 25)
                
                logging.info(f"  ADX (Trend Strength): {adx:.2f}")
                logging.info(f"  +DI (Bullish Force):  {plus_di:.2f}")
                logging.info(f"  -DI (Bearish Force):  {minus_di:.2f}")
                logging.info(f"  ADX Threshold:        {ADX_THRESHOLD}")
                
                if adx > ADX_THRESHOLD:
                    logging.info(f"  ✅ Strong trend detected (ADX {adx:.2f} > {ADX_THRESHOLD})")
                    
                    if signal == 1:  # BUY
                        if plus_di > minus_di:
                            di_diff = plus_di - minus_di
                            logging.info(f"  ✅ ADX FILTER PASSED!")
                            logging.info(f"     Strong bullish trend confirmed")
                            logging.info(f"     +DI {plus_di:.2f} > -DI {minus_di:.2f} (Difference: {di_diff:.2f})")
                            logging.info(f"     ADX {adx:.2f} confirms trend strength")
                        else:
                            di_diff = minus_di - plus_di
                            logging.info(f"  ❌ ADX FILTER REJECTED!")
                            logging.info(f"     Trend direction contradicts BUY signal")
                            logging.info(f"     -DI {minus_di:.2f} > +DI {plus_di:.2f} (Bearish by {di_diff:.2f})")
                            logging.info(f"     Strong bearish trend detected - cannot BUY")
                            logging.info("="*80)
                            return 0
                    elif signal == -1:  # SELL
                        if minus_di > plus_di:
                            di_diff = minus_di - plus_di
                            logging.info(f"  ✅ ADX FILTER PASSED!")
                            logging.info(f"     Strong bearish trend confirmed")
                            logging.info(f"     -DI {minus_di:.2f} > +DI {plus_di:.2f} (Difference: {di_diff:.2f})")
                            logging.info(f"     ADX {adx:.2f} confirms trend strength")
                        else:
                            di_diff = plus_di - minus_di
                            logging.info(f"  ❌ ADX FILTER REJECTED!")
                            logging.info(f"     Trend direction contradicts SELL signal")
                            logging.info(f"     +DI {plus_di:.2f} > -DI {minus_di:.2f} (Bullish by {di_diff:.2f})")
                            logging.info(f"     Strong bullish trend detected - cannot SELL")
                            logging.info("="*80)
                            return 0
                else:
                    logging.info(f"  ⚠️  Weak trend (ADX {adx:.2f} ≤ {ADX_THRESHOLD})")
                    logging.info(f"     Trend not strong enough for reliable directional filter")
                    logging.info(f"     Proceeding with caution - other filters must be strong")
            else:
                logging.info(f"  ⚠️  ADX data not available - skipping ADX filter")
        else:
            logging.info(f"  ⚠️  ADX filter disabled in configuration")
        
        # All filters passed
        logging.info("-"*80)
        
        # ADVANCED TREND DETECTION FILTER
        if self.trend_detection_engine and signal != 0:
            logging.info("🔍 ADVANCED TREND DETECTION FILTER:")
            signal_type_str = "buy" if signal == 1 else "sell"
            
            try:
                # Get comprehensive trend analysis
                trend_analysis = self.trend_detection_engine.analyze_trend_change(df, symbol)
                
                # Check if trend supports the signal
                should_trade, trend_confidence = self.trend_detection_engine.should_trade_trend(df, signal_type_str)
                
                if should_trade:
                    logging.info(f"  ✅ TREND DETECTION CONFIRMED!")
                    logging.info(f"     Trend analysis supports {signal_type_str.upper()} signal")
                    logging.info(f"     Overall trend confidence: {trend_confidence:.3f}")
                    logging.info(f"     Analysis confidence: {trend_analysis.confidence:.3f}")
                    
                    # Log detailed trend analysis results
                    if trend_analysis.signals:
                        logging.info(f"     Active trend signals ({len(trend_analysis.signals)}):")
                        for i, ts in enumerate(trend_analysis.signals[:3], 1):  # Show top 3
                            logging.info(f"       {i}. {ts.source}: {ts.signal_type}")
                            logging.info(f"          Confidence: {ts.confidence:.3f}, Strength: {ts.strength:.3f}")
                            logging.info(f"          Factors: {', '.join(ts.supporting_factors)}")
                    
                    # Log market structure analysis
                    if trend_analysis.market_structure:
                        ms = trend_analysis.market_structure
                        logging.info(f"     Market Structure: {ms.break_type}")
                        logging.info(f"       Break Level: {ms.break_level:.5f}")
                        logging.info(f"       Volume Confirmed: {ms.volume_confirmation}")
                        logging.info(f"       Strength: {ms.strength:.3f}")
                    
                    # Log divergence analysis
                    if trend_analysis.divergences:
                        logging.info(f"     Divergences detected ({len(trend_analysis.divergences)}):")
                        for div in trend_analysis.divergences:
                            logging.info(f"       - {div.divergence_type}: strength {div.strength:.3f}")
                    
                    # Log multi-timeframe confirmation
                    if trend_analysis.timeframe_alignment:
                        mta = trend_analysis.timeframe_alignment
                        logging.info(f"     Multi-Timeframe: {mta.confirmation_level}")
                        logging.info(f"       Primary: {mta.primary_timeframe}, Higher: {mta.higher_timeframe}")
                        logging.info(f"       Alignment Score: {mta.alignment_score:.3f}")
                    
                    # Log early warnings if any
                    if trend_analysis.early_warnings:
                        high_confidence_warnings = [w for w in trend_analysis.early_warnings if w.confidence >= 0.7]
                        if high_confidence_warnings:
                            logging.info(f"     Early Warnings ({len(high_confidence_warnings)} high confidence):")
                            for warning in high_confidence_warnings[:2]:  # Show top 2
                                logging.info(f"       - {warning.warning_type}: {warning.description}")
                                logging.info(f"         Confidence: {warning.confidence:.3f}")
                    
                    # Apply trend confidence boost to signal strength
                    if trend_confidence > 0.8:
                        logging.info(f"     🚀 HIGH CONFIDENCE TREND - Signal strength boosted!")
                    elif trend_confidence > 0.7:
                        logging.info(f"     📈 GOOD TREND CONFIRMATION - Signal validated")
                    else:
                        logging.info(f"     ✅ TREND CONFIRMATION - Minimum requirements met")
                        
                else:
                    logging.info(f"  ❌ TREND DETECTION REJECTED!")
                    logging.info(f"     Trend analysis does not support {signal_type_str.upper()} signal")
                    logging.info(f"     Trend confidence: {trend_confidence:.3f} (min required: {self.trend_detection_engine.min_confidence:.3f})")
                    
                    # Log why the trend detection failed
                    if trend_analysis.signals:
                        conflicting_signals = [s for s in trend_analysis.signals 
                                             if (signal == 1 and 'bearish' in s.signal_type) or 
                                                (signal == -1 and 'bullish' in s.signal_type)]
                        if conflicting_signals:
                            logging.info(f"     Conflicting trend signals detected:")
                            for cs in conflicting_signals:
                                logging.info(f"       - {cs.source}: {cs.signal_type} (confidence: {cs.confidence:.3f})")
                    
                    if trend_analysis.timeframe_alignment and trend_analysis.timeframe_alignment.confirmation_level == 'contradictory':
                        logging.info(f"     Higher timeframe contradicts signal")
                    
                    logging.info("="*80)
                    return 0
                    
            except Exception as e:
                logging.error(f"  ⚠️  Trend detection error: {e}")
                logging.info(f"     Proceeding without trend detection filter")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")
        else:
            if not self.trend_detection_engine:
                logging.info("  ⚠️  Advanced trend detection disabled")
            else:
                logging.info("  ⚠️  No signal to analyze with trend detection")
        
        logging.info(f"✅ ALL FILTERS PASSED - {signal_type} SIGNAL CONFIRMED!")
        logging.info(f"   Signal will proceed to risk management and position opening")
        logging.info("="*80)
        
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
        tp_prices = self.calculate_multiple_take_profits(entry_price, stop_loss, direction, symbol=symbol)
        
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
            if tick is None:
                logging.error(f"Failed to get tick data for {symbol} - symbol may not be available")
                logging.error(f"MT5 error: {mt5.last_error()}")
                continue
            
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
        if tick is None:
            logging.error(f"Failed to get tick data for {symbol} in trailing stop check")
            return 0
        
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
    
    def check_drawdown_limit(self):
        """
        Check if maximum drawdown limit has been exceeded
        Tracks peak equity and current drawdown from peak
        
        Returns:
            bool: True if can continue trading, False if drawdown limit exceeded
        """
        from datetime import datetime, timedelta
        
        # Get account info
        account_info = mt5.account_info()
        if not account_info:
            return True  # Can't check, allow trading
        
        current_equity = account_info.equity
        initial_balance = account_info.balance
        
        # Initialize peak equity tracking if not exists
        if not hasattr(self, 'peak_equity'):
            self.peak_equity = current_equity
            self.peak_equity_date = datetime.now()
        
        # Update peak equity if current is higher
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
            self.peak_equity_date = datetime.now()
            logging.info(f"📈 New peak equity: ${self.peak_equity:.2f}")
        
        # Calculate drawdown from peak
        drawdown = self.peak_equity - current_equity
        drawdown_percent = (drawdown / self.peak_equity * 100) if self.peak_equity > 0 else 0
        
        max_drawdown_percent = self.config.get('max_drawdown_percent', 10.0)
        
        # Check if drawdown limit exceeded
        if drawdown_percent >= max_drawdown_percent:
            logging.error("=" * 80)
            logging.error("🚨 MAXIMUM DRAWDOWN LIMIT EXCEEDED 🚨")
            logging.error("=" * 80)
            logging.error(f"Peak Equity: ${self.peak_equity:.2f} (on {self.peak_equity_date.strftime('%Y-%m-%d %H:%M')})")
            logging.error(f"Current Equity: ${current_equity:.2f}")
            logging.error(f"Drawdown: ${drawdown:.2f} ({drawdown_percent:.2f}%)")
            logging.error(f"Maximum Allowed: {max_drawdown_percent}%")
            logging.error("=" * 80)
            logging.error("⚠️  TRADING PAUSED - Manual intervention required")
            logging.error("⚠️  Review trading strategy and risk management")
            logging.error("⚠️  Reset peak equity or adjust max_drawdown_percent to resume")
            logging.error("=" * 80)
            return False
        
        # Log warning when approaching limit (at 80%)
        if drawdown_percent >= max_drawdown_percent * 0.8:
            logging.warning("=" * 80)
            logging.warning(f"⚠️  APPROACHING DRAWDOWN LIMIT: {drawdown_percent:.2f}% of {max_drawdown_percent}%")
            logging.warning(f"   Peak Equity: ${self.peak_equity:.2f}")
            logging.warning(f"   Current Equity: ${current_equity:.2f}")
            logging.warning(f"   Drawdown: ${drawdown:.2f}")
            logging.warning(f"   Remaining: ${(max_drawdown_percent * self.peak_equity / 100) - drawdown:.2f} ({max_drawdown_percent - drawdown_percent:.2f}%)")
            logging.warning("=" * 80)
        
        # Log current drawdown status periodically
        if drawdown_percent > 0:
            logging.info(f"📊 Drawdown Status: {drawdown_percent:.2f}% from peak (${drawdown:.2f})")
        
        return True
    
    def run_strategy(self, symbol):
        """
        Execute trading strategy for a symbol
        
        Args:
            symbol (str): Trading symbol
        """
        logging.info("")
        logging.info("╔" + "="*78 + "╗")
        logging.info(f"║ ANALYZING {symbol:^70} ║")
        logging.info("╚" + "="*78 + "╝")
        
        # Check daily loss limit before trading
        if not self.check_daily_loss_limit():
            logging.warning(f"⚠️  Daily loss limit reached - skipping {symbol}")
            logging.info("="*80)
            return
        
        # Check drawdown limit before trading
        if not self.check_drawdown_limit():
            logging.error(f"🚨 Drawdown limit exceeded - skipping {symbol}")
            logging.info("="*80)
            return
        
        # Check if already have maximum positions for this symbol
        positions = mt5.positions_get(symbol=symbol, magic=self.magic_number)
        max_per_symbol = self.config.get('max_trades_per_symbol', 1)
        
        if positions and len(positions) >= max_per_symbol:
            logging.info(f"📊 Position Check: Already have {len(positions)} position(s) for {symbol}")
            logging.info(f"   Maximum per symbol: {max_per_symbol} - Skipping new trades")
            logging.info("="*80)
            return
        else:
            logging.info(f"📊 Position Check: {len(positions) if positions else 0}/{max_per_symbol} positions for {symbol}")
        
        # Get data and calculate indicators
        logging.info(f"📈 Fetching historical data for {symbol} (Timeframe: M{self.timeframe})...")
        df = self.get_historical_data(symbol, self.timeframe)
        if df is None:
            logging.error(f"❌ Failed to get data for {symbol}")
            logging.info("="*80)
            return
        
        logging.info(f"✅ Retrieved {len(df)} bars of data")
        logging.info(f"📊 Calculating technical indicators...")
        df = self.calculate_indicators(df)
        logging.info(f"✅ Indicators calculated successfully")
        logging.info("")
        
        # Check for entry signal
        signal = self.check_entry_signal(df, symbol)
        
        if signal == 0:
            logging.info(f"Completed analysis for {symbol}")
            logging.info("="*80)
            return  # No signal
        
        logging.info(f"🎯 {'BUY' if signal == 1 else 'SELL'} signal detected for {symbol}!")
        logging.info("")
        
        # === PRICE LEVEL PROTECTION ===
        can_trade, limit_price, price_reason = self.check_existing_position_prices(symbol, signal)
        
        if not can_trade:
            logging.warning(f"❌ TRADE REJECTED by price level protection")
            logging.warning(f"   {price_reason}")
            logging.info("="*80)
            return
        else:
            if limit_price is not None:
                logging.info(f"✅ Price level check passed: {price_reason}")
        
        # === VOLUME ANALYSIS ===
        confidence_adjustment = 0.0
        if self.use_volume_filter and self.volume_analyzer:
            logging.info("="*80)
            logging.info(f"📊 VOLUME ANALYSIS for {symbol}")
            logging.info("="*80)
            
            # Check if trade should be taken based on volume
            should_trade, volume_confidence = self.volume_analyzer.should_trade(
                df, 'buy' if signal == 1 else 'sell'
            )
            
            if not should_trade:
                logging.warning(f"❌ TRADE REJECTED by volume filter for {symbol}")
                logging.warning(f"   Volume conditions not favorable for this trade")
                logging.info("="*80)
                return
            
            # Apply confidence boost from volume analysis
            confidence_adjustment = volume_confidence
            logging.info(f"✅ Volume analysis PASSED")
            logging.info(f"   Confidence boost: {confidence_adjustment:+.2%}")
            logging.info("")
        
        # === ADAPTIVE RISK MANAGEMENT ===
        if self.use_adaptive_risk and self.adaptive_risk_manager:
            logging.info("="*80)
            logging.info(f"🎯 ADAPTIVE RISK MANAGEMENT for {symbol}")
            logging.info("="*80)
            
            # Get adaptive parameters
            adaptive_params = integrate_adaptive_risk(self, symbol, signal, df)
            
            if adaptive_params is None:
                logging.info(f"❌ Trade rejected by adaptive risk manager for {symbol}")
                logging.info("="*80)
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
            if tick is None:
                logging.error(f"Failed to get tick data for {symbol} - cannot place trade")
                return
            
            entry_price = tick.ask if signal == 1 else tick.bid
            
            # Calculate SL
            stop_loss = self.calculate_stop_loss(entry_price, signal, current_atr, symbol)
            
            # Calculate position size
            total_lot_size = self.calculate_position_size(symbol, entry_price, stop_loss)
            
            # Use configured TP levels
            tp_prices = self.calculate_multiple_take_profits(entry_price, stop_loss, signal, symbol=symbol)
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
            take_profit = self.calculate_take_profit(entry_price, stop_loss, signal, symbol)
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
                        # Small delay between symbols to avoid MT5 rate limiting
                        time.sleep(0.5)  # 500ms delay between symbols
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
