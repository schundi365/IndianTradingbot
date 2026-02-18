"""
Integration tests for configuration presets
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'indian_dashboard'))

import pytest


def test_preset_configs_exist():
    """Test that preset configurations are defined"""
    from config import PRESET_CONFIGS
    
    expected_presets = [
        'nifty_futures',
        'banknifty_futures',
        'equity_intraday',
        'options_trading'
    ]
    
    assert len(PRESET_CONFIGS) == len(expected_presets)
    
    for preset_id in expected_presets:
        assert preset_id in PRESET_CONFIGS


def test_preset_structure():
    """Test that presets have correct structure"""
    from config import PRESET_CONFIGS
    
    for preset_id, preset_config in PRESET_CONFIGS.items():
        # Check required fields
        assert 'name' in preset_config
        assert 'description' in preset_config
        assert 'strategy' in preset_config
        assert 'timeframe' in preset_config
        assert 'risk_per_trade' in preset_config
        assert 'max_positions' in preset_config
        assert 'max_daily_loss' in preset_config
        assert 'trading_hours' in preset_config


def test_nifty_futures_preset():
    """Test NIFTY futures preset configuration"""
    from config import PRESET_CONFIGS
    
    nifty_preset = PRESET_CONFIGS['nifty_futures']
    
    assert nifty_preset['name'] == 'NIFTY 50 Futures'
    assert nifty_preset['strategy'] == 'trend_following'
    assert nifty_preset['timeframe'] == '15minute'
    assert nifty_preset['risk_per_trade'] == 1.0
    assert nifty_preset['max_positions'] == 3
    assert nifty_preset['max_daily_loss'] == 3.0
    assert nifty_preset['paper_trading'] is True


def test_banknifty_futures_preset():
    """Test BANKNIFTY futures preset configuration"""
    from config import PRESET_CONFIGS
    
    banknifty_preset = PRESET_CONFIGS['banknifty_futures']
    
    assert banknifty_preset['name'] == 'BANKNIFTY Futures'
    assert banknifty_preset['strategy'] == 'momentum'
    assert banknifty_preset['timeframe'] == '15minute'
    assert banknifty_preset['risk_per_trade'] == 1.5
    assert banknifty_preset['max_positions'] == 2
    assert banknifty_preset['max_daily_loss'] == 4.0


def test_equity_intraday_preset():
    """Test equity intraday preset configuration"""
    from config import PRESET_CONFIGS
    
    equity_preset = PRESET_CONFIGS['equity_intraday']
    
    assert equity_preset['name'] == 'Equity Intraday'
    assert equity_preset['strategy'] == 'mean_reversion'
    assert equity_preset['timeframe'] == '5minute'
    assert equity_preset['risk_per_trade'] == 0.5
    assert equity_preset['max_positions'] == 5
    assert equity_preset['max_daily_loss'] == 2.0


def test_options_trading_preset():
    """Test options trading preset configuration"""
    from config import PRESET_CONFIGS
    
    options_preset = PRESET_CONFIGS['options_trading']
    
    assert options_preset['name'] == 'Options Trading'
    assert options_preset['strategy'] == 'trend_following'
    assert options_preset['timeframe'] == '15minute'
    assert options_preset['risk_per_trade'] == 2.0
    assert options_preset['max_positions'] == 3
    assert options_preset['max_daily_loss'] == 5.0


def test_all_presets_have_required_parameters():
    """Test that all presets have all required parameters"""
    from config import PRESET_CONFIGS
    
    required_params = [
        'timeframe', 'strategy', 'risk_per_trade', 'max_positions',
        'max_daily_loss', 'trading_hours', 'indicator_period',
        'position_sizing', 'base_position_size', 'take_profit',
        'stop_loss', 'paper_trading'
    ]
    
    for preset_id, preset_config in PRESET_CONFIGS.items():
        for param in required_params:
            assert param in preset_config, f"Preset {preset_id} missing parameter: {param}"


def test_preset_risk_parameters_valid():
    """Test that preset risk parameters are within valid ranges"""
    from config import PRESET_CONFIGS
    
    for preset_id, config in PRESET_CONFIGS.items():
        # Risk per trade should be between 0.1 and 10%
        assert 0.1 <= config['risk_per_trade'] <= 10.0
        
        # Max positions should be positive
        assert config['max_positions'] > 0
        
        # Max daily loss should be positive
        assert config['max_daily_loss'] > 0
        
        # Take profit should be greater than stop loss
        assert config['take_profit'] > config['stop_loss']
        
        # Stop loss should be positive
        assert config['stop_loss'] > 0


def test_preset_trading_hours_valid():
    """Test that preset trading hours are valid"""
    from config import PRESET_CONFIGS
    
    for preset_id, config in PRESET_CONFIGS.items():
        trading_hours = config['trading_hours']
        
        assert 'start' in trading_hours
        assert 'end' in trading_hours
        
        # Check format (HH:MM)
        start = trading_hours['start']
        end = trading_hours['end']
        
        assert len(start) == 5 and start[2] == ':'
        assert len(end) == 5 and end[2] == ':'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
