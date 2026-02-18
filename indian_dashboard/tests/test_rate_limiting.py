"""
Tests for Rate Limiting
"""

import pytest
import time
from flask import Flask
from indian_dashboard.rate_limiter import (
    init_rate_limiter,
    get_rate_limit_key,
    rate_limit_exceeded_handler,
    AUTH_RATE_LIMIT,
    READ_RATE_LIMIT,
    WRITE_RATE_LIMIT,
    STATUS_RATE_LIMIT,
    EXPENSIVE_RATE_LIMIT
)


class TestRateLimiterInitialization:
    """Test rate limiter initialization"""
    
    def test_init_rate_limiter_default_storage(self):
        """Test rate limiter initialization with default storage"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        limiter = init_rate_limiter(app)
        
        assert limiter is not None
        assert hasattr(limiter, 'limit')
    
    def test_init_rate_limiter_custom_storage(self):
        """Test rate limiter initialization with custom storage"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        limiter = init_rate_limiter(app, storage_uri="memory://")
        
        assert limiter is not None
    
    def test_rate_limit_error_handler_registered(self):
        """Test that 429 error handler is registered"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        init_rate_limiter(app)
        
        # Check that 429 handler is registered
        assert 429 in app.error_handler_spec[None]


class TestRateLimitConstants:
    """Test rate limit constant values"""
    
    def test_auth_rate_limit(self):
        """Test AUTH_RATE_LIMIT is strict"""
        assert AUTH_RATE_LIMIT == "5 per minute"
    
    def test_write_rate_limit(self):
        """Test WRITE_RATE_LIMIT is moderate"""
        assert WRITE_RATE_LIMIT == "30 per minute"
    
    def test_read_rate_limit(self):
        """Test READ_RATE_LIMIT is relaxed"""
        assert READ_RATE_LIMIT == "100 per minute"
    
    def test_status_rate_limit(self):
        """Test STATUS_RATE_LIMIT is very relaxed"""
        assert STATUS_RATE_LIMIT == "200 per minute"
    
    def test_expensive_rate_limit(self):
        """Test EXPENSIVE_RATE_LIMIT is very strict"""
        assert EXPENSIVE_RATE_LIMIT == "3 per minute"


class TestRateLimitKeyGeneration:
    """Test rate limit key generation"""
    
    def test_get_rate_limit_key_with_session(self):
        """Test key generation with session ID"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.secret_key = 'test-secret'
        
        with app.test_request_context():
            from flask import session
            session['session_id'] = 'test-session-123'
            
            key = get_rate_limit_key()
            
            assert key == "session:test-session-123"
    
    def test_get_rate_limit_key_without_session(self):
        """Test key generation without session (falls back to IP)"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            key = get_rate_limit_key()
            
            assert key.startswith("ip:")


class TestRateLimitErrorHandler:
    """Test rate limit error handler"""
    
    def test_rate_limit_exceeded_handler_response(self):
        """Test error handler returns correct response"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        with app.test_request_context():
            # Create a mock exception
            class MockException:
                description = "Rate limit exceeded"
            
            response, status_code = rate_limit_exceeded_handler(MockException())
            
            assert status_code == 429
            assert response.json['status'] == 'error'
            assert response.json['error'] == 'rate_limit_exceeded'
            assert 'message' in response.json


class TestRateLimitIntegration:
    """Integration tests for rate limiting"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app with rate limiting"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.secret_key = 'test-secret'
        
        # Initialize rate limiter
        limiter = init_rate_limiter(app)
        
        # Create test routes with different rate limits
        @app.route('/auth')
        @limiter.limit(AUTH_RATE_LIMIT)
        def auth_endpoint():
            return {'success': True}, 200
        
        @app.route('/read')
        @limiter.limit(READ_RATE_LIMIT)
        def read_endpoint():
            return {'success': True}, 200
        
        @app.route('/write', methods=['POST'])
        @limiter.limit(WRITE_RATE_LIMIT)
        def write_endpoint():
            return {'success': True}, 200
        
        @app.route('/expensive', methods=['POST'])
        @limiter.limit(EXPENSIVE_RATE_LIMIT)
        def expensive_endpoint():
            return {'success': True}, 200
        
        return app
    
    def test_auth_endpoint_rate_limit(self, app):
        """Test auth endpoint respects rate limit (5 per minute)"""
        client = app.test_client()
        
        # First 5 requests should succeed
        for i in range(5):
            response = client.get('/auth')
            assert response.status_code == 200
        
        # 6th request should be rate limited
        response = client.get('/auth')
        assert response.status_code == 429
        assert response.json['error'] == 'rate_limit_exceeded'
    
    def test_read_endpoint_allows_many_requests(self, app):
        """Test read endpoint allows many requests"""
        client = app.test_client()
        
        # Should allow at least 50 requests
        for i in range(50):
            response = client.get('/read')
            assert response.status_code == 200
    
    def test_expensive_endpoint_strict_limit(self, app):
        """Test expensive endpoint has strict limit (3 per minute)"""
        client = app.test_client()
        
        # First 3 requests should succeed
        for i in range(3):
            response = client.post('/expensive')
            assert response.status_code == 200
        
        # 4th request should be rate limited
        response = client.post('/expensive')
        assert response.status_code == 429
    
    def test_rate_limit_headers_present(self, app):
        """Test rate limit headers are added to responses"""
        client = app.test_client()
        
        response = client.get('/read')
        
        # Check for rate limit headers
        assert 'X-RateLimit-Limit' in response.headers or 'RateLimit-Limit' in response.headers
    
    def test_different_endpoints_independent_limits(self, app):
        """Test different endpoints have independent rate limits"""
        client = app.test_client()
        
        # Exhaust auth endpoint
        for i in range(5):
            client.get('/auth')
        
        # Auth should be limited
        response = client.get('/auth')
        assert response.status_code == 429
        
        # But read endpoint should still work
        response = client.get('/read')
        assert response.status_code == 200


class TestRateLimitErrorMessages:
    """Test rate limit error messages"""
    
    def test_error_message_user_friendly(self):
        """Test error message is user-friendly"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        with app.test_request_context():
            class MockException:
                description = None
            
            response, _ = rate_limit_exceeded_handler(MockException())
            
            assert 'Too many requests' in response.json['message']
            assert 'slow down' in response.json['message'].lower()
    
    def test_error_includes_retry_info(self):
        """Test error includes retry information"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        with app.test_request_context():
            class MockException:
                description = "60 seconds"
            
            response, _ = rate_limit_exceeded_handler(MockException())
            
            assert 'retry_after' in response.json


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
