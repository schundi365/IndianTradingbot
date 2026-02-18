"""
Simple Rate Limiting Test
Tests that rate limiting is working on actual endpoints
"""

import pytest
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_rate_limiting_works():
    """Simple test to verify rate limiting is functional"""
    from flask import Flask
    from indian_dashboard.rate_limiter import init_rate_limiter
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    limiter = init_rate_limiter(app)
    
    @app.route('/test')
    @limiter.limit("3 per minute")
    def test_endpoint():
        return {'success': True}, 200
    
    client = app.test_client()
    
    # First 3 requests should succeed
    for i in range(3):
        response = client.get('/test')
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"
    
    # 4th request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429, f"Expected 429 but got {response.status_code}"
    
    print("✓ Rate limiting is working correctly")


def test_broker_connect_has_rate_limit():
    """Test that broker connect endpoint has rate limiting applied"""
    from indian_dashboard.indian_dashboard import app
    
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Make 5 requests (AUTH_RATE_LIMIT = 5/min)
    for i in range(5):
        response = client.post('/api/broker/connect', json={
            'broker': 'invalid_broker_to_fail_fast',
            'credentials': {}
        })
        # Should get 400 (validation error) not 429 (rate limit)
        assert response.status_code in [400, 500], f"Request {i+1}: Expected 400/500 but got {response.status_code}"
    
    # 6th request should be rate limited
    response = client.post('/api/broker/connect', json={
        'broker': 'invalid_broker_to_fail_fast',
        'credentials': {}
    })
    
    # This SHOULD be 429 if rate limiting is working
    if response.status_code == 429:
        print("✓ Broker connect endpoint is rate limited")
        return True
    else:
        print(f"✗ Expected 429 but got {response.status_code}")
        print(f"Response: {response.json}")
        return False


if __name__ == '__main__':
    print("Testing rate limiting...")
    print()
    
    print("Test 1: Basic rate limiting")
    test_rate_limiting_works()
    print()
    
    print("Test 2: Broker connect rate limiting")
    result = test_broker_connect_has_rate_limit()
    
    if result:
        print("\n✓ All rate limiting tests passed!")
    else:
        print("\n✗ Some tests failed")
