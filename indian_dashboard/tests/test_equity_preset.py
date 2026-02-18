"""
Unit tests for Equity Intraday preset configuration
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.config import PRESET_CONFIGS


class TestEquityIntradayPreset:
    """Test suite for equity intraday preset"""
    
    @pytest.fixture
    def preset(self):
        """Get equity intraday preset"""
        return PRESET_CONFIGS['equity_intraday']
    
    def test_preset_exists(self):
        """Test that equity_intraday preset exists"""
        assert 'equity_intraday' in PRESET_CONFIGS
    
    def test_basic_fields(self, preset):
        """Test basic preset fields"""
        assert preset['name'] == 'Equity Intraday'
        assert 'description' in preset
        assert len(preset['description']) > 50  # Meaningful description
        assert preset['broker'] == 'kite'
    
    def test_instruments(self, preset):
        """Test instruments configuration"""
        instruments = preset['instruments']
        assert isinstance(instruments, list)
        assert len(instruments) >= 3  # At least 3 liquid stocks
        
        # Check first instrument structure
        if len(instruments) > 0:
            inst = instruments[0]
            assert 'symbol' in inst
            assert 'name' in inst
            assert 'exchange' in inst
            assert inst['exchange'] in ['NSE', 'BSE']
            assert inst['instrument_type'] == 'EQ'
            assert inst['lot_size'] == 1  # Equities have lot size 1
            assert inst['tick_size'] > 0
    
    def test_strategy_settings(self, preset):
        """Test strategy configuration"""
        assert preset['strategy'] == 'mean_reversion'
        assert preset['timeframe'] == '5min'
        assert preset['indicator_period'] == 20
    
    def test_risk_management(self, preset):
        """Test risk management parameters"""
        # Risk per trade should be conservative for equities
        assert 0.1 <= preset['risk_per_trade'] <= 1.0
        
        # Max positions for diversification
        assert 3 <= preset['max_positions'] <= 10
        
        # Max daily loss should be reasonable
        assert 1.0 <= preset['max_daily_loss'] <= 5.0
        
        # Risk per trade should be less than max daily loss
        assert preset['risk_per_trade'] < preset['max_daily_loss']
    
    def test_trading_hours(self, preset):
        """Test trading hours configuration"""
        hours = preset['trading_hours']
        assert 'start' in hours
        assert 'end' in hours
        
        # Parse times
        start_hour, start_min = map(int, hours['start'].split(':'))
        end_hour, end_min = map(int, hours['end'].split(':'))
        
        # Start should be after market open (09:15)
        assert start_hour >= 9
        if start_hour == 9:
            assert start_min >= 15
        
        # End should be before market close (15:30)
        assert end_hour <= 15
        if end_hour == 15:
            assert end_min <= 30
        
        # Trading window should be reasonable (at least 2 hours)
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        assert (end_minutes - start_minutes) >= 120
    
    def test_position_sizing(self, preset):
        """Test position sizing configuration"""
        assert preset['position_sizing'] in ['fixed', 'percentage', 'risk_based']
        assert preset['base_position_size'] > 0
        
        # For equity intraday, position size should be reasonable
        assert 10000 <= preset['base_position_size'] <= 100000
    
    def test_profit_targets(self, preset):
        """Test profit and loss targets"""
        assert preset['take_profit'] > 0
        assert preset['stop_loss'] > 0
        
        # Take profit should be greater than stop loss for positive expectancy
        assert preset['take_profit'] > preset['stop_loss']
        
        # Reward-risk ratio should be at least 1.5:1
        reward_risk = preset['take_profit'] / preset['stop_loss']
        assert reward_risk >= 1.5
        
        # Targets should be reasonable for intraday equities
        assert 0.5 <= preset['take_profit'] <= 3.0
        assert 0.3 <= preset['stop_loss'] <= 2.0
    
    def test_operational_settings(self, preset):
        """Test operational settings"""
        assert preset['paper_trading'] is True  # Should start with paper trading
        assert preset['log_level'] in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        assert preset['data_refresh_interval'] > 0
        assert preset['data_refresh_interval'] <= 60  # Should refresh frequently
        assert isinstance(preset['enable_notifications'], bool)
    
    def test_equity_specific_parameters(self, preset):
        """Test equity-specific parameters"""
        # Volume filter
        assert 'min_volume' in preset
        assert preset['min_volume'] >= 100000  # Minimum liquidity requirement
        
        # Price filters
        if 'min_price' in preset:
            assert preset['min_price'] > 0
        if 'max_price' in preset:
            assert preset['max_price'] > preset.get('min_price', 0)
        
        # Bollinger Bands for mean reversion
        if 'bollinger_std' in preset:
            assert 1.5 <= preset['bollinger_std'] <= 3.0
        
        # RSI parameters
        if 'rsi_period' in preset:
            assert 10 <= preset['rsi_period'] <= 20
        if 'rsi_overbought' in preset:
            assert 65 <= preset['rsi_overbought'] <= 80
        if 'rsi_oversold' in preset:
            assert 20 <= preset['rsi_oversold'] <= 35
        
        # Spread filter
        if 'max_spread_percent' in preset:
            assert 0.05 <= preset['max_spread_percent'] <= 0.5
    
    def test_mean_reversion_parameters(self, preset):
        """Test mean reversion specific parameters"""
        # Mean reversion should not use trailing stops
        if 'trailing_stop' in preset:
            assert preset['trailing_stop'] is False
        
        # Check reversion distance
        if 'min_reversion_distance' in preset:
            assert 1.0 <= preset['min_reversion_distance'] <= 3.0
        
        # Check holding time limit
        if 'max_holding_time' in preset:
            assert 60 <= preset['max_holding_time'] <= 300  # 1-5 hours
    
    def test_scale_out_configuration(self, preset):
        """Test scale out configuration"""
        if 'scale_out' in preset and preset['scale_out']:
            assert 'scale_out_levels' in preset
            levels = preset['scale_out_levels']
            assert isinstance(levels, list)
            assert len(levels) >= 2
            
            # Levels should be in ascending order
            for i in range(len(levels) - 1):
                assert levels[i] < levels[i + 1]
            
            # Last level should match take profit
            assert levels[-1] == preset['take_profit']
    
    def test_configuration_consistency(self, preset):
        """Test overall configuration consistency"""
        # Max positions * base position size should be reasonable
        total_capital = preset['max_positions'] * preset['base_position_size']
        assert total_capital <= 1000000  # Should not exceed ₹10 lakhs
        
        # Risk per trade * max positions should not exceed max daily loss
        max_risk = preset['risk_per_trade'] * preset['max_positions']
        assert max_risk <= preset['max_daily_loss'] * 2  # Allow some buffer
        
        # Data refresh should be appropriate for timeframe
        if preset['timeframe'] == '5min':
            assert preset['data_refresh_interval'] <= 60  # Refresh at least every minute


class TestEquityPresetValidation:
    """Test preset validation"""
    
    def test_preset_validates(self):
        """Test that preset passes validation"""
        from indian_dashboard.api.config import validate_configuration
        
        preset = PRESET_CONFIGS['equity_intraday'].copy()
        errors = validate_configuration(preset)
        
        # Should have no validation errors
        assert len(errors) == 0, f"Validation errors: {errors}"
    
    def test_preset_has_required_fields(self):
        """Test that preset has all required fields"""
        preset = PRESET_CONFIGS['equity_intraday']
        
        required_fields = [
            'name', 'description', 'broker', 'instruments',
            'strategy', 'timeframe', 'risk_per_trade',
            'max_positions', 'max_daily_loss', 'trading_hours'
        ]
        
        for field in required_fields:
            assert field in preset, f"Missing required field: {field}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
