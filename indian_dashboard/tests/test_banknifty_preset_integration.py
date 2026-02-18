"""
Integration test for BANKNIFTY Futures Preset
Tests the preset through the API endpoints
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.indian_dashboard import app
from indian_dashboard.config import PRESET_CONFIGS


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestBankNiftyPresetIntegration:
    """Integration tests for BANKNIFTY preset"""
    
    def test_get_presets_includes_banknifty(self, client):
        """Test that GET /api/config/presets includes BANKNIFTY"""
        response = client.get('/api/config/presets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'presets' in data
        
        # Find BANKNIFTY preset
        banknifty_preset = None
        for preset in data['presets']:
            if preset['id'] == 'banknifty_futures':
                banknifty_preset = preset
                break
        
        assert banknifty_preset is not None, "BANKNIFTY preset not found in API response"
        assert banknifty_preset['name'] == "BANKNIFTY Futures"
        assert 'description' in banknifty_preset
        assert banknifty_preset['strategy'] == 'momentum'
    
    def test_banknifty_preset_structure(self, client):
        """Test BANKNIFTY preset has correct structure"""
        response = client.get('/api/config/presets')
        data = json.loads(response.data)
        
        # Find BANKNIFTY preset
        banknifty_preset = None
        for preset in data['presets']:
            if preset['id'] == 'banknifty_futures':
                banknifty_preset = preset['config']
                break
        
        assert banknifty_preset is not None
        
        # Verify key fields
        assert banknifty_preset['broker'] == 'kite'
        assert banknifty_preset['strategy'] == 'momentum'
        assert banknifty_preset['timeframe'] == '15min'
        assert len(banknifty_preset['instruments']) > 0
    
    def test_validate_banknifty_preset(self, client):
        """Test that BANKNIFTY preset passes validation"""
        # Get the preset
        preset = PRESET_CONFIGS['banknifty_futures']
        
        # Validate it
        response = client.post(
            '/api/config/validate',
            data=json.dumps({'config': preset}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['valid'] is True
        assert len(data['errors']) == 0
    
    def test_save_banknifty_preset(self, client):
        """Test saving BANKNIFTY preset as current config"""
        preset = PRESET_CONFIGS['banknifty_futures']
        
        response = client.post(
            '/api/config',
            data=json.dumps({'config': preset}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
    
    def test_save_and_load_banknifty_preset(self, client):
        """Test saving and loading BANKNIFTY preset"""
        preset = PRESET_CONFIGS['banknifty_futures']
        
        # Save with a name
        response = client.post(
            '/api/config',
            data=json.dumps({
                'config': preset,
                'name': 'test_banknifty'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Load it back
        response = client.get('/api/config/test_banknifty')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['name'] == 'test_banknifty'
        assert data['config']['strategy'] == 'momentum'
        assert data['config']['name'] == 'BANKNIFTY Futures'
        
        # Clean up
        client.delete('/api/config/test_banknifty')
    
    def test_banknifty_instruments_structure(self, client):
        """Test BANKNIFTY preset instruments have correct structure"""
        preset = PRESET_CONFIGS['banknifty_futures']
        instruments = preset['instruments']
        
        assert len(instruments) > 0
        
        for instrument in instruments:
            # Verify required fields
            assert 'symbol' in instrument
            assert 'name' in instrument
            assert 'exchange' in instrument
            assert 'instrument_type' in instrument
            assert 'lot_size' in instrument
            assert 'tick_size' in instrument
            
            # Verify BANKNIFTY specific values
            assert 'BANKNIFTY' in instrument['symbol']
            assert instrument['exchange'] == 'NFO'
            assert instrument['instrument_type'] == 'FUT'
            assert instrument['lot_size'] == 25
    
    def test_banknifty_risk_parameters(self, client):
        """Test BANKNIFTY risk parameters are appropriate"""
        preset = PRESET_CONFIGS['banknifty_futures']
        
        # Risk per trade should be higher than NIFTY
        assert preset['risk_per_trade'] == 1.5
        
        # Max positions should be limited
        assert preset['max_positions'] == 2
        
        # Max daily loss should be reasonable
        assert preset['max_daily_loss'] == 4.0
        
        # Profit/loss targets should be wider
        assert preset['take_profit'] == 2.5
        assert preset['stop_loss'] == 1.5
    
    def test_banknifty_momentum_parameters(self, client):
        """Test BANKNIFTY has momentum-specific parameters"""
        preset = PRESET_CONFIGS['banknifty_futures']
        
        # Should have momentum indicators
        assert 'momentum_threshold' in preset
        assert 'rsi_period' in preset
        assert 'rsi_overbought' in preset
        assert 'rsi_oversold' in preset
        
        # Verify values
        assert preset['rsi_period'] == 14
        assert preset['rsi_overbought'] == 70
        assert preset['rsi_oversold'] == 30
    
    def test_list_configs_after_save(self, client):
        """Test that saved BANKNIFTY config appears in list"""
        preset = PRESET_CONFIGS['banknifty_futures']
        
        # Save with a name
        client.post(
            '/api/config',
            data=json.dumps({
                'config': preset,
                'name': 'my_banknifty_strategy'
            }),
            content_type='application/json'
        )
        
        # List configs
        response = client.get('/api/config/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        
        # Find our config
        found = False
        for config in data['configs']:
            if config['name'] == 'my_banknifty_strategy':
                found = True
                assert config['strategy'] == 'momentum'
                assert config['broker'] == 'kite'
                break
        
        assert found, "Saved BANKNIFTY config not found in list"
        
        # Clean up
        client.delete('/api/config/my_banknifty_strategy')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
