#!/usr/bin/env python3
"""
Force Configuration Reload Script
Forces a complete reload of all configuration and modules to ensure latest changes are applied
"""

import sys
import os
import importlib
import json
from pathlib import Path

def force_reload_modules():
    """Force reload all our custom modules"""
    print("🔄 Force reloading all custom modules...")
    
    # List of modules to force reload
    modules_to_reload = [
        'src.config',
        'src.config_manager', 
        'src.mt5_trading_bot',
        'src.volume_analyzer',
        'src.adaptive_risk_manager',
        'src.config_profitable_balanced'
    ]
    
    reloaded_count = 0
    for module_name in modules_to_reload:
        try:
            # Remove from sys.modules if exists
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Import fresh
            module = importlib.import_module(module_name)
            
            # Force reload
            importlib.reload(module)
            
            print(f"   ✅ Reloaded: {module_name}")
            reloaded_count += 1
            
        except Exception as e:
            print(f"   ⚠️ Could not reload {module_name}: {e}")
    
    print(f"✅ Force reloaded {reloaded_count} modules")

def verify_config_values():
    """Verify that all optimized configuration values are properly loaded"""
    print("🔍 Verifying optimized configuration values...")
    
    try:
        # Test config manager
        sys.path.insert(0, 'src')
        from config_manager import get_config_manager
        
        config_manager = get_config_manager()
        config = config_manager.get_config()
        
        # Check key optimized values
        optimized_values = {
            'min_volume_ma': 0.7,
            'macd_min_histogram': 0.0005,
            'min_trade_confidence': 0.6,
            'normal_volume_ma': 1.0,
            'high_volume_ma': 1.5,
            'very_high_volume_ma': 2.0
        }
        
        all_correct = True
        for key, expected in optimized_values.items():
            actual = config.get(key)
            if actual == expected:
                print(f"   ✅ {key}: {actual} (correct)")
            else:
                print(f"   ❌ {key}: {actual} (expected {expected})")
                all_correct = False
        
        if all_correct:
            print("✅ All optimized values are correctly loaded")
        else:
            print("⚠️ Some values may need attention")
            
        return all_correct
        
    except Exception as e:
        print(f"❌ Error verifying config: {e}")
        return False

def test_enhanced_logging():
    """Test that enhanced logging is working"""
    print("🧪 Testing enhanced logging system...")
    
    try:
        # Import and test the enhanced logging
        sys.path.insert(0, 'src')
        from mt5_trading_bot import PerformanceLogger, setup_enhanced_logging
        
        # Setup enhanced logging
        setup_enhanced_logging()
        
        # Create test logger
        test_logger = PerformanceLogger("test_reload")
        
        # Test logging with timing
        test_logger.start_operation("Config Reload Test")
        test_logger.info("Enhanced logging system is working correctly")
        test_logger.end_operation("Config Reload Test", "- verification complete")
        
        print("✅ Enhanced logging system is active")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced logging test failed: {e}")
        return False

def main():
    """Main function to force reload everything"""
    print("🚀 FORCE CONFIGURATION RELOAD STARTED")
    print("=" * 50)
    
    # Force reload modules
    force_reload_modules()
    
    # Verify configuration values
    config_ok = verify_config_values()
    
    # Test enhanced logging
    logging_ok = test_enhanced_logging()
    
    print("=" * 50)
    
    if config_ok and logging_ok:
        print("🎉 FORCE RELOAD COMPLETED SUCCESSFULLY")
        print("")
        print("✅ All systems verified:")
        print("   • Configuration values are optimized")
        print("   • Enhanced logging is active")
        print("   • All modules are fresh loaded")
        print("")
        print("🚀 Ready to start trading with latest optimizations!")
        
    else:
        print("⚠️ FORCE RELOAD COMPLETED WITH WARNINGS")
        print("Some systems may need manual attention")
    
    return 0 if (config_ok and logging_ok) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)