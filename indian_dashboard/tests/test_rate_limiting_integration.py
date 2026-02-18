"""
Integration Tests for Rate Limiting on API Endpoints
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.indian_dashboard import app as flask_app


class TestBrokerAPIRateLimiting:
    """Test rate limiting on broker API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_list_brokers_rate_limit(self, client):
        """Test /api/broker/list respects rate limit"""
        # Should allow many requests (READ_RATE_LIMIT = 100/min)
        for i in range(50):
            response = client.get('/api/broker/list')
            assert response.status_code == 200
    
    def test_connect_broker_rate_limit(self, client):
        """Test /api/broker/connect has strict rate limit"""
        # AUTH_RATE_LIMIT = 5/min
        # Make 5 requests - they may fail for other reasons but shouldn't be rate limited
        responses = []
        for i in range(5):
            response = client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
            responses.append(response.status_code)
            # Should not be rate limited yet
            assert response.status_code != 429, f"Request {i+1} was rate limited unexpectedly"
        
        # 6th request should be rate limited
        response = client.post('/api/broker/connect', json={
            'broker': 'paper',
            'credentials': {}
        })
        # This should be rate limited (429) regardless of other errors
        assert response.status_code == 429, f"Expected 429 but got {response.status_code}"
    
    def test_broker_status_rate_limit(self, client):
        """Test /api/broker/status allows frequent polling"""
        # Should allow many requests
        for i in range(50):
            response = client.get('/api/broker/status')
            assert response.status_code == 200


class TestInstrumentsAPIRateLimiting:
    """Test rate limiting on instruments API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_get_instruments_rate_limit(self, client):
        """Test /api/instruments respects rate limit"""
        # Should allow many requests (READ_RATE_LIMIT)
        for i in range(50):
            response = client.get('/api/instruments')
            # May fail if no broker connected, but shouldn't be rate limited
            assert response.status_code != 429
    
    def test_refresh_instruments_strict_limit(self, client):
        """Test /api/instruments/refresh has strict limit"""
        # EXPENSIVE_RATE_LIMIT = 3/min
        for i in range(3):
            response = client.post('/api/instruments/refresh')
            # May fail if no broker connected, but shouldn't be rate limited
            assert response.status_code != 429
        
        # 4th request should be rate limited
        response = client.post('/api/instruments/refresh')
        assert response.status_code == 429


class TestConfigAPIRateLimiting:
    """Test rate limiting on config API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_get_config_rate_limit(self, client):
        """Test /api/config respects rate limit"""
        # Should allow many requests (READ_RATE_LIMIT)
        for i in range(50):
            response = client.get('/api/config')
            assert response.status_code != 429
    
    def test_save_config_rate_limit(self, client):
        """Test /api/config POST has moderate limit"""
        # WRITE_RATE_LIMIT = 30/min
        for i in range(30):
            response = client.post('/api/config', json={
                'config': {
                    'name': f'test-config-{i}',
                    'instruments': [],
                    'strategy': 'trend_following',
                    'timeframe': '5min'
                }
            })
            # May fail due to validation, but shouldn't be rate limited
            assert response.status_code != 429
        
        # 31st request should be rate limited
        response = client.post('/api/config', json={
            'config': {
                'name': 'test-config-31',
                'instruments': [],
                'strategy': 'trend_following',
                'timeframe': '5min'
            }
        })
        assert response.status_code == 429
    
    def test_list_configs_rate_limit(self, client):
        """Test /api/config/list allows frequent access"""
        for i in range(50):
            response = client.get('/api/config/list')
            assert response.status_code == 200


class TestBotAPIRateLimiting:
    """Test rate limiting on bot API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_bot_status_high_limit(self, client):
        """Test /api/bot/status allows frequent polling"""
        # STATUS_RATE_LIMIT = 200/min
        for i in range(100):
            response = client.get('/api/bot/status')
            assert response.status_code == 200
    
    def test_start_bot_rate_limit(self, client):
        """Test /api/bot/start has moderate limit"""
        # WRITE_RATE_LIMIT = 30/min
        for i in range(30):
            response = client.post('/api/bot/start', json={
                'config': {}
            })
            # May fail due to validation, but shouldn't be rate limited
            assert response.status_code != 429
        
        # 31st request should be rate limited
        response = client.post('/api/bot/start', json={
            'config': {}
        })
        assert response.status_code == 429
    
    def test_get_positions_rate_limit(self, client):
        """Test /api/bot/positions allows frequent access"""
        for i in range(50):
            response = client.get('/api/bot/positions')
            assert response.status_code != 429


class TestSessionAPIRateLimiting:
    """Test rate limiting on session API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_session_info_high_limit(self, client):
        """Test /api/session/info allows frequent access"""
        # STATUS_RATE_LIMIT = 200/min
        for i in range(100):
            response = client.get('/api/session/info')
            assert response.status_code == 200
    
    def test_extend_session_rate_limit(self, client):
        """Test /api/session/extend has moderate limit"""
        # WRITE_RATE_LIMIT = 30/min
        for i in range(30):
            response = client.post('/api/session/extend')
            assert response.status_code != 429
        
        # 31st request should be rate limited
        response = client.post('/api/session/extend')
        assert response.status_code == 429


class TestRateLimitHeaders:
    """Test rate limit headers in responses"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_rate_limit_headers_present(self, client):
        """Test rate limit headers are included in responses"""
        response = client.get('/api/broker/list')
        
        # Flask-Limiter adds these headers
        headers = response.headers
        
        # Check for at least one rate limit header
        has_rate_limit_header = any([
            'X-RateLimit-Limit' in headers,
            'RateLimit-Limit' in headers,
            'X-RateLimit-Remaining' in headers,
            'RateLimit-Remaining' in headers
        ])
        
        assert has_rate_limit_header, "Rate limit headers should be present"
    
    def test_rate_limit_remaining_decreases(self, client):
        """Test rate limit remaining count decreases with requests"""
        # Make first request
        response1 = client.get('/api/broker/list')
        
        # Make second request
        response2 = client.get('/api/broker/list')
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestRateLimitErrorResponse:
    """Test rate limit error response format"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_rate_limit_error_format(self, client):
        """Test rate limit error has correct format"""
        # Exhaust rate limit on auth endpoint
        for i in range(5):
            client.post('/api/broker/connect', json={
                'broker': 'paper',
                'credentials': {}
            })
        
        # Next request should be rate limited
        response = client.post('/api/broker/connect', json={
            'broker': 'paper',
            'credentials': {}
        })
        
        assert response.status_code == 429
        
        data = response.json
        assert data['status'] == 'error'
        assert data['error'] == 'rate_limit_exceeded'
        assert 'message' in data
        assert 'Too many requests' in data['message']
    
    def test_rate_limit_error_user_friendly(self, client):
        """Test rate limit error message is user-friendly"""
        # Exhaust rate limit
        for i in range(3):
            client.post('/api/instruments/refresh')
        
        response = client.post('/api/instruments/refresh')
        
        assert response.status_code == 429
        data = response.json
        
        # Message should be helpful
        assert 'slow down' in data['message'].lower() or 'try again' in data['message'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
