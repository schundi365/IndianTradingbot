"""
Tests for main bot loop functionality (Task 3.11)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.indian_trading_bot import IndianTradingBot
import time


class TestMainBotLoop:
    """Test main bot loop implementation"""
    
    def test_run_checks_market_hours_before_cycle(self):
        """Test that run() checks market hours before each cycle"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        
        # Create bot with minimal config
        config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock is_market_open to return False (market closed)
        with patch.object(bot, 'is_market_open', return_value=False):
            with patch('time.sleep') as mock_sleep:
                # Mock run_strategy to track if it's called
                with patch.object(bot, 'run_strategy') as mock_run_strategy:
                    # Run for a short time then interrupt
                    def interrupt_after_sleep(*args):
                        raise KeyboardInterrupt()
                    
                    mock_sleep.side_effect = interrupt_after_sleep
                    
                    # Run the bot
                    bot.run()
                    
                    # Verify run_strategy was NOT called (market closed)
                    assert mock_run_strategy.call_count == 0
                    # Verify sleep was called (waiting for market to open)
                    assert mock_sleep.called
    
    def test_run_iterates_through_configured_symbols(self):
        """Test that run() iterates through all configured symbols"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        
        # Create bot with multiple symbols
        config = {
            'symbols': ['RELIANCE', 'TCS', 'INFY'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock is_market_open to return True (market open)
        with patch.object(bot, 'is_market_open', return_value=True):
            with patch('time.sleep') as mock_sleep:
                # Mock run_strategy to track calls
                with patch.object(bot, 'run_strategy') as mock_run_strategy:
                    with patch.object(bot, 'manage_positions'):
                        # Interrupt after first iteration
                        def interrupt_after_sleep(*args):
                            raise KeyboardInterrupt()
                        
                        mock_sleep.side_effect = interrupt_after_sleep
                        
                        # Run the bot
                        bot.run()
                        
                        # Verify run_strategy was called for each symbol
                        assert mock_run_strategy.call_count == 3
                        mock_run_strategy.assert_any_call('RELIANCE')
                        mock_run_strategy.assert_any_call('TCS')
                        mock_run_strategy.assert_any_call('INFY')
    
    def test_run_calls_run_strategy_for_each_symbol(self):
        """Test that run() calls run_strategy() for each symbol"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        
        # Create bot with single symbol
        config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock is_market_open to return True
        with patch.object(bot, 'is_market_open', return_value=True):
            with patch('time.sleep') as mock_sleep:
                # Mock run_strategy
                with patch.object(bot, 'run_strategy') as mock_run_strategy:
                    with patch.object(bot, 'manage_positions'):
                        # Interrupt after first iteration
                        def interrupt_after_sleep(*args):
                            raise KeyboardInterrupt()
                        
                        mock_sleep.side_effect = interrupt_after_sleep
                        
                        # Run the bot
                        bot.run()
                        
                        # Verify run_strategy was called with correct symbol
                        mock_run_strategy.assert_called_once_with('RELIANCE')
    
    def test_run_handles_keyboard_interrupt_gracefully(self):
        """Test that run() handles KeyboardInterrupt gracefully"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        
        # Create bot
        config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock is_market_open to return True
        with patch.object(bot, 'is_market_open', return_value=True):
            with patch('time.sleep') as mock_sleep:
                with patch.object(bot, 'run_strategy'):
                    with patch.object(bot, 'manage_positions'):
                        # Raise KeyboardInterrupt
                        mock_sleep.side_effect = KeyboardInterrupt()
                        
                        # Run the bot - should not raise exception
                        bot.run()
                        
                        # Verify disconnect was called
                        mock_broker.disconnect.assert_called_once()
    
    def test_run_disconnects_on_error(self):
        """Test that run() disconnects broker even on unexpected errors"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        
        # Create bot
        config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock is_market_open to return True
        with patch.object(bot, 'is_market_open', return_value=True):
            with patch('time.sleep') as mock_sleep:
                with patch.object(bot, 'run_strategy'):
                    with patch.object(bot, 'manage_positions'):
                        # Raise unexpected error
                        mock_sleep.side_effect = RuntimeError("Unexpected error")
                        
                        # Run the bot - should handle error
                        bot.run()
                        
                        # Verify disconnect was called
                        mock_broker.disconnect.assert_called_once()
    
    def test_run_continues_on_symbol_error(self):
        """Test that run() continues processing other symbols if one fails"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        
        # Create bot with multiple symbols
        config = {
            'symbols': ['RELIANCE', 'TCS', 'INFY'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock is_market_open to return True
        with patch.object(bot, 'is_market_open', return_value=True):
            with patch('time.sleep') as mock_sleep:
                # Mock run_strategy to fail on first symbol
                with patch.object(bot, 'run_strategy') as mock_run_strategy:
                    with patch.object(bot, 'manage_positions'):
                        call_count = [0]
                        
                        def run_strategy_side_effect(symbol):
                            call_count[0] += 1
                            if symbol == 'RELIANCE':
                                raise RuntimeError("Error processing RELIANCE")
                        
                        mock_run_strategy.side_effect = run_strategy_side_effect
                        
                        # Interrupt after first iteration
                        def interrupt_after_sleep(*args):
                            raise KeyboardInterrupt()
                        
                        mock_sleep.side_effect = interrupt_after_sleep
                        
                        # Run the bot
                        bot.run()
                        
                        # Verify run_strategy was called for all symbols
                        assert mock_run_strategy.call_count == 3
    
    def test_run_stops_if_connection_fails(self):
        """Test that run() stops if broker connection fails"""
        # Create mock broker adapter
        mock_broker = Mock()
        mock_broker.connect.return_value = False  # Connection fails
        
        # Create bot
        config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'trading_hours': {'start': '09:15', 'end': '15:30'}
        }
        bot = IndianTradingBot(config, mock_broker)
        
        # Mock run_strategy to track if it's called
        with patch.object(bot, 'run_strategy') as mock_run_strategy:
            # Run the bot
            bot.run()
            
            # Verify run_strategy was NOT called (connection failed)
            assert mock_run_strategy.call_count == 0
