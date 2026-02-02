#!/usr/bin/env python3
"""
Test script for enhanced logging system
Tests the new PerformanceLogger and performance timing features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mt5_trading_bot import PerformanceLogger, performance_timer, setup_enhanced_logging
import time
import pandas as pd
import numpy as np

# Setup enhanced logging
setup_enhanced_logging()

# Create test logger
logger = PerformanceLogger("test_enhanced_logging")

def test_basic_logging():
    """Test basic enhanced logging features"""
    logger.info("🧪 Testing enhanced logging system")
    logger.info("This should show line numbers, package names, and timestamps")
    logger.warning("This is a warning message")
    logger.error("This is an error message (not a real error)")
    logger.debug("This is a debug message")

@performance_timer("Test Operation")
def test_performance_timing():
    """Test performance timing decorator"""
    logger.info("Starting performance test operation")
    time.sleep(0.1)  # Simulate work
    logger.info("Completed performance test operation")
    return "test_result"

def test_operation_timing():
    """Test manual operation timing"""
    logger.start_operation("Manual Operation Test")
    time.sleep(0.05)  # Simulate work
    logger.info("Doing some work in manual operation")
    time.sleep(0.05)  # More work
    logger.end_operation("Manual Operation Test", "- completed successfully")

def test_volume_analyzer_logging():
    """Test volume analyzer enhanced logging"""
    try:
        from src.volume_analyzer import VolumeAnalyzer
        
        # Create test config
        config = {
            'use_volume_filter': True,
            'min_volume_ma': 0.7,
            'volume_ma_period': 20
        }
        
        # Initialize volume analyzer (should show enhanced logging)
        volume_analyzer = VolumeAnalyzer(config)
        
        # Create test data
        test_data = pd.DataFrame({
            'tick_volume': np.random.randint(100, 1000, 50),
            'close': np.random.uniform(2000, 2100, 50),
            'high': np.random.uniform(2050, 2150, 50),
            'low': np.random.uniform(1950, 2050, 50),
            'open': np.random.uniform(2000, 2100, 50)
        })
        
        # Test volume analysis (should show detailed logging)
        result = volume_analyzer.is_above_average_volume(test_data)
        logger.info(f"Volume analysis result: {result}")
        
    except ImportError as e:
        logger.warning(f"Could not test volume analyzer: {e}")

def main():
    """Run all enhanced logging tests"""
    logger.info("="*80)
    logger.info("🚀 ENHANCED LOGGING SYSTEM TEST STARTING")
    logger.info("="*80)
    
    # Test 1: Basic logging
    logger.info("📝 Test 1: Basic Enhanced Logging")
    test_basic_logging()
    
    # Test 2: Performance timing decorator
    logger.info("\n⏱️ Test 2: Performance Timing Decorator")
    result = test_performance_timing()
    logger.info(f"Function returned: {result}")
    
    # Test 3: Manual operation timing
    logger.info("\n🔧 Test 3: Manual Operation Timing")
    test_operation_timing()
    
    # Test 4: Volume analyzer logging
    logger.info("\n📊 Test 4: Volume Analyzer Enhanced Logging")
    test_volume_analyzer_logging()
    
    logger.info("="*80)
    logger.info("✅ ENHANCED LOGGING SYSTEM TEST COMPLETED")
    logger.info("="*80)
    
    print("\n" + "="*80)
    print("🎉 Enhanced Logging Test Complete!")
    print("Check the trading_bot.log file to see the enhanced logging output")
    print("You should see:")
    print("  • Line numbers and package names in log entries")
    print("  • Performance timing for operations")
    print("  • Detailed timestamps with milliseconds")
    print("  • Duration tracking between log entries")
    print("="*80)

if __name__ == "__main__":
    main()