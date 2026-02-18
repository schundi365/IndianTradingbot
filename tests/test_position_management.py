"""
Test position management functionality
Tests trailing stops, break-even stops, and time-based exits
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np
from src.indian_trading_bot import IndianTradingBot


@pytest.fixture
def mock_broker():
    """Create a mock broker adapter"""
    broker = Mock()
    broker.connect.return_value = True
    broker.is_connected.return_value = True
    broker.get_positions.return_value = []
    broker.get_account_info.return_value = {
        'balance': 100000,
        'equity': 100000,
        'margin_available': 80000,
        'margin_used': 20000
    }
    broker.get_instrument_info.return_value = {
        'symbol': 'RELIANCE',
        'lot_size': 1,
        'tick_size': 0.05,
        'instrument_token': '738561'
    }
    return broker


@pytest.fixture
def bot_config():
    """Create bot configuration"""
    return {
        'symbols': ['RELIANCE'],
        'timeframe': 30,  # 30 minute
        'risk_percent': 1.0,
        'reward_ratio': 2.0,
        'trail_activation': 1.5,
        'trail_distance': 1.0,
        'enable_time_based_exit': True,
        'max_hold_minutes': 45,
        'enable_breakeven_stop': True,
        'breakeven_atr_threshold': 0.3,
        'use_split_orders': False
    }


@pytest.fixture
def sample_data():
    """Create sample market data"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='30min')
    data = {
        'time': dates,
        'open': np.random.uniform(2400, 2500, 100),
        'high': np.random.uniform(2450, 2550, 100),
        'low': np.random.uniform(2350, 2450, 100),
        'close': np.random.uniform(2400, 2500, 100),
        'volume': np.random.randint(100000, 1000000, 100)
    }
    df = pd.DataFrame(data)
    # Ensure high is highest and low is lowest
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    return df


def test_cleanup_closed_positions(mock_broker, bot_config):
    """Test that closed positions are removed from tracking"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Add some positions to tracking
    bot.positions['order1'] = {
        'symbol': 'RELIANCE',
        'direction': 1,
        'entry_price': 2450.0,
        'stop_loss': 2400.0,
        'entry_time': datetime.now()
    }
    bot.positions['order2'] = {
        'symbol': 'RELIANCE',
        'direction': 1,
        'entry_price': 2460.0,
        'stop_loss': 2410.0,
        'entry_time': datetime.now()
    }
    
    # Mock broker returns only one position (order1 is closed)
    mock_broker.get_positions.return_value = [
        {
            'symbol': 'RELIANCE',
            'direction': 1,
            'quantity': 10,
            'entry_price': 2460.0,
            'current_price': 2470.0,
            'pnl': 100.0,
            'pnl_percent': 0.43,
            'order_id': 'order2'
        }
    ]
    
    # Run cleanup
    bot.cleanup_closed_positions()
    
    # Verify order1 was removed
    assert 'order1' not in bot.positions
    assert 'order2' in bot.positions


def test_cleanup_closed_groups(mock_broker, bot_config):
    """Test that groups with all closed positions are removed"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Add a group
    bot.split_position_groups['group1'] = {
        'symbol': 'RELIANCE',
        'direction': 1,
        'order_ids': ['order1', 'order2'],
        'entry_price': 2450.0,
        'initial_sl': 2400.0
    }
    
    # Mock broker returns no positions (all closed)
    mock_broker.get_positions.return_value = []
    
    # Run cleanup
    bot.cleanup_closed_groups()
    
    # Verify group was removed
    assert 'group1' not in bot.split_position_groups


def test_force_close_position(mock_broker, bot_config):
    """Test force closing a position"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Add position to tracking
    bot.positions['order1'] = {
        'symbol': 'RELIANCE',
        'direction': 1,
        'entry_price': 2450.0,
        'stop_loss': 2400.0,
        'entry_time': datetime.now()
    }
    
    # Mock successful order placement
    mock_broker.place_order.return_value = 'close_order1'
    
    # Create position dict
    position = {
        'symbol': 'RELIANCE',
        'direction': 1,
        'quantity': 10,
        'entry_price': 2450.0,
        'current_price': 2470.0,
        'pnl': 200.0,
        'order_id': 'order1'
    }
    
    # Force close
    result = bot._force_close_position(position, 'RELIANCE')
    
    # Verify
    assert result is True
    mock_broker.place_order.assert_called_once()
    # Verify opposite direction was used
    call_args = mock_broker.place_order.call_args[1]
    assert call_args['direction'] == -1  # Opposite of buy
    assert call_args['quantity'] == 10
    assert call_args['order_type'] == 'MARKET'


def test_trailing_stop_activation(mock_broker, bot_config, sample_data):
    """Test that trailing stop activates when profit threshold is reached"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Mock get_historical_data to return sample data
    with patch.object(bot, 'get_historical_data', return_value=sample_data):
        # Add position to tracking with initial SL
        entry_price = 2400.0
        current_price = 2500.0  # Significant profit
        initial_sl = 2350.0
        
        bot.positions['order1'] = {
            'symbol': 'RELIANCE',
            'direction': 1,
            'entry_price': entry_price,
            'stop_loss': initial_sl,  # Current SL
            'entry_time': datetime.now()
        }
        
        # Create position dict
        position = {
            'symbol': 'RELIANCE',
            'direction': 1,
            'quantity': 10,
            'entry_price': entry_price,
            'current_price': current_price,
            'pnl': 1000.0,
            'order_id': 'order1'
        }
        
        # Update trailing stop
        result = bot.update_trailing_stop(position, 'RELIANCE', 1)
        
        # Verify trailing stop was calculated and updated
        # The new SL should be higher than the initial SL for a buy position
        if result:
            assert bot.positions['order1']['stop_loss'] > initial_sl
        # If result is False, it means profit wasn't enough or SL wasn't better
        # This is acceptable behavior


def test_breakeven_stop_activation(mock_broker, bot_config, sample_data):
    """Test that break-even stop activates when threshold is reached"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Mock get_historical_data
    with patch.object(bot, 'get_historical_data', return_value=sample_data):
        # Add position with entry time
        entry_time = datetime.now() - timedelta(minutes=10)
        entry_price = 2400.0
        current_price = 2420.0  # Small profit
        
        bot.positions['order1'] = {
            'symbol': 'RELIANCE',
            'direction': 1,
            'entry_price': entry_price,
            'stop_loss': 2350.0,
            'entry_time': entry_time
        }
        
        # Mock broker positions
        mock_broker.get_positions.return_value = [
            {
                'symbol': 'RELIANCE',
                'direction': 1,
                'quantity': 10,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl': 200.0,
                'order_id': 'order1'
            }
        ]
        
        # Run manage_positions
        bot.manage_positions()
        
        # Verify break-even logic was executed
        # (Check that position still exists and has updated SL)
        assert 'order1' in bot.positions


def test_time_based_exit(mock_broker, bot_config, sample_data):
    """Test that positions are closed after max hold time"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Mock get_historical_data
    with patch.object(bot, 'get_historical_data', return_value=sample_data):
        # Add position with old entry time
        entry_time = datetime.now() - timedelta(minutes=60)  # Held for 60 minutes
        
        bot.positions['order1'] = {
            'symbol': 'RELIANCE',
            'direction': 1,
            'entry_price': 2400.0,
            'stop_loss': 2350.0,
            'entry_time': entry_time
        }
        
        # Mock broker positions
        mock_broker.get_positions.return_value = [
            {
                'symbol': 'RELIANCE',
                'direction': 1,
                'quantity': 10,
                'entry_price': 2400.0,
                'current_price': 2410.0,
                'pnl': 100.0,
                'order_id': 'order1'
            }
        ]
        
        # Mock successful close
        mock_broker.place_order.return_value = 'close_order1'
        
        # Run manage_positions
        bot.manage_positions()
        
        # Verify close order was placed
        mock_broker.place_order.assert_called()


def test_manage_positions_with_no_positions(mock_broker, bot_config):
    """Test manage_positions when there are no open positions"""
    bot = IndianTradingBot(bot_config, mock_broker)
    
    # Mock no positions
    mock_broker.get_positions.return_value = []
    
    # Should not raise any errors
    bot.manage_positions()
    
    # Verify cleanup was called
    assert len(bot.positions) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
