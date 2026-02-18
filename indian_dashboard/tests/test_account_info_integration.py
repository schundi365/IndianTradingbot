"""
Integration tests for Account Info Card (Task 8.2)
Tests the account information display functionality
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.services.bot_controller import BotController


class TestAccountInfoIntegration:
    """Test account info card integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.bot_controller = BotController()
        
        # Create mock broker adapter
        self.adapter = Mock()
        self.adapter.is_connected = Mock(return_value=True)
        
        # Mock account info data
        self.sample_account_info = {
            'balance': 250000.00,
            'equity': 265000.00,
            'margin_available': 180000.00,
            'margin_used': 70000.00,
            'pnl_today': 5250.50
        }
        
        self.adapter.get_account_info = Mock(return_value=self.sample_account_info)
    
    def teardown_method(self):
        """Clean up after tests"""
        if self.bot_controller.is_running:
            self.bot_controller.stop()
    
    def test_get_account_info_returns_dict(self):
        """Test that get_account_info returns a dictionary"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify it's a dictionary
        assert isinstance(account_info, dict), "Account info should be a dictionary"
    
    def test_account_info_has_required_fields(self):
        """Test that account info contains all required fields"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify required fields exist
        required_fields = ['balance', 'equity', 'margin_available']
        for field in required_fields:
            assert field in account_info, f"Account info should contain '{field}'"
    
    def test_account_info_balance_is_numeric(self):
        """Test that balance is a numeric value"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify balance is numeric
        assert isinstance(account_info.get('balance'), (int, float)), \
            "Balance should be numeric"
        assert account_info['balance'] >= 0, "Balance should be non-negative"
    
    def test_account_info_equity_is_numeric(self):
        """Test that equity is a numeric value"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify equity is numeric
        assert isinstance(account_info.get('equity'), (int, float)), \
            "Equity should be numeric"
        assert account_info['equity'] >= 0, "Equity should be non-negative"
    
    def test_account_info_margin_available_is_numeric(self):
        """Test that margin_available is a numeric value"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify margin_available is numeric
        assert isinstance(account_info.get('margin_available'), (int, float)), \
            "Margin available should be numeric"
        assert account_info['margin_available'] >= 0, \
            "Margin available should be non-negative"
    
    def test_account_info_margin_used_if_present(self):
        """Test that margin_used is numeric if present"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # If margin_used is present, verify it's numeric
        if 'margin_used' in account_info:
            assert isinstance(account_info['margin_used'], (int, float)), \
                "Margin used should be numeric"
            assert account_info['margin_used'] >= 0, \
                "Margin used should be non-negative"
    
    def test_account_info_pnl_today_if_present(self):
        """Test that pnl_today is numeric if present"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # If pnl_today is present, verify it's numeric
        if 'pnl_today' in account_info:
            assert isinstance(account_info['pnl_today'], (int, float)), \
                "P&L today should be numeric"
    
    def test_account_info_without_broker_returns_none(self):
        """Test that get_account_info returns None when broker not connected"""
        # Don't set broker adapter
        self.bot_controller.broker_adapter = None
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify it returns None
        assert account_info is None, \
            "Account info should be None when broker not connected"
    
    def test_account_info_with_disconnected_broker_returns_none(self):
        """Test that get_account_info returns None when broker disconnected"""
        # Set broker adapter but mark it as disconnected
        self.adapter.is_connected = Mock(return_value=False)
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify it returns None
        assert account_info is None, \
            "Account info should be None when broker disconnected"
    
    def test_account_info_values_match_expected(self):
        """Test that account info values match expected sample data"""
        # Set broker adapter
        self.bot_controller.broker_adapter = self.adapter
        
        # Get account info
        account_info = self.bot_controller.get_account_info()
        
        # Verify values match sample data
        assert account_info['balance'] == self.sample_account_info['balance']
        assert account_info['equity'] == self.sample_account_info['equity']
        assert account_info['margin_available'] == self.sample_account_info['margin_available']
        assert account_info['margin_used'] == self.sample_account_info['margin_used']
        assert account_info['pnl_today'] == self.sample_account_info['pnl_today']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
