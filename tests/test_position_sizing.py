"""
Tests for position sizing functionality in Indian Trading Bot

Tests verify:
- Requirement 9.1: Position sizes based on available margin
- Requirement 9.2: Respect instrument lot sizes
- Requirement 9.3: Use instrument tick sizes for stop-loss
- Requirement 9.4: Prevent position sizes exceeding available margin
- Requirement 9.5: Calculate risk based on equity, not balance
"""

import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from indian_trading_bot import IndianTradingBot


class TestPositionSizing(unittest.TestCase):
    """Test position sizing calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'risk_percent': 1.0,
            'reward_ratio': 2.0,
            'fast_ma_period': 10,
            'slow_ma_period': 21,
            'atr_period': 14,
            'margin_multiplier': 0.20
        }
        
        # Create mock broker adapter
        self.mock_broker = Mock()
        self.bot = IndianTradingBot(self.config, self.mock_broker)
    
    def test_position_size_uses_equity_not_balance(self):
        """Test Requirement 9.5: Risk calculation uses equity, not balance"""
        # Setup
        self.mock_broker.get_account_info.return_value = {
            'balance': 100000,
            'equity': 120000,  # Different from balance
            'margin_available': 80000,
            'margin_used': 20000
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        
        # Calculate position size
        entry_price = 2500.0
        stop_loss = 2450.0
        quantity = self.bot.calculate_position_size('RELIANCE', entry_price, stop_loss)
        
        # Verify equity was used (1% of 120000 = 1200)
        # Risk per unit = 50, so quantity should be 1200/50 = 24
        self.assertEqual(quantity, 24.0)
    
    def test_position_size_respects_lot_size(self):
        """Test Requirement 9.2: Position size is multiple of lot size"""
        # Setup with lot size of 50 (like NIFTY futures)
        self.mock_broker.get_account_info.return_value = {
            'balance': 100000,
            'equity': 100000,
            'margin_available': 80000,
            'margin_used': 20000
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'NIFTY',
            'lot_size': 50,
            'tick_size': 0.05,
            'instrument_token': '256265'
        }
        
        # Calculate position size
        entry_price = 18000.0
        stop_loss = 17900.0
        quantity = self.bot.calculate_position_size('NIFTY', entry_price, stop_loss)
        
        # Verify quantity is multiple of lot size (50)
        self.assertEqual(quantity % 50, 0)
        self.assertGreaterEqual(quantity, 50)
    
    def test_position_size_uses_tick_size_for_stop_loss(self):
        """Test Requirement 9.3: Stop loss distance uses tick size"""
        # Setup
        self.mock_broker.get_account_info.return_value = {
            'balance': 100000,
            'equity': 100000,
            'margin_available': 80000,
            'margin_used': 20000
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        
        # Calculate with stop loss that's not exact multiple of tick size
        entry_price = 2500.0
        stop_loss = 2449.97  # Should round to nearest tick
        quantity = self.bot.calculate_position_size('RELIANCE', entry_price, stop_loss)
        
        # Verify calculation used tick-aligned stop loss
        # Distance should be rounded to multiple of 0.05
        sl_distance = abs(entry_price - stop_loss)
        sl_ticks = round(sl_distance / 0.05)
        expected_distance = sl_ticks * 0.05
        
        # Risk = 1% of 100000 = 1000
        # Expected quantity = 1000 / expected_distance
        expected_quantity = 1000 / expected_distance
        self.assertAlmostEqual(quantity, expected_quantity, places=0)
    
    def test_position_size_respects_margin_limit(self):
        """Test Requirement 9.4: Position size doesn't exceed available margin"""
        # Setup with limited margin
        self.mock_broker.get_account_info.return_value = {
            'balance': 100000,
            'equity': 100000,
            'margin_available': 10000,  # Limited margin
            'margin_used': 90000
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        
        # Calculate position size
        entry_price = 2500.0
        stop_loss = 2450.0
        quantity = self.bot.calculate_position_size('RELIANCE', entry_price, stop_loss)
        
        # Verify margin requirement doesn't exceed available
        margin_multiplier = self.config.get('margin_multiplier', 0.20)
        estimated_margin = quantity * entry_price * margin_multiplier
        
        self.assertLessEqual(estimated_margin, 10000)
    
    def test_position_size_minimum_lot_size(self):
        """Test that minimum position size is one lot"""
        # Setup with very small equity
        self.mock_broker.get_account_info.return_value = {
            'balance': 1000,
            'equity': 1000,
            'margin_available': 800,
            'margin_used': 200
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'RELIANCE',
            'lot_size': 50,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        
        # Calculate position size
        entry_price = 2500.0
        stop_loss = 2450.0
        quantity = self.bot.calculate_position_size('RELIANCE', entry_price, stop_loss)
        
        # Should return at least one lot
        self.assertEqual(quantity, 50.0)
    
    def test_position_size_with_zero_equity(self):
        """Test handling of zero equity"""
        # Setup with zero equity
        self.mock_broker.get_account_info.return_value = {
            'balance': 0,
            'equity': 0,
            'margin_available': 0,
            'margin_used': 0
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        
        # Calculate position size
        entry_price = 2500.0
        stop_loss = 2450.0
        quantity = self.bot.calculate_position_size('RELIANCE', entry_price, stop_loss)
        
        # Should return default minimum
        self.assertEqual(quantity, 1.0)
    
    def test_position_size_with_missing_instrument_info(self):
        """Test handling of missing instrument info"""
        # Setup
        self.mock_broker.get_account_info.return_value = {
            'balance': 100000,
            'equity': 100000,
            'margin_available': 80000,
            'margin_used': 20000
        }
        
        # Return None for instrument info
        self.mock_broker.get_instrument_info.return_value = None
        
        # Calculate position size
        entry_price = 2500.0
        stop_loss = 2450.0
        quantity = self.bot.calculate_position_size('UNKNOWN', entry_price, stop_loss)
        
        # Should return default
        self.assertEqual(quantity, 1.0)
    
    def test_position_size_with_very_tight_stop_loss(self):
        """Test handling of very tight stop loss (less than tick size)"""
        # Setup
        self.mock_broker.get_account_info.return_value = {
            'balance': 100000,
            'equity': 100000,
            'margin_available': 80000,
            'margin_used': 20000
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'RELIANCE',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '738561'
        }
        
        # Calculate with very tight stop loss
        entry_price = 2500.0
        stop_loss = 2499.99  # Less than one tick
        quantity = self.bot.calculate_position_size('RELIANCE', entry_price, stop_loss)
        
        # Should return minimum lot size
        self.assertEqual(quantity, 1.0)
    
    def test_position_size_calculation_accuracy(self):
        """Test accurate position size calculation with realistic values"""
        # Setup
        self.mock_broker.get_account_info.return_value = {
            'balance': 500000,
            'equity': 500000,
            'margin_available': 400000,
            'margin_used': 100000
        }
        
        self.mock_broker.get_instrument_info.return_value = {
            'symbol': 'TCS',
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '2953217'
        }
        
        # Calculate position size
        entry_price = 3500.0
        stop_loss = 3450.0  # 50 point stop loss
        quantity = self.bot.calculate_position_size('TCS', entry_price, stop_loss)
        
        # Risk = 1% of 500000 = 5000
        # SL distance = 50
        # Expected quantity = 5000 / 50 = 100
        self.assertEqual(quantity, 100.0)
        
        # Verify margin check
        margin_required = quantity * entry_price * 0.20
        self.assertLess(margin_required, 400000)


if __name__ == '__main__':
    unittest.main()
