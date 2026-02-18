"""
Unit tests for InstrumentService
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
from unittest.mock import Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.instrument_service import InstrumentService


class TestInstrumentService:
    """Test InstrumentService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for cache
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = InstrumentService(self.temp_dir, cache_ttl=3600)
        
        # Sample instruments
        self.sample_instruments = [
            {
                'instrument_token': 256265,
                'tradingsymbol': 'NIFTY24JANFUT',
                'name': 'NIFTY',
                'exchange': 'NFO',
                'instrument_type': 'FUT',
                'segment': 'NFO-FUT',
                'expiry': '2024-01-25',
                'strike': 0,
                'lot_size': 50,
                'tick_size': 0.05
            },
            {
                'instrument_token': 738561,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'segment': 'NSE',
                'expiry': '',
                'strike': 0,
                'lot_size': 1,
                'tick_size': 0.05
            }
        ]
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_cache(self):
        """Test saving and loading from cache"""
        broker = 'test_broker'
        
        # Save to cache
        success = self.service.save_to_cache(broker, self.sample_instruments)
        assert success is True
        
        # Load from cache
        loaded = self.service.load_from_cache(broker)
        assert loaded == self.sample_instruments
    
    def test_is_cache_valid(self):
        """Test cache validity check"""
        broker = 'test_broker'
        
        # No cache initially
        assert self.service.is_cache_valid(broker) is False
        
        # Save cache
        self.service.save_to_cache(broker, self.sample_instruments)
        
        # Should be valid now
        assert self.service.is_cache_valid(broker) is True
    
    def test_get_instruments_with_cache(self):
        """Test getting instruments with valid cache"""
        broker = 'test_broker'
        
        # Save to cache
        self.service.save_to_cache(broker, self.sample_instruments)
        
        # Mock adapter (should not be called)
        mock_adapter = Mock()
        
        # Get instruments (should use cache)
        instruments = self.service.get_instruments(mock_adapter, broker, force_refresh=False)
        
        assert instruments == self.sample_instruments
        mock_adapter.get_instruments.assert_not_called()
    
    def test_get_instruments_force_refresh(self):
        """Test forcing refresh from broker"""
        broker = 'test_broker'
        
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.get_instruments.return_value = self.sample_instruments
        
        # Get instruments with force refresh
        instruments = self.service.get_instruments(mock_adapter, broker, force_refresh=True)
        
        assert len(instruments) == 2
        mock_adapter.get_instruments.assert_called_once()
    
    def test_search_instruments(self):
        """Test searching instruments"""
        # Search by symbol
        results = self.service.search_instruments(self.sample_instruments, 'NIFTY')
        assert len(results) == 1
        assert results[0]['tradingsymbol'] == 'NIFTY24JANFUT'
        
        # Search by name
        results = self.service.search_instruments(self.sample_instruments, 'Reliance')
        assert len(results) == 1
        assert results[0]['tradingsymbol'] == 'RELIANCE'
        
        # No match
        results = self.service.search_instruments(self.sample_instruments, 'NOTFOUND')
        assert len(results) == 0
        
        # Empty query returns all
        results = self.service.search_instruments(self.sample_instruments, '')
        assert len(results) == 2
    
    def test_filter_instruments_by_exchange(self):
        """Test filtering by exchange"""
        filters = {'exchange': ['NSE']}
        results = self.service.filter_instruments(self.sample_instruments, filters)
        
        assert len(results) == 1
        assert results[0]['exchange'] == 'NSE'
    
    def test_filter_instruments_by_type(self):
        """Test filtering by instrument type"""
        filters = {'instrument_type': ['FUT']}
        results = self.service.filter_instruments(self.sample_instruments, filters)
        
        assert len(results) == 1
        assert results[0]['instrument_type'] == 'FUT'
    
    def test_filter_instruments_multiple(self):
        """Test filtering with multiple criteria"""
        filters = {
            'exchange': ['NFO'],
            'instrument_type': ['FUT']
        }
        results = self.service.filter_instruments(self.sample_instruments, filters)
        
        assert len(results) == 1
        assert results[0]['tradingsymbol'] == 'NIFTY24JANFUT'
    
    def test_get_instrument_by_token(self):
        """Test getting instrument by token"""
        # Found
        inst = self.service.get_instrument_by_token(self.sample_instruments, 256265)
        assert inst is not None
        assert inst['tradingsymbol'] == 'NIFTY24JANFUT'
        
        # Not found
        inst = self.service.get_instrument_by_token(self.sample_instruments, 999999)
        assert inst is None
    
    def test_get_instrument_by_symbol(self):
        """Test getting instrument by symbol"""
        # Found
        inst = self.service.get_instrument_by_symbol(self.sample_instruments, 'RELIANCE')
        assert inst is not None
        assert inst['exchange'] == 'NSE'
        
        # With exchange filter
        inst = self.service.get_instrument_by_symbol(self.sample_instruments, 'RELIANCE', 'NSE')
        assert inst is not None
        
        # Not found
        inst = self.service.get_instrument_by_symbol(self.sample_instruments, 'NOTFOUND')
        assert inst is None
    
    def test_get_cache_info(self):
        """Test getting cache information"""
        broker = 'test_broker'
        
        # No cache
        info = self.service.get_cache_info(broker)
        assert info['exists'] is False
        assert info['valid'] is False
        
        # With cache
        self.service.save_to_cache(broker, self.sample_instruments)
        info = self.service.get_cache_info(broker)
        
        assert info['exists'] is True
        assert info['valid'] is True
        assert info['count'] == 2
        assert info['timestamp'] is not None
        assert info['age_seconds'] is not None
