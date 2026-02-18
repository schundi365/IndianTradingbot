"""
Test ML Confidence Filtering
Verifies that the new ml_min_confidence feature works correctly
"""

import sys
import logging
from src.ml_integration import MLIntegration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_ml_confidence_filtering():
    """Test ML confidence filtering with different thresholds"""
    
    print("=" * 80)
    print("TESTING ML CONFIDENCE FILTERING")
    print("=" * 80)
    print()
    
    # Test configurations with different ml_min_confidence values
    test_configs = [
        {'ml_min_confidence': 0.5, 'name': 'Low threshold (0.5)'},
        {'ml_min_confidence': 0.6, 'name': 'Default threshold (0.6)'},
        {'ml_min_confidence': 0.7, 'name': 'High threshold (0.7)'},
        {'ml_min_confidence': 0.8, 'name': 'Very high threshold (0.8)'},
    ]
    
    # Base config
    base_config = {
        'ml_enabled': True,
        'sentiment_enabled': False,
        'pattern_enabled': True,
        'technical_weight': 0.4,
        'ml_weight': 0.3,
        'sentiment_weight': 0.15,
        'pattern_weight': 0.15,
    }
    
    print("Testing ML Confidence Filtering:")
    print("-" * 80)
    print()
    
    for test_config in test_configs:
        config = {**base_config, **test_config}
        
        print(f"📊 Test: {test_config['name']}")
        print(f"   Threshold: {test_config['ml_min_confidence']}")
        print()
        
        try:
            # Initialize ML Integration
            ml_integration = MLIntegration(config)
            
            # Check if threshold was loaded correctly
            if hasattr(ml_integration, 'ml_min_confidence'):
                actual_threshold = ml_integration.ml_min_confidence
                print(f"   ✅ Threshold loaded: {actual_threshold}")
                
                if actual_threshold == test_config['ml_min_confidence']:
                    print(f"   ✅ Threshold matches expected value")
                else:
                    print(f"   ❌ Threshold mismatch! Expected {test_config['ml_min_confidence']}, got {actual_threshold}")
            else:
                print(f"   ❌ ml_min_confidence attribute not found!")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Restart the bot to see ML confidence filtering in action")
    print("2. Monitor logs for messages like:")
    print("   ⚠️  'ML signal filtered: confidence 0.550 < threshold 0.600'")
    print("   ✅ 'ML signal accepted: BUY with confidence 0.750'")
    print()
    print("To restart bot: python run_bot.py")
    print()

if __name__ == "__main__":
    test_ml_confidence_filtering()
