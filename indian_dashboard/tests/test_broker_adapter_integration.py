"""
Integration tests for broker adapters with the dashboard

Tests the integration of KiteAdapter and PaperTradingAdapter with the
dashboard's BrokerManager service.

Requirements: 4.2
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.broker_adapter import BrokerAdapter
from src.adapters.kite_adapter import KiteAdapter
from src.adapters.paper_trading_adapter import PaperTradingAdapter
from services.broker_manager import BrokerManager


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def broker_manager():
    """Create a BrokerManager instance for testing"""
    return BrokerManager()


@pytest.fixture
def paper_trading_config():
    """Configuration for paper trading adapter"""
    return {
        'initial_balance': 100000.0,
        'default_exchange': 'NSE'
    }


@pytest.fixture
def kite_config():
    """Mock configuration for Kite adapter"""
    return {
        'kite_api_key': 'test_api_key',
        'kite_token_file': 'test_kite_token.json',
        'default_exchange': 'NSE'
    }


@pytest.fixture
def mock_kite_token_file(tmp_path):
    """Create a mock Kite token file"""
    token_file = tmp_path / "test_kite_token.json"
    token_data = {
        'access_token': 'test_access_token',
        'date': datetime.now().strftime("%Y-%m-%d")
    }
    import json
    with open(token_file, 'w') as f:
        json.dump(token_data, f)
    return str(token_file)


# ============================================================================
# PaperTradingAdapter Integration Tests
# ============================================================================

class TestPaperTradingAdapterIntegration:
    """Test PaperTradingAdapter integration with dashboard"""
    
    def test_paper_trading_connect(self, paper_trading_config):
        """Test connecting to paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        
        # Connect should succeed
        assert adapter.connect() is True
        assert adapter.is_connected() is True
        
        # Disconnect
        adapter.disconnect()
        assert adapter.is_connected() is False

    
    def test_paper_trading_get_instruments(self, paper_trading_config):
        """Test getting instruments from paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        instruments = adapter.get_instruments()
        
        # Should have mock instruments
        assert len(instruments) > 0
        assert any(inst['symbol'] == 'RELIANCE' for inst in instruments)
        assert any(inst['symbol'] == 'NIFTY 50' for inst in instruments)
        
        adapter.disconnect()
    
    def test_paper_trading_get_historical_data(self, paper_trading_config):
        """Test fetching historical data from paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        # Fetch data
        df = adapter.get_historical_data('RELIANCE', '30minute', 100)
        
        # Verify data structure
        assert df is not None
        assert len(df) == 100
        assert all(col in df.columns for col in ['time', 'open', 'high', 'low', 'close', 'volume'])
        
        # Verify OHLC relationships
        assert all(df['high'] >= df['low'])
        assert all(df['high'] >= df['open'])
        assert all(df['high'] >= df['close'])
        assert all(df['low'] <= df['open'])
        assert all(df['low'] <= df['close'])
        
        adapter.disconnect()
    
    def test_paper_trading_place_order(self, paper_trading_config):
        """Test placing orders with paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        # Place a market buy order
        order_id = adapter.place_order(
            symbol='RELIANCE',
            direction=1,
            quantity=10,
            order_type='MARKET',
            product_type='MIS'
        )
        
        assert order_id is not None
        
        # Verify position was created
        positions = adapter.get_positions('RELIANCE')
        assert len(positions) == 1
        assert positions[0]['symbol'] == 'RELIANCE'
        assert positions[0]['quantity'] == 10
        assert positions[0]['direction'] == 1
        
        adapter.disconnect()
    
    def test_paper_trading_get_account_info(self, paper_trading_config):
        """Test getting account info from paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        account_info = adapter.get_account_info()
        
        # Verify account info structure
        assert 'balance' in account_info
        assert 'equity' in account_info
        assert 'margin_available' in account_info
        assert 'margin_used' in account_info
        
        # Initial balance should match config
        assert account_info['balance'] == paper_trading_config['initial_balance']
        
        adapter.disconnect()
    
    def test_paper_trading_get_instrument_info(self, paper_trading_config):
        """Test getting instrument info from paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        info = adapter.get_instrument_info('RELIANCE')
        
        assert info is not None
        assert info['symbol'] == 'RELIANCE'
        assert 'lot_size' in info
        assert 'tick_size' in info
        assert 'instrument_token' in info
        
        adapter.disconnect()
    
    def test_paper_trading_full_trade_cycle(self, paper_trading_config):
        """Test complete trade cycle with paper trading adapter"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        initial_balance = adapter.get_account_info()['balance']
        
        # Place buy order
        buy_order_id = adapter.place_order(
            symbol='RELIANCE',
            direction=1,
            quantity=10,
            order_type='MARKET'
        )
        assert buy_order_id is not None
        
        # Verify position
        positions = adapter.get_positions('RELIANCE')
        assert len(positions) == 1
        
        # Close position (sell)
        sell_order_id = adapter.place_order(
            symbol='RELIANCE',
            direction=-1,
            quantity=10,
            order_type='MARKET'
        )
        assert sell_order_id is not None
        
        # Position should be closed
        positions = adapter.get_positions('RELIANCE')
        assert len(positions) == 0
        
        adapter.disconnect()



# ============================================================================
# KiteAdapter Integration Tests (with mocking)
# ============================================================================

class TestKiteAdapterIntegration:
    """Test KiteAdapter integration with dashboard (mocked)"""
    
    @patch('src.kite_adapter.KiteConnect')
    def test_kite_connect_with_valid_token(self, mock_kite_connect, kite_config, mock_kite_token_file):
        """Test connecting to Kite with valid token"""
        # Setup mock
        mock_kite = Mock()
        mock_kite.profile.return_value = {
            'user_id': 'TEST123',
            'user_name': 'Test User',
            'broker': 'ZERODHA'
        }
        mock_kite_connect.return_value = mock_kite
        
        # Update config with mock token file
        kite_config['kite_token_file'] = mock_kite_token_file
        
        adapter = KiteAdapter(kite_config)
        
        # Connect should succeed
        assert adapter.connect() is True
        assert adapter.is_connected() is True
    
    @patch('src.kite_adapter.KiteConnect')
    def test_kite_get_historical_data(self, mock_kite_connect, kite_config, mock_kite_token_file):
        """Test fetching historical data from Kite"""
        # Setup mock
        mock_kite = Mock()
        mock_kite.profile.return_value = {'user_name': 'Test User'}
        
        # Mock historical data
        mock_data = [
            {
                'date': datetime.now(),
                'open': 2450.0,
                'high': 2460.0,
                'low': 2440.0,
                'close': 2455.0,
                'volume': 100000
            }
            for _ in range(100)
        ]
        mock_kite.historical_data.return_value = mock_data
        mock_kite_connect.return_value = mock_kite
        
        kite_config['kite_token_file'] = mock_kite_token_file
        adapter = KiteAdapter(kite_config)
        adapter.connect()
        
        # Mock instrument cache
        adapter.instrument_cache = {
            'NSE:RELIANCE': {
                'instrument_token': 738561,
                'lot_size': 1,
                'tick_size': 0.05
            }
        }
        
        # Fetch data
        df = adapter.get_historical_data('RELIANCE', '30minute', 100)
        
        assert df is not None
        assert len(df) == 100
        assert all(col in df.columns for col in ['time', 'open', 'high', 'low', 'close', 'volume'])
    
    @patch('src.kite_adapter.KiteConnect')
    def test_kite_place_order(self, mock_kite_connect, kite_config, mock_kite_token_file):
        """Test placing order with Kite"""
        # Setup mock
        mock_kite = Mock()
        mock_kite.profile.return_value = {'user_name': 'Test User'}
        mock_kite.place_order.return_value = '240115000123456'
        mock_kite_connect.return_value = mock_kite
        
        kite_config['kite_token_file'] = mock_kite_token_file
        adapter = KiteAdapter(kite_config)
        adapter.connect()
        
        # Mock instrument info
        adapter.instrument_cache = {
            'NSE:RELIANCE': {
                'instrument_token': 738561,
                'lot_size': 1,
                'tick_size': 0.05
            }
        }
        
        # Place order
        order_id = adapter.place_order(
            symbol='RELIANCE',
            direction=1,
            quantity=10,
            order_type='MARKET'
        )
        
        assert order_id == '240115000123456'
        mock_kite.place_order.assert_called_once()
    
    @patch('src.kite_adapter.KiteConnect')
    def test_kite_get_positions(self, mock_kite_connect, kite_config, mock_kite_token_file):
        """Test getting positions from Kite"""
        # Setup mock
        mock_kite = Mock()
        mock_kite.profile.return_value = {'user_name': 'Test User'}
        mock_kite.positions.return_value = {
            'net': [
                {
                    'tradingsymbol': 'RELIANCE',
                    'quantity': 10,
                    'average_price': 2450.0,
                    'last_price': 2455.0,
                    'pnl': 50.0
                }
            ]
        }
        mock_kite_connect.return_value = mock_kite
        
        kite_config['kite_token_file'] = mock_kite_token_file
        adapter = KiteAdapter(kite_config)
        adapter.connect()
        
        positions = adapter.get_positions()
        
        assert len(positions) == 1
        assert positions[0]['symbol'] == 'RELIANCE'
        assert positions[0]['quantity'] == 10
        assert positions[0]['pnl'] == 50.0
    
    @patch('src.kite_adapter.KiteConnect')
    def test_kite_get_account_info(self, mock_kite_connect, kite_config, mock_kite_token_file):
        """Test getting account info from Kite"""
        # Setup mock
        mock_kite = Mock()
        mock_kite.profile.return_value = {'user_name': 'Test User'}
        mock_kite.margins.return_value = {
            'equity': {
                'net': 100000.0,
                'available': {
                    'live_balance': 100000.0,
                    'cash': 95000.0
                },
                'utilised': {
                    'debits': 5000.0
                }
            }
        }
        mock_kite_connect.return_value = mock_kite
        
        kite_config['kite_token_file'] = mock_kite_token_file
        adapter = KiteAdapter(kite_config)
        adapter.connect()
        
        account_info = adapter.get_account_info()
        
        assert 'balance' in account_info
        assert 'equity' in account_info
        assert 'margin_available' in account_info
        assert 'margin_used' in account_info



# ============================================================================
# BrokerManager Integration Tests
# ============================================================================

class TestBrokerManagerIntegration:
    """Test BrokerManager integration with adapters"""
    
    def test_broker_manager_get_supported_brokers(self, broker_manager):
        """Test getting list of supported brokers"""
        brokers = broker_manager.get_supported_brokers()
        
        assert len(brokers) > 0
        assert any(b['id'] == 'kite' for b in brokers)
    
    def test_broker_manager_paper_trading_connection(self, broker_manager):
        """Test connecting to paper trading through BrokerManager"""
        # Add paper trading to broker manager
        broker_manager.broker_adapters['paper'] = PaperTradingAdapter
        
        credentials = {
            'initial_balance': 100000.0
        }
        
        success, result = broker_manager.connect('paper', credentials)
        
        assert success is True
        assert 'user_info' in result
        assert broker_manager.is_connected() is True
        
        # Test getting adapter
        adapter = broker_manager.get_adapter()
        assert adapter is not None
        assert isinstance(adapter, PaperTradingAdapter)
        
        # Disconnect
        success, message = broker_manager.disconnect()
        assert success is True
        assert broker_manager.is_connected() is False
    
    def test_broker_manager_status(self, broker_manager):
        """Test getting broker status"""
        # Initially not connected
        status = broker_manager.get_status()
        assert status['connected'] is False
        
        # Connect to paper trading
        broker_manager.broker_adapters['paper'] = PaperTradingAdapter
        broker_manager.connect('paper', {'initial_balance': 100000.0})
        
        # Check status
        status = broker_manager.get_status()
        assert status['connected'] is True
        assert status['broker'] == 'paper'
        assert 'user_info' in status
        
        broker_manager.disconnect()
    
    def test_broker_manager_test_connection(self, broker_manager):
        """Test connection testing"""
        # Not connected
        success, message = broker_manager.test_connection()
        assert success is False
        
        # Connect
        broker_manager.broker_adapters['paper'] = PaperTradingAdapter
        broker_manager.connect('paper', {'initial_balance': 100000.0})
        
        # Test connection
        success, message = broker_manager.test_connection()
        assert success is True
        assert 'Balance' in message or 'OK' in message
        
        broker_manager.disconnect()
    
    @patch('src.kite_adapter.KiteConnect')
    def test_broker_manager_kite_connection(self, mock_kite_connect, broker_manager, mock_kite_token_file):
        """Test connecting to Kite through BrokerManager"""
        # Setup mock
        mock_kite = Mock()
        mock_kite.profile.return_value = {
            'user_id': 'TEST123',
            'user_name': 'Test User',
            'email': 'test@example.com',
            'broker': 'ZERODHA'
        }
        mock_kite.margins.return_value = {'equity': {'net': 100000.0}}
        mock_kite_connect.return_value = mock_kite
        
        credentials = {
            'api_key': 'test_api_key',
            'api_secret': 'test_api_secret'
        }
        
        config = {
            'kite_token_file': mock_kite_token_file
        }
        
        success, result = broker_manager.connect('kite', credentials, config)
        
        assert success is True
        assert 'user_info' in result
        assert result['user_info']['user_id'] == 'TEST123'
        
        broker_manager.disconnect()


# ============================================================================
# Cross-Adapter Compatibility Tests
# ============================================================================

class TestCrossAdapterCompatibility:
    """Test that all adapters implement the same interface correctly"""
    
    def test_adapter_interface_compliance(self):
        """Test that all adapters implement required methods"""
        required_methods = [
            'connect',
            'disconnect',
            'is_connected',
            'get_historical_data',
            'place_order',
            'modify_order',
            'cancel_order',
            'get_positions',
            'get_account_info',
            'get_instrument_info',
            'convert_timeframe'
        ]
        
        # Test PaperTradingAdapter
        paper_adapter = PaperTradingAdapter({'initial_balance': 100000.0})
        for method in required_methods:
            assert hasattr(paper_adapter, method), f"PaperTradingAdapter missing {method}"
        
        # Test KiteAdapter
        kite_adapter = KiteAdapter({'kite_api_key': 'test'})
        for method in required_methods:
            assert hasattr(kite_adapter, method), f"KiteAdapter missing {method}"
    
    def test_historical_data_format_consistency(self, paper_trading_config):
        """Test that historical data format is consistent across adapters"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        df = adapter.get_historical_data('RELIANCE', '30minute', 50)
        
        # Check required columns
        required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        assert all(col in df.columns for col in required_columns)
        
        # Check data types
        assert df['time'].dtype == 'datetime64[ns]'
        assert df['open'].dtype == 'float64'
        assert df['high'].dtype == 'float64'
        assert df['low'].dtype == 'float64'
        assert df['close'].dtype == 'float64'
        assert df['volume'].dtype == 'int64'
        
        adapter.disconnect()
    
    def test_position_format_consistency(self, paper_trading_config):
        """Test that position format is consistent across adapters"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        # Place order to create position
        adapter.place_order('RELIANCE', 1, 10, 'MARKET')
        
        positions = adapter.get_positions()
        
        # Check required fields
        required_fields = ['symbol', 'direction', 'quantity', 'entry_price', 
                          'current_price', 'pnl', 'pnl_percent']
        assert all(field in positions[0] for field in required_fields)
        
        adapter.disconnect()
    
    def test_account_info_format_consistency(self, paper_trading_config):
        """Test that account info format is consistent across adapters"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        account_info = adapter.get_account_info()
        
        # Check required fields
        required_fields = ['balance', 'equity', 'margin_available', 'margin_used']
        assert all(field in account_info for field in required_fields)
        
        # Check data types
        for field in required_fields:
            assert isinstance(account_info[field], (int, float))
        
        adapter.disconnect()


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestAdapterErrorHandling:
    """Test error handling across adapters"""
    
    def test_paper_trading_invalid_symbol(self, paper_trading_config):
        """Test handling of invalid symbol in paper trading"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        # Try to get data for non-existent symbol
        df = adapter.get_historical_data('INVALID_SYMBOL', '30minute', 50)
        
        assert df is None
        
        adapter.disconnect()
    
    def test_paper_trading_invalid_order_quantity(self, paper_trading_config):
        """Test handling of invalid order quantity"""
        adapter = PaperTradingAdapter(paper_trading_config)
        adapter.connect()
        
        # Try to place order with negative quantity
        order_id = adapter.place_order('RELIANCE', 1, -10, 'MARKET')
        
        assert order_id is None
        
        adapter.disconnect()
    
    def test_broker_manager_unsupported_broker(self, broker_manager):
        """Test handling of unsupported broker"""
        success, result = broker_manager.connect('unsupported_broker', {})
        
        assert success is False
        assert 'error' in result
        assert 'Unsupported broker' in result['error']
    
    def test_operations_when_not_connected(self, paper_trading_config):
        """Test that operations fail gracefully when not connected"""
        adapter = PaperTradingAdapter(paper_trading_config)
        
        # Don't connect
        
        # Try operations
        assert adapter.is_connected() is False
        assert adapter.place_order('RELIANCE', 1, 10, 'MARKET') is None
        assert adapter.get_positions() == []
        
        account_info = adapter.get_account_info()
        assert account_info['balance'] == 0.0
