"""
Test position opening functionality with split orders
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from src.indian_trading_bot import IndianTradingBot


class TestPositionOpening:
    """Test position opening with broker adapter"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            'symbols': ['RELIANCE'],
            'timeframe': 30,
            'risk_percent': 1.0,
            'reward_ratio': 2.0,
            'use_split_orders': False,
            'num_positions': 3,
            'tp_levels': [1, 1.5, 2.5],
            'partial_close_percent': [40, 30, 30],
            'product_type': 'MIS'
        }
        
        # Create mock broker adapter
        self.mock_broker = Mock()
        self.mock_broker.connect.return_value = True
        self.mock_broker.place_order.return_value = "ORDER123"
        self.mock_broker.get_instrument_info.return_value = {
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        }
        
        self.bot = IndianTradingBot(self.config, self.mock_broker)
    
    def test_single_position_opening(self):
        """Test opening a single position"""
        # Arrange
        symbol = "RELIANCE"
        direction = 1  # Buy
        entry_price = 2500.0
        stop_loss = 2480.0
        take_profit = 2540.0
        quantity = 10.0
        
        # Act
        result = self.bot.open_position(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity
        )
        
        # Assert
        assert result is True
        self.mock_broker.place_order.assert_called_once()
        
        # Verify order parameters
        call_args = self.mock_broker.place_order.call_args
        assert call_args[1]['symbol'] == symbol
        assert call_args[1]['direction'] == direction
        assert call_args[1]['quantity'] == quantity
        assert call_args[1]['order_type'] == "MARKET"
        assert call_args[1]['stop_loss'] == stop_loss
        assert call_args[1]['take_profit'] == take_profit
        
        # Verify position stored
        assert "ORDER123" in self.bot.positions
        position = self.bot.positions["ORDER123"]
        assert position['symbol'] == symbol
        assert position['direction'] == direction
        assert position['entry_price'] == entry_price
        assert position['is_split'] is False
    
    def test_split_position_opening(self):
        """Test opening split positions"""
        # Arrange
        self.bot.use_split_orders = True
        symbol = "RELIANCE"
        direction = 1  # Buy
        entry_price = 2500.0
        stop_loss = 2480.0
        take_profit = 2540.0  # Not used for split orders
        quantity = 30.0
        
        # Mock multiple order IDs
        order_ids = ["ORDER1", "ORDER2", "ORDER3"]
        self.mock_broker.place_order.side_effect = order_ids
        
        # Act
        result = self.bot.open_position(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity
        )
        
        # Assert
        assert result is True
        assert self.mock_broker.place_order.call_count == 3
        
        # Verify split quantities (40%, 30%, 30%)
        calls = self.mock_broker.place_order.call_args_list
        expected_quantities = [12.0, 9.0, 9.0]  # 40%, 30%, 30% of 30
        
        for i, call in enumerate(calls):
            assert call[1]['symbol'] == symbol
            assert call[1]['direction'] == direction
            assert call[1]['quantity'] == expected_quantities[i]
            assert call[1]['order_type'] == "MARKET"
            assert call[1]['stop_loss'] == stop_loss
            # Each position should have different TP
            assert call[1]['take_profit'] is not None
        
        # Verify all positions stored
        for order_id in order_ids:
            assert order_id in self.bot.positions
            position = self.bot.positions[order_id]
            assert position['is_split'] is True
            assert 'group_id' in position
        
        # Verify group tracking
        assert len(self.bot.split_position_groups) == 1
        group = list(self.bot.split_position_groups.values())[0]
        assert group['symbol'] == symbol
        assert group['direction'] == direction
        assert len(group['order_ids']) == 3
    
    def test_split_quantity_calculation(self):
        """Test quantity splitting logic"""
        # Arrange
        total_quantity = 100.0
        
        # Act
        quantities = self.bot._split_quantity(total_quantity)
        
        # Assert
        assert len(quantities) == 3
        assert quantities[0] == 40.0  # 40%
        assert quantities[1] == 30.0  # 30%
        assert quantities[2] == 30.0  # 30%
        assert sum(quantities) == total_quantity
    
    def test_multiple_take_profit_calculation(self):
        """Test multiple TP level calculation"""
        # Arrange
        entry_price = 2500.0
        stop_loss = 2480.0
        direction = 1  # Buy
        symbol = "RELIANCE"
        
        # Act
        tp_prices = self.bot._calculate_multiple_take_profits(
            entry_price, stop_loss, direction, symbol
        )
        
        # Assert
        assert len(tp_prices) == 3
        risk = abs(entry_price - stop_loss)  # 20.0
        
        # TP1: 1R = 2500 + 20 = 2520
        assert tp_prices[0] == pytest.approx(2520.0, rel=0.01)
        
        # TP2: 1.5R = 2500 + 30 = 2530
        assert tp_prices[1] == pytest.approx(2530.0, rel=0.01)
        
        # TP3: 2.5R = 2500 + 50 = 2550
        assert tp_prices[2] == pytest.approx(2550.0, rel=0.01)
    
    def test_position_opening_failure(self):
        """Test handling of order placement failure"""
        # Arrange
        self.mock_broker.place_order.return_value = None  # Simulate failure
        
        # Act
        result = self.bot.open_position(
            symbol="RELIANCE",
            direction=1,
            entry_price=2500.0,
            stop_loss=2480.0,
            take_profit=2540.0,
            quantity=10.0
        )
        
        # Assert
        assert result is False
        assert len(self.bot.positions) == 0
    
    def test_split_position_partial_failure(self):
        """Test split positions with some orders failing"""
        # Arrange
        self.bot.use_split_orders = True
        
        # First order succeeds, second fails, third succeeds
        self.mock_broker.place_order.side_effect = ["ORDER1", None, "ORDER3"]
        
        # Act
        result = self.bot.open_position(
            symbol="RELIANCE",
            direction=1,
            entry_price=2500.0,
            stop_loss=2480.0,
            take_profit=2540.0,
            quantity=30.0
        )
        
        # Assert
        assert result is True  # At least one succeeded
        assert len(self.bot.positions) == 2  # Only 2 positions stored
        assert "ORDER1" in self.bot.positions
        assert "ORDER3" in self.bot.positions
        
        # Verify group has only successful orders
        group = list(self.bot.split_position_groups.values())[0]
        assert len(group['order_ids']) == 2
    
    def test_split_position_complete_failure(self):
        """Test split positions when all orders fail"""
        # Arrange
        self.bot.use_split_orders = True
        self.mock_broker.place_order.return_value = None  # All fail
        
        # Act
        result = self.bot.open_position(
            symbol="RELIANCE",
            direction=1,
            entry_price=2500.0,
            stop_loss=2480.0,
            take_profit=2540.0,
            quantity=30.0
        )
        
        # Assert
        assert result is False
        assert len(self.bot.positions) == 0
        assert len(self.bot.split_position_groups) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
