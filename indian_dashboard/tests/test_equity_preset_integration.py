"""
Integration tests for Equity Intraday preset
Tests the preset through the API endpoints
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def client():
    """Create test client"""
    from indian_dashboard.indian_dashboard import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestEquityPresetAPI:
    """Test equity preset through API"""
    
    def test_get_presets_includes_equity(self, client):
        """Test that GET /api/config/presets includes equity_intraday"""
        response = client.get('/api/config/presets')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'presets' in data
        
        # Find equity preset
        equity_preset = None
        for preset in data['presets']:
            if preset['id'] == 'equity_intraday':
                equity_preset = preset
                break
        
        assert equity_preset is not None, "equity_intraday preset not found"
        assert equity_preset['name'] == 'Equity Intraday'
        assert 'description' in equity_preset
        assert equity_preset['strategy'] == 'mean_reversion'
    
    def test_equity_preset_structure(self, client):
        """Test equity preset has correct structure"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity_preset = next(
            (p for p in data['presets'] if p['id'] == 'equity_intraday'),
            None
        )
        
        assert equity_preset is not None
        config = equity_preset['config']
        
        # Check structure
        assert 'instruments' in config
        assert 'strategy' in config
        assert 'timeframe' in config
        assert 'risk_per_trade' in config
        assert 'max_positions' in config
        assert 'trading_hours' in config
    
    def test_equity_preset_instruments(self, client):
        """Test equity preset has valid instruments"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity_preset = next(
            (p for p in data['presets'] if p['id'] == 'equity_intraday'),
            None
        )
        
        instruments = equity_preset['config']['instruments']
        assert len(instruments) >= 3  # Should have multiple stocks
        
        # Check instrument structure
        for inst in instruments:
            assert 'symbol' in inst
            assert 'exchange' in inst
            assert inst['exchange'] in ['NSE', 'BSE']
            assert inst['instrument_type'] == 'EQ'
    
    def test_validate_equity_preset(self, client):
        """Test that equity preset passes validation"""
        # First get the preset
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity_preset = next(
            (p for p in data['presets'] if p['id'] == 'equity_intraday'),
            None
        )
        
        # Validate it
        response = client.post(
            '/api/config/validate',
            data=json.dumps({'config': equity_preset['config']}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['valid'] is True
        assert len(data['errors']) == 0
    
    def test_save_equity_preset(self, client):
        """Test saving equity preset as configuration"""
        # Get the preset
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity_preset = next(
            (p for p in data['presets'] if p['id'] == 'equity_intraday'),
            None
        )
        
        # Save it
        response = client.post(
            '/api/config',
            data=json.dumps({
                'config': equity_preset['config'],
                'name': 'test_equity_intraday'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_equity_preset_risk_parameters(self, client):
        """Test equity preset risk parameters are appropriate"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity_preset = next(
            (p for p in data['presets'] if p['id'] == 'equity_intraday'),
            None
        )
        
        config = equity_preset['config']
        
        # Risk should be conservative
        assert config['risk_per_trade'] <= 1.0
        assert config['max_daily_loss'] <= 3.0
        
        # Should have multiple positions for diversification
        assert config['max_positions'] >= 3
        
        # Reward-risk ratio should be positive
        assert config['take_profit'] > config['stop_loss']


class TestEquityPresetComparison:
    """Compare equity preset with other presets"""
    
    def test_equity_vs_futures_risk(self, client):
        """Test that equity preset has lower risk than futures"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity = next((p for p in data['presets'] if p['id'] == 'equity_intraday'), None)
        nifty = next((p for p in data['presets'] if p['id'] == 'nifty_futures'), None)
        
        if equity and nifty:
            # Equity should have lower risk per trade
            assert equity['config']['risk_per_trade'] <= nifty['config']['risk_per_trade']
            
            # Equity should have more positions (diversification)
            assert equity['config']['max_positions'] >= nifty['config']['max_positions']
    
    def test_equity_timeframe(self, client):
        """Test that equity uses shorter timeframe"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity = next((p for p in data['presets'] if p['id'] == 'equity_intraday'), None)
        
        assert equity is not None
        # Equity intraday should use 5min timeframe
        assert equity['config']['timeframe'] == '5min'
    
    def test_equity_strategy(self, client):
        """Test that equity uses mean reversion strategy"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        equity = next((p for p in data['presets'] if p['id'] == 'equity_intraday'), None)
        
        assert equity is not None
        # Equity intraday should use mean reversion
        assert equity['config']['strategy'] == 'mean_reversion'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
