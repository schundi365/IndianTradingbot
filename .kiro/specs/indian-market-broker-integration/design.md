# Design Document: Indian Market Broker Integration

## Overview

This design describes the migration of an existing MT5 forex trading bot to support Indian stock market trading through broker APIs, with Kite Connect (Zerodha) as the primary implementation. The architecture uses a broker abstraction layer that allows the bot to work with multiple Indian broker APIs while preserving 90% of the existing trading logic.

### Key Design Principles

1. **Separation of Concerns**: Broker-specific code is isolated from trading logic
2. **Interface-Based Design**: All broker implementations conform to a standard interface
3. **Minimal Disruption**: Existing indicator calculations, signal generation, and risk management remain unchanged
4. **Extensibility**: New brokers can be added by implementing the broker adapter interface
5. **Indian Market Compliance**: Respects trading hours, instrument formats, and market segments

### Migration Scope

**What Changes (10%)**:
- Connection and authentication
- Market data fetching
- Order placement and management
- Position tracking
- Account information retrieval

**What Stays the Same (90%)**:
- All technical indicators (RSI, MACD, EMA, ATR, ADX, Bollinger Bands)
- Signal generation logic (MA crossovers, momentum, pullback, breakout)
- Risk management (position sizing, stop loss, take profit calculation)
- Trailing stop logic
- Split order management
- Adaptive risk management
- ML integration
- Volume analysis
- Trend detection
- Configuration management

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Trading Bot Core                         │
│  (Indicators, Signals, Risk Management - UNCHANGED)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Broker Adapter Interface                        │
│  (Abstract base class defining standard operations)          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
   │  Kite   │  │  Alice  │  │  Angel  │  │ Upstox  │
   │ Connect │  │  Blue   │  │   One   │  │         │
   └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    indian_trading_bot.py                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  IndianTradingBot (main class)                         │  │
│  │  - Inherits core logic from MT5TradingBot             │  │
│  │  - Uses BrokerAdapter for all broker operations       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  broker_adapter.py                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  BrokerAdapter (abstract base class)                   │  │
│  │  - connect()                                           │  │
│  │  - disconnect()                                        │  │
│  │  - get_historical_data()                              │  │
│  │  - place_order()                                      │  │
│  │  - modify_order()                                     │  │
│  │  - cancel_order()                                     │  │
│  │  - get_positions()                                    │  │
│  │  - get_account_info()                                 │  │
│  │  - get_instrument_info()                              │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  kite_adapter.py                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  KiteAdapter (implements BrokerAdapter)                │  │
│  │  - Uses kiteconnect library                           │  │
│  │  - Handles Kite-specific authentication               │  │
│  │  - Converts between Kite and standard formats         │  │
│  │  - Implements rate limiting and retry logic           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```


## Components and Interfaces

### 1. BrokerAdapter (Abstract Base Class)

The `BrokerAdapter` defines the standard interface that all broker implementations must follow.

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

class BrokerAdapter(ABC):
    """Abstract base class for broker API adapters"""
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to broker API
        Returns: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to broker API"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active"""
        pass
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data
        
        Args:
            symbol: Instrument symbol
            timeframe: Timeframe (e.g., "30minute", "1hour", "day")
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with columns: time, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def place_order(
        self,
        symbol: str,
        direction: int,  # 1 for buy, -1 for sell
        quantity: float,
        order_type: str,  # "MARKET", "LIMIT", "SL", "SL-M"
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product_type: str = "MIS"  # "MIS" or "NRML"
    ) -> Optional[str]:
        """
        Place an order
        
        Returns:
            Order ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ) -> bool:
        """Modify an existing order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions
        
        Returns:
            List of position dictionaries with keys:
            - symbol: str
            - direction: int (1 for buy, -1 for sell)
            - quantity: float
            - entry_price: float
            - current_price: float
            - pnl: float
            - pnl_percent: float
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """
        Get account information
        
        Returns:
            Dictionary with keys:
            - balance: float
            - equity: float
            - margin_available: float
            - margin_used: float
        """
        pass
    
    @abstractmethod
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        """
        Get instrument information
        
        Returns:
            Dictionary with keys:
            - symbol: str
            - lot_size: int
            - tick_size: float
            - instrument_token: str (broker-specific ID)
        """
        pass
    
    @abstractmethod
    def convert_timeframe(self, mt5_timeframe: int) -> str:
        """Convert MT5 timeframe constant to broker-specific format"""
        pass
```

### 2. KiteAdapter (Kite Connect Implementation)


```python
from kiteconnect import KiteConnect
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging

class KiteAdapter(BrokerAdapter):
    """Kite Connect API adapter"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('kite_api_key')
        self.token_file = config.get('kite_token_file', 'kite_token.json')
        self.kite = None
        self.access_token = None
        self.instrument_cache = {}  # Cache for instrument tokens
        
    def connect(self) -> bool:
        """Authenticate with Kite Connect"""
        try:
            # Read access token from file
            token_path = Path(self.token_file)
            if not token_path.exists():
                logging.error(f"Token file not found: {self.token_file}")
                logging.error("Please run kite_login.py to authenticate")
                return False
            
            with open(token_path) as f:
                token_data = json.load(f)
            
            # Check if token is from today
            token_date = token_data.get('date')
            today = datetime.now().strftime("%Y-%m-%d")
            
            if token_date != today:
                logging.error(f"Token is from {token_date}, need today's token")
                logging.error("Please run kite_login.py to re-authenticate")
                return False
            
            self.access_token = token_data['access_token']
            
            # Initialize Kite Connect
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            
            # Verify connection by getting profile
            profile = self.kite.profile()
            logging.info(f"Connected to Kite: {profile['user_name']}")
            logging.info(f"Broker: {profile['broker']}")
            
            # Load instrument cache
            self._load_instrument_cache()
            
            return True
            
        except Exception as e:
            logging.error(f"Kite connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close Kite connection"""
        self.kite = None
        self.access_token = None
        logging.info("Disconnected from Kite")
    
    def is_connected(self) -> bool:
        """Check if Kite connection is active"""
        if not self.kite or not self.access_token:
            return False
        
        try:
            # Quick check by getting margins
            self.kite.margins()
            return True
        except Exception:
            return False
    
    def _load_instrument_cache(self):
        """Load instrument tokens for faster lookups"""
        try:
            instruments = self.kite.instruments()
            for inst in instruments:
                key = f"{inst['exchange']}:{inst['tradingsymbol']}"
                self.instrument_cache[key] = inst['instrument_token']
            logging.info(f"Loaded {len(self.instrument_cache)} instruments")
        except Exception as e:
            logging.warning(f"Failed to load instrument cache: {e}")
    
    def _get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[int]:
        """Get instrument token for a symbol"""
        key = f"{exchange}:{symbol}"
        return self.instrument_cache.get(key)
    
    def _retry_with_backoff(self, func, max_retries=3):
        """Execute function with exponential backoff on rate limit"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logging.warning(f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    raise
    
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data from Kite"""
        try:
            # Get instrument token
            exchange = self.config.get('default_exchange', 'NSE')
            instrument_token = self._get_instrument_token(symbol, exchange)
            
            if not instrument_token:
                logging.error(f"Instrument token not found for {symbol}")
                return None
            
            # Calculate date range
            to_date = datetime.now()
            
            # Estimate days needed based on timeframe and bars
            if "minute" in timeframe:
                minutes = int(timeframe.replace("minute", ""))
                days_needed = (bars * minutes) // (6 * 60) + 5  # 6 hours trading
            elif "hour" in timeframe:
                hours = int(timeframe.replace("hour", ""))
                days_needed = (bars * hours) // 6 + 5
            else:  # day
                days_needed = bars + 10
            
            from_date = to_date - timedelta(days=days_needed)
            
            # Fetch data with retry
            def fetch():
                return self.kite.historical_data(
                    instrument_token,
                    from_date,
                    to_date,
                    timeframe
                )
            
            data = self._retry_with_backoff(fetch)
            
            if not data:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df.rename(columns={'date': 'time'}, inplace=True)
            
            # Ensure correct types
            df['time'] = pd.to_datetime(df['time'])
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(int)
            
            # Return last N bars
            return df.tail(bars).reset_index(drop=True)
            
        except Exception as e:
            logging.error(f"Failed to fetch data for {symbol}: {e}")
            return None
    
    def place_order(
        self,
        symbol: str,
        direction: int,
        quantity: float,
        order_type: str,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product_type: str = "MIS"
    ) -> Optional[str]:
        """Place order on Kite"""
        try:
            exchange = self.config.get('default_exchange', 'NSE')
            
            # Convert direction to transaction type
            transaction_type = self.kite.TRANSACTION_TYPE_BUY if direction == 1 else self.kite.TRANSACTION_TYPE_SELL
            
            # Convert order type
            kite_order_type = {
                "MARKET": self.kite.ORDER_TYPE_MARKET,
                "LIMIT": self.kite.ORDER_TYPE_LIMIT,
                "SL": self.kite.ORDER_TYPE_SL,
                "SL-M": self.kite.ORDER_TYPE_SLM
            }.get(order_type, self.kite.ORDER_TYPE_MARKET)
            
            # Convert product type
            kite_product = self.kite.PRODUCT_MIS if product_type == "MIS" else self.kite.PRODUCT_NRML
            
            # Place order
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=int(quantity),
                order_type=kite_order_type,
                product=kite_product,
                price=price,
                trigger_price=trigger_price
            )
            
            logging.info(f"Order placed: {order_id}")
            
            # If SL/TP specified, place bracket orders
            if stop_loss or take_profit:
                # Note: Kite bracket orders have specific requirements
                # This is a simplified implementation
                logging.warning("SL/TP orders require bracket order implementation")
            
            return str(order_id)
            
        except Exception as e:
            logging.error(f"Failed to place order: {e}")
            return None
    
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ) -> bool:
        """Modify order on Kite"""
        try:
            params = {}
            if quantity:
                params['quantity'] = int(quantity)
            if price:
                params['price'] = price
            if trigger_price:
                params['trigger_price'] = trigger_price
            
            self.kite.modify_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id,
                **params
            )
            
            logging.info(f"Order modified: {order_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to modify order: {e}")
            return False
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order on Kite"""
        try:
            self.kite.cancel_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id
            )
            logging.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to cancel order: {e}")
            return False
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get positions from Kite"""
        try:
            positions = self.kite.positions()
            net_positions = positions.get('net', [])
            
            result = []
            for pos in net_positions:
                if pos['quantity'] == 0:
                    continue
                
                if symbol and pos['tradingsymbol'] != symbol:
                    continue
                
                direction = 1 if pos['quantity'] > 0 else -1
                
                result.append({
                    'symbol': pos['tradingsymbol'],
                    'direction': direction,
                    'quantity': abs(pos['quantity']),
                    'entry_price': pos['average_price'],
                    'current_price': pos['last_price'],
                    'pnl': pos['pnl'],
                    'pnl_percent': (pos['pnl'] / (pos['average_price'] * abs(pos['quantity']))) * 100
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to get positions: {e}")
            return []
    
    def get_account_info(self) -> Dict:
        """Get account info from Kite"""
        try:
            margins = self.kite.margins()
            equity_margins = margins.get('equity', {})
            
            return {
                'balance': equity_margins.get('net', 0),
                'equity': equity_margins.get('available', {}).get('live_balance', 0),
                'margin_available': equity_margins.get('available', {}).get('cash', 0),
                'margin_used': equity_margins.get('utilised', {}).get('debits', 0)
            }
            
        except Exception as e:
            logging.error(f"Failed to get account info: {e}")
            return {
                'balance': 0,
                'equity': 0,
                'margin_available': 0,
                'margin_used': 0
            }
    
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        """Get instrument info from Kite"""
        try:
            exchange = self.config.get('default_exchange', 'NSE')
            instruments = self.kite.instruments(exchange)
            
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    return {
                        'symbol': symbol,
                        'lot_size': inst.get('lot_size', 1),
                        'tick_size': inst.get('tick_size', 0.05),
                        'instrument_token': str(inst['instrument_token'])
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to get instrument info: {e}")
            return None
    
    def convert_timeframe(self, mt5_timeframe: int) -> str:
        """Convert MT5 timeframe to Kite format"""
        import MetaTrader5 as mt5
        
        timeframe_map = {
            mt5.TIMEFRAME_M1: "minute",
            mt5.TIMEFRAME_M5: "5minute",
            mt5.TIMEFRAME_M15: "15minute",
            mt5.TIMEFRAME_M30: "30minute",
            mt5.TIMEFRAME_H1: "60minute",
            mt5.TIMEFRAME_D1: "day"
        }
        
        return timeframe_map.get(mt5_timeframe, "30minute")
```

### 3. IndianTradingBot (Main Bot Class)


```python
class IndianTradingBot:
    """
    Trading bot for Indian markets using broker adapters
    Inherits core logic from MT5TradingBot but uses BrokerAdapter for all broker operations
    """
    
    def __init__(self, config: Dict, broker_adapter: BrokerAdapter):
        self.config = config
        self.broker = broker_adapter
        
        # Copy all configuration from MT5 bot
        self.symbols = config['symbols']
        self.timeframe = config['timeframe']
        self.magic_number = config.get('magic_number', 12345)
        
        # Risk management (same as MT5)
        self.risk_percent = config.get('risk_percent', 1.0)
        self.reward_ratio = config.get('reward_ratio', 2.0)
        
        # Indicator parameters (same as MT5)
        self.fast_ma_period = config.get('fast_ma_period', 10)
        self.slow_ma_period = config.get('slow_ma_period', 21)
        self.atr_period = config.get('atr_period', 14)
        self.atr_multiplier = config.get('atr_multiplier', 2.0)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        
        # Trailing parameters (same as MT5)
        self.trail_activation = config.get('trail_activation', 1.5)
        self.trail_distance = config.get('trail_distance', 1.0)
        
        # Split orders (same as MT5)
        self.use_split_orders = config.get('use_split_orders', True)
        self.num_positions = config.get('num_positions', 3)
        self.tp_levels = config.get('tp_levels', [1, 1.5, 2.5])
        self.partial_close_percent = config.get('partial_close_percent', [40, 30, 30])
        
        # Indian market specific
        self.trading_hours = config.get('trading_hours', {
            'start': '09:15',
            'end': '15:30'
        })
        
        # Initialize same components as MT5 bot
        self._init_components()
        
        self.positions = {}
        self.split_position_groups = {}
    
    def _init_components(self):
        """Initialize adaptive risk, ML, volume analyzer, etc. (same as MT5)"""
        # Adaptive risk manager
        if self.config.get('use_adaptive_risk', True):
            try:
                from src.adaptive_risk_manager import AdaptiveRiskManager
                self.adaptive_risk_manager = AdaptiveRiskManager(self.config)
            except ImportError:
                self.adaptive_risk_manager = None
        
        # ML integration
        if self.config.get('ml_enabled', False):
            try:
                from src.ml_integration import MLIntegration
                self.ml_integration = MLIntegration(self.config, logger=logging)
            except ImportError:
                self.ml_integration = None
        
        # Volume analyzer
        if self.config.get('use_volume_filter', True):
            try:
                from src.volume_analyzer import VolumeAnalyzer
                self.volume_analyzer = VolumeAnalyzer(self.config)
            except ImportError:
                self.volume_analyzer = None
        
        # Trend detection
        if self.config.get('use_trend_detection', True):
            try:
                from src.trend_detection_engine import TrendDetectionEngine
                self.trend_detection_engine = TrendDetectionEngine(self.config)
            except ImportError:
                self.trend_detection_engine = None
    
    def connect(self) -> bool:
        """Connect to broker"""
        return self.broker.connect()
    
    def disconnect(self):
        """Disconnect from broker"""
        self.broker.disconnect()
    
    def is_market_open(self) -> bool:
        """Check if Indian market is open"""
        from datetime import datetime
        import pytz
        
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
    
    def get_historical_data(self, symbol: str, timeframe: int, bars: int) -> Optional[pd.DataFrame]:
        """
        Fetch historical data using broker adapter
        Converts MT5 timeframe to broker-specific format
        """
        # Convert timeframe
        broker_timeframe = self.broker.convert_timeframe(timeframe)
        
        # Fetch data
        df = self.broker.get_historical_data(symbol, broker_timeframe, bars)
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        EXACTLY THE SAME as MT5 bot - no changes needed
        """
        # This method is copied directly from MT5TradingBot
        # All indicator calculations work the same way
        
        # Moving Averages
        df['fast_ma'] = df['close'].ewm(span=self.fast_ma_period, adjust=False).mean()
        df['slow_ma'] = df['close'].ewm(span=self.slow_ma_period, adjust=False).mean()
        
        # Early signal detection EMAs
        df['ema6'] = df['close'].ewm(span=6, adjust=False).mean()
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        
        # ROC
        df['roc3'] = df['close'].pct_change(3) * 100
        
        # ATR
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=self.atr_period).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
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
    
    def check_entry_signal(self, df: pd.DataFrame, symbol: str = "unknown") -> int:
        """
        Check for entry signals
        EXACTLY THE SAME as MT5 bot - no changes needed
        """
        # This method is copied directly from MT5TradingBot
        # All signal detection logic works the same way
        # (Implementation omitted for brevity - same as MT5)
        pass
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk
        Adapted to use broker adapter for account info
        """
        # Get account info from broker
        account_info = self.broker.get_account_info()
        balance = account_info['balance']
        margin_available = account_info['margin_available']
        
        # Calculate risk amount
        risk_amount = balance * (self.risk_percent / 100)
        
        # Get instrument info
        inst_info = self.broker.get_instrument_info(symbol)
        if not inst_info:
            return 1.0  # Default
        
        lot_size = inst_info['lot_size']
        tick_size = inst_info['tick_size']
        
        # Calculate stop loss distance in ticks
        sl_distance = abs(entry_price - stop_loss)
        sl_ticks = sl_distance / tick_size
        
        if sl_ticks == 0:
            return 1.0
        
        # Calculate quantity
        quantity = risk_amount / (sl_ticks * tick_size * lot_size)
        
        # Round to lot size
        quantity = round(quantity / lot_size) * lot_size
        
        # Ensure minimum
        quantity = max(lot_size, quantity)
        
        return quantity
    
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
        """
        # Place market order
        order_id = self.broker.place_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type="MARKET",
            stop_loss=stop_loss,
            take_profit=take_profit,
            product_type=self.config.get('product_type', 'MIS')
        )
        
        if not order_id:
            return False
        
        # Store position info
        self.positions[order_id] = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'initial_sl': stop_loss,
            'initial_tp': take_profit,
            'order_id': order_id
        }
        
        logging.info(f"Position opened: {symbol} {direction} at {entry_price}")
        return True
    
    def run_strategy(self, symbol: str):
        """
        Execute trading strategy
        MOSTLY THE SAME as MT5 bot with broker adapter calls
        """
        # Check if market is open
        if not self.is_market_open():
            logging.info(f"Market closed, skipping {symbol}")
            return
        
        # Get data
        df = self.get_historical_data(symbol, self.timeframe, 200)
        if df is None:
            logging.error(f"Failed to get data for {symbol}")
            return
        
        # Calculate indicators (same as MT5)
        df = self.calculate_indicators(df)
        
        # Check for signal (same as MT5)
        signal = self.check_entry_signal(df, symbol)
        
        if signal == 0:
            return
        
        # Calculate position parameters (same as MT5)
        latest = df.iloc[-1]
        current_atr = latest['atr']
        
        # Get current price from broker
        positions = self.broker.get_positions(symbol)
        # ... rest of position opening logic
    
    def run(self):
        """Main bot loop"""
        if not self.connect():
            logging.error("Failed to connect to broker")
            return
        
        try:
            while True:
                if not self.is_market_open():
                    logging.info("Market closed, waiting...")
                    time.sleep(60)
                    continue
                
                for symbol in self.symbols:
                    self.run_strategy(symbol)
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        finally:
            self.disconnect()
```


## Data Models

### Configuration Model

```python
{
    # Broker selection
    "broker": "kite",  # "kite", "alice_blue", "angel_one", etc.
    
    # Kite Connect specific
    "kite_api_key": "your_api_key",
    "kite_token_file": "kite_token.json",
    "default_exchange": "NSE",  # or "BSE"
    
    # Trading parameters (same as MT5)
    "symbols": ["RELIANCE", "TCS", "INFY"],
    "timeframe": 30,  # minutes
    "magic_number": 12345,
    "lot_size": 1,
    
    # Risk management (same as MT5)
    "risk_percent": 1.0,
    "reward_ratio": 2.0,
    "max_daily_loss_percent": 5.0,
    "max_drawdown_percent": 10.0,
    
    # Indicator parameters (same as MT5)
    "fast_ma_period": 10,
    "slow_ma_period": 21,
    "atr_period": 14,
    "atr_multiplier": 2.0,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    
    # Indian market specific
    "trading_hours": {
        "start": "09:15",
        "end": "15:30"
    },
    "product_type": "MIS",  # or "NRML"
    
    # Features (same as MT5)
    "use_split_orders": True,
    "use_adaptive_risk": True,
    "ml_enabled": False,
    "use_volume_filter": True,
    "use_trend_detection": True
}
```

### Token File Model

```python
{
    "access_token": "xxxxxxxxxxxxxxxxxxxxx",
    "date": "2024-01-15",
    "time": "2024-01-15T09:00:00"
}
```

### Position Model

```python
{
    "symbol": "RELIANCE",
    "direction": 1,  # 1 for buy, -1 for sell
    "quantity": 50,
    "entry_price": 2450.50,
    "current_price": 2455.75,
    "pnl": 262.50,
    "pnl_percent": 0.21
}
```

### Account Info Model

```python
{
    "balance": 500000.00,
    "equity": 505000.00,
    "margin_available": 450000.00,
    "margin_used": 50000.00
}
```

### Instrument Info Model

```python
{
    "symbol": "RELIANCE",
    "lot_size": 1,
    "tick_size": 0.05,
    "instrument_token": "738561"
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Broker Adapter Routing

*For any* broker operation request, the Broker_Adapter should route it to the correct broker implementation based on configuration.

**Validates: Requirements 1.2**

### Property 2: Kite Authentication Token Validation

*For any* valid token file with today's date, the Kite_Adapter should successfully authenticate and allow trading operations.

**Validates: Requirements 2.2, 3.1**

### Property 3: Authentication Failure Handling

*For any* invalid or expired token, the Authentication_Manager should return a descriptive error and prevent trading operations.

**Validates: Requirements 2.3, 3.3, 3.4**

### Property 4: Historical Data Format Consistency

*For any* valid instrument and timeframe, the Market_Data_Provider should return data in pandas DataFrame format with columns: time (datetime), open (float), high (float), low (float), close (float), volume (int).

**Validates: Requirements 2.4, 4.1, 4.2, 14.1, 14.2, 14.3, 14.4**

### Property 5: Order Placement Success

*For any* valid order parameters (symbol, direction, quantity, order type), the Order_Manager should successfully place the order and return a valid order ID.

**Validates: Requirements 2.5, 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 6: Position Data Completeness

*For any* open position, the Position_Tracker should return complete position data including entry price, current price, quantity, direction, and P&L (both absolute and percentage).

**Validates: Requirements 2.6, 6.1, 6.2, 6.4**

### Property 7: Account Information Retrieval

*For any* authenticated account, the system should successfully retrieve account balance, equity, available margin, and used margin.

**Validates: Requirements 2.7**

### Property 8: Symbol to Token Conversion

*For any* valid Indian market instrument symbol, the Kite_Adapter should convert it to the correct instrument token for API operations.

**Validates: Requirements 2.8, 8.4**

### Property 9: Rate Limit Retry Logic

*For any* rate limit error encountered, the system should implement exponential backoff retry logic with increasing wait times (2^attempt seconds).

**Validates: Requirements 2.9, 4.4, 12.3**

### Property 10: Trading Hours Enforcement

*For any* time outside NSE trading hours (9:15 AM - 3:30 PM IST) or on weekends, the Trading_Bot should not generate signals or place orders.

**Validates: Requirements 7.1, 7.5**

### Property 11: Timeframe Conversion

*For any* MT5 timeframe constant (TIMEFRAME_M1, TIMEFRAME_M5, TIMEFRAME_M15, TIMEFRAME_M30, TIMEFRAME_H1, TIMEFRAME_D1), the system should correctly convert it to broker-specific format ("minute", "5minute", "15minute", "30minute", "60minute", "day").

**Validates: Requirements 7.6, 11.4**

### Property 12: Instrument Validation

*For any* instrument configured in the configuration file, the Configuration_Manager should validate that it exists and is tradable before allowing trades.

**Validates: Requirements 8.3**

### Property 13: Position Size Lot Compliance

*For any* calculated position size, the Risk_Manager should ensure it is a multiple of the instrument's lot size.

**Validates: Requirements 9.2**

### Property 14: Stop Loss Tick Size Compliance

*For any* calculated stop loss distance, the Risk_Manager should ensure it respects the instrument's tick size (distance is a multiple of tick size).

**Validates: Requirements 9.3**

### Property 15: Margin Limit Enforcement

*For any* position size calculation, the Risk_Manager should ensure the required margin does not exceed available margin.

**Validates: Requirements 9.4**

### Property 16: Risk Calculation Based on Equity

*For any* risk calculation, the Risk_Manager should use account equity (not just balance) as the base for percentage calculations.

**Validates: Requirements 9.5**

### Property 17: Symbol Mapping Consistency

*For any* MT5 symbol (e.g., "XAUUSD"), the Configuration_Manager should consistently map it to the same Indian market equivalent (e.g., "GOLD" futures).

**Validates: Requirements 11.3**

### Property 18: Error Logging Completeness

*For any* broker API error, the system should log the error code, error message, and operation context.

**Validates: Requirements 12.1, 12.4**

### Property 19: Trading Decision Logging

*For any* trading decision (signal generation, entry, exit), the system should log it with timestamp, symbol, decision type, and reasoning.

**Validates: Requirements 12.5**

### Property 20: Broker Selection from Configuration

*For any* broker specified in the configuration file, the system should load and initialize the correct broker adapter implementation.

**Validates: Requirements 13.4**

### Property 21: Missing Data Handling

*For any* historical data with missing values, the Market_Data_Provider should either forward-fill the missing values or raise a descriptive error.

**Validates: Requirements 14.5**

### Property 22: Paper Trading Order Logging

*For any* order placed in paper trading mode, the system should log the simulated order with all parameters and the simulated outcome.

**Validates: Requirements 15.2**

### Property 23: Position Filtering by Symbol

*For any* symbol filter applied to position retrieval, the Position_Tracker should return only positions matching that symbol.

**Validates: Requirements 6.3**

### Property 24: Bot Position Identification

*For any* position opened by the bot, the Position_Tracker should be able to identify it using the magic number (or equivalent identifier).

**Validates: Requirements 6.5**

### Property 25: Order Parameter Validation

*For any* order parameters (quantity, price, instrument), the Order_Manager should validate them before submission and reject invalid parameters with descriptive errors.

**Validates: Requirements 5.9**

### Property 26: Order Modification Success

*For any* existing pending order, the Order_Manager should successfully modify its price, quantity, or order type.

**Validates: Requirements 5.6**

### Property 27: Order Cancellation Success

*For any* existing pending order, the Order_Manager should successfully cancel it by order ID.

**Validates: Requirements 5.7**

### Property 28: Order Failure Error Messages

*For any* failed order placement, the Order_Manager should return a descriptive error message explaining why the order failed.

**Validates: Requirements 5.8**

### Property 29: Data Fetch Minimum Bars

*For any* historical data request, the Market_Data_Provider should return at least the minimum number of bars required for indicator calculations (200 bars).

**Validates: Requirements 4.5**

### Property 30: Indian Instrument Name Support

*For any* valid Indian instrument naming convention (e.g., "RELIANCE", "NIFTY 50", "BANKNIFTY"), the Trading_Bot should recognize and process it correctly.

**Validates: Requirements 7.3**


## Error Handling

### Error Categories

1. **Authentication Errors**
   - Missing token file
   - Expired token (from previous day)
   - Invalid token
   - API key mismatch

2. **Connection Errors**
   - Network timeout
   - Broker API unavailable
   - Rate limit exceeded
   - WebSocket disconnection

3. **Data Errors**
   - Invalid instrument symbol
   - Insufficient historical data
   - Missing data points
   - Data format mismatch

4. **Order Errors**
   - Insufficient margin
   - Invalid order parameters
   - Order rejection by broker
   - Position limit exceeded

5. **Market Errors**
   - Market closed
   - Trading halt
   - Circuit breaker triggered
   - Holiday

### Error Handling Strategy

**Retry Logic**:
- Network errors: Retry up to 3 times with exponential backoff (1s, 2s, 4s)
- Rate limit errors: Exponential backoff starting at 2 seconds
- Transient errors: Retry with backoff
- Permanent errors: Log and skip

**Graceful Degradation**:
- If ML integration fails: Fall back to technical signals only
- If volume analyzer fails: Proceed without volume filter
- If trend detection fails: Proceed with basic signal detection
- If one symbol fails: Continue with other symbols

**User Notification**:
- Authentication errors: Clear instructions to run login script
- Configuration errors: Specific parameter that needs correction
- Trading errors: Reason for rejection and suggested action

**Logging**:
- All errors logged with full context
- Stack traces for unexpected errors
- Error counts tracked for monitoring
- Critical errors trigger alerts

## Testing Strategy

### Dual Testing Approach

The testing strategy combines unit tests for specific scenarios and property-based tests for comprehensive coverage:

**Unit Tests**:
- Specific examples of broker operations
- Edge cases (empty data, invalid tokens, etc.)
- Error conditions (network failures, invalid orders)
- Integration points between components
- Indian market specifics (trading hours, holidays)

**Property-Based Tests**:
- Universal properties that hold for all inputs
- Data format consistency across all instruments
- Order placement success for valid parameters
- Position tracking accuracy for all positions
- Risk management constraints for all calculations
- Minimum 100 iterations per property test

### Test Configuration

Property-based tests should be configured with:
- Minimum 100 iterations per test
- Random generation of valid inputs
- Edge case generation (boundary values)
- Invalid input generation for error testing

Each property test must reference its design document property:
```python
# Feature: indian-market-broker-integration, Property 4: Historical Data Format Consistency
def test_historical_data_format_property():
    # Test implementation
    pass
```

### Testing Phases

**Phase 1: Unit Testing**
- Test each broker adapter method individually
- Test authentication flow
- Test data format conversions
- Test error handling

**Phase 2: Integration Testing**
- Test broker adapter with real API (sandbox/paper trading)
- Test full trading flow (signal → order → position)
- Test with multiple instruments
- Test during different market conditions

**Phase 3: Property-Based Testing**
- Test data format properties with random instruments
- Test order placement properties with random parameters
- Test risk management properties with random account states
- Test timeframe conversion with all MT5 constants

**Phase 4: End-to-End Testing**
- Run bot in paper trading mode for full trading day
- Verify all signals logged correctly
- Verify all orders simulated correctly
- Verify position tracking accurate
- Verify risk limits enforced

### Validation Checklist

Before going live:
- [ ] Authentication works with real Kite account
- [ ] Historical data fetches correctly for all configured instruments
- [ ] Data format compatible with existing indicators
- [ ] All indicator calculations produce same results as MT5 bot
- [ ] Orders place successfully in paper trading mode
- [ ] Position tracking matches broker's position data
- [ ] Risk limits enforced correctly
- [ ] Trading hours respected
- [ ] Market holidays handled correctly
- [ ] Error handling works for all error types
- [ ] Logging captures all trading decisions
- [ ] Configuration migration from MT5 works correctly

### Test Data

**Mock Data**:
- Sample token files (valid, expired, invalid)
- Sample historical data (various instruments and timeframes)
- Sample account info (various margin levels)
- Sample positions (various P&L states)

**Real Data** (Sandbox/Paper Trading):
- Real Kite Connect API responses
- Real market data during trading hours
- Real order responses (paper trading)
- Real position updates

### Performance Testing

- Data fetch latency: < 1 second for 200 bars
- Order placement latency: < 500ms
- Position update latency: < 200ms
- Signal generation time: < 2 seconds per symbol
- Memory usage: < 500MB for 10 symbols
- CPU usage: < 50% average

## Migration Guide

### Step 1: Setup Kite Connect Account

1. Open Zerodha trading account
2. Complete KYC verification
3. Register for Kite Connect API at https://kite.trade
4. Get API key and API secret
5. Fund account with minimum capital

### Step 2: Install Dependencies

```bash
pip install kiteconnect pandas numpy pytz
```

### Step 3: Configure Authentication

1. Update `kite_login.py` with your API key and secret
2. Run `python kite_login.py` to authenticate
3. Verify `kite_token.json` is created with today's date

### Step 4: Migrate Configuration

1. Copy your MT5 bot configuration
2. Update broker settings:
   ```python
   "broker": "kite",
   "kite_api_key": "your_api_key",
   "kite_token_file": "kite_token.json",
   "default_exchange": "NSE"
   ```
3. Update symbols to Indian instruments:
   ```python
   "symbols": ["RELIANCE", "TCS", "INFY"]  # Instead of ["XAUUSD", "XAGUSD"]
   ```
4. Update trading hours:
   ```python
   "trading_hours": {
       "start": "09:15",
       "end": "15:30"
   }
   ```
5. Keep all other parameters (indicators, risk, etc.) the same

### Step 5: Test in Paper Trading Mode

1. Enable paper trading mode in configuration
2. Run bot for one full trading day
3. Verify signals generated correctly
4. Verify orders simulated correctly
5. Review logs for any errors

### Step 6: Start with Small Position Sizes

1. Set very small position sizes initially
2. Set conservative risk limits
3. Trade only 1-2 liquid instruments
4. Monitor every trade closely
5. Gradually increase size as confidence builds

### Step 7: Daily Authentication

Kite Connect tokens expire daily. Set up daily authentication:
1. Run `kite_login.py` every morning before market open
2. Or automate with a scheduled task
3. Bot will check token validity before trading

### Rollback Plan

If issues occur:
1. Stop the bot immediately
2. Close all open positions manually
3. Review logs to identify issue
4. Fix configuration or code
5. Test in paper trading mode again
6. Resume live trading only after verification

## Future Extensibility

### Adding New Brokers

To add support for a new Indian broker (e.g., Alice Blue, Angel One, Upstox):

1. Create new adapter class inheriting from `BrokerAdapter`
2. Implement all abstract methods
3. Handle broker-specific authentication
4. Convert broker-specific data formats to standard format
5. Add broker-specific configuration section
6. Update broker selection logic in main bot
7. Test thoroughly with broker's sandbox/paper trading

Example structure:
```python
class AliceBlueAdapter(BrokerAdapter):
    def __init__(self, config):
        # Initialize Alice Blue API
        pass
    
    def connect(self):
        # Implement Alice Blue authentication
        pass
    
    # Implement other methods...
```

### Adding New Market Segments

To add support for new market segments (e.g., commodities, currency):

1. Add segment-specific configuration
2. Update instrument validation logic
3. Add segment-specific trading hours if different
4. Update position sizing for segment-specific margin requirements
5. Test with instruments from new segment

### Adding Real-Time Data Streaming

To add WebSocket support for real-time data:

1. Implement WebSocket connection in broker adapter
2. Add callback handlers for tick data
3. Update signal generation to use real-time data
4. Add reconnection logic for WebSocket failures
5. Test with high-frequency data

### Adding Advanced Order Types

To add support for advanced order types (e.g., iceberg orders, GTT):

1. Extend `place_order` method with new order type parameters
2. Add broker-specific order type conversion
3. Update order tracking for new order types
4. Test order execution and modification

