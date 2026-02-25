"""
Indian Market Trading Bot
Automated trading for Indian markets using broker adapters (Kite Connect, etc.)
Preserves 90% of MT5 bot logic while replacing broker-specific operations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, List
import pytz

# Determine base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

# Log file path
LOG_FILE = BASE_DIR / 'indian_trading_bot.log'

# Import logging utilities for Windows console compatibility
from src.utils.logging_utils import configure_safe_logging

# Import broker adapter and validator
from src.adapters.broker_adapter import BrokerAdapter
from src.utils.instrument_validator import InstrumentValidator
from src.core.trading_decision_logger import TradingDecisionLogger

# Import optional components (same as MT5 bot)
try:
    from src.managers.adaptive_risk_manager import AdaptiveRiskManager
    ADAPTIVE_RISK_AVAILABLE = True
except ImportError:
    ADAPTIVE_RISK_AVAILABLE = False
    logging.warning("Adaptive risk management not available")

try:
    from src.ml.ml_integration import MLIntegration
    ML_INTEGRATION_AVAILABLE = True
except ImportError:
    ML_INTEGRATION_AVAILABLE = False
    logging.warning("ML integration not available")

try:
    from src.analyzers.volume_analyzer import VolumeAnalyzer
    VOLUME_ANALYZER_AVAILABLE = True
except ImportError:
    VOLUME_ANALYZER_AVAILABLE = False
    logging.warning("Volume Analyzer not available")

try:
    from src.analyzers.trend_detection_engine import TrendDetectionEngine
    TREND_DETECTION_AVAILABLE = True
except ImportError:
    TREND_DETECTION_AVAILABLE = False
    logging.warning("Trend Detection Engine not available")

# Reconfigure stdout for UTF-8 as early as possible for Windows compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
elif hasattr(sys.stdout, 'buffer'):
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    except Exception:
        pass

# Setup logging with UTF-8 encoding
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        stream_handler
    ],
    force=True  # Ensure we override any default handlers added by earlier logs
)

# Configure safe logging to strip emojis for Windows consoles that don't support UTF-8
configure_safe_logging()


class IndianTradingBot:
    """
    Trading bot for Indian markets using broker adapters
    Inherits core logic from MT5TradingBot but uses BrokerAdapter for all broker operations
    """
    
    def __init__(self, config: Dict, broker_adapter: BrokerAdapter):
        """
        Initialize the Indian Trading Bot
        
        Args:
            config (dict): Configuration dictionary with trading parameters
            broker_adapter (BrokerAdapter): Broker adapter instance for market operations
        """
        self.config = config
        self.broker = broker_adapter
        
        # Copy all configuration from MT5 bot
        self.symbols = config['symbols']
        self.timeframe = config['timeframe']  # In minutes for Indian markets
        self.magic_number = config.get('magic_number', 12345)
        
        # Risk management parameters (same as MT5)
        self.risk_percent = config.get('risk_percent', 1.0)
        self.reward_ratio = config.get('reward_ratio', 2.0)
        
        # Indicator parameters (same as MT5)
        self.fast_ma_period = config.get('fast_ma_period', 10)
        self.slow_ma_period = config.get('slow_ma_period', 21)
        self.atr_period = config.get('atr_period', 14)
        self.atr_multiplier = config.get('atr_multiplier', 2.0)
        
        # MACD parameters (same as MT5)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        
        # Additional indicator parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.roc_period = config.get('roc_period', 3)
        self.macd_min_histogram = config.get('macd_min_histogram', 0.0005)
        self.ema_micro_fast = config.get('ema_micro_fast', 6)
        self.ema_micro_slow = config.get('ema_micro_slow', 12)
        
        # ADX and Trend Detection parameters
        self.adx_period = config.get('adx_period', 14)
        self.adx_min_strength = config.get('adx_min_strength', 25)
        self.min_trend_confidence = config.get('min_trend_confidence', 0.6)
        self.trend_detection_sensitivity = config.get('trend_detection_sensitivity', 5)
        
        # Loop interval
        self.loop_interval = config.get('loop_interval', 60)
        
        # Trailing parameters (same as MT5)
        self.trail_activation = config.get('trail_activation', 1.5)
        self.trail_distance = config.get('trail_distance', 1.0)
        
        # Split orders configuration (same as MT5)
        self.use_split_orders = config.get('use_split_orders', True)
        self.num_positions = config.get('num_positions', 3)
        self.tp_levels = config.get('tp_levels', [1, 1.5, 2.5])
        self.partial_close_percent = config.get('partial_close_percent', [40, 30, 30])
        
        # Indian market specific
        self.trading_hours = config.get('trading_hours', {
            'start': '09:15',
            'end': '15:30'
        })
        self.product_type = config.get('product_type', 'MIS')  # MIS or NRML
        
        # Price level protection
        self.prevent_worse_entries = config.get('prevent_worse_entries', True)
        
        # Analysis parameters
        self.analysis_bars = config.get('analysis_bars', 200)
        self.max_positions = config.get('max_positions', 5)
        
        # Paper trading mode (Requirement 15.1)
        self.paper_trading = config.get('paper_trading', False)
        self.paper_trading_engine = None
        if self.paper_trading:
            from src.core.paper_trading import PaperTradingEngine
            initial_balance = config.get('paper_trading_initial_balance', 100000.0)
            self.paper_trading_engine = PaperTradingEngine(initial_balance)
        
        # Initialize same components as MT5 bot
        self._init_components()
        
        # Ensure logging is safe after all components (and their loggers) are initialized
        if self.config.get('enable_emoji_logging', True):
            import src.utils.logging_utils as logging_utils
            logging_utils.DISABLE_SAFE_LOGGING = True
            logging.info("Emoji logging enabled - Preserving emojis in logs")
            
        configure_safe_logging()
        
        # Position tracking
        self.positions = {}
        self.split_position_groups = {}
        
        # Initialize trading decision logger (Requirement 12.5)
        decision_log_file = config.get('decision_log_file', 'trading_decisions.log')
        self.decision_logger = TradingDecisionLogger(logger=logging.getLogger(), log_file=decision_log_file)
        
        # Activity logger (for dashboard)
        self.activity_logger = None
        
        logging.info("="*80)
        logging.info("Indian Trading Bot Initialized")
        logging.info(f"Symbols: {self.symbols}")
        logging.info(f"Timeframe: {self.timeframe} minutes")
        logging.info(f"Risk: {self.risk_percent}%, Reward Ratio: {self.reward_ratio}")
        logging.info(f"Trading Hours: {self.trading_hours['start']} - {self.trading_hours['end']} IST")
        logging.info(f"Decision logging enabled: {decision_log_file}")
        if self.paper_trading:
            logging.info(f"🧪 PAPER TRADING MODE ENABLED")
            initial_balance = config.get('paper_trading_initial_balance', 100000.0)
            logging.info(f"   Initial Balance: Rs.{initial_balance:,.2f}")
        logging.info("="*80)
    def set_activity_logger(self, activity_logger):
        """Set activity logger for dashboard integration"""
        self.activity_logger = activity_logger
        if activity_logger:
            activity_logger.log_analysis(
                symbol=None,
                message="Activity logger connected to bot",
                data={}
            )

    
    def _init_components(self):
        """Initialize adaptive risk, ML, volume analyzer, etc. (same as MT5)"""
        # Adaptive risk manager
        if self.config.get('use_adaptive_risk', True) and ADAPTIVE_RISK_AVAILABLE:
            self.adaptive_risk_manager = AdaptiveRiskManager(self.config)
            logging.info("Adaptive Risk Management enabled")
        else:
            self.adaptive_risk_manager = None
        
        # ML integration
        if self.config.get('ml_enabled', False) and ML_INTEGRATION_AVAILABLE:
            try:
                self.ml_integration = MLIntegration(self.config, logger=logging)
                logging.info("ML Integration enabled")
            except Exception as e:
                logging.error(f"ML Integration initialization failed: {e}")
                self.ml_integration = None
        else:
            self.ml_integration = None
        
        # Volume analyzer
        if self.config.get('use_volume_filter', True) and VOLUME_ANALYZER_AVAILABLE:
            self.volume_analyzer = VolumeAnalyzer(self.config)
            logging.info("Volume Analysis enabled")
        else:
            self.volume_analyzer = None
        
        # Trend detection
        if self.config.get('use_trend_detection', True) and TREND_DETECTION_AVAILABLE:
            self.trend_detection_engine = TrendDetectionEngine(self.config)
            logging.info("Advanced Trend Detection enabled")
        else:
            self.trend_detection_engine = None
    
    def connect(self) -> bool:
        """Connect to broker"""
        logging.info("Connecting to broker...")
        success = self.broker.connect()
        if success:
            logging.info("✅ Broker connection established")
        else:
            logging.error("❌ Broker connection failed")
        return success
    
    def disconnect(self):
        """Disconnect from broker"""
        logging.info("Disconnecting from broker...")
        self.broker.disconnect()
        logging.info("Broker connection closed")
    
    def _get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get positions from broker or paper trading engine.
        
        Args:
            symbol: Filter by symbol (optional)
        
        Returns:
            List of position dictionaries
        """
        if self.paper_trading and self.paper_trading_engine:
            return self.paper_trading_engine.get_positions(symbol)
        else:
            if symbol:
                return self.broker.get_positions(symbol)
            else:
                # Get positions for all symbols
                all_positions = []
                for sym in self.symbols:
                    positions = self.broker.get_positions(sym)
                    if positions:
                        all_positions.extend(positions)
                return all_positions
    
    def _get_account_info(self) -> Dict:
        """
        Get account information from broker or paper trading engine.
        
        Returns:
            Dictionary with balance, equity, margin info
        """
        if self.paper_trading and self.paper_trading_engine:
            return self.paper_trading_engine.get_account_info()
        else:
            return self.broker.get_account_info()
    
    def _update_paper_positions(self, symbol: str, current_price: float):
        """
        Update paper trading positions with current price.
        
        Args:
            symbol: Instrument symbol
            current_price: Current market price
        """
        if self.paper_trading and self.paper_trading_engine:
            self.paper_trading_engine.update_positions(symbol, current_price)
    
    def validate_instruments(self) -> bool:
        """
        Validate all configured instruments.
        
        Validates: Requirement 8.3
        
        Returns:
            True if all instruments are valid, False otherwise
        """
        logging.info("Validating configured instruments...")
        
        validator = InstrumentValidator(self.broker)
        all_valid, errors = validator.validate_config_instruments(self.config)
        
        if all_valid:
            logging.info("✅ All instruments validated successfully")
            
            # Log instrument details
            for symbol in self.symbols:
                _, _, info = validator.validate_instrument(symbol)
                if info:
                    logging.info(f"  {symbol}: Lot Size={info['lot_size']}, Tick Size={info['tick_size']}")
            
            return True
        else:
            logging.error("❌ Instrument validation failed:")
            for error in errors:
                logging.error(f"  {error}")
            return False
    
    def validate_instrument(self, symbol: str) -> bool:
        """
        Validate a single instrument.
        
        Validates: Requirement 8.3
        
        Args:
            symbol: Instrument symbol to validate
        
        Returns:
            True if instrument is valid, False otherwise
        """
        validator = InstrumentValidator(self.broker)
        is_valid, error_msg, _ = validator.validate_instrument(symbol)
        
        if not is_valid:
            logging.error(f"Instrument validation failed for {symbol}: {error_msg}")
        
        return is_valid
    def validate_instruments(self) -> bool:
        """
        Validate all configured instruments.

        Validates: Requirement 8.3

        Returns:
            True if all instruments are valid, False otherwise
        """
        logging.info("Validating configured instruments...")

        validator = InstrumentValidator(self.broker)
        all_valid, errors = validator.validate_config_instruments(self.config)

        if all_valid:
            logging.info("✅ All instruments validated successfully")

            # Log instrument details
            for symbol in self.symbols:
                _, _, info = validator.validate_instrument(symbol)
                if info:
                    logging.info(f"  {symbol}: Lot Size={info['lot_size']}, Tick Size={info['tick_size']}")

            return True
        else:
            logging.error("❌ Instrument validation failed:")
            for error in errors:
                logging.error(f"  {error}")
            return False

    def validate_instrument(self, symbol: str) -> bool:
        """
        Validate a single instrument.

        Validates: Requirement 8.3

        Args:
            symbol: Instrument symbol to validate

        Returns:
            True if instrument is valid, False otherwise
        """
        validator = InstrumentValidator(self.broker)
        is_valid, error_msg, _ = validator.validate_instrument(symbol)

        if not is_valid:
            logging.error(f"Instrument validation failed for {symbol}: {error_msg}")

        return is_valid
    
    def is_market_open(self) -> bool:
        """Check if Indian market is open"""
        # Allow bypass for testing/paper trading
        if self.config.get('allow_after_hours', False):
            return True
            
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Check if weekend
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check trading hours
        start_time = datetime.strptime(self.trading_hours['start'], '%H:%M').time()
        end_time = datetime.strptime(self.trading_hours['end'], '%H:%M').time()
        current_time = now.time()
        
        return start_time <= current_time <= end_time
    
    def get_historical_data(self, symbol: str, timeframe: int, bars: int = 200) -> Optional[pd.DataFrame]:
        """
        Fetch historical data using broker adapter
        
        Args:
            symbol (str): Trading symbol
            timeframe (int): Timeframe in minutes
            bars (int): Number of bars to fetch
            
        Returns:
            pd.DataFrame: Historical price data with columns: time, open, high, low, close, volume
        """
        # Convert timeframe to broker-specific format
        broker_timeframe = self.broker.convert_timeframe(timeframe)
        
        # Fetch data
        df = self.broker.get_historical_data(symbol, broker_timeframe, bars)
        
        if df is None:
            logging.error(f"Failed to fetch data for {symbol}")
            return None
        
        # Validate data format
        required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Data format invalid for {symbol}, missing required columns")
            return None
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        EXACTLY THE SAME as MT5 bot - no changes needed
        
        Args:
            df (pd.DataFrame): Price data
            
        Returns:
            pd.DataFrame: Data with calculated indicators
        """
        # Moving Averages - Using EMA for faster signal response
        df['fast_ma'] = df['close'].ewm(span=self.fast_ma_period, adjust=False).mean()
        df['slow_ma'] = df['close'].ewm(span=self.slow_ma_period, adjust=False).mean()
        
        # Early signal detection EMAs
        self.ema_micro_fast = self.config.get('ema_micro_fast', 6)
        self.ema_micro_slow = self.config.get('ema_micro_slow', 12)
        df['ema6'] = df['close'].ewm(span=self.ema_micro_fast, adjust=False).mean()
        df['ema12'] = df['close'].ewm(span=self.ema_micro_slow, adjust=False).mean()
        
        # Price momentum: rate-of-change over N bars
        self.roc_period = self.config.get('roc_period', 3)
        df['roc3'] = df['close'].pct_change(self.roc_period) * 100
        
        # ATR (Average True Range) for volatility-based stops
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=self.atr_period).mean()
        
        # RSI (Relative Strength Index)
        # self.rsi_period is already set in __init__
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
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
               (df['fast_ma'].shift(1) <= df['slow_ma'].shift(1)), 'ma_cross'] = 1
        df.loc[(df['fast_ma'] < df['slow_ma']) & 
               (df['fast_ma'].shift(1) >= df['slow_ma'].shift(1)), 'ma_cross'] = -1
        
        return df
    
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
        logging.info("-" * 80)
        
        # ENHANCED SIGNAL GENERATION - Multiple Signal Types
        signal = 0
        signal_reason = ""
        
        # ══════════════════════════════════════════════════════════════
        # EARLY SIGNAL DETECTION METHODS
        # ══════════════════════════════════════════════════════════════
        # These methods catch signals 2-3 candles before main crossover
        # Provides earlier entry at better prices
        # ══════════════════════════════════════════════════════════════
        
        # METHOD 0A: EMA6/12 MICRO-CROSSOVER (Ultra-fast, catches moves 2-3 candles early)
        logging.info("🔍 METHOD 0A: EMA6/12 MICRO-CROSSOVER (fastest signal):")
        if 'ema6' in df.columns and 'ema12' in df.columns:
            ema6_now = latest.get('ema6', float('nan'))
            ema12_now = latest.get('ema12', float('nan'))
            ema6_prev = previous.get('ema6', float('nan'))
            ema12_prev = previous.get('ema12', float('nan'))
            
            import math
            if not any(math.isnan(v) for v in [ema6_now, ema12_now, ema6_prev, ema12_prev]):
                bullish_micro = ema6_now > ema12_now and ema6_prev <= ema12_prev
                bearish_micro = ema6_now < ema12_now and ema6_prev >= ema12_prev
                
                if bullish_micro and latest['fast_ma'] > latest['slow_ma']:
                    logging.info(f"  ✅ EMA6 crossed ABOVE EMA12 in uptrend - early BUY signal!")
                    logging.info(f"     EMA6: {ema6_now:.5f}, EMA12: {ema12_now:.5f}")
                    signal = 1
                    signal_reason = "EMA6/12 Micro-Bullish Crossover"
                elif bearish_micro and latest['fast_ma'] < latest['slow_ma']:
                    logging.info(f"  ✅ EMA6 crossed BELOW EMA12 in downtrend - early SELL signal!")
                    logging.info(f"     EMA6: {ema6_now:.5f}, EMA12: {ema12_now:.5f}")
                    signal = -1
                    signal_reason = "EMA6/12 Micro-Bearish Crossover"
                else:
                    logging.info(f"  ❌ No micro-crossover (EMA6={ema6_now:.5f}, EMA12={ema12_now:.5f})")
            logging.info("-" * 80)
        
        # METHOD 0B: ROC MOMENTUM PRE-SIGNAL (fires when momentum surges before MA crosses)
        if signal == 0 and 'roc3' in df.columns:
            logging.info("-"*80)
            logging.info("🔍 METHOD 0B: MOMENTUM ROC PRE-SIGNAL:")
            roc = latest.get('roc3', float('nan'))
            
            import math
            if not math.isnan(roc):
                roc_threshold = self.config.get('roc_threshold', 0.15)  # 0.15% move in 3 candles
                
                if roc > roc_threshold and latest['ema6'] > latest['ema12']:
                    logging.info(f"  ✅ Bullish ROC surge ({roc:+.3f}%) with EMA alignment")
                    logging.info(f"     ROC threshold: {roc_threshold}%, EMA6 > EMA12")
                    signal = 1
                    signal_reason = "Bullish ROC Momentum"
                elif roc < -roc_threshold and latest['ema6'] < latest['ema12']:
                    logging.info(f"  ✅ Bearish ROC surge ({roc:+.3f}%) with EMA alignment")
                    logging.info(f"     ROC threshold: -{roc_threshold}%, EMA6 < EMA12")
                    signal = -1
                    signal_reason = "Bearish ROC Momentum"
                else:
                    logging.info(f"  ❌ ROC {roc:+.3f}% below threshold or no EMA alignment")
        
        # ══════════════════════════════════════════════════════════════
        # END EARLY SIGNAL DETECTION
        # ══════════════════════════════════════════════════════════════
        
        # METHOD 1: MA CROSSOVER (Original - High Confidence)
        if signal == 0:
            logging.info("-"*80)
        logging.info("🔍 METHOD 1: CHECKING MA CROSSOVER:")
        logging.info(f"  Previous: Fast MA={previous['fast_ma']:.5f}, Slow MA={previous['slow_ma']:.5f}")
        logging.info(f"  Current:  Fast MA={latest['fast_ma']:.5f}, Slow MA={latest['slow_ma']:.5f}")
        
        if latest['ma_cross'] == 1:
            logging.info(f"  ✅ BULLISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed ABOVE Slow MA")
            signal = 1
            signal_reason = "MA Bullish Crossover"
        elif latest['ma_cross'] == -1:
            logging.info(f"  ✅ BEARISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed BELOW Slow MA")
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
        logging.info("-" * 80)
        logging.info(f"🎯 {signal_type} SIGNAL DETECTED - Now checking filters...")
        logging.info("-" * 80)
        
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
                    rejection_reason = f"RSI {rsi:.2f} is too overbought (>{rsi_overbought})"
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     {rejection_reason}")
                    logging.info(f"     Market may be overextended - skipping trade")
                    logging.info("="*80)
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={"filter": "RSI", "reason": rejection_reason, "signal": signal_reason},
                        price=float(latest['close']),
                        indicators={
                            'rsi': float(latest['rsi']),
                            'fast_ma': float(latest['fast_ma']),
                            'slow_ma': float(latest['slow_ma'])
                        }
                    )
                    return 0
                
                # NEW: Check for minimum bullish strength (momentum confirmation)
                if rsi < 50:
                    rejection_reason = f"RSI {rsi:.2f} is too weak for BUY (<50)"
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     {rejection_reason}")
                    logging.info(f"     Not enough bullish momentum - skipping trade")
                    logging.info("="*80)
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={"filter": "RSI", "reason": rejection_reason, "signal": signal_reason},
                        price=float(latest['close']),
                        indicators={
                            'rsi': float(latest['rsi']),
                            'fast_ma': float(latest['fast_ma']),
                            'slow_ma': float(latest['slow_ma'])
                        }
                    )
                    return 0
                
                # RSI is in the sweet spot: 50-70 (or whatever overbought is set to)
                logging.info(f"  ✅ RSI FILTER PASSED!")
                logging.info(f"     RSI {rsi:.2f} shows good bullish momentum (50-{self.rsi_overbought})")
            elif signal == -1:  # SELL
                logging.info(f"  Checking SELL: RSI range {rsi_oversold}-50")
                
                # Check if oversold (too low)
                if rsi < self.rsi_oversold:
                    rejection_reason = f"RSI {rsi:.2f} is too oversold (<{self.rsi_oversold})"
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     {rejection_reason}")
                    logging.info(f"     Market may be overextended - skipping trade")
                    logging.info("="*80)
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={"filter": "RSI", "reason": rejection_reason, "signal": signal_reason},
                        price=float(latest['close']),
                        indicators={
                            'rsi': float(latest['rsi']),
                            'fast_ma': float(latest['fast_ma']),
                            'slow_ma': float(latest['slow_ma'])
                        }
                    )
                    return 0
                
                # NEW: Check for maximum bearish strength (momentum confirmation)
                if rsi > 50:
                    rejection_reason = f"RSI {rsi:.2f} is too strong for SELL (>50)"
                    logging.info(f"  ❌ RSI FILTER REJECTED!")
                    logging.info(f"     {rejection_reason}")
                    logging.info(f"     Not enough bearish momentum - skipping trade")
                    logging.info("="*80)
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={"filter": "RSI", "reason": rejection_reason, "signal": signal_reason},
                        price=float(latest['close']),
                        indicators={
                            'rsi': float(latest['rsi']),
                            'fast_ma': float(latest['fast_ma']),
                            'slow_ma': float(latest['slow_ma'])
                        }
                    )
                    return 0
                
                # RSI is in the sweet spot: 30-50 (or whatever oversold is set to)
                logging.info(f"  ✅ RSI FILTER PASSED!")
                logging.info(f"     RSI {rsi:.2f} shows good bearish momentum ({self.rsi_oversold}-50)")
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
            MACD_THRESHOLD = self.macd_min_histogram
            
            logging.info(f"  MACD Line:         {macd:.6f}")
            logging.info(f"  MACD Signal Line:  {macd_signal:.6f}")
            logging.info(f"  MACD Histogram:    {histogram:.6f}")
            logging.info(f"  MACD Threshold:    ±{MACD_THRESHOLD:.6f}")
            logging.info(f"  Histogram Position: {'POSITIVE' if histogram > 0 else 'NEGATIVE' if histogram < 0 else 'ZERO'}")
            
            if signal == 1:  # BUY
                logging.info(f"  Checking: Histogram {histogram:.6f} > {MACD_THRESHOLD:.6f}?")
                if histogram <= MACD_THRESHOLD:
                    rejection_reason = f"Histogram {histogram:.6f} is negative or too weak (≤{MACD_THRESHOLD:.6f})"
                    logging.info(f"  ❌ MACD FILTER REJECTED!")
                    if histogram <= 0:
                        logging.info(f"     Histogram {histogram:.6f} is negative - contradicts BUY signal")
                    else:
                        logging.info(f"     Histogram {histogram:.6f} is too weak (≤{MACD_THRESHOLD:.6f})")
                        logging.info(f"     MACD momentum insufficient for reliable entry")
                    logging.info("="*80)
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={"filter": "MACD", "reason": rejection_reason, "signal": signal_reason},
                        price=float(latest['close']),
                        indicators={
                            'macd_histogram': float(latest['macd_histogram']),
                            'fast_ma': float(latest['fast_ma']),
                            'slow_ma': float(latest['slow_ma'])
                        }
                    )
                    return 0
                else:
                    logging.info(f"  ✅ MACD FILTER PASSED!")
                    logging.info(f"     Histogram {histogram:.6f} shows strong bullish momentum")
                    logging.info(f"     MACD confirms BUY signal with sufficient strength")
            elif signal == -1:  # SELL
                logging.info(f"  Checking: Histogram {histogram:.6f} < -{MACD_THRESHOLD:.6f}?")
                if histogram >= -MACD_THRESHOLD:
                    rejection_reason = f"Histogram {histogram:.6f} is positive or too weak (≥-{MACD_THRESHOLD:.6f})"
                    logging.info(f"  ❌ MACD FILTER REJECTED!")
                    if histogram >= 0:
                        logging.info(f"     Histogram {histogram:.6f} is positive - contradicts SELL signal")
                    else:
                        logging.info(f"     Histogram {histogram:.6f} is too weak (≥-{MACD_THRESHOLD:.6f})")
                        logging.info(f"     MACD momentum insufficient for reliable entry")
                    logging.info("="*80)
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={"filter": "MACD", "reason": rejection_reason, "signal": signal_reason},
                        price=float(latest['close']),
                        indicators={
                            'macd_histogram': float(latest['macd_histogram']),
                            'fast_ma': float(latest['fast_ma']),
                            'slow_ma': float(latest['slow_ma'])
                        }
                    )
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
                adx_period = self.adx_period
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
                
                ADX_THRESHOLD = self.adx_min_strength
                
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
                            rejection_reason = f"Trend direction contradicts BUY signal: -DI {minus_di:.2f} > +DI {plus_di:.2f}"
                            logging.info(f"  ❌ ADX FILTER REJECTED!")
                            logging.info(f"     Trend direction contradicts BUY signal")
                            logging.info(f"     -DI {minus_di:.2f} > +DI {plus_di:.2f} (Bearish by {di_diff:.2f})")
                            logging.info(f"     Strong bearish trend detected - cannot BUY")
                            logging.info("="*80)
                            
                            self.decision_logger.log_signal(
                                symbol=symbol,
                                signal_type="SIGNAL_REJECTED",
                                direction=0,
                                reasoning={"filter": "ADX", "reason": rejection_reason, "signal": signal_reason},
                                price=float(latest['close']),
                                indicators={
                                    'adx': float(latest['adx']),
                                    'plus_di': float(latest['plus_di']),
                                    'minus_di': float(latest['minus_di'])
                                }
                            )
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
                            rejection_reason = f"Trend direction contradicts SELL signal: +DI {plus_di:.2f} > -DI {minus_di:.2f}"
                            logging.info(f"  ❌ ADX FILTER REJECTED!")
                            logging.info(f"     Trend direction contradicts SELL signal")
                            logging.info(f"     +DI {plus_di:.2f} > -DI {minus_di:.2f} (Bullish by {di_diff:.2f})")
                            logging.info(f"     Strong bullish trend detected - cannot SELL")
                            logging.info("="*80)
                            
                            self.decision_logger.log_signal(
                                symbol=symbol,
                                signal_type="SIGNAL_REJECTED",
                                direction=0,
                                reasoning={"filter": "ADX", "reason": rejection_reason, "signal": signal_reason},
                                price=float(latest['close']),
                                indicators={
                                    'adx': float(latest['adx']),
                                    'plus_di': float(latest['plus_di']),
                                    'minus_di': float(latest['minus_di'])
                                }
                            )
                            return 0
                else:
                    logging.info(f"  ⚠️  Weak trend (ADX {adx:.2f} ≤ {ADX_THRESHOLD})")
                    logging.info(f"     Trend not strong enough for reliable directional filter")
                    logging.info(f"     Proceeding with caution - other filters must be strong")
            else:
                logging.info(f"  ⚠️  ADX data not available - skipping ADX filter")
        else:
            logging.info(f"  ⚠️  Advanced trend detection disabled")
        
        logging.info("-" * 80)
        
        # Log the signal with reasoning (Requirement 12.5)
        reasoning = {
            'signal_type': signal_reason,
            'price': float(latest['close']),
            'fast_ma': float(latest['fast_ma']),
            'slow_ma': float(latest['slow_ma']),
            'rsi': float(latest['rsi']) if not pd.isna(latest['rsi']) else None,
            'macd_histogram': float(latest['macd_histogram']) if not pd.isna(latest['macd_histogram']) else None,
            'filters_passed': ['RSI', 'MACD', 'ADX', 'Trend Detection']
        }
        
        indicators = {
            'rsi': float(latest['rsi']) if not pd.isna(latest['rsi']) else None,
            'macd': float(latest['macd']) if not pd.isna(latest['macd']) else None,
            'macd_signal': float(latest['macd_signal']) if not pd.isna(latest['macd_signal']) else None,
            'macd_histogram': float(latest['macd_histogram']) if not pd.isna(latest['macd_histogram']) else None,
            'atr': float(latest['atr']) if not pd.isna(latest['atr']) else None,
            'fast_ma': float(latest['fast_ma']),
            'slow_ma': float(latest['slow_ma'])
        }
        
        self.decision_logger.log_signal(
            symbol=symbol,
            signal_type=signal_reason,
            direction=signal,
            reasoning=reasoning,
            price=float(latest['close']),
            indicators=indicators
        )
        
        # ADVANCED TREND DETECTION FILTER
        if self.trend_detection_engine and signal != 0:
            logging.info("🔍 ADVANCED TREND DETECTION FILTER:")
            signal_type_str = "buy" if signal == 1 else "sell"
            
            try:
                # Get comprehensive trend analysis
                trend_analysis = self.trend_detection_engine.analyze_trend_change(df, symbol)
                
                # Check if trend supports the signal
                should_trade, trend_confidence = self.trend_detection_engine.should_trade_trend(df, signal_type_str, symbol)
                
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
                    rejection_reason = f"Trend confidence {trend_confidence:.3f} < {self.trend_detection_engine.min_confidence:.3f}"
                    logging.info(f"  ❌ TREND DETECTION REJECTED!")
                    logging.info(f"     Trend analysis does not support {signal_type_str.upper()} signal")
                    logging.info(f"     Trend confidence: {trend_confidence:.3f} (min required: {self.trend_detection_engine.min_confidence:.3f})")
                    
                    # Log why the trend detection failed
                    conflicting_sources = []
                    if trend_analysis.signals:
                        conflicting_signals = [s for s in trend_analysis.signals 
                                             if (signal == 1 and 'bearish' in s.signal_type) or 
                                                (signal == -1 and 'bullish' in s.signal_type)]
                        if conflicting_signals:
                            logging.info(f"     Conflicting trend signals detected:")
                            for cs in conflicting_signals:
                                logging.info(f"       - {cs.source}: {cs.signal_type} (confidence: {cs.confidence:.3f})")
                                conflicting_sources.append(cs.source)
                    
                    if trend_analysis.timeframe_alignment and trend_analysis.timeframe_alignment.confirmation_level == 'contradictory':
                        logging.info(f"     Higher timeframe contradicts signal")
                        conflicting_sources.append("Higher Timeframe")
                    
                    self.decision_logger.log_signal(
                        symbol=symbol,
                        signal_type="SIGNAL_REJECTED",
                        direction=0,
                        reasoning={
                            "filter": "Trend Detection", 
                            "reason": rejection_reason, 
                            "signal": signal_reason,
                            "conflicts": conflicting_sources
                        },
                        price=float(latest['close']),
                        indicators={
                            'trend_confidence': trend_confidence,
                            'analysis_confidence': trend_analysis.confidence
                        }
                    )
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
        
        # ══════════════════════════════════════════════════════════════
        # HOUR-BASED FILTERING - Block known dead hours
        # ══════════════════════════════════════════════════════════════
        # Based on historical analysis: Hours 1am and 5pm UTC account for £12,388 in losses
        # Dead hours show consistent losses, Golden hours show consistent profits
        # ══════════════════════════════════════════════════════════════
        if signal != 0 and self.config.get('enable_hour_filter', True):
            logging.info("-"*80)
            logging.info("🕐 HOUR-BASED FILTER CHECK:")
            
            from datetime import datetime as _dt
            current_hour = _dt.now().hour
            dead_hours = self.config.get('dead_hours', [0, 1, 2, 17, 20, 21, 22])
            golden_hours = self.config.get('golden_hours', [8, 11, 13, 14, 15, 19, 23])
            
            logging.info(f"  Current Hour (UTC): {current_hour}:xx")
            logging.info(f"  Dead Hours:   {dead_hours}")
            logging.info(f"  Golden Hours: {golden_hours}")
            
            if current_hour in dead_hours:
                rejection_reason = f"Hour {current_hour}:xx is a DEAD hour"
                logging.info(f"  ❌ HOUR FILTER REJECTED!")
                logging.info(f"     {rejection_reason}")
                logging.info(f"     Historical data shows consistent losses at this hour")
                logging.info(f"     Signal suppressed to protect capital")
                logging.info(f"     Golden hours for trading: {golden_hours}")
                logging.info("="*80)
                
                self.decision_logger.log_signal(
                    symbol=symbol,
                    signal_type="SIGNAL_REJECTED",
                    direction=0,
                    reasoning={"filter": "Hour Filter", "reason": rejection_reason, "signal": signal_reason},
                    price=float(latest['close']),
                    indicators={'hour_utc': float(current_hour)}
                )
                return 0
            elif current_hour in golden_hours:
                logging.info(f"  ✅ HOUR FILTER PASSED!")
                logging.info(f"     Hour {current_hour}:xx is a GOLDEN hour")
                logging.info(f"     Historical data shows consistent profits at this hour")
                logging.info(f"     Signal confirmed - optimal trading time")
            else:
                logging.info(f"  ⚠️  Hour {current_hour}:xx is NEUTRAL")
                logging.info(f"     Not in dead hours or golden hours")
                logging.info(f"     Proceeding with caution")
        
        logging.info(f"✅ ALL FILTERS PASSED - {signal_type} SIGNAL CONFIRMED!")
        logging.info(f"   Signal will proceed to risk management and position opening")
        logging.info("="*80)
        
        return signal
    
    def calculate_stop_loss(self, entry_price: float, direction: int, atr: float) -> float:
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
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float, direction: int) -> float:
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
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk
        Adapted to use broker adapter for account info
        
        Requirements:
        - 9.1: Calculate position sizes based on available margin from broker
        - 9.2: Respect instrument-specific lot sizes
        - 9.3: Use instrument-specific tick sizes for stop-loss distances
        - 9.4: Prevent position sizes that exceed available margin
        - 9.5: Calculate risk as percentage of account equity, not just balance
        
        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            
        Returns:
            float: Position size (quantity)
        """
        # Get account info from broker or paper trading (Requirement 9.1)
        account_info = self._get_account_info()
        equity = account_info.get('equity', 0)
        margin_available = account_info.get('margin_available', 0)
        
        if equity == 0:
            logging.warning("Equity is 0, using default position size")
            return 1.0
        
        # Calculate risk amount based on equity (Requirement 9.5)
        risk_amount = equity * (self.risk_percent / 100)
        
        # Get instrument info (Requirements 9.2, 9.3)
        inst_info = self.broker.get_instrument_info(symbol)
        if not inst_info:
            logging.warning(f"Could not get instrument info for {symbol}, using default")
            return 1.0
        
        lot_size = inst_info.get('lot_size', 1)
        tick_size = inst_info.get('tick_size', 0.05)
        
        # Calculate stop loss distance in ticks (Requirement 9.3)
        sl_distance = abs(entry_price - stop_loss)
        
        # Ensure stop loss distance is a multiple of tick size
        sl_ticks = round(sl_distance / tick_size) if tick_size > 0 else 1
        sl_distance = sl_ticks * tick_size
        
        if sl_ticks == 0:
            logging.warning(f"Stop loss distance too small for {symbol}, using minimum lot size")
            return float(lot_size)
        
        # Calculate quantity based on risk per share/contract
        risk_per_unit = sl_distance
        if risk_per_unit == 0:
            return float(lot_size)
        
        quantity = risk_amount / risk_per_unit
        
        # Round to lot size (Requirement 9.2)
        quantity = round(quantity / lot_size) * lot_size
        
        # Ensure minimum
        quantity = max(lot_size, quantity)
        
        # Check margin availability (Requirement 9.4)
        # Calculate estimated margin requirement
        # For Indian markets: typically 15-25% for equity, varies for F&O
        margin_multiplier = self.config.get('margin_multiplier', 0.20)
        estimated_margin = quantity * entry_price * margin_multiplier
        
        if estimated_margin > margin_available:
            # Reduce position size to fit available margin
            max_quantity = (margin_available * 0.9) / (entry_price * margin_multiplier)
            quantity = round(max_quantity / lot_size) * lot_size
            quantity = max(lot_size, quantity)
            logging.warning(f"Position size reduced due to margin constraint: {quantity} (Available margin: {margin_available:.2f}, Required: {estimated_margin:.2f})")
        
        # Final validation
        if quantity < lot_size:
            logging.warning(f"Calculated quantity {quantity} is less than lot size {lot_size}, using lot size")
            quantity = lot_size
        
        logging.info(f"Position size calculated for {symbol}: {quantity} lots (Risk: {risk_amount:.2f}, SL distance: {sl_distance:.2f}, Equity: {equity:.2f})")
        return float(quantity)
    
    def open_position(
        self,
        symbol: str,
        direction: int,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        quantity: float
    ) -> bool:
        """
        Open position using broker adapter
        Handles both single and split orders based on configuration

        Requirements:
        - 5.1: Place market orders with specified quantity and direction
        - 5.2: Place limit orders with specified price, quantity, and direction
        - 5.3: Place stop-loss orders with trigger price, quantity, and direction
        - 5.4: Place bracket orders with entry, stop-loss, and take-profit levels

        Args:
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            take_profit (float): Take profit price (used for single orders)
            quantity (float): Position size

        Returns:
            bool: True if successful
        """
        # Check if split orders are enabled
        if self.use_split_orders:
            return self._open_split_positions(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                stop_loss=stop_loss,
                total_quantity=quantity
            )
        else:
            return self._open_single_position(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                quantity=quantity
            )

    def _open_single_position(
        self,
        symbol: str,
        direction: int,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        quantity: float
    ) -> bool:
        """
        Open a single position using broker adapter or paper trading

        Args:
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            take_profit (float): Take profit price
            quantity (float): Position size

        Returns:
            bool: True if successful
        """
        # Use paper trading if enabled (Requirement 15.1, 15.2)
        if self.paper_trading and self.paper_trading_engine:
            order_id = self.paper_trading_engine.place_order(
                symbol=symbol,
                direction=direction,
                quantity=quantity,
                order_type="MARKET",
                stop_loss=stop_loss,
                take_profit=take_profit,
                product_type=self.product_type,
                current_price=entry_price
            )
        else:
            # Place market order (Requirement 5.1)
            order_id = self.broker.place_order(
                symbol=symbol,
                direction=direction,
                quantity=quantity,
                order_type="MARKET",
                stop_loss=stop_loss,
                take_profit=take_profit,
                product_type=self.product_type
            )

        if not order_id:
            logging.error(f"Failed to place order for {symbol}")
            # Log order placement failure (Requirement 12.5)
            self.decision_logger.log_order_placement(
                symbol=symbol,
                direction=direction,
                quantity=quantity,
                order_type="MARKET",
                stop_loss=stop_loss,
                take_profit=take_profit,
                success=False,
                error_message="Broker returned no order ID"
            )
            # Activity log
            if self.activity_logger:
                self.activity_logger.log_error(
                    message=f"Failed to place order for {symbol}",
                    symbol=symbol
                )
            return False

        # Log successful order placement (Requirement 12.5)
        self.decision_logger.log_order_placement(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type="MARKET",
            stop_loss=stop_loss,
            take_profit=take_profit,
            order_id=order_id,
            success=True
        )
        
        # Activity log
        order_type_str = "BUY" if direction == 1 else "SELL"
        if self.activity_logger:
            self.activity_logger.log_order(
                symbol=symbol,
                order_type=order_type_str,
                message=f"Order placed: {order_type_str} {quantity} {symbol} @ Rs.{entry_price:.2f}",
                data={
                    'order_id': order_id,
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }
            )

        # Store position info for tracking (Requirement 5.1)
        self.positions[order_id] = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'initial_sl': stop_loss,
            'initial_tp': take_profit,
            'stop_loss': stop_loss,  # Current SL for trailing stop tracking
            'order_id': order_id,
            'quantity': quantity,
            'entry_time': datetime.now(),  # For time-based exit
            'opened_at': datetime.now(),
            'is_split': False
        }

        direction_str = "BUY" if direction == 1 else "SELL"
        logging.info(f"✅ Position opened: {symbol} {direction_str} {quantity} @ {entry_price:.2f}")
        logging.info(f"   SL: {stop_loss:.2f}, TP: {take_profit:.2f}, Order ID: {order_id}")

        return True

    def _open_split_positions(
        self,
        symbol: str,
        direction: int,
        entry_price: float,
        stop_loss: float,
        total_quantity: float
    ) -> bool:
        """
        Open multiple positions with different take profit levels
        Implements split order functionality for partial profit taking

        Args:
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            total_quantity (float): Total quantity to split

        Returns:
            bool: True if at least one position opened successfully
        """
        import uuid
        import time

        # Generate unique group ID for this set of positions
        group_id = str(uuid.uuid4())[:8]

        # Calculate split quantities
        quantities = self._split_quantity(total_quantity)

        # Calculate multiple TP levels
        tp_prices = self._calculate_multiple_take_profits(entry_price, stop_loss, direction, symbol)

        # Get instrument info for rounding
        inst_info = self.broker.get_instrument_info(symbol)
        if inst_info:
            tick_size = inst_info.get('tick_size', 0.05)
            lot_size = inst_info.get('lot_size', 1)

            # Round prices to tick size
            stop_loss = round(stop_loss / tick_size) * tick_size
            tp_prices = [round(tp / tick_size) * tick_size for tp in tp_prices]

            # Round quantities to lot size
            quantities = [round(qty / lot_size) * lot_size for qty in quantities]
            quantities = [max(lot_size, qty) for qty in quantities]  # Ensure minimum lot size

        logging.info(f"Opening split positions for {symbol}:")
        logging.info(f"  Group ID: {group_id}")
        logging.info(f"  Total quantity: {total_quantity}, Split into: {quantities}")
        logging.info(f"  TP levels: {tp_prices}")

        order_ids = []

        # Open each position with its respective TP level
        for i, (qty, tp) in enumerate(zip(quantities, tp_prices)):
            if qty <= 0:
                logging.warning(f"Quantity {qty} too small for position {i+1}, skipping")
                continue

            # Place market order for this split (Requirement 5.4 - bracket order with SL/TP)
            if self.paper_trading and self.paper_trading_engine:
                order_id = self.paper_trading_engine.place_order(
                    symbol=symbol,
                    direction=direction,
                    quantity=qty,
                    order_type="MARKET",
                    stop_loss=stop_loss,
                    take_profit=tp,
                    product_type=self.product_type,
                    current_price=entry_price
                )
            else:
                order_id = self.broker.place_order(
                    symbol=symbol,
                    direction=direction,
                    quantity=qty,
                    order_type="MARKET",
                    stop_loss=stop_loss,
                    take_profit=tp,
                    product_type=self.product_type
                )

            if not order_id:
                logging.error(f"Split position {i+1} failed to open")
                # Log placement failure for this split
                self.decision_logger.log_order_placement(
                    symbol=symbol,
                    direction=direction,
                    quantity=qty,
                    order_type="MARKET",
                    stop_loss=stop_loss,
                    take_profit=tp,
                    success=False,
                    error_message=f"Split position {i+1} failed to open"
                )
                continue
            
            # Log successful placement for this split
            self.decision_logger.log_order_placement(
                symbol=symbol,
                direction=direction,
                quantity=qty,
                order_type="MARKET",
                stop_loss=stop_loss,
                take_profit=tp,
                order_id=order_id,
                success=True
            )

            logging.info(f"  Position {i+1}: {qty} @ {entry_price:.2f}, TP: {tp:.2f} (Order ID: {order_id})")

            order_ids.append(order_id)

            # Store position info for tracking
            self.positions[order_id] = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'initial_sl': stop_loss,
                'initial_tp': tp,
                'stop_loss': stop_loss,  # Current SL for trailing stop tracking
                'order_id': order_id,
                'quantity': qty,
                'entry_time': datetime.now(),  # For time-based exit
                'opened_at': datetime.now(),
                'is_split': True,
                'group_id': group_id,
                'position_number': i + 1,
                'total_positions': len(quantities)
            }

            # Small delay between orders to avoid rate limiting
            time.sleep(0.5)

        if len(order_ids) == 0:
            logging.error("Failed to open any split positions")
            return False

        # Store group info for tracking
        self.split_position_groups[group_id] = {
            'symbol': symbol,
            'direction': direction,
            'order_ids': order_ids,
            'entry_price': entry_price,
            'initial_sl': stop_loss,
            'created_at': datetime.now()
        }

        direction_str = "BUY" if direction == 1 else "SELL"
        logging.info(f"✅ Successfully opened {len(order_ids)} split positions for {symbol} {direction_str} (Group: {group_id})")

        return True

    def _split_quantity(self, total_quantity: float) -> list:
        """
        Split total quantity into smaller orders based on configuration

        Args:
            total_quantity (float): Total quantity to split

        Returns:
            list: List of quantities for each split
        """
        percentages = self.partial_close_percent
        num_splits = self.num_positions

        # Ensure percentages sum to 100
        if sum(percentages) != 100:
            # Normalize
            total = sum(percentages)
            percentages = [p / total * 100 for p in percentages]

        quantities = []
        for i, percent in enumerate(percentages[:num_splits]):
            qty = total_quantity * (percent / 100)
            quantities.append(qty)

        return quantities

    def _calculate_multiple_take_profits(
        self,
        entry_price: float,
        stop_loss: float,
        direction: int,
        symbol: str
    ) -> list:
        """
        Calculate multiple take profit levels for partial closing

        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            symbol (str): Trading symbol

        Returns:
            list: List of take profit prices
        """
        ratios = self.tp_levels
        risk = abs(entry_price - stop_loss)
        tp_prices = []

        logging.info(f"  Calculating multiple TP levels:")
        logging.info(f"    Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, Risk: {risk:.2f}")

        for i, ratio in enumerate(ratios):
            reward = risk * ratio

            if direction == 1:  # Buy
                tp = entry_price + reward
            else:  # Sell
                tp = entry_price - reward

            tp_prices.append(tp)
            logging.info(f"    TP Level {i+1}: ratio {ratio}, reward {reward:.2f} = {tp:.2f}")

        return tp_prices

    
    def check_existing_position_prices(self, symbol: str, signal: int) -> tuple:
        """
        Check existing position prices to prevent placing orders at worse levels
        
        Args:
            symbol (str): Trading symbol
            signal (int): 1 for BUY, -1 for SELL
            
        Returns:
            tuple: (can_trade, limit_price, reason)
        """
        if not self.prevent_worse_entries:
            return True, None, "Price level protection disabled"
        
        # Get existing positions for this symbol
        positions = self._get_positions(symbol)
        
        if not positions or len(positions) == 0:
            return True, None, "No existing positions"
        
        # Get current price from latest position data
        current_price = positions[0].get('current_price', 0)
        if current_price == 0:
            return True, None, "Cannot determine current price"
        
        if signal == 1:  # BUY signal
            # Find highest existing BUY position price
            buy_positions = [p for p in positions if p['direction'] == 1]
            
            if not buy_positions:
                return True, None, "No existing BUY positions"
            
            highest_buy_price = max(p['entry_price'] for p in buy_positions)
            
            # Don't place BUY if current price is higher than highest existing BUY
            if current_price > highest_buy_price:
                reason = f"Cannot place BUY at {current_price:.2f} - higher than highest existing BUY at {highest_buy_price:.2f}"
                logging.warning(f"🚫 PRICE LEVEL PROTECTION: {reason}")
                return False, highest_buy_price, reason
            else:
                return True, highest_buy_price, f"BUY allowed - below highest existing BUY at {highest_buy_price:.2f}"
        
        else:  # SELL signal
            # Find lowest existing SELL position price
            sell_positions = [p for p in positions if p['direction'] == -1]
            
            if not sell_positions:
                return True, None, "No existing SELL positions"
            
            lowest_sell_price = min(p['entry_price'] for p in sell_positions)
            
            # Don't place SELL if current price is lower than lowest existing SELL
            if current_price < lowest_sell_price:
                reason = f"Cannot place SELL at {current_price:.2f} - lower than lowest existing SELL at {lowest_sell_price:.2f}"
                logging.warning(f"🚫 PRICE LEVEL PROTECTION: {reason}")
                return False, lowest_sell_price, reason
            else:
                return True, lowest_sell_price, f"SELL allowed - above lowest existing SELL at {lowest_sell_price:.2f}"
    
    def run_strategy(self, symbol: str):
        """
        Execute trading strategy for a symbol
        MOSTLY THE SAME as MT5 bot with broker adapter calls
        
        Args:
            symbol (str): Trading symbol to analyze
        """
        # Log analysis start with header
        logging.info("╔" + "="*78 + "╗")
        logging.info(f"║ ANALYZING                                 {symbol:<38} ║")
        logging.info("╚" + "="*78 + "╝")

        if self.activity_logger:
            self.activity_logger.log_symbol_analysis_start(symbol)
            
            # Log position check
            positions = self.broker.get_positions(symbol)
            current_positions = len(positions) if positions else 0
            
            logging.info(f"📊 Position Check: {current_positions}/{self.max_positions} positions for {symbol}")
            
            self.activity_logger.log_position_check(
                symbol=symbol,
                current=current_positions,
                max_allowed=self.max_positions
            )
        else:
            # Fallback if activity logger is not set
            positions = self.broker.get_positions(symbol)
            current_positions = len(positions) if positions else 0
            logging.info(f"📊 Position Check: {current_positions}/{self.max_positions} positions for {symbol}")
        
        # Check if market is open
        if not self.is_market_open():
            return
        
        # Get historical data
        logging.info(f"📈 Fetching historical data for {symbol} (Timeframe: {self.timeframe})...")
        logging.info(f"    Requesting {self.analysis_bars} bars for analysis")
        
        if self.activity_logger:
            self.activity_logger.log_analysis(
                symbol=symbol,
                message=f"📈 Fetching historical data for {symbol} (Timeframe: {self.timeframe})",
                data={'bars_requested': self.analysis_bars}
            )
        
        df = self.get_historical_data(symbol, self.timeframe, self.analysis_bars)
        if df is None or len(df) < 50:
            logging.error(f"Insufficient data for {symbol}")
            if self.activity_logger:
                self.activity_logger.log_error(
                    message=f"❌ Insufficient data for {symbol}",
                    symbol=symbol
                )
            return
        
        # Log data fetch success
        logging.info(f"✅ Retrieved {len(df)} bars of data (requested: {self.analysis_bars})")
        
        if self.activity_logger:
            self.activity_logger.log_data_fetch(
                symbol=symbol,
                bars_requested=self.analysis_bars,
                bars_received=len(df)
            )
        
        # Calculate indicators
        logging.info(f"📊 Calculating technical indicators...")
        
        if self.activity_logger:
            self.activity_logger.log_analysis(
                symbol=symbol,
                message=f"📊 Calculating technical indicators...",
                data={}
            )
        
        df = self.calculate_indicators(df)
        logging.info(f"✅ Indicators calculated successfully")
        logging.info("")
        
        # Log key indicators
        if self.activity_logger and len(df) > 0:
            latest = df.iloc[-1]
            indicators = {
                'Current Price': latest.get('close', 0),
                'RSI': latest.get('rsi', 0),
                'MACD': latest.get('macd', 0),
                'ATR': latest.get('atr', 0),
                'Fast MA': latest.get('fast_ma', 0),
                'Slow MA': latest.get('slow_ma', 0)
            }
            self.activity_logger.log_indicator_calculation(symbol, indicators)
        
        # Check for entry signal
        signal = self.check_entry_signal(df, symbol)
        
        if signal == 0:
            if self.activity_logger:
                self.activity_logger.log_trade_decision(
                    symbol=symbol,
                    decision="NO SIGNAL",
                    reason="Market conditions not favorable for entry"
                )
            return
        
        # Log signal generation
        signal_type = "BUY" if signal == 1 else "SELL"
        if self.activity_logger:
            self.activity_logger.log_signal(
                symbol=symbol,
                signal_type=signal_type,
                message=f"🎯 {signal_type} signal detected",
                data={'signal': signal}
            )
        
        # Check price level protection
        can_trade, limit_price, reason = self.check_existing_position_prices(symbol, signal)
        if not can_trade:
            logging.info(f"Trade blocked for {symbol}: {reason}")
            if self.activity_logger:
                self.activity_logger.log_trade_decision(
                    symbol=symbol,
                    decision="SIGNAL REJECTED",
                    reason=f"Price level protection: {reason}"
                )
            return
        
        # Calculate position parameters
        latest = df.iloc[-1]
        current_price = latest['close']
        current_atr = latest['atr']
        
        # Update paper trading positions with current price
        self._update_paper_positions(symbol, current_price)
        
        # Calculate SL and TP
        stop_loss = self.calculate_stop_loss(current_price, signal, current_atr)
        take_profit = self.calculate_take_profit(current_price, stop_loss, signal)
        
        # Calculate position size
        quantity = self.calculate_position_size(symbol, current_price, stop_loss)
        
        # Log risk calculation
        if self.activity_logger:
            risk_amount = abs(current_price - stop_loss) * quantity
            risk_data = {
                'Entry Price': f"Rs.{current_price:.2f}",
                'Stop Loss': f"Rs.{stop_loss:.2f}",
                'Take Profit': f"Rs.{take_profit:.2f}",
                'Quantity': quantity,
                'Risk Amount': f"Rs.{risk_amount:.2f}",
                'Risk %': f"{self.risk_percent}%"
            }
            self.activity_logger.log_risk_calculation(symbol, risk_data)
        
        # Open position
        success = self.open_position(
            symbol=symbol,
            direction=signal,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity
        )
        
        if success:
            direction_str = "BUY" if signal == 1 else "SELL"
            logging.info(f"🎯 Trade executed: {symbol} {direction_str}")
            if self.activity_logger:
                self.activity_logger.log_trade_decision(
                    symbol=symbol,
                    decision="TRADE EXECUTED",
                    reason=f"{direction_str} order placed successfully"
                )
        else:
            logging.error(f"❌ Trade failed: {symbol}")
            if self.activity_logger:
                self.activity_logger.log_trade_decision(
                    symbol=symbol,
                    decision="TRADE FAILED",
                    reason="Order placement failed"
                )
        
        # Log completion
        if self.activity_logger:
            self.activity_logger.log_separator()
    
    def update_trailing_stop(self, position_dict, symbol, direction):
        """
        Update trailing stop loss for an open position
        Adapted from MT5 bot to use broker adapter
        
        Args:
            position_dict (dict): Position dictionary from broker adapter
            symbol (str): Trading symbol
            direction (int): 1 for buy, -1 for sell
            
        Returns:
            bool: True if updated
        """
        try:
            # Get current price from position
            current_price = position_dict['current_price']
            entry_price = position_dict['entry_price']
            
            # Get current ATR
            df = self.get_historical_data(symbol, self.timeframe, 50)
            if df is None or len(df) == 0:
                return False
            
            df = self.calculate_indicators(df)
            current_atr = df.iloc[-1]['atr']
            
            # Check if trailing should be activated
            profit_in_atr = abs(current_price - entry_price) / current_atr
            
            if profit_in_atr < self.trail_activation:
                return False  # Not enough profit to activate trailing
            
            # Get instrument info for tick size
            inst_info = self.broker.get_instrument_info(symbol)
            if not inst_info:
                logging.warning(f"Could not get instrument info for {symbol}")
                return False
            
            tick_size = inst_info.get('tick_size', 0.05)
            
            # Calculate new trailing stop
            if direction == 1:  # Buy position
                new_sl = current_price - (self.trail_distance * current_atr)
                # Round to tick size
                new_sl = round(new_sl / tick_size) * tick_size
                
                # Get current SL from position tracking
                position_id = position_dict.get('order_id') or position_dict.get('position_id')
                if position_id and position_id in self.positions:
                    current_sl = self.positions[position_id].get('stop_loss', 0)
                    if new_sl <= current_sl:
                        return False  # Only move SL up
                else:
                    # No tracking info, assume we should update
                    pass
            else:  # Sell position
                new_sl = current_price + (self.trail_distance * current_atr)
                # Round to tick size
                new_sl = round(new_sl / tick_size) * tick_size
                
                # Get current SL from position tracking
                position_id = position_dict.get('order_id') or position_dict.get('position_id')
                if position_id and position_id in self.positions:
                    current_sl = self.positions[position_id].get('stop_loss', 0)
                    if current_sl > 0 and new_sl >= current_sl:
                        return False  # Only move SL down
                else:
                    # No tracking info, assume we should update
                    pass
            
            # Note: Kite Connect doesn't support direct SL modification for positions
            # We need to place a new SL order or use bracket orders
            # For now, we'll log the trailing stop level
            # Full implementation would require placing new SL orders
            logging.info(f"Trailing stop calculated for {symbol}: New SL = {new_sl:.2f} (Current implementation logs only)")
            
            # Update tracking
            if position_id and position_id in self.positions:
                old_sl = self.positions[position_id].get('stop_loss', 0)
                self.positions[position_id]['stop_loss'] = new_sl
                
                # Log position update (Requirement 12.5)
                self.decision_logger.log_position_update(
                    symbol=symbol,
                    update_type="TRAILING_STOP",
                    old_value=old_sl,
                    new_value=new_sl,
                    current_price=current_price,
                    pnl=position_dict.get('pnl', 0),
                    details={
                        'profit_in_atr': float(profit_in_atr),
                        'trail_distance_atr': self.trail_distance
                    }
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating trailing stop for {symbol}: {e}")
            return False
    
    def update_group_trailing_stop(self, group_id):
        """
        Update trailing stop for all positions in a split position group
        Updates all positions together to maintain consistency
        Adapted from MT5 bot to use broker adapter
        
        Args:
            group_id (str): Group ID for split positions
            
        Returns:
            int: Number of positions updated
        """
        if group_id not in self.split_position_groups:
            return 0
        
        try:
            group = self.split_position_groups[group_id]
            symbol = group['symbol']
            direction = group['direction']
            order_ids = group['order_ids']
            
            # Get current data
            df = self.get_historical_data(symbol, self.timeframe, 50)
            if df is None or len(df) == 0:
                return 0
            
            df = self.calculate_indicators(df)
            current_atr = df.iloc[-1]['atr']
            
            # Get current positions from broker or paper trading
            broker_positions = self._get_positions(symbol)
            if not broker_positions:
                return 0
            
            # Find positions in this group
            group_positions = []
            for pos in broker_positions:
                pos_id = pos.get('order_id') or pos.get('position_id')
                if pos_id in order_ids:
                    group_positions.append(pos)
            
            if not group_positions:
                return 0
            
            # Use first position to calculate trailing stop
            current_price = group_positions[0]['current_price']
            entry_price = group['entry_price']
            
            # Check if trailing should activate
            profit_in_atr = abs(current_price - entry_price) / current_atr
            
            if profit_in_atr < self.trail_activation:
                return 0
            
            # Get instrument info for tick size
            inst_info = self.broker.get_instrument_info(symbol)
            if not inst_info:
                return 0
            
            tick_size = inst_info.get('tick_size', 0.05)
            
            # Calculate new trailing stop (same for all positions in group)
            if direction == 1:  # Buy
                new_sl = current_price - (self.trail_distance * current_atr)
            else:  # Sell
                new_sl = current_price + (self.trail_distance * current_atr)
            
            new_sl = round(new_sl / tick_size) * tick_size
            
            updated_count = 0
            
            # Update all positions in the group
            for order_id in order_ids:
                if order_id in self.positions:
                    current_sl = self.positions[order_id].get('stop_loss', 0)
                    
                    # Only move SL in profitable direction
                    should_update = False
                    if direction == 1 and new_sl > current_sl:
                        should_update = True
                    elif direction == -1 and (current_sl == 0 or new_sl < current_sl):
                        should_update = True
                    
                    if should_update:
                        self.positions[order_id]['stop_loss'] = new_sl
                        updated_count += 1
            
            if updated_count > 0:
                logging.info(f"Group {group_id}: Updated trailing stop for {updated_count} positions to {new_sl:.2f}")
            
            return updated_count
            
        except Exception as e:
            logging.error(f"Error updating group trailing stop for {group_id}: {e}")
            return 0
    
    def _force_close_position(self, position_dict, symbol):
        """
        Force-close a single position at market price.
        Called by time-based exit logic in manage_positions.
        Adapted from MT5 bot to use broker adapter or paper trading
        
        Args:
            position_dict (dict): Position dictionary from broker adapter
            symbol (str): Trading symbol
            
        Returns:
            bool: True if closed successfully
        """
        try:
            direction = position_dict['direction']
            quantity = position_dict['quantity']
            current_price = position_dict.get('current_price', 0)
            
            # Close position based on mode
            if self.paper_trading and self.paper_trading_engine:
                # Close paper trading position
                pos_id = position_dict.get('order_id') or position_dict.get('position_id')
                success = self.paper_trading_engine.close_position(pos_id, current_price)
                order_id = pos_id if success else None
            else:
                # Place opposite order to close position
                close_direction = -direction  # Opposite direction
                
                # Place market order to close
                order_id = self.broker.place_order(
                    symbol=symbol,
                    direction=close_direction,
                    quantity=quantity,
                    order_type="MARKET",
                    product_type=self.product_type
                )
            
            if order_id:
                pnl = position_dict.get('pnl', 0)
                pnl_percent = position_dict.get('pnl_percent', 0)
                entry_price = position_dict.get('entry_price', 0)
                
                # Calculate hold time
                pos_id = position_dict.get('order_id') or position_dict.get('position_id')
                hold_time = None
                if pos_id and pos_id in self.positions:
                    entry_time = self.positions[pos_id].get('entry_time')
                    if entry_time:
                        hold_duration = datetime.now() - entry_time
                        hold_minutes = hold_duration.total_seconds() / 60
                        hold_time = f"{int(hold_minutes)}m"
                
                # Log position exit (Requirement 12.5)
                self.decision_logger.log_position_exit(
                    symbol=symbol,
                    direction=direction,
                    quantity=quantity,
                    entry_price=entry_price,
                    exit_price=current_price,
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    exit_reason="TIME_EXIT",
                    hold_time=hold_time
                )
                
                # Activity log
                if self.activity_logger:
                    pnl_sign = "+" if pnl >= 0 else ""
                    self.activity_logger.log_position(
                        symbol=symbol,
                        message=f"Position closed: {symbol} P&L: {pnl_sign}Rs.{pnl:.2f} ({pnl_sign}{pnl_percent:.2f}%)",
                        data={
                            'pnl': pnl,
                            'pnl_percent': pnl_percent,
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'hold_time': hold_time
                        }
                    )
                
                logging.info(f"✅ Position closed successfully | Symbol: {symbol} | P&L: {pnl:.2f}")
                
                # Remove from tracking
                if pos_id and pos_id in self.positions:
                    del self.positions[pos_id]
                
                return True
            else:
                logging.error(f"❌ Failed to close position for {symbol}")
                return False
                
        except Exception as e:
            logging.error(f"Error force closing position for {symbol}: {e}")
            return False
    
    def manage_positions(self):
        """
        Check and manage all open positions with dynamic SL/TP
        Adapted from MT5 bot to use broker adapter
        Implements:
        - Trailing stops
        - Break-even stops
        - Time-based exits
        """
        # Get all positions from broker
        all_positions = []
        for symbol in self.symbols:
            positions = self._get_positions(symbol)
            if positions:
                all_positions.extend(positions)
        
        if not all_positions:
            # Clean up tracking dictionaries if no positions
            self.cleanup_closed_positions()
            return
        
        logging.debug(f"Managing {len(all_positions)} open positions")
        
        # Track which groups we've already processed
        processed_groups = set()
        
        for position in all_positions:
            symbol = position['symbol']
            direction = position['direction']
            pos_id = position.get('order_id') or position.get('position_id')
            
            try:
                # ══════════════════════════════════════════════════════════════
                # PROACTIVE PROFIT BOOKING
                # ══════════════════════════════════════════════════════════════
                # Time-based exit: Close positions held too long
                # Break-even: Move SL to entry once position reaches threshold
                # ══════════════════════════════════════════════════════════════
                
                enable_time_exit = self.config.get('enable_time_based_exit', False)
                enable_breakeven = self.config.get('enable_breakeven_stop', True)
                
                if enable_time_exit or enable_breakeven:
                    # Check if we have tracking info with entry time
                    if pos_id and pos_id in self.positions:
                        position_open_time = self.positions[pos_id].get('entry_time')
                        
                        if position_open_time:
                            hold_minutes = (datetime.now() - position_open_time).total_seconds() / 60
                            
                            # Action 1: Time-based exit
                            if enable_time_exit:
                                max_hold_minutes = self.config.get('max_hold_minutes', 45)
                                
                                if hold_minutes >= max_hold_minutes:
                                    close_result = self._force_close_position(position, symbol)
                                    if close_result:
                                        pnl = position.get('pnl', 0)
                                        reason = "TIME LIMIT" if pnl >= 0 else "TIME STOP"
                                        logging.info(f"⏰ {reason}: Closed {symbol} after {hold_minutes:.0f}min | P&L: {pnl:.2f}")
                                    continue  # Skip further processing for this position
                            
                            # Action 2: Break-even stop
                            if enable_breakeven:
                                df_be = self.get_historical_data(symbol, self.timeframe, 20)
                                if df_be is not None and len(df_be) > 0:
                                    df_be = self.calculate_indicators(df_be)
                                    atr_be = df_be.iloc[-1]['atr']
                                    
                                    entry_price = position['entry_price']
                                    current_price = position['current_price']
                                    
                                    profit_atr = (current_price - entry_price) * direction / atr_be
                                    be_threshold = self.config.get('breakeven_atr_threshold', 0.3)
                                    
                                    if profit_atr >= be_threshold:
                                        # Get instrument info for tick size
                                        inst_info = self.broker.get_instrument_info(symbol)
                                        if inst_info:
                                            tick_size = inst_info.get('tick_size', 0.05)
                                            
                                            # Calculate break-even SL (entry price + small buffer)
                                            if direction == 1:  # BUY position
                                                be_sl = entry_price + (2 * tick_size)  # Small buffer above entry
                                                be_sl = round(be_sl / tick_size) * tick_size
                                                
                                                current_sl = self.positions[pos_id].get('stop_loss', 0)
                                                if current_sl < be_sl:
                                                    old_sl = current_sl
                                                    self.positions[pos_id]['stop_loss'] = be_sl
                                                    
                                                    # Log break-even update (Requirement 12.5)
                                                    self.decision_logger.log_position_update(
                                                        symbol=symbol,
                                                        update_type="BREAK_EVEN",
                                                        old_value=old_sl,
                                                        new_value=be_sl,
                                                        current_price=current_price,
                                                        pnl=position.get('pnl', 0),
                                                        details={
                                                            'profit_atr': float(profit_atr),
                                                            'threshold_atr': be_threshold
                                                        }
                                                    )
                                                    
                                                    logging.info(f"🔒 BREAK-EVEN: {symbol} SL moved to entry {be_sl:.2f}")
                                            else:  # SELL position
                                                be_sl = entry_price - (2 * tick_size)  # Small buffer below entry
                                                be_sl = round(be_sl / tick_size) * tick_size
                                                
                                                current_sl = self.positions[pos_id].get('stop_loss', 0)
                                                if current_sl == 0 or current_sl > be_sl:
                                                    old_sl = current_sl
                                                    self.positions[pos_id]['stop_loss'] = be_sl
                                                    
                                                    # Log break-even update (Requirement 12.5)
                                                    self.decision_logger.log_position_update(
                                                        symbol=symbol,
                                                        update_type="BREAK_EVEN",
                                                        old_value=old_sl,
                                                        new_value=be_sl,
                                                        current_price=current_price,
                                                        pnl=position.get('pnl', 0),
                                                        details={
                                                            'profit_atr': float(profit_atr),
                                                            'threshold_atr': be_threshold
                                                        }
                                                    )
                                                    
                                                    logging.info(f"🔒 BREAK-EVEN: {symbol} SL moved to entry {be_sl:.2f}")
                
                # ══════════════════════════════════════════════════════════════
                # END PROACTIVE PROFIT BOOKING
                # ══════════════════════════════════════════════════════════════
                
                # Standard trailing stop logic
                # Check if this is part of a split position group
                if pos_id and pos_id in self.positions and 'group_id' in self.positions[pos_id]:
                    group_id = self.positions[pos_id]['group_id']
                    
                    # Update entire group together (only once)
                    if group_id not in processed_groups:
                        self.update_group_trailing_stop(group_id)
                        processed_groups.add(group_id)
                else:
                    # Single position, update individually
                    self.update_trailing_stop(position, symbol, direction)
                    
            except Exception as e:
                logging.warning(f"Error updating position for {symbol}: {e}")
                continue
        
        # Clean up closed positions and groups
        self.cleanup_closed_positions()
        self.cleanup_closed_groups()
    
    def cleanup_closed_groups(self):
        """
        Remove groups where all positions are closed
        Adapted from MT5 bot to use broker adapter
        """
        groups_to_remove = []
        
        for group_id, group in self.split_position_groups.items():
            symbol = group['symbol']
            order_ids = group['order_ids']
            
            # Get current positions from broker or paper trading
            broker_positions = self._get_positions(symbol)
            
            # Check if any positions in this group are still open
            all_closed = True
            if broker_positions:
                for pos in broker_positions:
                    pos_id = pos.get('order_id') or pos.get('position_id')
                    if pos_id in order_ids:
                        all_closed = False
                        break
            
            if all_closed:
                groups_to_remove.append(group_id)
        
        for group_id in groups_to_remove:
            del self.split_position_groups[group_id]
            logging.info(f"Cleaned up closed group: {group_id}")
    
    def cleanup_closed_positions(self):
        """
        Remove closed positions from tracking dictionary
        Adapted from MT5 bot to use broker adapter
        """
        # Get all currently open positions from broker
        all_open_positions = []
        for symbol in self.symbols:
            positions = self._get_positions(symbol)
            if positions:
                all_open_positions.extend(positions)
        
        # Extract open position IDs
        open_position_ids = set()
        for pos in all_open_positions:
            pos_id = pos.get('order_id') or pos.get('position_id')
            if pos_id:
                open_position_ids.add(pos_id)
        
        # Find positions in tracking that are no longer open
        positions_to_remove = []
        for pos_id in self.positions.keys():
            if pos_id not in open_position_ids:
                positions_to_remove.append(pos_id)
        
        # Remove closed positions from tracking
        for pos_id in positions_to_remove:
            del self.positions[pos_id]
            logging.debug(f"Cleaned up closed position: {pos_id}")
        
        if len(positions_to_remove) > 0:
            logging.info(f"Cleaned up {len(positions_to_remove)} closed position(s)")
    
    def run(self):
        """Main bot loop"""
        logging.info("="*80)
        logging.info("Starting Indian Trading Bot")
        logging.info("="*80)
        
        # Log bot start (Requirement 12.5)
        self.decision_logger.log_bot_action("START", {
            'symbols': self.symbols,
            'timeframe': self.timeframe,
            'risk_percent': self.risk_percent
        })
        
        if not self.connect():
            logging.error("Failed to connect to broker")
            self.decision_logger.log_bot_action("ERROR", {'message': 'Failed to connect to broker'})
            return
        
        try:
            while True:
                # Connection check and reconnection
                if not self.broker.is_connected():
                    logging.warning("⚠️  MT5 connection lost, attempting to reconnect...")
                    reconnect_success = False
                    for i in range(5):  # Try 5 times
                        time.sleep(1)  # Progressive delay
                        if self.connect():
                            logging.info("✅ MT5 reconnected successfully")
                            reconnect_success = True
                            break
                        logging.warning(f"   Reconnection attempt {i+1} failed...")
                    
                    if not reconnect_success:
                        logging.error("❌ Reconnection failed, stopping bot")
                        break

                # Check if market is open
                if not self.is_market_open():
                    ist = pytz.timezone('Asia/Kolkata')
                    now = datetime.now(ist)
                    logging.info(f"Market closed (Current time: {now.strftime('%H:%M:%S IST')})")
                    
                    # Log market status once per hour to avoid spam
                    if now.minute == 0:
                        self.decision_logger.log_market_status("CLOSED", f"Market closed at {now.strftime('%H:%M:%S IST')}")
                    
                    time.sleep(60)
                    continue
                
                # Log if bypassing market hours
                if self.config.get('allow_after_hours', False):
                    ist = pytz.timezone('Asia/Kolkata')
                    now = datetime.now(ist)
                    # Check if actual market is closed
                    actual_start = datetime.strptime(self.trading_hours['start'], '%H:%M').time()
                    actual_end = datetime.strptime(self.trading_hours['end'], '%H:%M').time()
                    current_time = now.time()
                    
                    is_actual_open = (now.weekday() < 5 and actual_start <= current_time <= actual_end)
                    
                    if not is_actual_open:
                        logging.info(f"🧪 AFTER-HOURS TRADING ENABLED (Current time: {now.strftime('%H:%M:%S IST')})")
                
                # Run strategy for each symbol
                for symbol in self.symbols:
                    try:
                        self.run_strategy(symbol)
                    except Exception as e:
                        logging.error(f"Error processing {symbol}: {e}")
                        import traceback
                        logging.error(traceback.format_exc())
                
                # Manage open positions
                try:
                    self.manage_positions()
                except Exception as e:
                    logging.error(f"Error managing positions: {e}")
                    import traceback
                    logging.error(traceback.format_exc())
                
                # Wait before next iteration
                interval = self.loop_interval
                if interval < 1: interval = 1 # Minimum 1 second
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            self.decision_logger.log_bot_action("STOP", {'reason': 'User interrupt'})
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            self.decision_logger.log_bot_action("ERROR", {'error': str(e)})
        finally:
            self.disconnect()
            logging.info("Bot shutdown complete")
            self.decision_logger.log_bot_action("SHUTDOWN", {'status': 'complete'})


if __name__ == "__main__":
    # Example usage
    logging.info("Indian Trading Bot - Direct execution not recommended")
    logging.info("Please use a configuration file and main script to run the bot")
