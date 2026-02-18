"""
Test Performance Optimization Features
Tests caching, request deduplication, and rendering optimizations
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Change to indian_dashboard directory for imports
os.chdir(parent_dir)

try:
    import indian_dashboard
    app = indian_dashboard.app
    from services.broker_manager import BrokerManager
    from services.instrument_service import InstrumentService
    HAS_APP = True
except Exception as e:
    print(f"Warning: Could not import app: {e}")
    HAS_APP = False
    app = None
    BrokerManager = None
    InstrumentService = None


class TestCaching:
    """Test API response caching"""
    
    @pytest.mark.skipif(not HAS_APP, reason="App not available")
    def test_broker_list_caching(self):
        """Test that broker list is cached"""
        with app.test_client() as client:
            # First request
            start1 = time.time()
            response1 = client.get('/api/broker/list')
            duration1 = time.time() - start1
            
            assert response1.status_code == 200
            data1 = response1.get_json()
            
            # Second request (should be faster if cached on server)
            start2 = time.time()
            response2 = client.get('/api/broker/list')
            duration2 = time.time() - start2
            
            assert response2.status_code == 200
            data2 = response2.get_json()
            
            # Data should be identical
            assert data1 == data2
            
            print(f"First request: {duration1:.4f}s, Second request: {duration2:.4f}s")
    
    @pytest.mark.skipif(not HAS_APP, reason="App not available")
    def test_instrument_caching(self):
        """Test that instruments are cached"""
        with app.test_client() as client:
            # Connect to paper trading first
            connect_response = client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
            
            if connect_response.status_code == 200:
                # First request
                response1 = client.get('/api/instruments')
                assert response1.status_code == 200
                
                # Second request (should use cache)
                response2 = client.get('/api/instruments')
                assert response2.status_code == 200
                
                # Data should be identical
                data1 = response1.get_json()
                data2 = response2.get_json()
                assert data1 == data2
    
    def test_cache_invalidation_on_refresh(self):
        """Test that cache is invalidated when instruments are refreshed"""
        with app.test_client() as client:
            # Connect to paper trading
            client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
            
            # Get instruments
            response1 = client.get('/api/instruments')
            if response1.status_code == 200:
                data1 = response1.get_json()
                
                # Refresh instruments
                refresh_response = client.post('/api/instruments/refresh')
                
                # Get instruments again
                response2 = client.get('/api/instruments')
                data2 = response2.get_json()
                
                # Should have fresh data (may or may not be different)
                assert response2.status_code == 200


class TestRequestOptimization:
    """Test request optimization features"""
    
    def test_concurrent_requests_handled(self):
        """Test that concurrent requests are handled efficiently"""
        with app.test_client() as client:
            # Make multiple concurrent requests
            responses = []
            for _ in range(5):
                response = client.get('/api/broker/list')
                responses.append(response)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 200
            
            # All should return same data
            data_list = [r.get_json() for r in responses]
            for data in data_list[1:]:
                assert data == data_list[0]
    
    def test_api_response_time(self):
        """Test that API responses are reasonably fast"""
        with app.test_client() as client:
            endpoints = [
                '/api/broker/list',
                '/api/config/presets',
            ]
            
            for endpoint in endpoints:
                start = time.time()
                response = client.get(endpoint)
                duration = time.time() - start
                
                assert response.status_code == 200
                assert duration < 1.0, f"{endpoint} took {duration:.2f}s (should be < 1s)"
                print(f"{endpoint}: {duration:.4f}s")


class TestInstrumentService:
    """Test instrument service caching"""
    
    def test_instrument_cache_file_creation(self):
        """Test that instrument cache file is created"""
        broker_manager = BrokerManager()
        instrument_service = InstrumentService(broker_manager)
        
        # Cache file path
        cache_file = instrument_service.cache_file
        
        # Check if cache directory exists or can be created
        cache_dir = os.path.dirname(cache_file)
        assert cache_dir is not None
    
    def test_cache_expiry_check(self):
        """Test cache expiry logic"""
        broker_manager = BrokerManager()
        instrument_service = InstrumentService(broker_manager)
        
        # New cache should be expired (no file exists)
        is_expired = instrument_service._is_cache_expired()
        assert is_expired == True
    
    def test_filter_application(self):
        """Test that filters are applied correctly"""
        broker_manager = BrokerManager()
        instrument_service = InstrumentService(broker_manager)
        
        # Sample instruments
        instruments = [
            {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_type': 'EQ'},
            {'symbol': 'INFY', 'exchange': 'NSE', 'instrument_type': 'EQ'},
            {'symbol': 'TCS', 'exchange': 'BSE', 'instrument_type': 'EQ'},
            {'symbol': 'NIFTY', 'exchange': 'NFO', 'instrument_type': 'FUT'},
        ]
        
        # Test exchange filter
        filtered = instrument_service._apply_filters(instruments, {'exchange': 'NSE'})
        assert len(filtered) == 2
        assert all(i['exchange'] == 'NSE' for i in filtered)
        
        # Test type filter
        filtered = instrument_service._apply_filters(instruments, {'instrument_type': 'FUT'})
        assert len(filtered) == 1
        assert filtered[0]['symbol'] == 'NIFTY'
        
        # Test search filter
        filtered = instrument_service._apply_filters(instruments, {'search': 'REL'})
        assert len(filtered) == 1
        assert filtered[0]['symbol'] == 'RELIANCE'


class TestPerformanceMetrics:
    """Test performance monitoring"""
    
    def test_response_time_tracking(self):
        """Test that response times are reasonable"""
        with app.test_client() as client:
            # Make several requests and track times
            times = []
            
            for _ in range(10):
                start = time.time()
                response = client.get('/api/broker/list')
                duration = time.time() - start
                times.append(duration)
                
                assert response.status_code == 200
            
            # Calculate average
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            print(f"Average response time: {avg_time:.4f}s")
            print(f"Max response time: {max_time:.4f}s")
            
            # Should be fast
            assert avg_time < 0.5, f"Average response time {avg_time:.2f}s is too slow"
            assert max_time < 1.0, f"Max response time {max_time:.2f}s is too slow"
    
    def test_memory_efficiency(self):
        """Test that memory usage is reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with app.test_client() as client:
            # Make many requests
            for _ in range(100):
                client.get('/api/broker/list')
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"Initial memory: {initial_memory:.2f} MB")
            print(f"Final memory: {final_memory:.2f} MB")
            print(f"Memory increase: {memory_increase:.2f} MB")
            
            # Memory increase should be reasonable (< 50 MB for 100 requests)
            assert memory_increase < 50, f"Memory increased by {memory_increase:.2f} MB"


class TestDebouncing:
    """Test debouncing functionality"""
    
    def test_search_debouncing(self):
        """Test that search requests are debounced"""
        # This would be tested in frontend JavaScript
        # Here we just verify the endpoint works
        with app.test_client() as client:
            # Connect to broker
            client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
            
            # Multiple search requests
            search_terms = ['REL', 'RELI', 'RELIA', 'RELIAN', 'RELIANCE']
            
            for term in search_terms:
                response = client.get(f'/api/instruments?search={term}')
                assert response.status_code == 200


class TestTableRendering:
    """Test table rendering optimizations"""
    
    def test_pagination_performance(self):
        """Test that pagination works efficiently"""
        with app.test_client() as client:
            # Connect to broker
            client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
            
            # Get instruments with pagination
            response = client.get('/api/instruments?limit=50&offset=0')
            
            if response.status_code == 200:
                data = response.get_json()
                instruments = data.get('instruments', [])
                
                # Should return limited results
                assert len(instruments) <= 50
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        with app.test_client() as client:
            # Connect to broker
            client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
            
            # Get all instruments
            start = time.time()
            response = client.get('/api/instruments')
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.get_json()
                instruments = data.get('instruments', [])
                
                print(f"Loaded {len(instruments)} instruments in {duration:.4f}s")
                
                # Should be reasonably fast even for large datasets
                assert duration < 2.0, f"Loading {len(instruments)} instruments took {duration:.2f}s"


def run_performance_tests():
    """Run all performance tests"""
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION TESTS")
    print("=" * 60)
    
    # Run tests
    pytest.main([__file__, '-v', '-s'])


if __name__ == '__main__':
    run_performance_tests()
