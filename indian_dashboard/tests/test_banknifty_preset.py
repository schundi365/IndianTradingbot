"""
Test BANKNIFTY Futures Preset Configuration
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.config import PRESET_CONFIGS


class TestBankNiftyPreset:
    """Test BANKNIFTY futures preset configuration"""
    
    def test_preset_exists(self):
        """Test that BANKNIFTY preset exists"""
        assert "banknifty_futures" in PRESET_CONFIGS
    
    def test_preset_structure(self):
        """Test that preset has all required fields"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        # Required fields
        required_fields = [
            "name", "description", "broker", "instruments", "strategy",
            "timeframe", "risk_per_trade", "max_positions", "max_daily_loss",
            "trading_hours", "indicator_period", "position_sizing",
            "base_position_size", "take_profit", "stop_loss", "paper_trading"
        ]
        
        for field in required_fields:
            assert field in preset, f"Missing required field: {field}"
    
    def test_preset_name(self):
        """Test preset name"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        assert preset["name"] == "BANKNIFTY Futures"
    
    def test_preset_description(self):
        """Test preset has meaningful description"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        assert len(preset["description"]) > 50
        assert "BANKNIFTY" in preset["description"]
        assert "momentum" in preset["description"].lower()
    
    def test_broker_configuration(self):
        """Test broker is configured"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        assert preset["broker"] == "kite"
    
    def test_instruments_configuration(self):
        """Test instruments are configured"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        instruments = preset["instruments"]
        
        assert len(instruments) > 0, "No instruments configured"
        
        # Check first instrument structure
        instrument = instruments[0]
        assert "symbol" in instrument
        assert "name" in instrument
        assert "exchange" in instrument
        assert "instrument_type" in instrument
        assert "lot_size" in instrument
        assert "tick_size" in instrument
        
        # Verify BANKNIFTY specific values
        assert "BANKNIFTY" in instrument["symbol"]
        assert instrument["exchange"] == "NFO"
        assert instrument["instrument_type"] == "FUT"
        assert instrument["lot_size"] == 25  # BANKNIFTY lot size
    
    def test_strategy_configuration(self):
        """Test strategy is momentum"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        assert preset["strategy"] == "momentum"
    
    def test_timeframe_configuration(self):
        """Test timeframe is 15min"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        assert preset["timeframe"] == "15min"
    
    def test_risk_parameters(self):
        """Test risk parameters are appropriate for BANKNIFTY"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        # Risk per trade should be higher than NIFTY (1.0%) but reasonable
        assert 1.0 <= preset["risk_per_trade"] <= 2.0
        
        # Max positions should be limited
        assert 1 <= preset["max_positions"] <= 3
        
        # Max daily loss should be reasonable
        assert 3.0 <= preset["max_daily_loss"] <= 5.0
    
    def test_trading_hours(self):
        """Test trading hours are configured"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        trading_hours = preset["trading_hours"]
        
        assert "start" in trading_hours
        assert "end" in trading_hours
        assert trading_hours["start"] == "09:15"
        assert trading_hours["end"] == "15:15"
    
    def test_indicator_parameters(self):
        """Test indicator parameters"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        # Indicator period should be shorter for momentum (14 vs 20 for trend)
        assert preset["indicator_period"] == 14
    
    def test_position_sizing(self):
        """Test position sizing configuration"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        assert preset["position_sizing"] == "risk_based"
        assert preset["base_position_size"] > 0
        # BANKNIFTY base should be lower than NIFTY due to higher volatility
        assert preset["base_position_size"] <= 100000
    
    def test_profit_loss_targets(self):
        """Test take profit and stop loss targets"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        # Take profit should be higher than stop loss
        assert preset["take_profit"] > preset["stop_loss"]
        
        # BANKNIFTY should have wider targets due to volatility
        assert preset["take_profit"] >= 2.0
        assert preset["stop_loss"] >= 1.0
        
        # Reward-risk ratio should be reasonable
        reward_risk = preset["take_profit"] / preset["stop_loss"]
        assert reward_risk >= 1.5  # At least 1.5:1
    
    def test_paper_trading_enabled(self):
        """Test paper trading is enabled by default"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        assert preset["paper_trading"] is True
    
    def test_additional_parameters(self):
        """Test BANKNIFTY-specific additional parameters"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        # Should have volume filter
        assert "min_volume" in preset
        assert preset["min_volume"] > 0
        
        # Should have ATR for volatility
        assert "atr_period" in preset
        assert preset["atr_period"] > 0
        
        # Should have trailing stop
        assert "trailing_stop" in preset
        assert preset["trailing_stop"] is True
        assert "trailing_stop_activation" in preset
        assert "trailing_stop_distance" in preset
        
        # Should have momentum-specific parameters
        assert "momentum_threshold" in preset
        assert "rsi_period" in preset
        assert "rsi_overbought" in preset
        assert "rsi_oversold" in preset
    
    def test_comparison_with_nifty(self):
        """Test BANKNIFTY preset differs appropriately from NIFTY"""
        banknifty = PRESET_CONFIGS["banknifty_futures"]
        nifty = PRESET_CONFIGS["nifty_futures"]
        
        # BANKNIFTY should have higher risk tolerance
        assert banknifty["risk_per_trade"] > nifty["risk_per_trade"]
        assert banknifty["max_daily_loss"] > nifty["max_daily_loss"]
        
        # BANKNIFTY should have different strategy
        assert banknifty["strategy"] != nifty["strategy"]
        
        # BANKNIFTY should have wider profit targets
        assert banknifty["take_profit"] > nifty["take_profit"]
        assert banknifty["stop_loss"] > nifty["stop_loss"]
        
        # BANKNIFTY should have lower base position size
        assert banknifty["base_position_size"] < nifty["base_position_size"]
    
    def test_configuration_validity(self):
        """Test that configuration values are valid"""
        preset = PRESET_CONFIGS["banknifty_futures"]
        
        # All numeric values should be positive
        assert preset["risk_per_trade"] > 0
        assert preset["max_positions"] > 0
        assert preset["max_daily_loss"] > 0
        assert preset["indicator_period"] > 0
        assert preset["base_position_size"] > 0
        assert preset["take_profit"] > 0
        assert preset["stop_loss"] > 0
        
        # Percentages should be reasonable
        assert preset["risk_per_trade"] <= 10  # Max 10% per trade
        assert preset["max_daily_loss"] <= 20  # Max 20% daily loss
        
        # Trading hours should be valid time strings
        assert ":" in preset["trading_hours"]["start"]
        assert ":" in preset["trading_hours"]["end"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
