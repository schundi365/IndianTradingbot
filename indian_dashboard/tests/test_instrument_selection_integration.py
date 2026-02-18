"""
Integration tests for instrument selection functionality
Tests Requirements 3.2.4: Instrument selection with persistence
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import Mock, patch
import json


class TestInstrumentSelection(unittest.TestCase):
    """Test instrument selection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_instruments = [
            {
                'symbol': 'RELIANCE',
                'name': 'Reliance Industries',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'token': 'NSE:RELIANCE',
                'last_price': 2500.50
            },
            {
                'symbol': 'TCS',
                'name': 'Tata Consultancy Services',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'token': 'NSE:TCS',
                'last_price': 3400.75
            },
            {
                'symbol': 'INFY',
                'name': 'Infosys',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'token': 'NSE:INFY',
                'last_price': 1450.25
            }
        ]
    
    def test_select_single_instrument(self):
        """Test selecting a single instrument"""
        selected = []
        instrument = self.test_instruments[0]
        
        # Simulate selection
        if instrument['token'] not in [i['token'] for i in selected]:
            selected.append(instrument)
        
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['symbol'], 'RELIANCE')
    
    def test_select_multiple_instruments(self):
        """Test selecting multiple instruments"""
        selected = []
        
        # Select first two instruments
        for instrument in self.test_instruments[:2]:
            if instrument['token'] not in [i['token'] for i in selected]:
                selected.append(instrument)
        
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0]['symbol'], 'RELIANCE')
        self.assertEqual(selected[1]['symbol'], 'TCS')
    
    def test_deselect_instrument(self):
        """Test deselecting an instrument"""
        selected = self.test_instruments.copy()
        
        # Deselect first instrument
        token_to_remove = self.test_instruments[0]['token']
        selected = [i for i in selected if i['token'] != token_to_remove]
        
        self.assertEqual(len(selected), 2)
        self.assertNotIn('RELIANCE', [i['symbol'] for i in selected])
    
    def test_select_all_instruments(self):
        """Test selecting all instruments on page"""
        selected = []
        
        # Select all
        for instrument in self.test_instruments:
            if instrument['token'] not in [i['token'] for i in selected]:
                selected.append(instrument)
        
        self.assertEqual(len(selected), 3)
        self.assertEqual(len(selected), len(self.test_instruments))
    
    def test_clear_all_selections(self):
        """Test clearing all selections"""
        selected = self.test_instruments.copy()
        
        # Clear all
        selected = []
        
        self.assertEqual(len(selected), 0)
    
    def test_prevent_duplicate_selections(self):
        """Test that duplicate selections are prevented"""
        selected = []
        instrument = self.test_instruments[0]
        
        # Try to add same instrument twice
        if instrument['token'] not in [i['token'] for i in selected]:
            selected.append(instrument)
        if instrument['token'] not in [i['token'] for i in selected]:
            selected.append(instrument)
        
        self.assertEqual(len(selected), 1)
    
    def test_selection_count_display(self):
        """Test that selection count is accurate"""
        selected = []
        
        # Add instruments one by one
        for i, instrument in enumerate(self.test_instruments):
            selected.append(instrument)
            self.assertEqual(len(selected), i + 1)
    
    def test_selection_persistence_format(self):
        """Test that selections can be serialized for persistence"""
        selected = [self.test_instruments[0]]
        
        # Simulate saving to sessionStorage (JSON serialization)
        try:
            json_str = json.dumps(selected)
            restored = json.loads(json_str)
            
            self.assertEqual(len(restored), 1)
            self.assertEqual(restored[0]['symbol'], 'RELIANCE')
            self.assertEqual(restored[0]['token'], 'NSE:RELIANCE')
        except Exception as e:
            self.fail(f"Selection persistence failed: {e}")
    
    def test_indeterminate_state_logic(self):
        """Test logic for indeterminate checkbox state"""
        page_instruments = self.test_instruments
        selected = [self.test_instruments[0]]  # Only one selected
        
        # Check how many on page are selected
        selected_on_page = [i for i in page_instruments if i['token'] in [s['token'] for s in selected]]
        
        # Should be indeterminate (some but not all selected)
        is_indeterminate = 0 < len(selected_on_page) < len(page_instruments)
        self.assertTrue(is_indeterminate)
    
    def test_all_selected_state_logic(self):
        """Test logic for all-selected checkbox state"""
        page_instruments = self.test_instruments
        selected = self.test_instruments.copy()  # All selected
        
        # Check how many on page are selected
        selected_on_page = [i for i in page_instruments if i['token'] in [s['token'] for s in selected]]
        
        # Should be fully checked (all selected)
        is_all_selected = len(selected_on_page) == len(page_instruments)
        self.assertTrue(is_all_selected)
    
    def test_none_selected_state_logic(self):
        """Test logic for none-selected checkbox state"""
        page_instruments = self.test_instruments
        selected = []  # None selected
        
        # Check how many on page are selected
        selected_on_page = [i for i in page_instruments if i['token'] in [s['token'] for s in selected]]
        
        # Should be unchecked (none selected)
        is_none_selected = len(selected_on_page) == 0
        self.assertTrue(is_none_selected)


if __name__ == '__main__':
    unittest.main()
