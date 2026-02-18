"""
Integration tests for API input validation

Tests that all API endpoints properly validate and sanitize inputs
to prevent XSS attacks and ensure data integrity.
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.indian_dashboard import create_app


@pytest.fixture
def app():
    """Create test Flask app"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestBrokerAPIValidation:
    """Test broker API input validation"""
    
    def test_connect_missing_broker(self, client):
        """Test connect endpoint - missing broker field"""
        response = client.post('/api/broker/connect',
                              json={'credentials': {}},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'broker' in data['error'].lower()
    
    def test_connect_invalid_broker(self, client):
        """Test connect endpoint - invalid broker type"""
        response = client.post('/api/broker/connect',
                              json={'broker': 'invalid_broker', 'credentials': {}},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_connect_xss_in_broker(self, client):
        """Test connect endpoint - XSS attempt in broker field"""
        response = client.post('/api/broker/connect',
                              json={'broker': '<script>alert(1)</script>', 'credentials': {}},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        # Should not contain unescaped script tags
        assert '<script>' not in str(data)
    
    def test_connect_invalid_json(self, client):
        """Test connect endpoint - invalid JSON"""
        response = client.post('/api/broker/connect',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'json' in data['error'].lower()
    
    def test_connect_missing_credentials(self, client):
        """Test connect endpoint - missing credentials"""
        response = client.post('/api/broker/connect',
                              json={'broker': 'kite'},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_credentials_form_invalid_broker(self, client):
        """Test credentials form endpoint - invalid broker"""
        response = client.get('/api/broker/credentials-form/invalid_broker')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_credentials_form_xss_attempt(self, client):
        """Test credentials form endpoint - XSS attempt"""
        response = client.get('/api/broker/credentials-form/<script>alert(1)</script>')
        assert response.status_code == 400
    
    def test_oauth_initiate_missing_broker(self, client):
        """Test OAuth initiate - missing broker"""
        response = client.post('/api/broker/oauth/initiate',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestInstrumentsAPIValidation:
    """Test instruments API input validation"""
    
    def test_get_instruments_xss_in_search(self, client):
        """Test get instruments - XSS in search parameter"""
        response = client.get('/api/instruments?search=<script>alert(1)</script>')
        # Should not fail, but search should be sanitized
        # Note: Will fail if broker not connected, but validation should happen first
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = json.loads(response.data)
            # Ensure no unescaped script tags in response
            assert '<script>' not in str(data)
    
    def test_get_instruments_long_search(self, client):
        """Test get instruments - excessively long search query"""
        long_query = 'a' * 1000
        response = client.get(f'/api/instruments?search={long_query}')
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_get_instrument_by_token_invalid(self, client):
        """Test get instrument by token - invalid token"""
        response = client.get('/api/instruments/abc')
        assert response.status_code == 404  # Flask converts invalid int to 404
    
    def test_get_instrument_by_token_negative(self, client):
        """Test get instrument by token - negative token"""
        response = client.get('/api/instruments/-1')
        # Should be rejected or handled gracefully
        assert response.status_code in [400, 404]
    
    def test_get_quote_xss_in_symbol(self, client):
        """Test get quote - XSS in symbol"""
        response = client.get('/api/instruments/quote/<script>alert(1)</script>')
        assert response.status_code in [400, 404]


class TestConfigAPIValidation:
    """Test config API input validation"""
    
    def test_save_config_missing_config(self, client):
        """Test save config - missing config field"""
        response = client.post('/api/config',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'config' in data['error'].lower()
    
    def test_save_config_invalid_config(self, client):
        """Test save config - invalid configuration"""
        response = client.post('/api/config',
                              json={'config': {'invalid': 'data'}},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_save_config_xss_in_name(self, client):
        """Test save config - XSS in name field"""
        config = {
            'broker': 'paper',
            'instruments': [{'symbol': 'TEST'}],
            'strategy': 'test',
            'timeframe': '1min'
        }
        response = client.post('/api/config',
                              json={'config': config, 'name': '<script>alert(1)</script>'},
                              content_type='application/json')
        # Should either reject or sanitize
        if response.status_code == 200:
            data = json.loads(response.data)
            assert '<script>' not in str(data)
    
    def test_save_config_path_traversal_in_name(self, client):
        """Test save config - path traversal in name"""
        config = {
            'broker': 'paper',
            'instruments': [{'symbol': 'TEST'}],
            'strategy': 'test',
            'timeframe': '1min'
        }
        response = client.post('/api/config',
                              json={'config': config, 'name': '../../../etc/passwd'},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_config_path_traversal(self, client):
        """Test get config - path traversal attempt"""
        response = client.get('/api/config/../../../etc/passwd')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'traversal' in data['error'].lower()
    
    def test_delete_config_path_traversal(self, client):
        """Test delete config - path traversal attempt"""
        response = client.delete('/api/config/../../../etc/passwd')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_validate_config_missing_required_fields(self, client):
        """Test validate config - missing required fields"""
        response = client.post('/api/config/validate',
                              json={'config': {}},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert len(data['errors']) > 0
    
    def test_validate_config_invalid_risk(self, client):
        """Test validate config - invalid risk percentage"""
        config = {
            'broker': 'paper',
            'instruments': [{'symbol': 'TEST'}],
            'strategy': 'test',
            'timeframe': '1min',
            'risk_per_trade': 150  # Invalid: > 100
        }
        response = client.post('/api/config/validate',
                              json={'config': config},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert any('risk' in err.lower() for err in data['errors'])
    
    def test_validate_config_invalid_timeframe(self, client):
        """Test validate config - invalid timeframe"""
        config = {
            'broker': 'paper',
            'instruments': [{'symbol': 'TEST'}],
            'strategy': 'test',
            'timeframe': 'invalid_timeframe'
        }
        response = client.post('/api/config/validate',
                              json={'config': config},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False


class TestBotAPIValidation:
    """Test bot API input validation"""
    
    def test_start_bot_missing_config(self, client):
        """Test start bot - missing config"""
        response = client.post('/api/bot/start',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'config' in data['error'].lower()
    
    def test_start_bot_invalid_config_type(self, client):
        """Test start bot - config is not a dict"""
        response = client.post('/api/bot/start',
                              json={'config': 'not a dict'},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_close_position_xss_in_symbol(self, client):
        """Test close position - XSS in symbol"""
        response = client.delete('/api/bot/positions/<script>alert(1)</script>')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_close_position_path_traversal(self, client):
        """Test close position - path traversal in symbol"""
        response = client.delete('/api/bot/positions/../../../etc/passwd')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_trades_invalid_date_format(self, client):
        """Test get trades - invalid date format"""
        response = client.get('/api/bot/trades?from_date=invalid-date')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_trades_xss_in_date(self, client):
        """Test get trades - XSS in date parameter"""
        response = client.get('/api/bot/trades?from_date=<script>alert(1)</script>')
        assert response.status_code == 400


class TestContentTypeValidation:
    """Test content type validation"""
    
    def test_json_endpoint_wrong_content_type(self, client):
        """Test JSON endpoint with wrong content type"""
        response = client.post('/api/broker/connect',
                              data='{"broker": "kite"}',
                              content_type='text/plain')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'json' in data['error'].lower()
    
    def test_json_endpoint_no_content_type(self, client):
        """Test JSON endpoint without content type"""
        response = client.post('/api/broker/connect',
                              data='{"broker": "kite"}')
        assert response.status_code == 400


class TestInputSizeLimits:
    """Test input size limits"""
    
    def test_extremely_large_json(self, client):
        """Test handling of extremely large JSON payload"""
        large_config = {
            'broker': 'paper',
            'instruments': [{'symbol': f'TEST{i}'} for i in range(10000)],
            'strategy': 'test',
            'timeframe': '1min'
        }
        response = client.post('/api/config',
                              json={'config': large_config},
                              content_type='application/json')
        # Should handle gracefully (either accept or reject with proper error)
        assert response.status_code in [200, 400, 413]
    
    def test_deeply_nested_json(self, client):
        """Test handling of deeply nested JSON"""
        nested = {'level': 1}
        current = nested
        for i in range(100):
            current['nested'] = {'level': i + 2}
            current = current['nested']
        
        response = client.post('/api/config',
                              json={'config': nested},
                              content_type='application/json')
        # Should handle gracefully
        assert response.status_code in [200, 400]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
