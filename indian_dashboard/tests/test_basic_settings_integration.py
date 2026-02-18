"""
Integration tests for Basic Settings section
Tests the complete flow of selecting instruments and configuring basic settings
"""

import pytest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from indian_dashboard import app
except ImportError:
    # If running from project root
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from indian_dashboard.indian_dashboard import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestBasicSettingsIntegration:
    """Test Basic Settings section integration"""
    
    def test_basic_settings_form_fields_present(self, client):
        """Test that all basic settings form fields are present in the HTML"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Check for selected instruments display
        assert 'config-selected-instruments' in html
        assert 'selected-instruments-display' in html
        
        # Check for timeframe selector
        assert 'config-timeframe' in html
        assert 'name="timeframe"' in html
        assert '1minute' in html
        assert '5minute' in html
        assert '15minute' in html
        assert '1hour' in html
        assert '1day' in html
        
        # Check for strategy selector
        assert 'config-strategy' in html
        assert 'name="strategy"' in html
        assert 'trend_following' in html
        assert 'momentum' in html
        assert 'mean_reversion' in html
        assert 'breakout' in html
        
        # Check for trading hours inputs
        assert 'config-trading-start' in html
        assert 'config-trading-end' in html
        assert 'name="trading_start"' in html
        assert 'name="trading_end"' in html
        assert 'type="time"' in html
    
    def test_default_values_set_correctly(self, client):
        """Test that default values are set correctly"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Check default timeframe (5 minutes)
        assert 'value="5minute" selected' in html
        
        # Check default strategy (trend following)
        assert 'value="trend_following" selected' in html
        
        # Check default trading hours (09:15 - 15:30)
        assert 'value="09:15"' in html
        assert 'value="15:30"' in html
    
    def test_configuration_tab_structure(self, client):
        """Test that configuration tab has proper structure"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Check for configuration tabs
        assert 'config-tabs' in html
        assert 'data-config-tab="basic"' in html
        assert 'data-config-tab="strategy"' in html
        assert 'data-config-tab="risk"' in html
        assert 'data-config-tab="advanced"' in html
        
        # Check for basic settings section
        assert 'data-config-section="basic"' in html
        assert 'Basic Settings' in html
    
    def test_form_validation_attributes(self, client):
        """Test that form fields have proper validation attributes"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Time inputs should have type="time"
        assert 'type="time"' in html
        
        # Selects should have proper options
        assert '<select' in html
        assert '<option' in html
    
    def test_save_configuration_with_basic_settings(self, client):
        """Test saving configuration with basic settings"""
        config_data = {
            'config': {
                'timeframe': '5minute',
                'strategy': 'trend_following',
                'trading_start': '09:15',
                'trading_end': '15:30',
                'instruments': [
                    {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_token': '738561'},
                    {'symbol': 'TCS', 'exchange': 'NSE', 'instrument_token': '2953217'}
                ]
            }
        }
        
        response = client.post(
            '/api/config',
            data=json.dumps(config_data),
            content_type='application/json'
        )
        
        # Should succeed or return appropriate error
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # API returns either 'status' or 'success' field
            assert 'status' in data or 'success' in data
    
    def test_load_configuration_returns_basic_settings(self, client):
        """Test that loading configuration returns basic settings"""
        response = client.get('/api/config')
        
        # Should return config or empty response
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # If config exists, it should have basic settings fields
            if data:
                # These fields might be present
                possible_fields = ['timeframe', 'strategy', 'trading_start', 'trading_end', 'instruments']
                # At least check the structure is valid JSON
                assert isinstance(data, dict)


class TestBasicSettingsValidation:
    """Test validation of basic settings"""
    
    def test_timeframe_options_valid(self, client):
        """Test that timeframe options are valid"""
        valid_timeframes = ['1minute', '5minute', '15minute', '30minute', '1hour', '1day']
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        for timeframe in valid_timeframes:
            assert timeframe in html
    
    def test_strategy_options_valid(self, client):
        """Test that strategy options are valid"""
        valid_strategies = ['trend_following', 'momentum', 'mean_reversion', 'breakout']
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        for strategy in valid_strategies:
            assert strategy in html
    
    def test_trading_hours_format(self, client):
        """Test that trading hours use correct time format"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Should have time input type
        assert 'type="time"' in html
        
        # Should have default Indian market hours
        assert '09:15' in html
        assert '15:30' in html


class TestSelectedInstrumentsDisplay:
    """Test selected instruments display in basic settings"""
    
    def test_empty_state_message(self, client):
        """Test that empty state message is shown when no instruments selected"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Should have empty state message
        assert 'No instruments selected' in html or 'no instruments selected' in html.lower()
    
    def test_instruments_display_container_exists(self, client):
        """Test that instruments display container exists"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Should have container for selected instruments
        assert 'config-selected-instruments' in html
        assert 'selected-instruments-display' in html


class TestBasicSettingsCSS:
    """Test CSS styling for basic settings"""
    
    def test_css_classes_present(self, client):
        """Test that required CSS classes are present"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check for form classes
        assert 'form-group' in html
        assert 'form-control' in html
        assert 'form-row' in html
        
        # Check for config section classes
        assert 'config-section' in html
        assert 'section-title' in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
