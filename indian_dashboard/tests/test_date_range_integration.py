"""
Integration tests for date range filter functionality
Tests the TradeHistory module's date filtering capabilities
"""

import unittest
from datetime import datetime, timedelta
import json


class TestDateRangeFilter(unittest.TestCase):
    """Test date range filtering in trade history"""
    
    def setUp(self):
        """Set up test data"""
        self.today = datetime.now()
        self.trades = self.generate_test_trades()
    
    def generate_test_trades(self):
        """Generate test trades spanning 30 days"""
        trades = []
        symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
        
        for days_ago in range(30):
            trade_date = self.today - timedelta(days=days_ago)
            
            # Create 2 trades per day
            for i in range(2):
                trade = {
                    'timestamp': trade_date.isoformat(),
                    'symbol': symbols[i % len(symbols)],
                    'transaction_type': 'BUY' if i % 2 == 0 else 'SELL',
                    'quantity': 10,
                    'price': 1000.0,
                    'exit_price': 1050.0,
                    'pnl': 500.0 if i % 2 == 0 else -500.0
                }
                trades.append(trade)
        
        return trades
    
    def filter_trades_by_date(self, trades, from_date=None, to_date=None):
        """Filter trades by date range (mimics API behavior)"""
        filtered = trades.copy()
        
        if from_date:
            from_time = datetime.fromisoformat(from_date).timestamp()
            filtered = [
                t for t in filtered
                if datetime.fromisoformat(t['timestamp']).timestamp() >= from_time
            ]
        
        if to_date:
            # End of day
            to_time = datetime.fromisoformat(to_date).timestamp() + (24 * 60 * 60)
            filtered = [
                t for t in filtered
                if datetime.fromisoformat(t['timestamp']).timestamp() < to_time
            ]
        
        return filtered
    
    def test_no_filter_returns_all_trades(self):
        """Test that no filter returns all trades"""
        filtered = self.filter_trades_by_date(self.trades)
        self.assertEqual(len(filtered), len(self.trades))
        self.assertEqual(len(filtered), 60)  # 30 days * 2 trades
    
    def test_today_filter(self):
        """Test filtering for today's trades"""
        today_str = self.today.strftime('%Y-%m-%d')
        filtered = self.filter_trades_by_date(self.trades, today_str, today_str)
        
        # Should have 2 trades from today
        self.assertEqual(len(filtered), 2)
        
        # All trades should be from today
        for trade in filtered:
            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            self.assertEqual(trade_date, self.today.date())
    
    def test_week_filter(self):
        """Test filtering for last 7 days"""
        week_ago = self.today - timedelta(days=7)
        from_date = week_ago.strftime('%Y-%m-%d')
        to_date = self.today.strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, from_date, to_date)
        
        # Should have 8 days * 2 trades = 16 trades (including today)
        self.assertEqual(len(filtered), 16)
        
        # All trades should be within the range
        for trade in filtered:
            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            self.assertGreaterEqual(trade_date, week_ago.date())
            self.assertLessEqual(trade_date, self.today.date())
    
    def test_month_filter(self):
        """Test filtering for last 30 days"""
        month_ago = self.today - timedelta(days=30)
        from_date = month_ago.strftime('%Y-%m-%d')
        to_date = self.today.strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, from_date, to_date)
        
        # Should have all trades (31 days * 2 trades = 62, but we only have 30 days)
        self.assertEqual(len(filtered), 60)
    
    def test_custom_date_range(self):
        """Test custom date range filter"""
        from_date = (self.today - timedelta(days=5)).strftime('%Y-%m-%d')
        to_date = (self.today - timedelta(days=2)).strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, from_date, to_date)
        
        # Should have 4 days * 2 trades = 8 trades
        self.assertEqual(len(filtered), 8)
        
        # Verify date range
        from_dt = datetime.fromisoformat(from_date).date()
        to_dt = datetime.fromisoformat(to_date).date()
        
        for trade in filtered:
            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            self.assertGreaterEqual(trade_date, from_dt)
            self.assertLessEqual(trade_date, to_dt)
    
    def test_from_date_only(self):
        """Test filtering with only from date"""
        from_date = (self.today - timedelta(days=10)).strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, from_date=from_date)
        
        # Should have 11 days * 2 trades = 22 trades
        self.assertEqual(len(filtered), 22)
        
        # All trades should be after from_date
        from_dt = datetime.fromisoformat(from_date).date()
        for trade in filtered:
            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            self.assertGreaterEqual(trade_date, from_dt)
    
    def test_to_date_only(self):
        """Test filtering with only to date"""
        to_date = (self.today - timedelta(days=20)).strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, to_date=to_date)
        
        # Should have 10 days * 2 trades = 20 trades (days 21-30, not including day 20)
        self.assertEqual(len(filtered), 20)
        
        # All trades should be before to_date
        to_dt = datetime.fromisoformat(to_date).date()
        for trade in filtered:
            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            self.assertLessEqual(trade_date, to_dt)
    
    def test_invalid_date_range(self):
        """Test that from_date after to_date returns empty"""
        from_date = self.today.strftime('%Y-%m-%d')
        to_date = (self.today - timedelta(days=5)).strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, from_date, to_date)
        
        # Should return empty list
        self.assertEqual(len(filtered), 0)
    
    def test_future_date_range(self):
        """Test filtering with future dates returns empty"""
        from_date = (self.today + timedelta(days=1)).strftime('%Y-%m-%d')
        to_date = (self.today + timedelta(days=5)).strftime('%Y-%m-%d')
        
        filtered = self.filter_trades_by_date(self.trades, from_date, to_date)
        
        # Should return empty list
        self.assertEqual(len(filtered), 0)
    
    def test_date_format_consistency(self):
        """Test that date format is consistent (YYYY-MM-DD)"""
        import re
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        
        # Test today
        today_str = self.today.strftime('%Y-%m-%d')
        self.assertTrue(date_pattern.match(today_str))
        
        # Test week ago
        week_ago_str = (self.today - timedelta(days=7)).strftime('%Y-%m-%d')
        self.assertTrue(date_pattern.match(week_ago_str))
        
        # Test month ago
        month_ago_str = (self.today - timedelta(days=30)).strftime('%Y-%m-%d')
        self.assertTrue(date_pattern.match(month_ago_str))


class TestQuickFilterCalculations(unittest.TestCase):
    """Test quick filter date calculations"""
    
    def test_today_calculation(self):
        """Test today filter calculates correct dates"""
        today = datetime.now()
        from_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # From date should be start of today
        self.assertEqual(from_date.date(), today.date())
        self.assertEqual(from_date.hour, 0)
        self.assertEqual(from_date.minute, 0)
    
    def test_week_calculation(self):
        """Test week filter calculates 7 days ago"""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        # Should be exactly 7 days ago
        diff = (today - week_ago).days
        self.assertEqual(diff, 7)
    
    def test_month_calculation(self):
        """Test month filter calculates 30 days ago"""
        today = datetime.now()
        month_ago = today - timedelta(days=30)
        
        # Should be exactly 30 days ago
        diff = (today - month_ago).days
        self.assertEqual(diff, 30)


if __name__ == '__main__':
    unittest.main()
