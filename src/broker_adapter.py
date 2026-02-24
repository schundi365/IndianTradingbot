"""
Broker Adapter - Abstract Base Class

This module defines the standard interface that all broker implementations must follow.
It provides a uniform API for broker operations, allowing the trading bot to work with
multiple Indian broker APIs without changing the core trading logic.

Requirements: 1.1, 1.2, 1.5
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


class BrokerAdapter(ABC):
    """
    Abstract base class for broker API adapters.
    
    All broker implementations (Kite Connect, Alice Blue, Angel One, etc.) must
    inherit from this class and implement all abstract methods to ensure
    compatibility with the trading bot.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to broker API.
        
        This method should handle authentication, token validation, and any
        initialization required to start using the broker API.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Example:
            >>> adapter = KiteAdapter(config)
            >>> if adapter.connect():
            ...     print("Connected successfully")
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close connection to broker API.
        
        This method should clean up any resources, close connections, and
        perform any necessary cleanup operations.
        
        Returns:
            None
            
        Example:
            >>> adapter.disconnect()
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connection to broker API is active.
        
        This method should verify that the connection is still valid and
        can be used for trading operations.
        
        Returns:
            bool: True if connected and ready for operations, False otherwise
            
        Example:
            >>> if adapter.is_connected():
            ...     # Proceed with trading operations
            ...     pass
        """
        pass
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for a given instrument.
        
        This method retrieves historical market data in a standardized format
        that is compatible with the trading bot's indicator calculations.
        
        Args:
            symbol (str): Instrument symbol (e.g., "RELIANCE", "NIFTY 50")
            timeframe (str): Timeframe for the data (e.g., "minute", "5minute", 
                           "15minute", "30minute", "60minute", "day")
            bars (int): Number of bars to fetch (minimum 200 recommended for
                       indicator calculations)
        
        Returns:
            Optional[pd.DataFrame]: DataFrame with columns:
                - time (datetime): Timestamp of the bar
                - open (float): Opening price
                - high (float): Highest price
                - low (float): Lowest price
                - close (float): Closing price
                - volume (int): Trading volume
            Returns None if data fetch fails.
            
        Example:
            >>> df = adapter.get_historical_data("RELIANCE", "30minute", 200)
            >>> if df is not None:
            ...     print(f"Fetched {len(df)} bars")
        """
        pass
    
    @abstractmethod
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
        Place an order with the broker.
        
        This method places a trading order with the specified parameters.
        It supports various order types including market, limit, stop-loss,
        and stop-loss market orders.
        
        Args:
            symbol (str): Instrument symbol to trade
            direction (int): Trade direction (1 for buy, -1 for sell)
            quantity (float): Number of units to trade (should be multiple of lot size)
            order_type (str): Type of order - "MARKET", "LIMIT", "SL" (stop-loss),
                            or "SL-M" (stop-loss market)
            price (Optional[float]): Limit price for LIMIT orders
            trigger_price (Optional[float]): Trigger price for SL and SL-M orders
            stop_loss (Optional[float]): Stop loss price for bracket orders
            take_profit (Optional[float]): Take profit price for bracket orders
            product_type (str): Product type - "MIS" (intraday) or "NRML" (delivery)
        
        Returns:
            Optional[str]: Order ID if successful, None if order placement fails
            
        Example:
            >>> # Place a market buy order
            >>> order_id = adapter.place_order(
            ...     symbol="RELIANCE",
            ...     direction=1,
            ...     quantity=50,
            ...     order_type="MARKET",
            ...     product_type="MIS"
            ... )
            >>> if order_id:
            ...     print(f"Order placed: {order_id}")
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
        """
        Modify an existing pending order.
        
        This method allows modification of order parameters for pending orders
        that have not yet been executed.
        
        Args:
            order_id (str): Unique identifier of the order to modify
            quantity (Optional[float]): New quantity (if changing)
            price (Optional[float]): New limit price (if changing)
            trigger_price (Optional[float]): New trigger price (if changing)
        
        Returns:
            bool: True if modification successful, False otherwise
            
        Example:
            >>> # Modify order price
            >>> success = adapter.modify_order(
            ...     order_id="240115000123456",
            ...     price=2455.50
            ... )
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.
        
        This method cancels an order that has not yet been executed.
        
        Args:
            order_id (str): Unique identifier of the order to cancel
        
        Returns:
            bool: True if cancellation successful, False otherwise
            
        Example:
            >>> success = adapter.cancel_order("240115000123456")
            >>> if success:
            ...     print("Order cancelled successfully")
        """
        pass
    
    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions from the broker.
        
        This method retrieves all open positions or positions for a specific
        symbol, with complete position information including P&L.
        
        Args:
            symbol (Optional[str]): Filter positions by symbol. If None, returns
                                   all positions.
        
        Returns:
            List[Dict]: List of position dictionaries, each containing:
                - symbol (str): Instrument symbol
                - direction (int): Position direction (1 for long, -1 for short)
                - quantity (float): Number of units in position
                - entry_price (float): Average entry price
                - current_price (float): Current market price
                - pnl (float): Profit/Loss in absolute currency terms
                - pnl_percent (float): Profit/Loss as percentage of investment
            
        Example:
            >>> positions = adapter.get_positions("RELIANCE")
            >>> for pos in positions:
            ...     print(f"{pos['symbol']}: P&L = {pos['pnl']:.2f}")
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """
        Get account information including balance and margin.
        
        This method retrieves current account status including available
        funds and margin utilization.
        
        Returns:
            Dict: Account information dictionary containing:
                - balance (float): Total account balance
                - equity (float): Current equity (balance + unrealized P&L)
                - margin_available (float): Available margin for new trades
                - margin_used (float): Margin currently used by open positions
            
        Example:
            >>> account = adapter.get_account_info()
            >>> print(f"Available margin: {account['margin_available']:.2f}")
        """
        pass
    
    @abstractmethod
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        """
        Get instrument-specific information.
        
        This method retrieves trading parameters for a specific instrument,
        including lot size, tick size, and broker-specific identifiers.
        
        Args:
            symbol (str): Instrument symbol
        
        Returns:
            Optional[Dict]: Instrument information dictionary containing:
                - symbol (str): Instrument symbol
                - lot_size (int): Minimum trading quantity (lot size)
                - tick_size (float): Minimum price movement
                - instrument_token (str): Broker-specific instrument identifier
            Returns None if instrument not found.
            
        Example:
            >>> info = adapter.get_instrument_info("RELIANCE")
            >>> if info:
            ...     print(f"Lot size: {info['lot_size']}")
            ...     print(f"Tick size: {info['tick_size']}")
        """
        pass
    
    @abstractmethod
    def get_orders(self) -> List[Dict]:
        """
        Get all orders for the current day.
        
        This method retrieves a list of all orders placed through the broker
        during the current trading session.
        
        Returns:
            List[Dict]: List of order dictionaries, each containing:
                - order_id (str): Unique identifier for the order
                - symbol (str): Instrument symbol
                - status (str): Order status (e.g., "COMPLETE", "CANCELLED", "REJECTED")
                - direction (str): "BUY" or "SELL"
                - quantity (int): Number of units
                - filled_quantity (int): Number of units executed
                - average_price (float): Average execution price
                - order_timestamp (datetime): When the order was placed
            
        Example:
            >>> orders = adapter.get_orders()
            >>> for order in orders:
            ...     print(f"Order {order['order_id']}: {order['status']}")
        """
        pass


    @abstractmethod
    def convert_timeframe(self, mt5_timeframe: int) -> str:
        """
        Convert MT5 timeframe constant to broker-specific format.
        
        This method translates MetaTrader 5 timeframe constants to the
        format expected by the broker's API.
        
        Args:
            mt5_timeframe (int): MT5 timeframe constant (e.g., TIMEFRAME_M1,
                               TIMEFRAME_M5, TIMEFRAME_M15, TIMEFRAME_M30,
                               TIMEFRAME_H1, TIMEFRAME_D1)
        
        Returns:
            str: Broker-specific timeframe string (e.g., "minute", "5minute",
                "15minute", "30minute", "60minute", "day")
            
        Example:
            >>> import MetaTrader5 as mt5
            >>> timeframe = adapter.convert_timeframe(mt5.TIMEFRAME_M30)
            >>> print(timeframe)  # Output: "30minute"
        """
        pass
