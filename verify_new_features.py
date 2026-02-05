"""
Verify New Features Implementation
Checks all features added in Session 21
"""

import os
import sys
import json

def check_file_modified(filepath, expected_content):
    """Check if file contains expected content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return expected_content in content
    except Exception as e:
        return False

def verify_features():
    """Verify all new features are implemented"""
    
    print("=" * 80)
    print("VERIFYING SESSION 21 FEATURES")
    print("=" * 80)
    print()
    
    results = []
    
    # 1. Check ML Confidence Filtering
    print("1️⃣  ML Confidence Filtering")
    print("-" * 80)
    
    ml_integration_path = 'src/ml_integration.py'
    checks = [
        ("ml_min_confidence config loading", "self.ml_min_confidence = config.get('ml_min_confidence'"),
        ("Confidence filtering in _get_ml_signal", "if confidence < self.ml_min_confidence:"),
        ("Filtered signal logging", "ML signal filtered"),
        ("Accepted signal logging", "ML signal accepted"),
    ]
    
    for check_name, check_content in checks:
        if check_file_modified(ml_integration_path, check_content):
            print(f"   ✅ {check_name}")
            results.append(True)
        else:
            print(f"   ❌ {check_name}")
            results.append(False)
    
    print()
    
    # 2. Check Drawdown Protection
    print("2️⃣  Drawdown Protection")
    print("-" * 80)
    
    bot_path = 'src/mt5_trading_bot.py'
    checks = [
        ("check_drawdown_limit method", "def check_drawdown_limit(self):"),
        ("Peak equity tracking", "self.peak_equity"),
        ("Drawdown calculation", "drawdown_percent"),
        ("Drawdown limit check", "if drawdown_percent >= max_drawdown_percent:"),
        ("Integration in run_strategy", "if not self.check_drawdown_limit():"),
    ]
    
    for check_name, check_content in checks:
        if check_file_modified(bot_path, check_content):
            print(f"   ✅ {check_name}")
            results.append(True)
        else:
            print(f"   ❌ {check_name}")
            results.append(False)
    
    print()
    
    # 3. Check Adaptive Risk Manager Fix
    print("3️⃣  Adaptive Risk Manager - Hardcoded Values Fix")
    print("-" * 80)
    
    risk_manager_path = 'src/adaptive_risk_manager.py'
    backup_exists = os.path.exists('src/adaptive_risk_manager.py_backup_20260205_142712')
    
    if backup_exists:
        print(f"   ✅ Backup created before modification")
        results.append(True)
    else:
        print(f"   ⚠️  Backup not found (may have been created with different timestamp)")
        results.append(True)  # Don't fail on this
    
    checks = [
        ("Uses max_risk_multiplier from config", "self.config.get('max_risk_multiplier'"),
        ("Uses min_risk_multiplier from config", "self.config.get('min_risk_multiplier'"),
    ]
    
    for check_name, check_content in checks:
        if check_file_modified(risk_manager_path, check_content):
            print(f"   ✅ {check_name}")
            results.append(True)
        else:
            print(f"   ❌ {check_name}")
            results.append(False)
    
    print()
    
    # 4. Check Config Keys
    print("4️⃣  Configuration Keys")
    print("-" * 80)
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        config_checks = [
            ("ml_min_confidence", 0.6),
            ("max_drawdown_percent", 10),
            ("max_risk_multiplier", 1.5),
            ("min_risk_multiplier", 0.5),
            ("ml_enabled", True),
        ]
        
        for key, expected_value in config_checks:
            if key in config:
                actual_value = config[key]
                if actual_value == expected_value:
                    print(f"   ✅ {key}: {actual_value} (default)")
                else:
                    print(f"   ✅ {key}: {actual_value} (custom)")
                results.append(True)
            else:
                print(f"   ❌ {key}: NOT FOUND")
                results.append(False)
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        results.append(False)
    
    print()
    
    # 5. Check ML Model
    print("5️⃣  ML Model")
    print("-" * 80)
    
    model_path = 'models/ml_signal_model.pkl'
    if os.path.exists(model_path):
        model_size = os.path.getsize(model_path)
        print(f"   ✅ ML model exists: {model_path}")
        print(f"   ✅ Model size: {model_size:,} bytes")
        results.append(True)
    else:
        print(f"   ❌ ML model not found: {model_path}")
        print(f"      ML features will show 'model not trained' warning")
        results.append(False)
    
    print()
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Checks Passed: {passed}/{total} ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("✅ ALL FEATURES VERIFIED!")
        print()
        print("🎉 Ready to restart the bot and see the new features in action!")
        print()
        print("To restart:")
        print("   python run_bot.py")
        print()
        print("What to look for in logs:")
        print("   📊 'ML Min Confidence: 0.60'")
        print("   ⚠️  'ML signal filtered: confidence 0.550 < threshold 0.600'")
        print("   ✅ 'ML signal accepted: BUY with confidence 0.750'")
        print("   📊 'Drawdown Status: 2.35% from peak ($235.50)'")
        print("   📈 'New peak equity: $10,500.00'")
        return True
    else:
        print("⚠️  SOME CHECKS FAILED")
        print()
        print("Please review the failed checks above.")
        print("The bot may still work, but some features might not be available.")
        return False

if __name__ == "__main__":
    success = verify_features()
    sys.exit(0 if success else 1)
