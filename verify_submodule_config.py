"""
Verify Sub-Module Configuration Usage
Check that trend detection, ML, and other modules use config properly
"""

import os

modules_to_check = {
    'src/trend_detection_engine.py': [
        'max_analysis_time_ms',
        'min_trend_confidence',
        'aroon_period',
        'ema_fast_period',
        'ema_slow_period',
        'divergence_lookback',
        'min_swing_strength',
    ],
    'src/ml_integration.py': [
        'ml_enabled',
        'ml_weight',
        'technical_weight',
        'pattern_weight',
        'sentiment_weight',
        'ml_min_confidence',
    ],
    'src/volume_analyzer.py': [
        'volume_ma_period',
        'normal_volume_ma',
        'high_volume_ma',
        'very_high_volume_ma',
    ],
    'src/adaptive_risk_manager.py': [
        'max_risk_multiplier',
        'min_risk_multiplier',
        'max_drawdown_percent',
    ],
}

print("="*100)
print("SUB-MODULE CONFIGURATION USAGE VERIFICATION")
print("="*100)

total_checked = 0
total_found = 0
issues = []

for filepath, config_keys in modules_to_check.items():
    if not os.path.exists(filepath):
        print(f"\n[SKIP] {filepath} - File not found")
        continue
    
    print(f"\n{'='*100}")
    print(f"FILE: {filepath}")
    print(f"{'='*100}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\nChecking {len(config_keys)} config keys...")
    
    for key in config_keys:
        total_checked += 1
        # Check if config key is used
        patterns = [
            f'config.get("{key}"',
            f'config.get(\'{key}\'',
            f'self.config.get("{key}"',
            f'self.config.get(\'{key}\'',
            f'config["{key}"]',
            f'config[\'{key}\']',
        ]
        
        found = any(pattern in content for pattern in patterns)
        
        if found:
            print(f"  [OK] {key}")
            total_found += 1
        else:
            print(f"  [!] {key} - NOT FOUND")
            issues.append((filepath, key))

print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

print(f"\nTotal config keys checked: {total_checked}")
print(f"Found in code: {total_found}")
print(f"Not found: {len(issues)}")

if issues:
    print("\nConfig keys not found in code:")
    for filepath, key in issues:
        print(f"  - {key} (expected in {filepath})")
    
    print("\nPossible reasons:")
    print("  1. Config key is unused (can be removed)")
    print("  2. Config key is used with different name")
    print("  3. Feature not yet implemented")
    print("  4. Hardcoded value used instead (BUG!)")

print(f"\n{'='*100}")
print("RECOMMENDATIONS")
print(f"{'='*100}")

print("\n1. For unused config keys: Remove from bot_config.json and dashboard")
print("2. For hardcoded values: Update code to use config.get()")
print("3. For unimplemented features: Either implement or remove config")
print("4. Test that changing config values affects module behavior")

print(f"\n{'='*100}")
print("NEXT STEPS")
print(f"{'='*100}")

print("\n1. Review the issues found above")
print("2. Decide: Remove unused keys OR implement their usage")
print("3. Update dashboard to match actual config usage")
print("4. Create config validation to catch unused keys")
print("5. Document which config keys affect which modules")
