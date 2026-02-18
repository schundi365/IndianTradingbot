"""
Unit tests for data fetching functionality in IndianTradingBot

Tests verify that the bot correctly fetches historical data using the broker adapter,
converts timeframes appropriately, and validates data format.
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.indian_trading_bot import IndianTradingBot
from src.broker_adapter import BrokerAdapter


class TestDataFetching:
    """Test suite for data fetching using broker adapter"""
    
    @pytest.fixture
    def mock_broker(self):
        """Create a mock broker adapter"""
        broker = Mock(spec=BrokerAdapter)
        return broker
    
    @pytest.fixture
    def bot_config(self):
        """Create a basic bot configuration"""
        return {
            'symbols': ['RELIANCE', 'TCS'],
            'timeframe': 30,  # 30 minutes
            'magic_number': 12345,
            'risk_percent': 1.0,
            'reward_ratio': 2.0,
            'fast_ma_period': 10,
            'slow_ma_period': 21,
            'atr_period': 14,
            'trading_hours': {
                'start': '09:15',
                'end': '15:30'
            }
        }
    
    @pytest.fixture
    def sample_data(self):
        """Create sample historical data"""
        data = {
            'time': pd.date_range(start='2024-01-01', periods=200, freq='30min'),
            'open': [100.0 + i * 0.1 for i in range(200)],
            'high': [101.0 + i * 0.1 for i in range(200)],
            'low': [99.0 + i * 0.1 for i in range(200)],
            'close': [100.5 + i * 0.1 for i in range(200)],
            'volume': [1000 + i * 10 for i in range(200)]
        }
        return pd.DataFrame(data)
    
    def test_get_historical_data_success(self, mock_broker, bot_config, sample_data):
        """Test successful historical data fetching"""
        # Setup mock broker
        mock_broker.convert_timeframe.return_value = "30minute"
        mock_broker.get_historical_data.return_value = sample_data
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        # Fetch data
        result = bot.get_historical_data('RELIANCE', 30, 200)
        
        # Verify broker methods were called correctly
        mock_broker.convert_timeframe.assert_called_once_with(30)
        mock_broker.get_historical_data.assert_called_once_with('RELIANCE', '30minute', 200)
        
        # Verify result
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 200
        assert all(col in result.columns for col in ['time', 'open', 'high', 'low', 'close', 'volume'])
    
    def test_get_historical_data_broker_failure(self, mock_broker, bot_config):
        """Test handling of broker data fetch failure"""
        # Setup mock broker to return None (failure)
        mock_broker.convert_timeframe.return_value = "30minute"
        mock_broker.get_historical_data.return_value = None
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        # Fetch data
        result = bot.get_historical_data('INVALID_SYMBOL', 30, 200)
        
        # Verify result is None
        assert result is None
    
    def test_get_historical_data_invalid_format(self, mock_broker, bot_config):
        """Test handling of invalid data format from broker"""
        # Setup mock broker to return data with missing columns
        invalid_data = pd.DataFrame({
            'time': pd.date_range(start='2024-01-01', periods=10, freq='30min'),
            'close': [100.0] * 10
            # Missing: open, high, low, volume
        })
        mock_broker.convert_timeframe.return_value = "30minute"
        mock_broker.get_historical_data.return_value = invalid_data
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        # Fetch data
        result = bot.get_historical_data('RELIANCE', 30, 200)
        
        # Verify result is None due to invalid format
        assert result is None
    
    def test_timeframe_conversion(self, mock_broker, bot_config, sample_data):
        """Test that timeframe is correctly converted to broker format"""
        # Setup mock broker
        mock_broker.convert_timeframe.return_value = "5minute"
        mock_broker.get_historical_data.return_value = sample_data
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        # Fetch data with 5-minute timeframe
        bot.get_historical_data('TCS', 5, 200)
        
        # Verify timeframe conversion was called with correct parameter
        mock_broker.convert_timeframe.assert_called_once_with(5)
        mock_broker.get_historical_data.assert_called_once_with('TCS', '5minute', 200)
    
    def test_data_format_validation(self, mock_broker, bot_config, sample_data):
        """Test that returned data has correct format and types"""
        # Setup mock broker
        mock_broker.convert_timeframe.return_value = "30minute"
        mock_broker.get_historical_data.return_value = sample_data
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        # Fetch data
        result = bot.get_historical_data('RELIANCE', 30, 200)
        
        # Verify data format
        assert result is not None
        assert 'time' in result.columns
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
        
        # Verify data types (broker adapter should ensure correct types)
        assert pd.api.types.is_datetime64_any_dtype(result['time'])
        assert pd.api.types.is_numeric_dtype(result['open'])
        assert pd.api.types.is_numeric_dtype(result['high'])
        assert pd.api.types.is_numeric_dtype(result['low'])
        assert pd.api.types.is_numeric_dtype(result['close'])
        assert pd.api.types.is_numeric_dtype(result['volume'])
    
    def test_multiple_timeframes(self, mock_broker, bot_config, sample_data):
        """Test data fetching with different timeframes"""
        timeframes = [1, 5, 15, 30, 60]
        expected_formats = ["minute", "5minute", "15minute", "30minute", "60minute"]
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        for tf, expected_format in zip(timeframes, expected_formats):
            # Reset mock
            mock_broker.reset_mock()
            mock_broker.convert_timeframe.return_value = expected_format
            mock_broker.get_historical_data.return_value = sample_data
            
            # Fetch data
            bot.get_historical_data('RELIANCE', tf, 200)
            
            # Verify correct timeframe conversion
            mock_broker.convert_timeframe.assert_called_once_with(tf)
            mock_broker.get_historical_data.assert_called_once_with('RELIANCE', expected_format, 200)
    
    def test_default_bars_parameter(self, mock_broker, bot_config, sample_data):
        """Test that default bars parameter is used when not specified"""
        # Setup mock broker
        mock_broker.convert_timeframe.return_value = "30minute"
        mock_broker.get_historical_data.return_value = sample_data
        
        # Create bot
        bot = IndianTradingBot(bot_config, mock_broker)
        
        # Fetch data without specifying bars (should default to 200)
        bot.get_historical_data('RELIANCE', 30)
        
        # Verify default bars value was used
        mock_broker.get_historical_data.assert_called_once_with('RELIANCE', '30minute', 200)
