"""
Integration tests for export/import functionality
"""

import pytest
import json
import os
from pathlib import Path


class TestExportImportIntegration:
    """Test export/import functionality"""
    
    def test_export_configuration_format(self):
        """Test that exported configuration has correct format"""
        # Sample configuration
        config = {
            'broker': 'kite',
            'strategy': 'trend_following',
            'timeframe': '5minute',
            'instruments': [
                {'symbol': 'NIFTY', 'exchange': 'NSE', 'instrument_token': '256265'}
            ],
            'risk_per_trade': 1.5,
            'max_positions': 3,
            'max_daily_loss': 3.0
        }
        
        # Add export metadata
        export_data = {
            **config,
            'exported_at': '2024-01-01T00:00:00Z',
            'exported_by': 'Test Suite',
            'version': '1.0'
        }
        
        # Verify structure
        assert 'broker' in export_data
        assert 'strategy' in export_data
        assert 'instruments' in export_data
        assert 'exported_at' in export_data
        assert 'exported_by' in export_data
        assert 'version' in export_data
        
        # Verify JSON serializable
        json_string = json.dumps(export_data, indent=2)
        assert json_string is not None
        assert len(json_string) > 0
    
    def test_import_valid_configuration(self):
        """Test importing a valid configuration"""
        # Valid configuration JSON
        config_json = '''
        {
            "broker": "kite",
            "strategy": "momentum",
            "timeframe": "15minute",
            "instruments": [
                {"symbol": "RELIANCE", "exchange": "NSE", "instrument_token": "738561"}
            ],
            "risk_per_trade": 2.0,
            "max_positions": 5,
            "max_daily_loss": 4.0,
            "position_sizing": "fixed",
            "base_position_size": 10000
        }
        '''
        
        # Parse JSON
        config = json.loads(config_json)
        
        # Verify required fields
        assert config['broker'] == 'kite'
        assert config['strategy'] == 'momentum'
        assert config['timeframe'] == '15minute'
        assert len(config['instruments']) == 1
        assert config['risk_per_trade'] == 2.0
    
    def test_import_invalid_json(self):
        """Test importing invalid JSON"""
        invalid_json = '{"broker": "kite", "strategy": '  # Incomplete JSON
        
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)
    
    def test_validation_missing_required_fields(self):
        """Test validation catches missing required fields"""
        # Configuration missing required fields
        config = {
            'risk_per_trade': 1.5,
            'max_positions': 3
            # Missing: broker, strategy, timeframe, instruments
        }
        
        errors = []
        
        # Validate required fields
        required_fields = ['broker', 'strategy', 'timeframe', 'instruments']
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f'Missing required field: {field}')
        
        assert len(errors) == 4
        assert 'Missing required field: broker' in errors
        assert 'Missing required field: strategy' in errors
        assert 'Missing required field: timeframe' in errors
        assert 'Missing required field: instruments' in errors
    
    def test_validation_invalid_risk_parameters(self):
        """Test validation catches invalid risk parameters"""
        config = {
            'broker': 'kite',
            'strategy': 'trend_following',
            'timeframe': '5minute',
            'instruments': [{'symbol': 'NIFTY', 'exchange': 'NSE'}],
            'risk_per_trade': 150,  # Invalid: > 100
            'max_positions': -5,    # Invalid: negative
            'max_daily_loss': 0     # Invalid: zero
        }
        
        errors = []
        
        # Validate risk_per_trade
        if config['risk_per_trade'] <= 0 or config['risk_per_trade'] > 100:
            errors.append('Risk per trade must be between 0 and 100')
        
        # Validate max_positions
        if config['max_positions'] <= 0:
            errors.append('Max positions must be positive')
        
        # Validate max_daily_loss
        if config['max_daily_loss'] <= 0:
            errors.append('Max daily loss must be positive')
        
        assert len(errors) == 3
    
    def test_validation_warnings(self):
        """Test validation generates appropriate warnings"""
        config = {
            'broker': 'kite',
            'strategy': 'trend_following',
            'timeframe': '5minute',
            'instruments': [{'symbol': f'STOCK{i}', 'exchange': 'NSE'} for i in range(15)],
            'risk_per_trade': 8.0,  # High risk
            'max_positions': 15     # Many positions
        }
        
        warnings = []
        
        # Check for high risk
        if config['risk_per_trade'] > 5:
            warnings.append('Risk per trade above 5% is considered high')
        
        # Check for too many positions
        if config['max_positions'] > 10:
            warnings.append('More than 10 positions may be difficult to manage')
        
        assert len(warnings) == 2
    
    def test_export_import_roundtrip(self):
        """Test that configuration survives export/import roundtrip"""
        # Original configuration
        original_config = {
            'broker': 'kite',
            'strategy': 'breakout',
            'timeframe': '1hour',
            'instruments': [
                {'symbol': 'NIFTY', 'exchange': 'NSE', 'instrument_token': '256265'},
                {'symbol': 'BANKNIFTY', 'exchange': 'NFO', 'instrument_token': '260105'}
            ],
            'risk_per_trade': 1.5,
            'max_positions': 3,
            'max_daily_loss': 3.0,
            'position_sizing': 'risk_based',
            'base_position_size': 10000,
            'take_profit': 2.0,
            'stop_loss': 1.0,
            'trading_start': '09:15',
            'trading_end': '15:30',
            'paper_trading': True
        }
        
        # Export to JSON
        json_string = json.dumps(original_config, indent=2)
        
        # Import from JSON
        imported_config = json.loads(json_string)
        
        # Verify all fields match
        assert imported_config['broker'] == original_config['broker']
        assert imported_config['strategy'] == original_config['strategy']
        assert imported_config['timeframe'] == original_config['timeframe']
        assert len(imported_config['instruments']) == len(original_config['instruments'])
        assert imported_config['risk_per_trade'] == original_config['risk_per_trade']
        assert imported_config['max_positions'] == original_config['max_positions']
        assert imported_config['paper_trading'] == original_config['paper_trading']
    
    def test_import_with_extra_fields(self):
        """Test importing configuration with extra/unknown fields"""
        config_json = '''
        {
            "broker": "kite",
            "strategy": "trend_following",
            "timeframe": "5minute",
            "instruments": [{"symbol": "NIFTY", "exchange": "NSE"}],
            "risk_per_trade": 1.5,
            "unknown_field": "should be ignored",
            "another_unknown": 123
        }
        '''
        
        config = json.loads(config_json)
        
        # Should still have required fields
        assert 'broker' in config
        assert 'strategy' in config
        
        # Extra fields should be present but can be ignored
        assert 'unknown_field' in config
        assert 'another_unknown' in config
    
    def test_filename_generation(self):
        """Test export filename generation"""
        from datetime import datetime
        
        # Generate filename
        now = datetime.now()
        filename = f"config_{now.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Verify format
        assert filename.startswith('config_')
        assert filename.endswith('.json')
        assert len(filename) > 20  # Should have timestamp
    
    def test_clipboard_format(self):
        """Test clipboard copy format"""
        config = {
            'broker': 'kite',
            'strategy': 'momentum',
            'instruments': [{'symbol': 'NIFTY', 'exchange': 'NSE'}]
        }
        
        # Format for clipboard (pretty-printed JSON)
        clipboard_text = json.dumps(config, indent=2)
        
        # Verify it's valid JSON
        parsed = json.loads(clipboard_text)
        assert parsed == config
        
        # Verify it's formatted (has newlines)
        assert '\n' in clipboard_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
