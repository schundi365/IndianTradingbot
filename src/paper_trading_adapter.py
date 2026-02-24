"""
Paper Trading Adapter - Implementation of BrokerAdapter for simulated trading

This module implements the BrokerAdapter interface for paper trading,
providing simulated order execution without real broker API calls.

Requirements: 15.1, 15.2
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
import pandas as pd

from src.broker_adapter import BrokerAdapter
from src.paper_trading import PaperTradingEngine


class PaperTradingAdapter(BrokerAdapter):
    """
    Paper Trading adapter implementing the BrokerAdapter interface.
    
    This adapter simulates trading operations without connecting to a real broker,
    useful for testing strategies and learning without risking real capital.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Paper Trading adapter with configuration.
        
        Args:
            config (Dict): Configuration dictionary containing:
                - initial_balance: Starting balance (default: 100000.0)
                - default_exchange: Default exchange (default: 'NSE')
        """
        self.config = config
        self.initial_balance = config.get('paper_trading_initial_balance', 100000.0)
        self.default_exchange = config.get('default_exchange', 'NSE')
        
        self.engine = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
        # Initialize current_prices before creating mock instruments
        self.current_prices = {}  # symbol -> current price
        
        # Mock instrument data for paper trading
        self.mock_instruments = self._create_mock_instruments()
    
    def _create_mock_instruments(self) -> Dict:
        """
        Create mock instrument data for paper trading.
        
        Returns:
            Dictionary of instrument data keyed by symbol
        """
        instruments = {
            'RELIANCE': {
                'symbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'MOCK_RELIANCE',
                'lot_size': 1,
                'tick_size': 0.05,
                'last_price': 2450.00
            },
            'TCS': {
                'symbol': 'TCS',
                'name': 'Tata Consultancy Services Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'MOCK_TCS',
                'lot_size': 1,
                'tick_size': 0.05,
                'last_price': 3650.00
            },
            'INFY': {
                'symbol': 'INFY',
                'name': 'Infosys Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'MOCK_INFY',
                'lot_size': 1,
                'tick_size': 0.05,
                'last_price': 1450.00
            },
            'NIFTY 50': {
                'symbol': 'NIFTY 50',
                'name': 'Nifty 50 Index',
                'exchange': 'NSE',
                'instrument_type': 'INDEX',
                'instrument_token': 'MOCK_NIFTY50',
                'lot_size': 50,
                'tick_size': 0.05,
                'last_price': 21500.00
            },
            'BANKNIFTY': {
                'symbol': 'BANKNIFTY',
                'name': 'Bank Nifty Index',
                'exchange': 'NSE',
                'instrument_type': 'INDEX',
                'instrument_token': 'MOCK_BANKNIFTY',
                'lot_size': 25,
                'tick_size': 0.05,
                'last_price': 45000.00
            }
        }
        
        # Initialize current prices
        for symbol, data in instruments.items():
            self.current_prices[symbol] = data['last_price']
        
        return instruments
    
    def connect(self) -> bool:
        """
        Establish connection to paper trading engine.
        
        Returns:
            bool: True (always succeeds for paper trading)
        """
        try:
            self.engine = PaperTradingEngine(self.initial_balance)
            self.connected = True
            self.logger.info(f"Paper Trading connected with balance: Rs.{self.initial_balance:,.2f}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize paper trading: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Close connection to paper trading engine.
        
        Returns:
            None
        """
        if self.engine:
            stats = self.engine.get_trade_statistics()
            self.logger.info("="*80)
            self.logger.info("🧪 PAPER TRADING SESSION SUMMARY")
            self.logger.info(f"Total Trades: {stats['total_trades']}")
            self.logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
            self.logger.info(f"Total P&L: Rs.{stats['total_pnl']:,.2f}")
            self.logger.info(f"Return: {stats.get('return_percent', 0):.2f}%")
            self.logger.info(f"Final Balance: Rs.{self.engine.balance:,.2f}")
            self.logger.info(f"Final Equity: Rs.{self.engine.equity:,.2f}")
            self.logger.info("="*80)
        
        self.engine = None
        self.connected = False
        self.logger.info("Paper Trading disconnected")
    
    def is_connected(self) -> bool:
        """
        Check if connection to paper trading engine is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected and self.engine is not None
    
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int
    ) -> Optional[pd.DataFrame]:
        """
        Generate simulated historical OHLCV data.
        
        Args:
            symbol (str): Instrument symbol
            timeframe (str): Timeframe (e.g., "minute", "5minute", "30minute", "day")
            bars (int): Number of bars to generate
        
        Returns:
            Optional[pd.DataFrame]: DataFrame with simulated OHLCV data
        """
        try:
            if symbol not in self.mock_instruments:
                self.logger.warning(f"Symbol {symbol} not found in mock instruments")
                return None
            
            base_price = self.mock_instruments[symbol]['last_price']
            
            # Generate simulated data with random walk
            import numpy as np
            
            # Set seed for reproducibility in tests
            np.random.seed(hash(symbol) % 2**32)
            
            # Generate price movements (random walk with slight upward bias)
            returns = np.random.normal(0.0001, 0.02, bars)
            prices = base_price * np.exp(np.cumsum(returns))
            
            # Generate OHLCV data
            data = []
            current_time = datetime.now()
            
            # Calculate time delta based on timeframe
            if "minute" in timeframe:
                minutes = int(timeframe.replace("minute", "")) if timeframe != "minute" else 1
                time_delta = pd.Timedelta(minutes=minutes)
            elif "hour" in timeframe:
                hours = int(timeframe.replace("hour", ""))
                time_delta = pd.Timedelta(hours=hours)
            else:  # day
                time_delta = pd.Timedelta(days=1)
            
            for i in range(bars):
                close_price = prices[i]
                
                # Generate OHLC from close price
                high = close_price * (1 + abs(np.random.normal(0, 0.005)))
                low = close_price * (1 - abs(np.random.normal(0, 0.005)))
                open_price = close_price * (1 + np.random.normal(0, 0.003))
                
                # Ensure OHLC relationships are valid
                high = max(high, open_price, close_price)
                low = min(low, open_price, close_price)
                
                # Generate volume
                volume = int(np.random.uniform(100000, 1000000))
                
                data.append({
                    'time': current_time - (bars - i - 1) * time_delta,
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            
            # Update current price
            self.current_prices[symbol] = df.iloc[-1]['close']
            
            self.logger.info(f"Generated {len(df)} bars of simulated data for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to generate historical data: {e}")
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
        Place a simulated order.
        
        Args:
            symbol (str): Instrument symbol
            direction (int): Trade direction (1 for buy, -1 for sell)
            quantity (float): Number of units to trade
            order_type (str): Order type - "MARKET", "LIMIT", "SL", "SL-M"
            price (Optional[float]): Limit price for LIMIT orders
            trigger_price (Optional[float]): Trigger price for SL orders
            stop_loss (Optional[float]): Stop loss price
            take_profit (Optional[float]): Take profit price
            product_type (str): Product type - "MIS" (intraday) or "NRML" (delivery)
        
        Returns:
            Optional[str]: Order ID if successful, None otherwise
        """
        if not self.is_connected():
            self.logger.error("Not connected to paper trading engine")
            return None
        
        # Get current price for the symbol
        current_price = self.current_prices.get(symbol)
        if current_price is None:
            # Try to get from mock instruments
            if symbol in self.mock_instruments:
                current_price = self.mock_instruments[symbol]['last_price']
            else:
                self.logger.error(f"No price data available for {symbol}")
                return None
        
        return self.engine.place_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=order_type,
            price=price,
            trigger_price=trigger_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            product_type=product_type,
            current_price=current_price
        )
    
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ) -> bool:
        """
        Modify a simulated pending order.
        
        Args:
            order_id (str): Order ID to modify
            quantity (Optional[float]): New quantity
            price (Optional[float]): New limit price
            trigger_price (Optional[float]): New trigger price
        
        Returns:
            bool: True if modification successful, False otherwise
        """
        if not self.is_connected():
            self.logger.error("Not connected to paper trading engine")
            return False
        
        return self.engine.modify_order(order_id, quantity, price, trigger_price)
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a simulated pending order.
        
        Args:
            order_id (str): Order ID to cancel
        
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if not self.is_connected():
            self.logger.error("Not connected to paper trading engine")
            return False
        
        return self.engine.cancel_order(order_id)
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get simulated open positions.
        
        Args:
            symbol (Optional[str]): Filter by symbol. If None, returns all positions.
        
        Returns:
            List[Dict]: List of position dictionaries
        """
        if not self.is_connected():
            return []
        
        # Update positions with current prices
        positions = self.engine.get_positions(symbol)
        
        for pos in positions:
            pos_symbol = pos['symbol']
            if pos_symbol in self.current_prices:
                self.engine.update_positions(pos_symbol, self.current_prices[pos_symbol])
        
        # Get updated positions
        return self.engine.get_positions(symbol)
    
    def get_account_info(self) -> Dict:
        """
        Get simulated account information.
        
        Returns:
            Dict: Account information dictionary
        """
        if not self.is_connected():
            return {
                'balance': 0.0,
                'equity': 0.0,
                'margin_available': 0.0,
                'margin_used': 0.0
            }
        
        return self.engine.get_account_info()
    
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        """
        Get mock instrument information.
        
        Args:
            symbol (str): Instrument symbol
        
        Returns:
            Optional[Dict]: Instrument information or None if not found
        """
        if symbol in self.mock_instruments:
            return {
                'symbol': symbol,
                'lot_size': self.mock_instruments[symbol]['lot_size'],
                'tick_size': self.mock_instruments[symbol]['tick_size'],
                'instrument_token': self.mock_instruments[symbol]['instrument_token']
            }
        
        self.logger.warning(f"Instrument not found: {symbol}")
        return None
    
    def get_orders(self) -> List[Dict]:
        """
        Get all simulated orders.
        
        Returns:
            List[Dict]: List of standardized order dictionaries
        """
        if not self.is_connected():
            return []
        
        return self.engine.get_orders()

    def convert_timeframe(self, mt5_timeframe: int) -> str:
        """
        Convert MT5 timeframe constant to string format.
        
        Args:
            mt5_timeframe (int): MT5 timeframe constant
        
        Returns:
            str: Timeframe string
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
            
            return timeframe_map.get(mt5_timeframe, "30minute")
            
        except ImportError:
            # If MT5 not available, assume numeric input in minutes
            minute_map = {
                1: "minute",
                5: "5minute",
                15: "15minute",
                30: "30minute",
                60: "60minute",
                1440: "day"
            }
            
            return minute_map.get(mt5_timeframe, "30minute")
    
    def get_instruments(self) -> List[Dict]:
        """
        Get list of available mock instruments.
        
        Returns:
            List of instrument dictionaries
        """
        return list(self.mock_instruments.values())
    
    def close_position(self, order_id: str) -> bool:
        """
        Close a simulated position.
        
        Args:
            order_id: Order ID of position to close
        
        Returns:
            True if position closed successfully
        """
        if not self.is_connected():
            return False
        
        # Find position to get symbol
        positions = self.engine.get_positions()
        for pos in positions:
            if pos['order_id'] == order_id:
                symbol = pos['symbol']
                current_price = self.current_prices.get(symbol, pos['current_price'])
                return self.engine.close_position(order_id, current_price)
        
        return False
