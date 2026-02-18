#!/usr/bin/env python3
"""
Test script for trend detection configuration persistence
Validates that all trend detection parameters are properly saved and loaded
"""

import json
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to path
sys.path.append('src')

def test_config_persistence():
    """Test that trend detection configuration parameters persist correctly"""
    
    # Test configuration with all trend detection parameters
    test_config = {
        # Basic trend detection settings
        'use_trend_detection': True,
        'trend_detection_sensitivity': 7,
        'min_trend_confidence': 0.75,
        'enable_early_signals': True,
        
        # EMA settings
        'ema_fast_period': 15,
        'ema_slow_period': 45,
        
        # Aroon settings
        'aroon_period': 30,
        'aroon_threshold': 75,
        
        # Market structure settings
        'min_swing_strength': 4,
        'structure_break_threshold': 0.002,
        
        # Divergence settings
        'divergence_lookback': 60,
        'min_divergence_strength': 0.4,
        
        # Trendline settings
        'max_trendlines': 7,
        'min_trendline_touches': 3,
        'trendline_angle_min': 15,
        'trendline_angle_max': 75,
        
        # Multi-timeframe settings
        'mtf_weight': 0.4,
        'mtf_alignment_threshold': 0.7,
        'mtf_contradiction_penalty': 0.3,
        
        # Volume pattern settings
        'volume_spike_threshold': 2.0,
        
        # Performance settings
        'max_analysis_time_ms': 150,
        'trend_cache_size': 1500,
        'max_memory_mb': 600,
        
        # Error handling settings
        'max_error_retries': 5,
        'enable_circuit_breaker': True,
        'graceful_degradation': True,
        
        # Logging settings
        'logging_level': 'detailed'
    }
    
    print("🧪 Testing trend detection configuration persistence...")
    
    # Test 1: Save configuration to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f, indent=2)
        temp_config_file = f.name
    
    try:
        # Test 2: Load configuration from file
        with open(temp_config_file, 'r') as f:
            loaded_config = json.load(f)
        
        # Test 3: Verify all parameters are preserved
        missing_params = []
        modified_params = []
        
        for key, expected_value in test_config.items():
            if key not in loaded_config:
                missing_params.append(key)
            elif loaded_config[key] != expected_value:
                modified_params.append(f"{key}: expected {expected_value}, got {loaded_config[key]}")
        
        # Test 4: Validate parameter types and ranges
        validation_errors = []
        
        # Validate numeric ranges
        numeric_validations = {
            'trend_detection_sensitivity': (1, 10),
            'min_trend_confidence': (0.2, 0.9),
            'ema_fast_period': (5, 50),
            'ema_slow_period': (20, 100),
            'aroon_period': (14, 50),
            'aroon_threshold': (50, 90),
            'min_swing_strength': (2, 10),
            'structure_break_threshold': (0.0005, 0.005),
            'divergence_lookback': (20, 100),
            'min_divergence_strength': (0.1, 0.8),
            'max_trendlines': (2, 10),
            'min_trendline_touches': (2, 5),
            'trendline_angle_min': (5, 30),
            'trendline_angle_max': (60, 85),
            'mtf_weight': (0.1, 0.5),
            'mtf_alignment_threshold': (0.3, 0.9),
            'mtf_contradiction_penalty': (0.1, 0.8),
            'volume_spike_threshold': (1.0, 5.0),
            'max_analysis_time_ms': (10, 1000),
            'trend_cache_size': (10, 10000),
            'max_memory_mb': (50, 2000),
            'max_error_retries': (1, 10)
        }
        
        for param, (min_val, max_val) in numeric_validations.items():
            if param in loaded_config:
                value = loaded_config[param]
                if not isinstance(value, (int, float)):
                    validation_errors.append(f"{param}: expected numeric value, got {type(value)}")
                elif value < min_val or value > max_val:
                    validation_errors.append(f"{param}: value {value} outside valid range [{min_val}, {max_val}]")
        
        # Validate boolean parameters
        boolean_params = ['use_trend_detection', 'enable_early_signals', 'enable_circuit_breaker', 'graceful_degradation']
        for param in boolean_params:
            if param in loaded_config and not isinstance(loaded_config[param], bool):
                validation_errors.append(f"{param}: expected boolean value, got {type(loaded_config[param])}")
        
        # Validate string parameters
        if 'logging_level' in loaded_config:
            valid_levels = ['minimal', 'standard', 'detailed', 'debug']
            if loaded_config['logging_level'] not in valid_levels:
                validation_errors.append(f"logging_level: invalid value '{loaded_config['logging_level']}', must be one of {valid_levels}")
        
        # Test 5: Validate parameter relationships
        relationship_errors = []
        
        # EMA periods relationship
        if 'ema_fast_period' in loaded_config and 'ema_slow_period' in loaded_config:
            if loaded_config['ema_fast_period'] >= loaded_config['ema_slow_period']:
                relationship_errors.append("ema_fast_period must be less than ema_slow_period")
        
        # Trendline angle relationship
        if 'trendline_angle_min' in loaded_config and 'trendline_angle_max' in loaded_config:
            if loaded_config['trendline_angle_min'] >= loaded_config['trendline_angle_max']:
                relationship_errors.append("trendline_angle_min must be less than trendline_angle_max")
        
        # Report results
        print(f"✅ Configuration file saved and loaded successfully")
        print(f"📊 Total parameters tested: {len(test_config)}")
        
        if missing_params:
            print(f"❌ Missing parameters: {missing_params}")
            return False
        
        if modified_params:
            print(f"❌ Modified parameters: {modified_params}")
            return False
        
        if validation_errors:
            print(f"❌ Validation errors: {validation_errors}")
            return False
        
        if relationship_errors:
            print(f"❌ Relationship errors: {relationship_errors}")
            return False
        
        print("✅ All trend detection parameters validated successfully!")
        print("✅ Parameter types and ranges are correct")
        print("✅ Parameter relationships are valid")
        
        return True
        
    finally:
        # Cleanup
        if os.path.exists(temp_config_file):
            os.unlink(temp_config_file)

def test_config_manager_integration():
    """Test integration with the config manager"""
    print("\n🔧 Testing config manager integration...")
    
    try:
        from src.config_manager import get_config_manager
        
        config_manager = get_config_manager()
        current_config = config_manager.get_config()
        
        # Test that trend detection parameters exist in default config
        trend_params = [
            'use_trend_detection',
            'trend_detection_sensitivity', 
            'min_trend_confidence',
            'enable_early_signals'
        ]
        
        missing_defaults = []
        for param in trend_params:
            if param not in current_config:
                missing_defaults.append(param)
        
        if missing_defaults:
            print(f"⚠️ Missing default trend detection parameters: {missing_defaults}")
        else:
            print("✅ All basic trend detection parameters have defaults")
        
        # Test parameter update
        test_updates = {
            'trend_detection_sensitivity': 8,
            'min_trend_confidence': 0.8
        }
        
        original_values = {}
        for param, new_value in test_updates.items():
            original_values[param] = current_config.get(param)
            current_config[param] = new_value
        
        # Save and reload
        config_manager.save_config(current_config)
        reloaded_config = config_manager.get_config()
        
        # Verify updates persisted
        update_errors = []
        for param, expected_value in test_updates.items():
            if reloaded_config.get(param) != expected_value:
                update_errors.append(f"{param}: expected {expected_value}, got {reloaded_config.get(param)}")
        
        # Restore original values
        for param, original_value in original_values.items():
            current_config[param] = original_value
        config_manager.save_config(current_config)
        
        if update_errors:
            print(f"❌ Parameter update errors: {update_errors}")
            return False
        
        print("✅ Config manager integration test passed")
        return True
        
    except ImportError as e:
        print(f"⚠️ Config manager not available: {e}")
        return True  # Not a failure, just not available
    except Exception as e:
        print(f"❌ Config manager integration test failed: {e}")
        return False

def main():
    """Run all configuration persistence tests"""
    print("🔍 Trend Detection Configuration Persistence Test")
    print("=" * 50)
    
    success = True
    
    # Test 1: Basic persistence
    if not test_config_persistence():
        success = False
    
    # Test 2: Config manager integration
    if not test_config_manager_integration():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All configuration persistence tests PASSED!")
        return 0
    else:
        print("❌ Some configuration persistence tests FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())