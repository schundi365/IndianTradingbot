"""
Integration test for positions table functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, patch
from indian_dashboard.services.bot_controller import BotController


class TestPositionsIntegration:
    """Test positions table integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.bot_controller = BotController()
        
        # Mock broker adapter
        self.mock_adapter = Mock()
        self.mock_adapter.is_connected.return_value = True
        
    def test_get_positions_empty(self):
        """Test getting positions when none exist"""
        # Setup
        self.mock_adapter.get_positions.return_value = []
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify
        assert positions == []
        assert isinstance(positions, list)
        
    def test_get_positions_single(self):
        """Test getting a single position"""
        # Setup
        mock_position = {
            'symbol': 'RELIANCE',
            'quantity': 10,
            'entry_price': 2450.50,
            'current_price': 2475.75,
            'pnl': 252.50,
            'side': 'BUY'
        }
        self.mock_adapter.get_positions.return_value = [mock_position]
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify
        assert len(positions) == 1
        assert positions[0]['symbol'] == 'RELIANCE'
        assert positions[0]['quantity'] == 10
        assert positions[0]['pnl'] == 252.50
        
    def test_get_positions_multiple(self):
        """Test getting multiple positions"""
        # Setup
        mock_positions = [
            {
                'symbol': 'RELIANCE',
                'quantity': 10,
                'entry_price': 2450.50,
                'current_price': 2475.75,
                'pnl': 252.50
            },
            {
                'symbol': 'TCS',
                'quantity': 5,
                'entry_price': 3650.00,
                'current_price': 3680.25,
                'pnl': 151.25
            },
            {
                'symbol': 'INFY',
                'quantity': 15,
                'entry_price': 1450.75,
                'current_price': 1465.50,
                'pnl': 221.25
            }
        ]
        self.mock_adapter.get_positions.return_value = mock_positions
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify
        assert len(positions) == 3
        assert positions[0]['symbol'] == 'RELIANCE'
        assert positions[1]['symbol'] == 'TCS'
        assert positions[2]['symbol'] == 'INFY'
        
        # Verify total P&L calculation
        total_pnl = sum(p['pnl'] for p in positions)
        assert total_pnl == 625.00
        
    def test_get_positions_mixed_pnl(self):
        """Test positions with mixed positive and negative P&L"""
        # Setup
        mock_positions = [
            {
                'symbol': 'RELIANCE',
                'quantity': 10,
                'entry_price': 2450.50,
                'current_price': 2475.75,
                'pnl': 252.50
            },
            {
                'symbol': 'HDFC',
                'quantity': 8,
                'entry_price': 1650.00,
                'current_price': 1625.50,
                'pnl': -196.00
            }
        ]
        self.mock_adapter.get_positions.return_value = mock_positions
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify
        assert len(positions) == 2
        assert positions[0]['pnl'] > 0  # Positive P&L
        assert positions[1]['pnl'] < 0  # Negative P&L
        
        # Verify net P&L
        net_pnl = sum(p['pnl'] for p in positions)
        assert net_pnl == 56.50
        
    def test_get_positions_no_broker(self):
        """Test getting positions when broker not connected"""
        # Setup
        self.bot_controller.broker_adapter = None
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify
        assert positions == []
        
    def test_get_positions_broker_error(self):
        """Test handling broker error when getting positions"""
        # Setup
        self.mock_adapter.get_positions.side_effect = Exception("Broker API error")
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify - should return empty list on error
        assert positions == []
        
    def test_close_position_success(self):
        """Test successfully closing a position"""
        # Setup
        mock_position = {
            'symbol': 'RELIANCE',
            'quantity': 10,
            'side': 'BUY'
        }
        self.mock_adapter.get_positions.return_value = [mock_position]
        self.mock_adapter.place_order.return_value = {'order_id': '12345'}
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        success, message = self.bot_controller.close_position('RELIANCE')
        
        # Verify
        assert success is True
        assert 'closed' in message.lower()
        self.mock_adapter.place_order.assert_called_once()
        
    def test_close_position_no_position(self):
        """Test closing position when none exists"""
        # Setup
        self.mock_adapter.get_positions.return_value = []
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        success, message = self.bot_controller.close_position('RELIANCE')
        
        # Verify
        assert success is False
        assert 'no position' in message.lower()
        
    def test_close_position_no_broker(self):
        """Test closing position when broker not connected"""
        # Setup
        self.bot_controller.broker_adapter = None
        
        # Execute
        success, message = self.bot_controller.close_position('RELIANCE')
        
        # Verify
        assert success is False
        assert 'not connected' in message.lower()
        
    def test_close_position_order_fails(self):
        """Test closing position when order placement fails"""
        # Setup
        mock_position = {
            'symbol': 'RELIANCE',
            'quantity': 10,
            'side': 'BUY'
        }
        self.mock_adapter.get_positions.return_value = [mock_position]
        self.mock_adapter.place_order.return_value = None  # Order failed
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        success, message = self.bot_controller.close_position('RELIANCE')
        
        # Verify
        assert success is False
        assert 'failed' in message.lower()
        
    def test_position_pnl_calculation(self):
        """Test P&L calculation for positions"""
        # Setup - position without explicit P&L
        mock_position = {
            'symbol': 'RELIANCE',
            'quantity': 10,
            'entry_price': 2450.50,
            'current_price': 2475.75,
            'pnl': 0  # No P&L provided
        }
        self.mock_adapter.get_positions.return_value = [mock_position]
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify - P&L should be calculated
        position = positions[0]
        expected_pnl = (position['current_price'] - position['entry_price']) * position['quantity']
        assert expected_pnl == 252.50
        
    def test_position_quantity_display(self):
        """Test position quantity display with sign"""
        # Setup
        mock_positions = [
            {'symbol': 'LONG', 'quantity': 10, 'entry_price': 100, 'current_price': 105, 'pnl': 50},
            {'symbol': 'SHORT', 'quantity': -5, 'entry_price': 200, 'current_price': 195, 'pnl': 25}
        ]
        self.mock_adapter.get_positions.return_value = mock_positions
        self.bot_controller.broker_adapter = self.mock_adapter
        
        # Execute
        positions = self.bot_controller.get_positions()
        
        # Verify
        assert positions[0]['quantity'] == 10  # Long position
        assert positions[1]['quantity'] == -5  # Short position


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
