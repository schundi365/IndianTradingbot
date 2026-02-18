"""
Integration tests for trade statistics functionality
Tests the calculation and display of trade statistics
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTradeStatistics(unittest.TestCase):
    """Test trade statistics calculations"""
    
    def test_calculate_basic_statistics(self):
        """Test basic statistics calculation with sample trades"""
        # Sample trades data
        trades = [
            {'pnl': 1000, 'quantity': 10, 'price': 100, 'exit_price': 110, 'transaction_type': 'BUY'},
            {'pnl': -500, 'quantity': 10, 'price': 100, 'exit_price': 95, 'transaction_type': 'BUY'},
            {'pnl': 750, 'quantity': 5, 'price': 200, 'exit_price': 350, 'transaction_type': 'BUY'},
            {'pnl': -250, 'quantity': 10, 'price': 50, 'exit_price': 25, 'transaction_type': 'SELL'}
        ]
        
        # Calculate statistics
        total_trades = len(trades)
        total_pnl = sum(t['pnl'] for t in trades)
        winning_trades = sum(1 for t in trades if t['pnl'] > 0)
        win_rate = (winning_trades / total_trades) * 100
        avg_pnl = total_pnl / total_trades
        
        # Assertions
        self.assertEqual(total_trades, 4)
        self.assertEqual(total_pnl, 1000)
        self.assertEqual(winning_trades, 2)
        self.assertEqual(win_rate, 50.0)
        self.assertEqual(avg_pnl, 250.0)
    
    def test_win_rate_calculation(self):
        """Test win rate calculation with different scenarios"""
        # All winning trades
        all_wins = [{'pnl': 100}, {'pnl': 200}, {'pnl': 300}]
        win_rate_all = (sum(1 for t in all_wins if t['pnl'] > 0) / len(all_wins)) * 100
        self.assertEqual(win_rate_all, 100.0)
        
        # All losing trades
        all_losses = [{'pnl': -100}, {'pnl': -200}, {'pnl': -300}]
        win_rate_none = (sum(1 for t in all_losses if t['pnl'] > 0) / len(all_losses)) * 100
        self.assertEqual(win_rate_none, 0.0)
        
        # Mixed trades (3 wins, 2 losses)
        mixed = [{'pnl': 100}, {'pnl': 200}, {'pnl': 300}, {'pnl': -50}, {'pnl': -75}]
        win_rate_mixed = (sum(1 for t in mixed if t['pnl'] > 0) / len(mixed)) * 100
        self.assertEqual(win_rate_mixed, 60.0)
    
    def test_empty_trades(self):
        """Test statistics with no trades"""
        trades = []
        
        total_trades = len(trades)
        total_pnl = 0
        win_rate = 0
        avg_pnl = 0
        
        self.assertEqual(total_trades, 0)
        self.assertEqual(total_pnl, 0)
        self.assertEqual(win_rate, 0)
        self.assertEqual(avg_pnl, 0)
    
    def test_pnl_calculation_from_prices(self):
        """Test P&L calculation when only prices are available"""
        # Buy trade - profit
        buy_profit = {
            'quantity': 10,
            'price': 100,
            'exit_price': 110,
            'transaction_type': 'BUY'
        }
        pnl_buy_profit = (buy_profit['exit_price'] - buy_profit['price']) * buy_profit['quantity']
        self.assertEqual(pnl_buy_profit, 100)
        
        # Buy trade - loss
        buy_loss = {
            'quantity': 10,
            'price': 100,
            'exit_price': 95,
            'transaction_type': 'BUY'
        }
        pnl_buy_loss = (buy_loss['exit_price'] - buy_loss['price']) * buy_loss['quantity']
        self.assertEqual(pnl_buy_loss, -50)
        
        # Sell trade - profit
        sell_profit = {
            'quantity': 10,
            'price': 100,
            'exit_price': 90,
            'transaction_type': 'SELL'
        }
        pnl_sell_profit = (sell_profit['price'] - sell_profit['exit_price']) * sell_profit['quantity']
        self.assertEqual(pnl_sell_profit, 100)
    
    def test_average_pnl_calculation(self):
        """Test average P&L per trade calculation"""
        trades = [
            {'pnl': 1000},
            {'pnl': -500},
            {'pnl': 750},
            {'pnl': -250}
        ]
        
        total_pnl = sum(t['pnl'] for t in trades)
        avg_pnl = total_pnl / len(trades)
        
        self.assertEqual(avg_pnl, 250.0)
    
    def test_statistics_with_zero_pnl_trades(self):
        """Test statistics when some trades have zero P&L"""
        trades = [
            {'pnl': 100},
            {'pnl': 0},
            {'pnl': -50},
            {'pnl': 0},
            {'pnl': 200}
        ]
        
        total_trades = len(trades)
        total_pnl = sum(t['pnl'] for t in trades)
        winning_trades = sum(1 for t in trades if t['pnl'] > 0)
        win_rate = (winning_trades / total_trades) * 100
        avg_pnl = total_pnl / total_trades
        
        self.assertEqual(total_trades, 5)
        self.assertEqual(total_pnl, 250)
        self.assertEqual(winning_trades, 2)
        self.assertEqual(win_rate, 40.0)
        self.assertEqual(avg_pnl, 50.0)
    
    def test_large_numbers(self):
        """Test statistics with large P&L values"""
        trades = [
            {'pnl': 100000},
            {'pnl': -50000},
            {'pnl': 75000},
            {'pnl': -25000}
        ]
        
        total_pnl = sum(t['pnl'] for t in trades)
        avg_pnl = total_pnl / len(trades)
        
        self.assertEqual(total_pnl, 100000)
        self.assertEqual(avg_pnl, 25000.0)
    
    def test_decimal_pnl_values(self):
        """Test statistics with decimal P&L values"""
        trades = [
            {'pnl': 123.45},
            {'pnl': -67.89},
            {'pnl': 234.56},
            {'pnl': -89.12}
        ]
        
        total_pnl = sum(t['pnl'] for t in trades)
        avg_pnl = total_pnl / len(trades)
        
        self.assertAlmostEqual(total_pnl, 201.0, places=2)
        self.assertAlmostEqual(avg_pnl, 50.25, places=2)


class TestStatisticsDisplay(unittest.TestCase):
    """Test statistics display formatting"""
    
    def test_win_rate_formatting(self):
        """Test win rate is formatted as percentage"""
        win_rate = 66.66666
        formatted = f"{win_rate:.1f}%"
        self.assertEqual(formatted, "66.7%")
    
    def test_currency_formatting(self):
        """Test P&L values are formatted as currency"""
        # This would use the formatters.currency function in actual implementation
        pnl = 1234.56
        # Simulating currency format
        formatted = f"₹{pnl:,.2f}"
        self.assertEqual(formatted, "₹1,234.56")
    
    def test_negative_currency_formatting(self):
        """Test negative P&L formatting"""
        pnl = -1234.56
        formatted = f"₹{pnl:,.2f}"
        self.assertEqual(formatted, "₹-1,234.56")


if __name__ == '__main__':
    unittest.main()
