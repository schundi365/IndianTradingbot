"""
Integration test for refresh instruments functionality
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.instrument_service import InstrumentService


class TestRefreshInstruments:
    """Test refresh instruments functionality"""
    
    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create temporary cache directory"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir
    
    @pytest.fixture
    def instrument_service(self, temp_cache_dir):
        """Create instrument service with temp cache"""
        return InstrumentService(temp_cache_dir, cache_ttl=3600)
    
    @pytest.fixture
    def mock_broker_adapter(self):
        """Create mock broker adapter"""
        adapter = Mock()
        adapter.get_instruments.return_value = [
            {
                'instrument_token': 123,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'segment': 'NSE',
                'lot_size': 1,
                'tick_size': 0.05
            },
            {
                'instrument_token': 456,
                'tradingsymbol': 'TCS',
                'name': 'Tata Consultancy Services Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'segment': 'NSE',
                'lot_size': 1,
                'tick_size': 0.05
            }
        ]
        return adapter
    
    def test_refresh_creates_cache(self, instrument_service, mock_broker_adapter):
        """Test that refresh creates cache file"""
        # Refresh instruments
        instruments = instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        
        # Verify cache file exists
        cache_file = instrument_service.get_cache_file('kite')
        assert cache_file.exists()
        
        # Verify instruments returned
        assert len(instruments) == 2
        assert instruments[0]['symbol'] == 'RELIANCE'
        assert instruments[1]['symbol'] == 'TCS'
    
    def test_refresh_updates_cache_timestamp(self, instrument_service, mock_broker_adapter):
        """Test that refresh updates cache timestamp"""
        # Create initial cache
        instruments = instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        cache_file = instrument_service.get_cache_file('kite')
        initial_mtime = cache_file.stat().st_mtime
        
        # Wait a bit
        time.sleep(0.1)
        
        # Refresh again
        instruments = instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        new_mtime = cache_file.stat().st_mtime
        
        # Verify timestamp updated
        assert new_mtime > initial_mtime
    
    def test_get_cache_info_returns_correct_data(self, instrument_service, mock_broker_adapter):
        """Test that get_cache_info returns correct information"""
        # Create cache
        instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        
        # Get cache info
        cache_info = instrument_service.get_cache_info('kite')
        
        # Verify cache info
        assert cache_info['exists'] is True
        assert cache_info['valid'] is True
        assert cache_info['timestamp'] is not None
        assert cache_info['age_seconds'] >= 0
        assert cache_info['count'] == 2
    
    def test_cache_info_for_nonexistent_cache(self, instrument_service):
        """Test cache info when cache doesn't exist"""
        cache_info = instrument_service.get_cache_info('nonexistent')
        
        assert cache_info['exists'] is False
        assert cache_info['valid'] is False
        assert cache_info['timestamp'] is None
        assert cache_info['age_seconds'] is None
        assert cache_info['count'] == 0
    
    def test_cache_expiry_detection(self, temp_cache_dir, mock_broker_adapter):
        """Test that expired cache is detected"""
        # Create service with short TTL
        service = InstrumentService(temp_cache_dir, cache_ttl=1)
        
        # Create cache
        service.refresh_instruments(mock_broker_adapter, 'kite')
        
        # Verify cache is valid
        assert service.is_cache_valid('kite') is True
        
        # Wait for expiry
        time.sleep(1.5)
        
        # Verify cache is expired
        assert service.is_cache_valid('kite') is False
        
        # Get cache info
        cache_info = service.get_cache_info('kite')
        assert cache_info['exists'] is True
        assert cache_info['valid'] is False
    
    def test_refresh_forces_broker_fetch(self, instrument_service, mock_broker_adapter):
        """Test that refresh always fetches from broker"""
        # Create initial cache
        instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        
        # Verify broker was called once
        assert mock_broker_adapter.get_instruments.call_count == 1
        
        # Get instruments (should use cache)
        instrument_service.get_instruments(mock_broker_adapter, 'kite', force_refresh=False)
        
        # Verify broker was not called again
        assert mock_broker_adapter.get_instruments.call_count == 1
        
        # Refresh (should call broker)
        instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        
        # Verify broker was called again
        assert mock_broker_adapter.get_instruments.call_count == 2
    
    def test_cache_info_age_calculation(self, instrument_service, mock_broker_adapter):
        """Test that cache age is calculated correctly"""
        # Create cache
        instrument_service.refresh_instruments(mock_broker_adapter, 'kite')
        
        # Get cache info immediately
        cache_info = instrument_service.get_cache_info('kite')
        
        # Age should be very small (less than 1 second)
        assert cache_info['age_seconds'] < 1
        
        # Wait a bit
        time.sleep(1)
        
        # Get cache info again
        cache_info = instrument_service.get_cache_info('kite')
        
        # Age should be at least 1 second
        assert cache_info['age_seconds'] >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
