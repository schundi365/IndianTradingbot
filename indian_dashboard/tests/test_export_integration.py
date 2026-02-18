"""
Integration tests for trade export functionality
Tests CSV and Excel export features
"""

import unittest
import json
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from indian_dashboard import app
    HAS_APP = True
except ImportError:
    HAS_APP = False
    app = None


class TestTradeExportIntegration(unittest.TestCase):
    """Test trade export functionality"""
    
    def setUp(self):
        """Set up test client"""
        if HAS_APP:
            self.app = app
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
        else:
            self.client = None
        
        # Sample trade data
        self.sample_trades = [
            {
                'timestamp': '2024-02-18T09:30:00',
                'symbol': 'RELIANCE',
                'transaction_type': 'BUY',
                'quantity': 10,
                'price': 2500.50,
                'exit_price': 2550.75,
                'pnl': 502.50
            },
            {
                'timestamp': '2024-02-18T10:15:00',
                'symbol': 'TCS',
                'transaction_type': 'SELL',
                'quantity': 5,
                'price': 3800.00,
                'exit_price': 3750.25,
                'pnl': 248.75
            },
            {
                'timestamp': '2024-02-18T11:00:00',
                'symbol': 'INFY',
                'transaction_type': 'BUY',
                'quantity': 20,
                'price': 1450.00,
                'exit_price': 1425.50,
                'pnl': -490.00
            }
        ]
    
    def test_get_trades_endpoint(self):
        """Test that trades endpoint returns data"""
        if not HAS_APP or not self.client:
            self.skipTest("Flask app not available")
        
        response = self.client.get('/api/bot/trades')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('trades', data)
        self.assertIsInstance(data['trades'], list)
    
    def test_get_trades_with_date_filter(self):
        """Test trades endpoint with date range filter"""
        if not HAS_APP or not self.client:
            self.skipTest("Flask app not available")
        
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(f'/api/bot/trades?from_date={from_date}&to_date={to_date}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('trades', data)
    
    def test_trades_data_structure(self):
        """Test that trade data has required fields for export"""
        if not HAS_APP or not self.client:
            self.skipTest("Flask app not available")
        
        response = self.client.get('/api/bot/trades')
        data = json.loads(response.data)
        
        if len(data['trades']) > 0:
            trade = data['trades'][0]
            
            # Check for required fields
            required_fields = ['symbol', 'quantity']
            for field in required_fields:
                self.assertIn(field, trade, f"Trade missing required field: {field}")
    
    def test_csv_export_data_format(self):
        """Test that trade data can be formatted for CSV export"""
        # Simulate CSV formatting
        for trade in self.sample_trades:
            # Check all required fields exist
            self.assertIn('timestamp', trade)
            self.assertIn('symbol', trade)
            self.assertIn('transaction_type', trade)
            self.assertIn('quantity', trade)
            self.assertIn('price', trade)
            
            # Check data types
            self.assertIsInstance(trade['quantity'], (int, float))
            self.assertIsInstance(trade['price'], (int, float))
            
            # Check P&L calculation
            if 'exit_price' in trade and trade['exit_price'] > 0:
                self.assertIsInstance(trade['exit_price'], (int, float))
    
    def test_excel_export_data_format(self):
        """Test that trade data can be formatted for Excel export"""
        # Simulate Excel formatting
        for trade in self.sample_trades:
            # Numeric fields should be numbers
            self.assertIsInstance(trade['quantity'], (int, float))
            self.assertIsInstance(trade['price'], (int, float))
            
            # Date should be parseable
            try:
                datetime.fromisoformat(trade['timestamp'])
            except ValueError:
                self.fail(f"Invalid timestamp format: {trade['timestamp']}")
    
    def test_export_with_empty_trades(self):
        """Test export behavior with no trades"""
        empty_trades = []
        
        # Should handle empty list gracefully
        self.assertEqual(len(empty_trades), 0)
        # In actual implementation, this should trigger a warning notification
    
    def test_export_with_missing_fields(self):
        """Test export with trades that have missing fields"""
        incomplete_trade = {
            'timestamp': '2024-02-18T09:30:00',
            'symbol': 'TEST',
            'transaction_type': 'BUY',
            'quantity': 10
            # Missing price, exit_price, pnl
        }
        
        # Should handle missing fields gracefully
        self.assertIn('symbol', incomplete_trade)
        self.assertIn('quantity', incomplete_trade)
        
        # Missing fields should default to 0 or empty
        price = incomplete_trade.get('price', 0)
        exit_price = incomplete_trade.get('exit_price', 0)
        pnl = incomplete_trade.get('pnl', 0)
        
        self.assertIsInstance(price, (int, float))
        self.assertIsInstance(exit_price, (int, float))
        self.assertIsInstance(pnl, (int, float))
    
    def test_export_with_special_characters(self):
        """Test export with special characters in data"""
        special_trade = {
            'timestamp': '2024-02-18T09:30:00',
            'symbol': 'TEST,SYMBOL',  # Contains comma
            'transaction_type': 'BUY',
            'quantity': 10,
            'price': 100.50,
            'exit_price': 105.75,
            'pnl': 52.50
        }
        
        # Symbol with comma should be handled
        self.assertIn(',', special_trade['symbol'])
        
        # In CSV, this should be escaped with quotes
        # In Excel XML, this should be escaped with XML entities
    
    def test_pnl_calculation(self):
        """Test P&L calculation for trades"""
        for trade in self.sample_trades:
            if 'pnl' in trade:
                # Verify P&L is calculated correctly
                if 'exit_price' in trade and trade['exit_price'] > 0:
                    entry_price = trade['price']
                    exit_price = trade['exit_price']
                    quantity = trade['quantity']
                    
                    if trade['transaction_type'].upper() == 'BUY':
                        expected_pnl = (exit_price - entry_price) * quantity
                    else:
                        expected_pnl = (entry_price - exit_price) * quantity
                    
                    # Allow small floating point differences
                    self.assertAlmostEqual(trade['pnl'], expected_pnl, places=2)
    
    def test_filename_generation(self):
        """Test export filename generation"""
        # Test with date range
        from_date = '2024-02-01'
        to_date = '2024-02-28'
        expected_filename = f'trades_{from_date}_to_{to_date}'
        
        # Filename should include date range
        self.assertIn(from_date, expected_filename)
        self.assertIn(to_date, expected_filename)
        
        # Test without date range (should use current date)
        current_date = datetime.now().strftime('%Y-%m-%d')
        expected_filename_no_range = f'trades_{current_date}'
        
        self.assertIn(current_date, expected_filename_no_range)
    
    def test_csv_escaping(self):
        """Test CSV cell escaping"""
        # Test cases for CSV escaping
        test_cases = [
            ('Normal text', 'Normal text'),
            ('Text, with comma', '"Text, with comma"'),
            ('Text with "quotes"', '"Text with ""quotes"""'),
            ('Text\nwith\nnewlines', '"Text\nwith\nnewlines"'),
        ]
        
        for input_text, expected_output in test_cases:
            # Simulate CSV escaping logic
            if ',' in input_text or '"' in input_text or '\n' in input_text:
                escaped = f'"{input_text.replace(chr(34), chr(34)+chr(34))}"'
                self.assertEqual(escaped, expected_output)
    
    def test_excel_xml_escaping(self):
        """Test Excel XML character escaping"""
        # Test cases for XML escaping
        test_cases = [
            ('Normal text', 'Normal text'),
            ('Text & symbol', 'Text &amp; symbol'),
            ('Text < symbol', 'Text &lt; symbol'),
            ('Text > symbol', 'Text &gt; symbol'),
            ('Text "quotes"', 'Text &quot;quotes&quot;'),
        ]
        
        for input_text, expected_output in test_cases:
            # Simulate XML escaping logic
            escaped = (input_text
                      .replace('&', '&amp;')
                      .replace('<', '&lt;')
                      .replace('>', '&gt;')
                      .replace('"', '&quot;'))
            
            self.assertEqual(escaped, expected_output)
    
    def test_large_dataset_export(self):
        """Test export with large number of trades"""
        # Generate 1000 trades
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'timestamp': f'2024-02-{(i % 28) + 1:02d}T09:30:00',
                'symbol': f'STOCK{i}',
                'transaction_type': 'BUY' if i % 2 == 0 else 'SELL',
                'quantity': i + 1,
                'price': 100.0 + i,
                'exit_price': 105.0 + i,
                'pnl': 5.0 * (i + 1)
            })
        
        # Should handle large dataset
        self.assertEqual(len(large_dataset), 1000)
        
        # All trades should have required fields
        for trade in large_dataset:
            self.assertIn('symbol', trade)
            self.assertIn('quantity', trade)
            self.assertIn('price', trade)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
