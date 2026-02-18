"""
Test broker selector UI functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from indian_dashboard.indian_dashboard import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_dashboard_loads(client):
    """Test that dashboard page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Indian Market Trading Dashboard' in response.data


def test_broker_list_api(client):
    """Test broker list API endpoint"""
    response = client.get('/api/broker/list')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert 'brokers' in data
    assert len(data['brokers']) > 0
    
    # Check broker structure
    broker = data['brokers'][0]
    assert 'id' in broker
    assert 'name' in broker
    assert 'logo' in broker
    assert 'oauth_enabled' in broker


def test_broker_credentials_form_api(client):
    """Test credentials form API endpoint"""
    response = client.get('/api/broker/credentials-form/kite')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert 'fields' in data
    assert len(data['fields']) > 0
    
    # Check field structure
    field = data['fields'][0]
    assert 'name' in field
    assert 'type' in field
    assert 'label' in field


def test_broker_status_api(client):
    """Test broker status API endpoint"""
    response = client.get('/api/broker/status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert 'status' in data
    assert 'connected' in data['status']


def test_dashboard_has_broker_selector(client):
    """Test that dashboard HTML contains broker selector elements"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Check for broker selector elements
    assert 'broker-list' in html
    assert 'broker-grid' in html
    assert 'change-broker-btn' in html
    assert 'broker-status-indicator' in html
    assert 'credentials-section' in html
    assert 'connection-status' in html


def test_dashboard_has_broker_styles(client):
    """Test that dashboard includes broker selector CSS"""
    response = client.get('/static/css/dashboard.css')
    assert response.status_code == 200
    
    css = response.data.decode('utf-8')
    
    # Check for broker-specific styles
    assert '.broker-card' in css
    assert '.broker-logo' in css
    assert '.broker-name' in css
    assert '.broker-status-indicator' in css
    assert '.broker-oauth-badge' in css
    assert '.change-broker-section' in css
    assert '.btn-change-broker' in css


def test_dashboard_has_broker_scripts(client):
    """Test that dashboard includes broker selector JavaScript"""
    response = client.get('/static/js/app.js')
    assert response.status_code == 200
    
    js = response.data.decode('utf-8')
    
    # Check for broker-specific functions
    assert 'loadBrokers' in js
    assert 'selectBroker' in js
    assert 'connectBroker' in js
    assert 'disconnectBroker' in js
    assert 'changeBroker' in js
    assert 'broker-status-indicator' in js


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
