"""
Kite Connect Adapter - Implementation of BrokerAdapter for Zerodha Kite Connect

This module implements the BrokerAdapter interface for Kite Connect API,
providing authentication, connection management, data fetching, order placement,
and position tracking for Indian stock market trading.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
import logging
import pandas as pd

from kiteconnect import KiteConnect
from src.broker_adapter import BrokerAdapter
from src.error_handler import (
    ErrorHandler,
    AuthenticationError,
    ConnectionError,
    DataError,
    OrderError,
    MarketError,
    ValidationError
)


class KiteAdapter(BrokerAdapter):
    """
    Kite Connect API adapter implementing the BrokerAdapter interface.
    
    This adapter handles:
    - Authentication using token file
    - Connection management with health checks
    - Historical data fetching with retry logic
    - Order placement and management
    - Position tracking
    - Account information retrieval
    - Instrument token caching for faster lookups
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Kite adapter with configuration.
        
        Args:
            config (Dict): Configuration dictionary containing:
                - kite_api_key: API key from Kite Connect
                - kite_token_file: Path to token file (default: 'kite_token.json')
                - default_exchange: Default exchange (default: 'NSE')
        """
        self.config = config
        self.api_key = config.get('kite_api_key')
        self.token_file = config.get('kite_token_file', 'kite_token.json')
        self.default_exchange = config.get('default_exchange', 'NSE')
        
        self.kite = None
        self.access_token = None
        self.instrument_cache = {}  # Cache for instrument tokens
        
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler(self.logger)
    
    def connect(self) -> bool:
        """
        Establish connection to Kite Connect API.
        
        Validates: Requirements 2.2, 3.1, 3.2, 3.3, 3.4
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Read access token from file
            token_path = Path(self.token_file)
            if not token_path.exists():
                self.error_handler.handle_authentication_error(
                    FileNotFoundError(f"Token file not found: {self.token_file}"),
                    self.token_file
                )
                return False
            
            with open(token_path) as f:
                token_data = json.load(f)
            
            # Check if token is from today
            token_date = token_data.get('date')
            today = datetime.now().strftime("%Y-%m-%d")
            
            if token_date != today:
                self.error_handler.handle_authentication_error(
                    ValueError(f"Token is from {token_date}, need today's token ({today})"),
                    self.token_file
                )
                return False
            
            self.access_token = token_data['access_token']
            
            # Initialize Kite Connect
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            
            # Verify connection by getting profile
            profile = self.kite.profile()
            self.logger.info(f"Connected to Kite: {profile['user_name']}")
            self.logger.info(f"Broker: {profile['broker']}")
            
            # Load instrument cache
            self._load_instrument_cache()
            
            return True
            
        except AuthenticationError:
            return False
        except Exception as e:
            self.error_handler.handle_authentication_error(e, self.token_file)
            return False
    
    def disconnect(self) -> None:
        """
        Close connection to Kite Connect API.
        
        Returns:
            None
        """
        self.kite = None
        self.access_token = None
        self.instrument_cache.clear()
        self.logger.info("Disconnected from Kite")
    
    def is_connected(self) -> bool:
        """
        Check if connection to Kite Connect is active.
        
        Returns:
            bool: True if connected and ready for operations, False otherwise
        """
        if not self.kite or not self.access_token:
            return False
        
        try:
            # Quick health check by getting margins
            self.kite.margins()
            return True
        except Exception as e:
            self.logger.warning(f"Connection health check failed: {e}")
            return False
    
    def _load_instrument_cache(self):
        """
        Load instrument tokens for faster lookups.
        
        Validates: Requirement 2.8
        
        This method caches instrument tokens to avoid repeated API calls
        for symbol-to-token conversion.
        """
        try:
            instruments = self.kite.instruments()
            for inst in instruments:
                key = f"{inst['exchange']}:{inst['tradingsymbol']}"
                self.instrument_cache[key] = {
                    'instrument_token': inst['instrument_token'],
                    'lot_size': inst.get('lot_size', 1),
                    'tick_size': inst.get('tick_size', 0.05)
                }
            self.logger.info(f"Loaded {len(self.instrument_cache)} instruments into cache")
        except Exception as e:
            self.logger.warning(f"Failed to load instrument cache: {e}")
    
    def _get_instrument_token(self, symbol: str, exchange: str = None) -> Optional[int]:
        """
        Get instrument token for a symbol.
        
        Validates: Requirement 2.8
        
        Args:
            symbol (str): Instrument symbol
            exchange (str): Exchange (defaults to configured default_exchange)
        
        Returns:
            Optional[int]: Instrument token if found, None otherwise
        """
        if exchange is None:
            exchange = self.default_exchange
        
        key = f"{exchange}:{symbol}"
        cached = self.instrument_cache.get(key)
        return cached['instrument_token'] if cached else None
    
    def _retry_with_backoff(self, func, max_retries=3):
        """
        Execute function with exponential backoff on rate limit.
        
        Validates: Requirement 2.9, 12.3
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
        
        Returns:
            Result of function execution
        
        Raises:
            Exception: If all retries fail
        """
        return self.error_handler.retry_with_backoff(
            func,
            max_retries=max_retries,
            initial_delay=1.0,
            backoff_factor=2.0,
            exceptions=(Exception,)
        )
    
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data from Kite Connect.
        
        Validates: Requirements 2.4, 4.1, 4.2, 4.3, 4.4, 4.5, 14.1, 14.2, 14.3, 14.4
        
        Args:
            symbol (str): Instrument symbol
            timeframe (str): Timeframe (e.g., "minute", "5minute", "30minute", "day")
            bars (int): Number of bars to fetch
        
        Returns:
            Optional[pd.DataFrame]: DataFrame with columns: time, open, high, low, close, volume
                                   Returns None if data fetch fails
        """
        try:
            # Get instrument token
            exchange = self.default_exchange
            instrument_token = self._get_instrument_token(symbol, exchange)
            
            if not instrument_token:
                self.error_handler.handle_data_error(
                    ValueError(f"Instrument token not found for {symbol}"),
                    symbol,
                    timeframe,
                    "get_instrument_token"
                )
                return None
            
            # Calculate date range
            to_date = datetime.now()
            
            # Estimate days needed based on timeframe and bars
            if "minute" in timeframe:
                minutes = int(timeframe.replace("minute", ""))
                days_needed = (bars * minutes) // (6 * 60) + 5  # 6 hours trading day
            elif "hour" in timeframe:
                hours = int(timeframe.replace("hour", ""))
                days_needed = (bars * hours) // 6 + 5
            else:  # day
                days_needed = bars + 10
            
            from_date = to_date - timedelta(days=days_needed)
            
            # Fetch data with retry logic
            def fetch():
                return self.kite.historical_data(
                    instrument_token,
                    from_date,
                    to_date,
                    timeframe
                )
            
            data = self._retry_with_backoff(fetch)
            
            if not data:
                self.logger.warning(f"No data returned for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df.rename(columns={'date': 'time'}, inplace=True)
            
            # Ensure correct data types
            df['time'] = pd.to_datetime(df['time'])
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(int)
            
            # Return last N bars
            result = df.tail(bars).reset_index(drop=True)
            
            self.logger.info(f"Fetched {len(result)} bars for {symbol} ({timeframe})")
            return result
            
        except DataError:
            return None
        except Exception as e:
            self.error_handler.handle_data_error(e, symbol, timeframe, "fetch_historical_data")
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
        """
        Place an order on Kite Connect.
        
        Validates: Requirements 2.5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.8, 5.9, 12.4
        
        Args:
            symbol (str): Instrument symbol
            direction (int): Trade direction (1 for buy, -1 for sell)
            quantity (float): Number of units to trade
            order_type (str): Order type - "MARKET", "LIMIT", "SL", "SL-M"
            price (Optional[float]): Limit price for LIMIT orders
            trigger_price (Optional[float]): Trigger price for SL orders
            stop_loss (Optional[float]): Stop loss price (for bracket orders)
            take_profit (Optional[float]): Take profit price (for bracket orders)
            product_type (str): Product type - "MIS" (intraday) or "NRML" (delivery)
        
        Returns:
            Optional[str]: Order ID if successful, None otherwise
        """
        order_params = {
            'symbol': symbol,
            'direction': direction,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'trigger_price': trigger_price,
            'product_type': product_type
        }
        
        try:
            # Validate quantity
            if quantity <= 0:
                self.error_handler.handle_validation_error(
                    "quantity",
                    quantity,
                    "positive number"
                )
                return None
            
            # Get instrument info for validation
            inst_info = self.get_instrument_info(symbol)
            if not inst_info:
                self.error_handler.handle_validation_error(
                    "symbol",
                    symbol,
                    "valid tradable instrument"
                )
                return None
            
            # Validate quantity is multiple of lot size
            lot_size = inst_info['lot_size']
            if quantity % lot_size != 0:
                self.error_handler.handle_validation_error(
                    "quantity",
                    quantity,
                    f"multiple of lot size ({lot_size})"
                )
                return None
            
            # Validate price is multiple of tick size if provided
            tick_size = inst_info['tick_size']
            if price is not None:
                if price <= 0:
                    self.error_handler.handle_validation_error(
                        "price",
                        price,
                        "positive number"
                    )
                    return None
                
                # Check tick size compliance (with small tolerance for floating point)
                remainder = abs(price % tick_size)
                if remainder > 0.0001 and remainder < (tick_size - 0.0001):
                    self.error_handler.handle_validation_error(
                        "price",
                        price,
                        f"multiple of tick size ({tick_size})"
                    )
                    return None
            
            # Validate order type
            if order_type not in ["MARKET", "LIMIT", "SL", "SL-M"]:
                self.error_handler.handle_validation_error(
                    "order_type",
                    order_type,
                    "MARKET, LIMIT, SL, or SL-M"
                )
                return None
            
            # Validate required parameters for order types
            if order_type == "LIMIT" and price is None:
                self.error_handler.handle_validation_error(
                    "price",
                    None,
                    "required for LIMIT orders"
                )
                return None
            
            if order_type in ["SL", "SL-M"] and trigger_price is None:
                self.error_handler.handle_validation_error(
                    "trigger_price",
                    None,
                    f"required for {order_type} orders"
                )
                return None
            
            exchange = self.default_exchange
            
            # Convert direction to transaction type
            transaction_type = (
                self.kite.TRANSACTION_TYPE_BUY if direction == 1 
                else self.kite.TRANSACTION_TYPE_SELL
            )
            
            # Convert order type
            kite_order_type = {
                "MARKET": self.kite.ORDER_TYPE_MARKET,
                "LIMIT": self.kite.ORDER_TYPE_LIMIT,
                "SL": self.kite.ORDER_TYPE_SL,
                "SL-M": self.kite.ORDER_TYPE_SLM
            }.get(order_type, self.kite.ORDER_TYPE_MARKET)
            
            # Convert product type
            kite_product = (
                self.kite.PRODUCT_MIS if product_type == "MIS" 
                else self.kite.PRODUCT_NRML
            )
            
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
            
            self.logger.info(
                f"Order placed: {order_id} | {symbol} | "
                f"{'BUY' if direction == 1 else 'SELL'} | "
                f"Qty: {quantity} | Type: {order_type}"
            )
            
            # Note: Bracket orders with SL/TP require special handling
            if stop_loss or take_profit:
                self.logger.warning(
                    "Stop loss and take profit require bracket order implementation. "
                    "Place separate SL orders manually for now."
                )
            
            return str(order_id)
            
        except (ValidationError, OrderError):
            return None
        except Exception as e:
            self.error_handler.handle_order_error(e, order_params)
            return None
    
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ) -> bool:
        """
        Modify an existing pending order.
        
        Validates: Requirement 5.6, 12.4
        
        Args:
            order_id (str): Order ID to modify
            quantity (Optional[float]): New quantity
            price (Optional[float]): New limit price
            trigger_price (Optional[float]): New trigger price
        
        Returns:
            bool: True if modification successful, False otherwise
        """
        try:
            params = {}
            if quantity is not None:
                if quantity <= 0:
                    self.error_handler.handle_validation_error(
                        "quantity",
                        quantity,
                        "positive number"
                    )
                    return False
                params['quantity'] = int(quantity)
            
            if price is not None:
                if price <= 0:
                    self.error_handler.handle_validation_error(
                        "price",
                        price,
                        "positive number"
                    )
                    return False
                params['price'] = price
            
            if trigger_price is not None:
                if trigger_price <= 0:
                    self.error_handler.handle_validation_error(
                        "trigger_price",
                        trigger_price,
                        "positive number"
                    )
                    return False
                params['trigger_price'] = trigger_price
            
            if not params:
                self.logger.warning("No parameters provided for order modification")
                return False
            
            self.kite.modify_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id,
                **params
            )
            
            self.logger.info(f"Order modified: {order_id} | {params}")
            return True
            
        except ValidationError:
            return False
        except Exception as e:
            self.error_handler.handle_order_error(e, {'order_id': order_id, 'operation': 'modify', **params})
            return False
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.
        
        Validates: Requirement 5.7, 12.4
        
        Args:
            order_id (str): Order ID to cancel
        
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        try:
            self.kite.cancel_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id
            )
            self.logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            self.error_handler.handle_order_error(e, {'order_id': order_id, 'operation': 'cancel'})
            return False
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions from Kite Connect.
        
        Validates: Requirements 2.6, 6.1, 6.2, 6.3, 6.4, 12.1
        
        Args:
            symbol (Optional[str]): Filter by symbol. If None, returns all positions.
        
        Returns:
            List[Dict]: List of position dictionaries with keys:
                - symbol: str
                - direction: int (1 for long, -1 for short)
                - quantity: float
                - entry_price: float
                - current_price: float
                - pnl: float
                - pnl_percent: float
        """
        try:
            positions = self.kite.positions()
            net_positions = positions.get('net', [])
            
            result = []
            for pos in net_positions:
                # Skip closed positions
                if pos['quantity'] == 0:
                    continue
                
                # Filter by symbol if specified
                if symbol and pos['tradingsymbol'] != symbol:
                    continue
                
                direction = 1 if pos['quantity'] > 0 else -1
                quantity = abs(pos['quantity'])
                entry_price = pos['average_price']
                current_price = pos['last_price']
                pnl = pos['pnl']
                
                # Calculate P&L percentage
                investment = entry_price * quantity
                pnl_percent = (pnl / investment * 100) if investment > 0 else 0.0
                
                result.append({
                    'symbol': pos['tradingsymbol'],
                    'direction': direction,
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent
                })
            
            return result
            
        except Exception as e:
            self.error_handler.log_error(e, {'operation': 'get_positions', 'symbol': symbol})
            return []
    
    def get_account_info(self) -> Dict:
        """
        Get account information from Kite Connect.
        
        Validates: Requirement 2.7, 12.1
        
        Returns:
            Dict: Account information with keys:
                - balance: float
                - equity: float
                - margin_available: float
                - margin_used: float
        """
        try:
            margins = self.kite.margins()
            equity_margins = margins.get('equity', {})
            
            return {
                'balance': equity_margins.get('net', 0.0),
                'equity': equity_margins.get('available', {}).get('live_balance', 0.0),
                'margin_available': equity_margins.get('available', {}).get('cash', 0.0),
                'margin_used': equity_margins.get('utilised', {}).get('debits', 0.0)
            }
            
        except Exception as e:
            self.error_handler.log_error(e, {'operation': 'get_account_info'})
            return {
                'balance': 0.0,
                'equity': 0.0,
                'margin_available': 0.0,
                'margin_used': 0.0
            }
    
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        """
        Get instrument-specific information.
        
        Validates: Requirement 8.4, 12.1
        
        Args:
            symbol (str): Instrument symbol
        
        Returns:
            Optional[Dict]: Instrument information with keys:
                - symbol: str
                - lot_size: int
                - tick_size: float
                - instrument_token: str
            Returns None if instrument not found.
        """
        try:
            exchange = self.default_exchange
            key = f"{exchange}:{symbol}"
            
            # Check cache first
            cached = self.instrument_cache.get(key)
            if cached:
                return {
                    'symbol': symbol,
                    'lot_size': cached.get('lot_size', 1),
                    'tick_size': cached.get('tick_size', 0.05),
                    'instrument_token': str(cached['instrument_token'])
                }
            
            # If not in cache, fetch from API
            instruments = self.kite.instruments(exchange)
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    return {
                        'symbol': symbol,
                        'lot_size': inst.get('lot_size', 1),
                        'tick_size': inst.get('tick_size', 0.05),
                        'instrument_token': str(inst['instrument_token'])
                    }
            
            self.logger.warning(f"Instrument not found: {symbol}")
            return None
            
        except Exception as e:
            self.error_handler.log_error(e, {'operation': 'get_instrument_info', 'symbol': symbol})
            return None
    
    def convert_timeframe(self, mt5_timeframe: int) -> str:
        """
        Convert MT5 timeframe constant to Kite Connect format.
        
        Validates: Requirement 11.4
        
        Args:
            mt5_timeframe (int): MT5 timeframe constant
        
        Returns:
            str: Kite Connect timeframe string
        """
        try:
            import MetaTrader5 as mt5
            
            timeframe_map = {
                mt5.TIMEFRAME_M1: "minute",
                mt5.TIMEFRAME_M5: "5minute",
                mt5.TIMEFRAME_M15: "15minute",
                mt5.TIMEFRAME_M30: "30minute",
                mt5.TIMEFRAME_H1: "60minute",
                mt5.TIMEFRAME_D1: "day"
            }
            
            result = timeframe_map.get(mt5_timeframe, "30minute")
            return result
            
        except ImportError:
            # If MT5 not available, assume numeric input in minutes
            self.logger.warning("MetaTrader5 not available, using numeric timeframe conversion")
            
            # Map common minute values to Kite format
            minute_map = {
                1: "minute",
                5: "5minute",
                15: "15minute",
                30: "30minute",
                60: "60minute",
                1440: "day"
            }
            
            return minute_map.get(mt5_timeframe, "30minute")
