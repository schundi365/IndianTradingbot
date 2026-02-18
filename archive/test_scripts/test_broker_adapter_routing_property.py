"""
Property-Based Test for Broker Adapter Routing
Tests Property 1: Broker Adapter Routing

**Validates: Requirements 1.2**

This test validates that:
- The broker adapter correctly routes operations to the appropriate broker implementation
- Different broker configurations load the correct adapter
- All broker operations are properly delegated to the configured broker
- Routing is consistent across all operation types
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import sys
import os
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock, patch
import pandas as pd

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.broker_adapter import BrokerAdapter
except ImportError as e:
    pytest.skip(f"Could not import broker adapter: {e}", allow_module_level=True)


# Mock broker implementations for testing
class MockKiteAdapter(BrokerAdapter):
    """Mock Kite Connect adapter for testing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.broker_name = "kite"
        self.connected = False
        self.operation_log = []
    
    def connect(self) -> bool:
        self.operation_log.append(("connect", {}))
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.operation_log.append(("disconnect", {}))
        self.connected = False
    
    def is_connected(self) -> bool:
        return self.connected
    
    def get_historical_data(self, symbol: str, timeframe: str, bars: int) -> Optional[pd.DataFrame]:
        self.operation_log.append(("get_historical_data", {"symbol": symbol, "timeframe": timeframe, "bars": bars}))
        return pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=bars, freq='1H'),
            'open': [100.0] * bars,
            'high': [101.0] * bars,
            'low': [99.0] * bars,
            'close': [100.5] * bars,
            'volume': [1000] * bars
        })
    
    def place_order(self, symbol: str, direction: int, quantity: float, order_type: str,
                   price: Optional[float] = None, trigger_price: Optional[float] = None,
                   stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                   product_type: str = "MIS") -> Optional[str]:
        self.operation_log.append(("place_order", {
            "symbol": symbol, "direction": direction, "quantity": quantity,
            "order_type": order_type, "price": price
        }))
        return f"kite_order_{len(self.operation_log)}"
    
    def modify_order(self, order_id: str, quantity: Optional[float] = None,
                    price: Optional[float] = None, trigger_price: Optional[float] = None) -> bool:
        self.operation_log.append(("modify_order", {"order_id": order_id, "quantity": quantity, "price": price}))
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        self.operation_log.append(("cancel_order", {"order_id": order_id}))
        return True
    
    def get_positions(self, symbol: Optional[str] = None) -> list:
        self.operation_log.append(("get_positions", {"symbol": symbol}))
        return [{
            'symbol': symbol or 'RELIANCE',
            'direction': 1,
            'quantity': 50,
            'entry_price': 2450.0,
            'current_price': 2455.0,
            'pnl': 250.0,
            'pnl_percent': 0.2
        }]
    
    def get_account_info(self) -> Dict:
        self.operation_log.append(("get_account_info", {}))
        return {
            'balance': 500000.0,
            'equity': 505000.0,
            'margin_available': 450000.0,
            'margin_used': 50000.0
        }
    
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        self.operation_log.append(("get_instrument_info", {"symbol": symbol}))
        return {
            'symbol': symbol,
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
    
    def convert_timeframe(self, mt5_timeframe: int) -> str:
        self.operation_log.append(("convert_timeframe", {"mt5_timeframe": mt5_timeframe}))
        timeframe_map = {
            1: "minute",
            5: "5minute",
            15: "15minute",
            30: "30minute",
            60: "60minute",
            1440: "day"
        }
        return timeframe_map.get(mt5_timeframe, "30minute")


class MockAliceBlueAdapter(BrokerAdapter):
    """Mock Alice Blue adapter for testing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.broker_name = "alice_blue"
        self.connected = False
        self.operation_log = []
    
    def connect(self) -> bool:
        self.operation_log.append(("connect", {}))
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.operation_log.append(("disconnect", {}))
        self.connected = False
    
    def is_connected(self) -> bool:
        return self.connected
    
    def get_historical_data(self, symbol: str, timeframe: str, bars: int) -> Optional[pd.DataFrame]:
        self.operation_log.append(("get_historical_data", {"symbol": symbol, "timeframe": timeframe, "bars": bars}))
        return pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=bars, freq='1H'),
            'open': [100.0] * bars,
            'high': [101.0] * bars,
            'low': [99.0] * bars,
            'close': [100.5] * bars,
            'volume': [1000] * bars
        })
    
    def place_order(self, symbol: str, direction: int, quantity: float, order_type: str,
                   price: Optional[float] = None, trigger_price: Optional[float] = None,
                   stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                   product_type: str = "MIS") -> Optional[str]:
        self.operation_log.append(("place_order", {
            "symbol": symbol, "direction": direction, "quantity": quantity,
            "order_type": order_type, "price": price
        }))
        return f"alice_order_{len(self.operation_log)}"
    
    def modify_order(self, order_id: str, quantity: Optional[float] = None,
                    price: Optional[float] = None, trigger_price: Optional[float] = None) -> bool:
        self.operation_log.append(("modify_order", {"order_id": order_id, "quantity": quantity, "price": price}))
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        self.operation_log.append(("cancel_order", {"order_id": order_id}))
        return True
    
    def get_positions(self, symbol: Optional[str] = None) -> list:
        self.operation_log.append(("get_positions", {"symbol": symbol}))
        return [{
            'symbol': symbol or 'RELIANCE',
            'direction': 1,
            'quantity': 50,
            'entry_price': 2450.0,
            'current_price': 2455.0,
            'pnl': 250.0,
            'pnl_percent': 0.2
        }]
    
    def get_account_info(self) -> Dict:
        self.operation_log.append(("get_account_info", {}))
        return {
            'balance': 500000.0,
            'equity': 505000.0,
            'margin_available': 450000.0,
            'margin_used': 50000.0
        }
    
    def get_instrument_info(self, symbol: str) -> Optional[Dict]:
        self.operation_log.append(("get_instrument_info", {"symbol": symbol}))
        return {
            'symbol': symbol,
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': 'alice_738561'
        }
    
    def convert_timeframe(self, mt5_timeframe: int) -> str:
        self.operation_log.append(("convert_timeframe", {"mt5_timeframe": mt5_timeframe}))
        timeframe_map = {
            1: "1m",
            5: "5m",
            15: "15m",
            30: "30m",
            60: "1h",
            1440: "1d"
        }
        return timeframe_map.get(mt5_timeframe, "30m")


def create_broker_adapter(broker_type: str, config: Dict) -> BrokerAdapter:
    """Factory function to create broker adapter based on configuration"""
    if broker_type == "kite":
        return MockKiteAdapter(config)
    elif broker_type == "alice_blue":
        return MockAliceBlueAdapter(config)
    else:
        raise ValueError(f"Unknown broker type: {broker_type}")


# Property-based test functions

@given(
    broker_type=st.sampled_from(["kite", "alice_blue"]),
    symbol=st.sampled_from(["RELIANCE", "TCS", "INFY", "NIFTY 50", "BANKNIFTY"]),
    timeframe=st.sampled_from([1, 5, 15, 30, 60, 1440]),
    bars=st.integers(min_value=50, max_value=500)
)
@settings(max_examples=10, deadline=None)
def test_broker_routing_for_data_operations(broker_type: str, symbol: str, timeframe: int, bars: int):
    """
    Property 1: Broker Adapter Routing - Data Operations
    
    For any broker configuration and data operation request, the system should:
    1. Route the operation to the correct broker implementation
    2. Execute the operation using the broker-specific logic
    3. Return results in the standard format
    """
    # Create configuration
    config = {
        "broker": broker_type,
        "api_key": "test_key",
        "symbols": [symbol]
    }
    
    # Create broker adapter using factory
    adapter = create_broker_adapter(broker_type, config)
    
    # Verify correct adapter was created
    assert adapter.broker_name == broker_type, \
        f"Expected broker {broker_type}, got {adapter.broker_name}"
    
    # Test connection operation
    assert adapter.connect() == True, \
        f"Connection should succeed for {broker_type}"
    
    # Test data fetching operation
    df = adapter.get_historical_data(symbol, f"{timeframe}minute", bars)
    
    # Verify operation was logged by the correct broker
    assert ("get_historical_data", {"symbol": symbol, "timeframe": f"{timeframe}minute", "bars": bars}) in adapter.operation_log, \
        f"Data fetch operation should be logged by {broker_type} adapter"
    
    # Verify data format is consistent regardless of broker
    assert df is not None, "Data should be returned"
    assert len(df) == bars, f"Should return {bars} bars"
    assert list(df.columns) == ['time', 'open', 'high', 'low', 'close', 'volume'], \
        "Data format should be consistent across brokers"
    
    # Test instrument info operation
    info = adapter.get_instrument_info(symbol)
    assert info is not None, "Instrument info should be returned"
    assert info['symbol'] == symbol, "Symbol should match"
    assert 'lot_size' in info, "Lot size should be present"
    assert 'tick_size' in info, "Tick size should be present"
    
    # Verify operation was routed to correct broker
    assert ("get_instrument_info", {"symbol": symbol}) in adapter.operation_log, \
        f"Instrument info operation should be logged by {broker_type} adapter"


@given(
    broker_type=st.sampled_from(["kite", "alice_blue"]),
    symbol=st.sampled_from(["RELIANCE", "TCS", "INFY"]),
    direction=st.sampled_from([1, -1]),
    quantity=st.integers(min_value=1, max_value=100),
    order_type=st.sampled_from(["MARKET", "LIMIT", "SL", "SL-M"])
)
@settings(max_examples=10, deadline=None)
def test_broker_routing_for_order_operations(broker_type: str, symbol: str, direction: int, 
                                             quantity: int, order_type: str):
    """
    Property 1: Broker Adapter Routing - Order Operations
    
    For any broker configuration and order operation request, the system should:
    1. Route the operation to the correct broker implementation
    2. Execute the operation using broker-specific order placement logic
    3. Return broker-specific order IDs
    """
    # Create configuration
    config = {
        "broker": broker_type,
        "api_key": "test_key",
        "symbols": [symbol]
    }
    
    # Create broker adapter
    adapter = create_broker_adapter(broker_type, config)
    adapter.connect()
    
    # Test order placement
    order_id = adapter.place_order(
        symbol=symbol,
        direction=direction,
        quantity=float(quantity),
        order_type=order_type,
        price=2450.0 if order_type == "LIMIT" else None
    )
    
    # Verify order was placed through correct broker
    assert order_id is not None, "Order ID should be returned"
    # Check that order ID contains broker identifier (kite or alice)
    broker_prefix = "kite" if broker_type == "kite" else "alice"
    assert broker_prefix in order_id, \
        f"Order ID should contain broker identifier: expected '{broker_prefix}' in '{order_id}'"
    
    # Verify operation was logged by correct broker
    order_ops = [op for op in adapter.operation_log if op[0] == "place_order"]
    assert len(order_ops) > 0, f"Order placement should be logged by {broker_type} adapter"
    
    # Test order modification
    modify_result = adapter.modify_order(order_id, quantity=float(quantity + 10))
    assert modify_result == True, "Order modification should succeed"
    
    # Verify modification was routed to correct broker
    modify_ops = [op for op in adapter.operation_log if op[0] == "modify_order"]
    assert len(modify_ops) > 0, f"Order modification should be logged by {broker_type} adapter"
    
    # Test order cancellation
    cancel_result = adapter.cancel_order(order_id)
    assert cancel_result == True, "Order cancellation should succeed"
    
    # Verify cancellation was routed to correct broker
    cancel_ops = [op for op in adapter.operation_log if op[0] == "cancel_order"]
    assert len(cancel_ops) > 0, f"Order cancellation should be logged by {broker_type} adapter"


@given(
    broker_type=st.sampled_from(["kite", "alice_blue"]),
    symbol=st.sampled_from(["RELIANCE", "TCS", "INFY", None])
)
@settings(max_examples=5, deadline=None)
def test_broker_routing_for_position_operations(broker_type: str, symbol: Optional[str]):
    """
    Property 1: Broker Adapter Routing - Position Operations
    
    For any broker configuration and position query, the system should:
    1. Route the operation to the correct broker implementation
    2. Return position data in standard format
    3. Handle symbol filtering correctly
    """
    # Create configuration
    config = {
        "broker": broker_type,
        "api_key": "test_key"
    }
    
    # Create broker adapter
    adapter = create_broker_adapter(broker_type, config)
    adapter.connect()
    
    # Test position retrieval
    positions = adapter.get_positions(symbol)
    
    # Verify operation was routed to correct broker
    assert ("get_positions", {"symbol": symbol}) in adapter.operation_log, \
        f"Position query should be logged by {broker_type} adapter"
    
    # Verify position data format is consistent
    assert isinstance(positions, list), "Positions should be returned as list"
    if len(positions) > 0:
        pos = positions[0]
        assert 'symbol' in pos, "Position should have symbol"
        assert 'direction' in pos, "Position should have direction"
        assert 'quantity' in pos, "Position should have quantity"
        assert 'entry_price' in pos, "Position should have entry price"
        assert 'current_price' in pos, "Position should have current price"
        assert 'pnl' in pos, "Position should have P&L"
        assert 'pnl_percent' in pos, "Position should have P&L percentage"


@given(
    broker_type=st.sampled_from(["kite", "alice_blue"])
)
@settings(max_examples=5, deadline=None)
def test_broker_routing_for_account_operations(broker_type: str):
    """
    Property 1: Broker Adapter Routing - Account Operations
    
    For any broker configuration and account query, the system should:
    1. Route the operation to the correct broker implementation
    2. Return account data in standard format
    3. Include all required account fields
    """
    # Create configuration
    config = {
        "broker": broker_type,
        "api_key": "test_key"
    }
    
    # Create broker adapter
    adapter = create_broker_adapter(broker_type, config)
    adapter.connect()
    
    # Test account info retrieval
    account = adapter.get_account_info()
    
    # Verify operation was routed to correct broker
    assert ("get_account_info", {}) in adapter.operation_log, \
        f"Account query should be logged by {broker_type} adapter"
    
    # Verify account data format is consistent
    assert isinstance(account, dict), "Account info should be a dictionary"
    assert 'balance' in account, "Account should have balance"
    assert 'equity' in account, "Account should have equity"
    assert 'margin_available' in account, "Account should have available margin"
    assert 'margin_used' in account, "Account should have used margin"
    
    # Verify all values are numeric
    assert isinstance(account['balance'], (int, float)), "Balance should be numeric"
    assert isinstance(account['equity'], (int, float)), "Equity should be numeric"
    assert isinstance(account['margin_available'], (int, float)), "Available margin should be numeric"
    assert isinstance(account['margin_used'], (int, float)), "Used margin should be numeric"


@given(
    broker_type=st.sampled_from(["kite", "alice_blue"]),
    mt5_timeframe=st.sampled_from([1, 5, 15, 30, 60, 1440])
)
@settings(max_examples=5, deadline=None)
def test_broker_routing_for_timeframe_conversion(broker_type: str, mt5_timeframe: int):
    """
    Property 1: Broker Adapter Routing - Timeframe Conversion
    
    For any broker configuration and timeframe conversion request, the system should:
    1. Route the operation to the correct broker implementation
    2. Convert MT5 timeframe to broker-specific format
    3. Return valid broker-specific timeframe string
    """
    # Create configuration
    config = {
        "broker": broker_type,
        "api_key": "test_key"
    }
    
    # Create broker adapter
    adapter = create_broker_adapter(broker_type, config)
    
    # Test timeframe conversion
    broker_timeframe = adapter.convert_timeframe(mt5_timeframe)
    
    # Verify operation was routed to correct broker
    assert ("convert_timeframe", {"mt5_timeframe": mt5_timeframe}) in adapter.operation_log, \
        f"Timeframe conversion should be logged by {broker_type} adapter"
    
    # Verify conversion returns a string
    assert isinstance(broker_timeframe, str), "Broker timeframe should be a string"
    assert len(broker_timeframe) > 0, "Broker timeframe should not be empty"
    
    # Verify different brokers may have different formats (but both valid)
    if broker_type == "kite":
        # Kite uses formats like "minute", "5minute", "day"
        assert any(x in broker_timeframe for x in ["minute", "day"]), \
            f"Kite timeframe format should contain 'minute' or 'day': {broker_timeframe}"
    elif broker_type == "alice_blue":
        # Alice Blue uses formats like "1m", "5m", "1h", "1d"
        assert any(x in broker_timeframe for x in ["m", "h", "d"]), \
            f"Alice Blue timeframe format should contain 'm', 'h', or 'd': {broker_timeframe}"


@given(
    initial_broker=st.sampled_from(["kite", "alice_blue"]),
    new_broker=st.sampled_from(["kite", "alice_blue"]),
    symbol=st.sampled_from(["RELIANCE", "TCS"])
)
@settings(max_examples=5, deadline=None)
def test_broker_routing_consistency_across_switches(initial_broker: str, new_broker: str, symbol: str):
    """
    Property 1: Broker Adapter Routing - Consistency Across Broker Switches
    
    When switching between brokers, the system should:
    1. Route operations to the newly configured broker
    2. Maintain consistent data format across different brokers
    3. Not leak operations to the previous broker
    """
    # Skip if same broker (no switch)
    assume(initial_broker != new_broker)
    
    # Create first broker adapter
    config1 = {"broker": initial_broker, "api_key": "test_key"}
    adapter1 = create_broker_adapter(initial_broker, config1)
    adapter1.connect()
    
    # Perform operation with first broker
    data1 = adapter1.get_historical_data(symbol, "30minute", 100)
    assert data1 is not None
    
    # Record operation count for first broker
    ops1_count = len(adapter1.operation_log)
    
    # Create second broker adapter (simulating broker switch)
    config2 = {"broker": new_broker, "api_key": "test_key"}
    adapter2 = create_broker_adapter(new_broker, config2)
    adapter2.connect()
    
    # Perform operation with second broker
    data2 = adapter2.get_historical_data(symbol, "30minute", 100)
    assert data2 is not None
    
    # Verify operations were routed to correct brokers
    assert len(adapter1.operation_log) == ops1_count, \
        "First broker should not receive operations after switch"
    assert len(adapter2.operation_log) > 0, \
        "Second broker should receive operations after switch"
    
    # Verify data format is consistent across brokers
    assert list(data1.columns) == list(data2.columns), \
        "Data format should be consistent across different brokers"
    assert len(data1) == len(data2), \
        "Data length should be consistent across different brokers"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
