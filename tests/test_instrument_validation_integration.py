"""
Integration tests for instrument validation in IndianTradingBot

Validates: Requirement 8.3
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.indian_trading_bot import IndianTradingBot
from src.broker_adapter import BrokerAdapter


class TestInstrumentValidationIntegration:
    """Test instrument validation integration with IndianTradingBot"""
    
    @pytest.fixture
    def mock_broker(self):
        """Create a mock broker adapter"""
        broker = Mock(spec=BrokerAdapter)
        broker.is_connected.return_value = True
        return broker
    
    @pytest.fixture
    def config(self):
        """Create a test configuration"""
        return {
            'symbols': ['RELIANCE', 'TCS', 'INFY'],
            'timeframe': 30,
            'risk_percent': 1.0,
            'reward_ratio': 2.0
        }
    
    @pytest.fixture
    def bot(self, config, mock_broker):
        """Create an IndianTradingBot instance"""
        return IndianTradingBot(config, mock_broker)
    
    def test_validate_instruments_success(self, bot, mock_broker):
        """Test successful validation of all configured instruments"""
        # Arrange
        def get_instrument_info(symbol):
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        result = bot.validate_instruments()
        
        # Assert
        assert result is True
        assert mock_broker.get_instrument_info.call_count == 6  # 3 symbols x 2 calls
    
    def test_validate_instruments_failure(self, bot, mock_broker):
        """Test validation failure when instrument doesn't exist"""
        # Arrange
        def get_instrument_info(symbol):
            if symbol == "TCS":
                return None  # TCS not found
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        result = bot.validate_instruments()
        
        # Assert
        assert result is False
    
    def test_validate_single_instrument_success(self, bot, mock_broker):
        """Test validation of a single instrument"""
        # Arrange
        instrument_info = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        mock_broker.get_instrument_info.return_value = instrument_info
        
        # Act
        result = bot.validate_instrument('RELIANCE')
        
        # Assert
        assert result is True
        mock_broker.get_instrument_info.assert_called_once_with('RELIANCE')
    
    def test_validate_single_instrument_failure(self, bot, mock_broker):
        """Test validation failure for a single instrument"""
        # Arrange
        mock_broker.get_instrument_info.return_value = None
        
        # Act
        result = bot.validate_instrument('INVALID')
        
        # Assert
        assert result is False
    
    def test_validate_instruments_broker_not_connected(self, bot, mock_broker):
        """Test validation when broker is not connected"""
        # Arrange
        mock_broker.is_connected.return_value = False
        
        # Act
        result = bot.validate_instruments()
        
        # Assert
        assert result is False
    
    def test_validate_instruments_with_invalid_parameters(self, bot, mock_broker):
        """Test validation with invalid instrument parameters"""
        # Arrange
        def get_instrument_info(symbol):
            if symbol == "INFY":
                return {
                    'symbol': symbol,
                    'lot_size': 0,  # Invalid lot size
                    'tick_size': 0.05,
                    'instrument_token': f'{hash(symbol)}'
                }
            return {
                'symbol': symbol,
                'lot_size': 1,
                'tick_size': 0.05,
                'instrument_token': f'{hash(symbol)}'
            }
        
        mock_broker.get_instrument_info.side_effect = get_instrument_info
        
        # Act
        result = bot.validate_instruments()
        
        # Assert
        assert result is False
