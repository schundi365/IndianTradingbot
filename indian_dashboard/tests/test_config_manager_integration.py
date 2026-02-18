"""
Integration tests for Configuration Manager
Tests save/load/delete configuration functionality
"""

import pytest
import json
import os
from pathlib import Path
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask app module
from indian_dashboard import indian_dashboard


@pytest.fixture
def test_config_dir():
    """Create temporary config directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def app(test_config_dir):
    """Get Flask app with test configuration"""
    # Modify config to use test directory
    from config import DASHBOARD_CONFIG
    original_config_dir = DASHBOARD_CONFIG['config_dir']
    DASHBOARD_CONFIG['config_dir'] = Path(test_config_dir)
    
    # Get the app
    app = indian_dashboard.app
    app.config['TESTING'] = True
    
    yield app
    
    # Restore original config
    DASHBOARD_CONFIG['config_dir'] = original_config_dir


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_save_configuration(client):
    """Test saving a configuration"""
    config_data = {
        'config': {
            'name': 'Test Config',
            'description': 'Test configuration',
            'broker': 'kite',
            'strategy': 'trend_following',
            'timeframe': '5minute',
            'risk_per_trade': 1.0,
            'max_positions': 3,
            'instruments': [
                {'symbol': 'NIFTY', 'exchange': 'NSE'}
            ]
        },
        'name': 'test_config'
    }
    
    response = client.post('/api/config',
                          data=json.dumps(config_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'test_config' in data['message']


def test_list_configurations(client):
    """Test listing configurations"""
    # First save a config
    config_data = {
        'config': {
            'broker': 'kite',
            'strategy': 'trend_following',
            'instruments': []
        },
        'name': 'test_list_config'
    }
    
    client.post('/api/config',
               data=json.dumps(config_data),
               content_type='application/json')
    
    # Now list configs
    response = client.get('/api/config/list')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'configs' in data
    assert len(data['configs']) > 0
    
    # Check if our config is in the list
    config_names = [c['name'] for c in data['configs']]
    assert 'test_list_config' in config_names


def test_get_configuration(client):
    """Test getting a specific configuration"""
    # First save a config
    config_data = {
        'config': {
            'broker': 'kite',
            'strategy': 'momentum',
            'timeframe': '15minute',
            'instruments': []
        },
        'name': 'test_get_config'
    }
    
    client.post('/api/config',
               data=json.dumps(config_data),
               content_type='application/json')
    
    # Now get the config
    response = client.get('/api/config/test_get_config')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['name'] == 'test_get_config'
    assert data['config']['broker'] == 'kite'
    assert data['config']['strategy'] == 'momentum'


def test_delete_configuration(client):
    """Test deleting a configuration"""
    # First save a config
    config_data = {
        'config': {
            'broker': 'kite',
            'instruments': []
        },
        'name': 'test_delete_config'
    }
    
    client.post('/api/config',
               data=json.dumps(config_data),
               content_type='application/json')
    
    # Now delete it
    response = client.delete('/api/config/test_delete_config')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'deleted' in data['message'].lower()
    
    # Verify it's gone
    response = client.get('/api/config/test_delete_config')
    assert response.status_code == 404


def test_get_nonexistent_configuration(client):
    """Test getting a configuration that doesn't exist"""
    response = client.get('/api/config/nonexistent_config')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'not found' in data['error'].lower()


def test_delete_nonexistent_configuration(client):
    """Test deleting a configuration that doesn't exist"""
    response = client.delete('/api/config/nonexistent_config')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'not found' in data['error'].lower()


def test_save_configuration_without_name(client):
    """Test saving configuration without providing a name"""
    config_data = {
        'config': {
            'broker': 'kite',
            'instruments': []
        }
        # No 'name' field
    }
    
    response = client.post('/api/config',
                          data=json.dumps(config_data),
                          content_type='application/json')
    
    # Should still succeed (saves as current config)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_save_configuration_with_description(client):
    """Test saving configuration with description"""
    config_data = {
        'config': {
            'description': 'NIFTY intraday strategy with 5min timeframe',
            'broker': 'kite',
            'strategy': 'trend_following',
            'instruments': []
        },
        'name': 'nifty_intraday'
    }
    
    response = client.post('/api/config',
                          data=json.dumps(config_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    # Verify description is saved
    response = client.get('/api/config/nifty_intraday')
    data = json.loads(response.data)
    assert data['config']['description'] == 'NIFTY intraday strategy with 5min timeframe'


def test_list_configurations_metadata(client):
    """Test that list configurations returns proper metadata"""
    # Save a config with metadata
    config_data = {
        'config': {
            'description': 'Test description',
            'broker': 'kite',
            'strategy': 'momentum',
            'instruments': [
                {'symbol': 'NIFTY', 'exchange': 'NSE'},
                {'symbol': 'BANKNIFTY', 'exchange': 'NSE'}
            ]
        },
        'name': 'test_metadata'
    }
    
    client.post('/api/config',
               data=json.dumps(config_data),
               content_type='application/json')
    
    # List configs
    response = client.get('/api/config/list')
    data = json.loads(response.data)
    
    # Find our config
    test_config = next((c for c in data['configs'] if c['name'] == 'test_metadata'), None)
    assert test_config is not None
    assert test_config['description'] == 'Test description'
    assert test_config['broker'] == 'kite'
    assert test_config['strategy'] == 'momentum'
    assert test_config['instruments_count'] == 2


def test_overwrite_existing_configuration(client):
    """Test overwriting an existing configuration"""
    # Save initial config
    config_data = {
        'config': {
            'broker': 'kite',
            'strategy': 'trend_following',
            'instruments': []
        },
        'name': 'test_overwrite'
    }
    
    client.post('/api/config',
               data=json.dumps(config_data),
               content_type='application/json')
    
    # Overwrite with new data
    new_config_data = {
        'config': {
            'broker': 'alice_blue',
            'strategy': 'momentum',
            'instruments': []
        },
        'name': 'test_overwrite'
    }
    
    response = client.post('/api/config',
                          data=json.dumps(new_config_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    # Verify it was overwritten
    response = client.get('/api/config/test_overwrite')
    data = json.loads(response.data)
    assert data['config']['broker'] == 'alice_blue'
    assert data['config']['strategy'] == 'momentum'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
