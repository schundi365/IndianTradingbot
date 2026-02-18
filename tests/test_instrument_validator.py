"""
Tests for Instrument Validator

Validates: Requirement 8.3
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.instrument_validator import InstrumentValidator
from src.broker_adapter import BrokerAdapter


class TestInstrumentValidator:
    """Test suite for InstrumentValidator"""
    
    @pytest.fixture
    def mock_broker(self):
        """Create a mock broker adapter"""
        broker = Mock(spec=BrokerAdapter)
        broker.is_connected.return_value = True
        return broker
    
    @pytest.fixture
    def validator(self, mock_broker):
        """Create an InstrumentValidator instance"""
        return InstrumentValidator(mock_broker)
    
    def test_validate_instrument_success(self, validator, mock_broker):
        """Test successful instrument validation"""
        # Arrange
        symbol = "RELIANCE"
        instrument_info = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        mock_broker.get_instrument_info.return_value = instrument_info
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument(symbol)
        
        # Assert
        assert is_valid is True
        assert error_msg is None
        assert info == instrument_info
        mock_broker.get_instrument_info.assert_called_once_with(symbol)
    
    def test_validate_instrument_not_found(self, validator, mock_broker):
        """Test validation when instrument doesn't exist"""
        # Arrange
        symbol = "INVALID_SYMBOL"
        mock_broker.get_instrument_info.return_value = None
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument(symbol)
        
        # Assert
        assert is_valid is False
        assert "does not exist" in error_msg
        assert info is None
    
    def test_validate_instrument_broker_not_connected(self, validator, mock_broker):
        """Test validation when broker is not connected"""
        # Arrange
        mock_broker.is_connected.return_value = False
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument("RELIANCE")
        
        # Assert
        assert is_valid is False
        assert "not connected" in error_msg
        assert info is None
    
    def test_validate_instrument_invalid_lot_size(self, validator, mock_broker):
        """Test validation with invalid lot size"""
        # Arrange
        instrument_info = {
            'symbol': 'TEST',
            'lot_size': 0,  # Invalid
            'tick_size': 0.05,
            'instrument_token': '123456'
        }
        mock_broker.get_instrument_info.return_value = instrument_info
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument("TEST")
        
        # Assert
        assert is_valid is False
        assert "Invalid lot size" in error_msg
        assert info is None
    
    def test_validate_instrument_invalid_tick_size(self, validator, mock_broker):
        """Test validation with invalid tick size"""
        # Arrange
        instrument_info = {
            'symbol': 'TEST',
            'lot_size': 1,
            'tick_size': 0,  # Invalid
            'instrument_token': '123456'
        }
        mock_broker.get_instrument_info.return_value = instrument_info
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument("TEST")
        
        # Assert
        assert is_valid is False
        assert "Invalid tick size" in error_msg
        assert info is None
    
    def test_validate_instrument_missing_token(self, validator, mock_broker):
        """Test validation with missing instrument token"""
        # Arrange
        instrument_info = {
            'symbol': 'TEST',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': ''  # Missing
        }
        mock_broker.get_instrument_info.return_value = instrument_info
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument("TEST")
        
        # Assert
        assert is_valid is False
        assert "Missing instrument token" in error_msg
        assert info is None
    
    def test_validate_instruments_multiple_success(self, validator, mock_broker):
        """Test validation of multiple valid instruments"""
        # Arrange
        symbols = ["RELIANCE", "TCS", "INFY"]
        
        def get_instrument_info(symbol):
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        results = validator.validate_instruments(symbols)
        
        # Assert
        assert results['summary']['total'] == 3
        assert results['summary']['valid_count'] == 3
        assert results['summary']['invalid_count'] == 0
        assert len(results['valid']) == 3
        assert len(results['invalid']) == 0
        assert all(symbol in results['valid'] for symbol in symbols)
    
    def test_validate_instruments_mixed_results(self, validator, mock_broker):
        """Test validation with mix of valid and invalid instruments"""
        # Arrange
        symbols = ["RELIANCE", "INVALID", "TCS"]
        
        def get_instrument_info(symbol):
            if symbol == "INVALID":
                return None
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        results = validator.validate_instruments(symbols)
        
        # Assert
        assert results['summary']['total'] == 3
        assert results['summary']['valid_count'] == 2
        assert results['summary']['invalid_count'] == 1
        assert "RELIANCE" in results['valid']
        assert "TCS" in results['valid']
        assert "INVALID" in results['invalid']
    
    def test_validate_config_instruments_success(self, validator, mock_broker):
        """Test validation of config with valid instruments"""
        # Arrange
        config = {
            'symbols': ['RELIANCE', 'TCS']
        }
        
        def get_instrument_info(symbol):
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        all_valid, errors = validator.validate_config_instruments(config)
        
        # Assert
        assert all_valid is True
        assert len(errors) == 0
    
    def test_validate_config_instruments_with_invalid(self, validator, mock_broker):
        """Test validation of config with invalid instruments"""
        # Arrange
        config = {
            'symbols': ['RELIANCE', 'INVALID']
        }
        
        def get_instrument_info(symbol):
            if symbol == "INVALID":
                return None
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        all_valid, errors = validator.validate_config_instruments(config)
        
        # Assert
        assert all_valid is False
        assert len(errors) == 1
        assert "INVALID" in errors[0]
    
    def test_validate_config_instruments_no_symbols(self, validator, mock_broker):
        """Test validation of config with no symbols"""
        # Arrange
        config = {}
        
        # Act
        all_valid, errors = validator.validate_config_instruments(config)
        
        # Assert
        assert all_valid is False
        assert len(errors) == 1
        assert "No symbols configured" in errors[0]
    
    def test_is_instrument_tradable_true(self, validator, mock_broker):
        """Test is_instrument_tradable returns True for valid instrument"""
        # Arrange
        instrument_info = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        mock_broker.get_instrument_info.return_value = instrument_info
        
        # Act
        is_tradable = validator.is_instrument_tradable("RELIANCE")
        
        # Assert
        assert is_tradable is True
    
    def test_is_instrument_tradable_false(self, validator, mock_broker):
        """Test is_instrument_tradable returns False for invalid instrument"""
        # Arrange
        mock_broker.get_instrument_info.return_value = None
        
        # Act
        is_tradable = validator.is_instrument_tradable("INVALID")
        
        # Assert
        assert is_tradable is False
    
    def test_validate_instrument_exception_handling(self, validator, mock_broker):
        """Test exception handling during validation"""
        # Arrange
        mock_broker.get_instrument_info.side_effect = Exception("API Error")
        
        # Act
        is_valid, error_msg, info = validator.validate_instrument("RELIANCE")
        
        # Assert
        assert is_valid is False
        assert "Error validating instrument" in error_msg
        assert "API Error" in error_msg
        assert info is None
