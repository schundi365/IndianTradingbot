"""
Unit tests for order parameter validation in KiteAdapter

Tests that order parameters are properly validated before submission,
including quantity, price, instrument existence, lot size, and tick size compliance.

Validates: Requirements 5.9
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.kite_adapter import KiteAdapter
from src.error_handler import ValidationError


@pytest.fixture
def mock_kite_api():
    """Create a mock Kite Connect API"""
    mock_api = MagicMock()
    mock_api.TRANSACTION_TYPE_BUY = "BUY"
    mock_api.TRANSACTION_TYPE_SELL = "SELL"
    mock_api.ORDER_TYPE_MARKET = "MARKET"
    mock_api.ORDER_TYPE_LIMIT = "LIMIT"
    mock_api.ORDER_TYPE_SL = "SL"
    mock_api.ORDER_TYPE_SLM = "SL-M"
    mock_api.PRODUCT_MIS = "MIS"
    mock_api.PRODUCT_NRML = "NRML"
    mock_api.VARIETY_REGULAR = "regular"
    return mock_api


@pytest.fixture
def kite_adapter(mock_kite_api):
    """Create a KiteAdapter instance with mocked dependencies"""
    config = {
        'kite_api_key': 'test_key',
        'kite_token_file': 'test_token.json',
        'default_exchange': 'NSE'
    }
    
    adapter = KiteAdapter(config)
    adapter.kite = mock_kite_api
    adapter.access_token = 'test_token'
    
    # Mock error handler
    adapter.error_handler = Mock()
    adapter.error_handler.handle_validation_error = Mock(side_effect=ValidationError("Validation failed"))
    
    # Mock logger
    adapter.logger = Mock()
    
    return adapter


class TestQuantityValidation:
    """Test quantity parameter validation"""
    
    def test_negative_quantity_rejected(self, kite_adapter):
        """Test that negative quantity is rejected"""
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=-10,
            order_type="MARKET"
        )
        
        assert result is None
        kite_adapter.error_handler.handle_validation_error.assert_called_once_with(
            "quantity",
            -10,
            "positive number"
        )
    
    def test_zero_quantity_rejected(self, kite_adapter):
        """Test that zero quantity is rejected"""
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=0,
            order_type="MARKET"
        )
        
        assert result is None
        kite_adapter.error_handler.handle_validation_error.assert_called_once_with(
            "quantity",
            0,
            "positive number"
        )
    
    def test_quantity_not_multiple_of_lot_size_rejected(self, kite_adapter):
        """Test that quantity not multiple of lot size is rejected"""
        # Mock get_instrument_info to return lot size of 50
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'NIFTY24JANFUT',
            'lot_size': 50,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="NIFTY24JANFUT",
            direction=1,
            quantity=75,  # Not a multiple of 50
            order_type="MARKET"
        )
        
        assert result is None
        kite_adapter.error_handler.handle_validation_error.assert_called_once_with(
            "quantity",
            75,
            "multiple of lot size (50)"
        )
    
    def test_valid_quantity_multiple_of_lot_size_accepted(self, kite_adapter, mock_kite_api):
        """Test that valid quantity multiple of lot size is accepted"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'NIFTY24JANFUT',
            'lot_size': 50,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Mock successful order placement
        mock_kite_api.place_order = Mock(return_value='ORDER123')
        
        result = kite_adapter.place_order(
            symbol="NIFTY24JANFUT",
            direction=1,
            quantity=100,  # Valid: 2 * 50
            order_type="MARKET"
        )
        
        assert result == 'ORDER123'
        mock_kite_api.place_order.assert_called_once()


class TestPriceValidation:
    """Test price parameter validation"""
    
    def test_negative_price_rejected(self, kite_adapter):
        """Test that negative price is rejected"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="LIMIT",
            price=-2500.00
        )
        
        assert result is None
        # Should be called twice: once for quantity validation passing, once for price
        assert kite_adapter.error_handler.handle_validation_error.call_count >= 1
        # Check that price validation was called
        calls = kite_adapter.error_handler.handle_validation_error.call_args_list
        price_call = [c for c in calls if c[0][0] == "price" and c[0][1] == -2500.00]
        assert len(price_call) > 0
    
    def test_zero_price_rejected(self, kite_adapter):
        """Test that zero price is rejected"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="LIMIT",
            price=0
        )
        
        assert result is None
    
    def test_price_not_multiple_of_tick_size_rejected(self, kite_adapter):
        """Test that price not multiple of tick size is rejected"""
        # Mock get_instrument_info with tick size of 0.05
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="LIMIT",
            price=2500.03  # Not a multiple of 0.05
        )
        
        assert result is None
    
    def test_valid_price_multiple_of_tick_size_accepted(self, kite_adapter, mock_kite_api):
        """Test that valid price multiple of tick size is accepted"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Mock successful order placement
        mock_kite_api.place_order = Mock(return_value='ORDER123')
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="LIMIT",
            price=2500.05  # Valid: multiple of 0.05
        )
        
        assert result == 'ORDER123'
        mock_kite_api.place_order.assert_called_once()


class TestInstrumentValidation:
    """Test instrument existence validation"""
    
    def test_invalid_instrument_rejected(self, kite_adapter):
        """Test that invalid/non-existent instrument is rejected"""
        # Mock get_instrument_info to return None (instrument not found)
        kite_adapter.get_instrument_info = Mock(return_value=None)
        
        result = kite_adapter.place_order(
            symbol="INVALID_SYMBOL",
            direction=1,
            quantity=1,
            order_type="MARKET"
        )
        
        assert result is None
        kite_adapter.error_handler.handle_validation_error.assert_called_once_with(
            "symbol",
            "INVALID_SYMBOL",
            "valid tradable instrument"
        )
    
    def test_valid_instrument_accepted(self, kite_adapter, mock_kite_api):
        """Test that valid instrument is accepted"""
        # Mock get_instrument_info to return valid instrument
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Mock successful order placement
        mock_kite_api.place_order = Mock(return_value='ORDER123')
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="MARKET"
        )
        
        assert result == 'ORDER123'
        kite_adapter.get_instrument_info.assert_called_once_with("RELIANCE")


class TestOrderTypeValidation:
    """Test order type validation"""
    
    def test_invalid_order_type_rejected(self, kite_adapter):
        """Test that invalid order type is rejected"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="INVALID_TYPE"
        )
        
        assert result is None
    
    def test_limit_order_without_price_rejected(self, kite_adapter):
        """Test that LIMIT order without price is rejected"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="LIMIT",
            price=None  # Missing required price
        )
        
        assert result is None
    
    def test_sl_order_without_trigger_price_rejected(self, kite_adapter):
        """Test that SL order without trigger price is rejected"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="SL",
            trigger_price=None  # Missing required trigger price
        )
        
        assert result is None
    
    def test_slm_order_without_trigger_price_rejected(self, kite_adapter):
        """Test that SL-M order without trigger price is rejected"""
        # Mock get_instrument_info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=1,
            order_type="SL-M",
            trigger_price=None  # Missing required trigger price
        )
        
        assert result is None


class TestDescriptiveErrors:
    """Test that descriptive error messages are returned"""
    
    def test_error_message_includes_parameter_name(self, kite_adapter):
        """Test that error message includes the parameter name"""
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=-10,
            order_type="MARKET"
        )
        
        assert result is None
        # Verify error handler was called with parameter name
        call_args = kite_adapter.error_handler.handle_validation_error.call_args
        assert call_args[0][0] == "quantity"
    
    def test_error_message_includes_invalid_value(self, kite_adapter):
        """Test that error message includes the invalid value"""
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=-10,
            order_type="MARKET"
        )
        
        assert result is None
        # Verify error handler was called with invalid value
        call_args = kite_adapter.error_handler.handle_validation_error.call_args
        assert call_args[0][1] == -10
    
    def test_error_message_includes_expected_format(self, kite_adapter):
        """Test that error message includes expected format"""
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=-10,
            order_type="MARKET"
        )
        
        assert result is None
        # Verify error handler was called with expected format
        call_args = kite_adapter.error_handler.handle_validation_error.call_args
        assert call_args[0][2] == "positive number"


class TestComplexValidationScenarios:
    """Test complex validation scenarios with multiple parameters"""
    
    def test_futures_order_with_lot_size_and_tick_size(self, kite_adapter, mock_kite_api):
        """Test futures order with proper lot size and tick size validation"""
        # Mock NIFTY futures with lot size 50 and tick size 0.05
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'NIFTY24JANFUT',
            'lot_size': 50,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Mock successful order placement
        mock_kite_api.place_order = Mock(return_value='ORDER123')
        
        result = kite_adapter.place_order(
            symbol="NIFTY24JANFUT",
            direction=1,
            quantity=150,  # 3 lots
            order_type="LIMIT",
            price=21500.05  # Multiple of 0.05
        )
        
        assert result == 'ORDER123'
        mock_kite_api.place_order.assert_called_once()
    
    def test_equity_order_with_single_lot_size(self, kite_adapter, mock_kite_api):
        """Test equity order with lot size 1"""
        # Mock equity with lot size 1 and tick size 0.05
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Mock successful order placement
        mock_kite_api.place_order = Mock(return_value='ORDER123')
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=25,  # Any positive integer works with lot size 1
            order_type="LIMIT",
            price=2500.10
        )
        
        assert result == 'ORDER123'
        mock_kite_api.place_order.assert_called_once()
    
    def test_market_order_without_price_validation(self, kite_adapter, mock_kite_api):
        """Test that market orders don't require price validation"""
        # Mock instrument info
        kite_adapter.get_instrument_info = Mock(return_value={
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Mock successful order placement
        mock_kite_api.place_order = Mock(return_value='ORDER123')
        
        result = kite_adapter.place_order(
            symbol="RELIANCE",
            direction=1,
            quantity=10,
            order_type="MARKET"
            # No price parameter for market order
        )
        
        assert result == 'ORDER123'
        mock_kite_api.place_order.assert_called_once()
