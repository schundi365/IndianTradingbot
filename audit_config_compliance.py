"""
Configuration Compliance Audit
Scan the codebase for hardcoded values that should use config
"""

import re
import json

# Load current config to see what should be configurable
with open('bot_config.json', 'r') as f:
    config = json.load(f)

print("="*100)
print("CONFIGURATION COMPLIANCE AUDIT")
print("="*100)

# Known hardcoded values to search for
hardcoded_patterns = {
    'RSI Thresholds': [
        (r'\b70\b(?!.*config)', 'RSI overbought threshold (should use config.get("rsi_overbought", 70))'),
        (r'\b30\b(?!.*config)', 'RSI oversold threshold (should use config.get("rsi_oversold", 30))'),
        (r'\b50\b(?!.*RSI)', 'RSI neutral level'),
    ],
    'MACD Values': [
        (r'\b12\b(?!.*config)', 'MACD fast period (should use config.get("macd_fast", 12))'),
        (r'\b26\b(?!.*config)', 'MACD slow period (should use config.get("macd_slow", 26))'),
        (r'\b9\b(?!.*config)', 'MACD signal period (should use config.get("macd_signal", 9))'),
        (r'0\.0005', 'MACD histogram threshold (should use config.get("macd_min_histogram"))'),
        (r'0\.0003', 'MACD histogram threshold (should use config.get("macd_min_histogram"))'),
    ],
    'ADX Values': [
        (r'\b25\b(?!.*config)', 'ADX minimum strength (should use config.get("adx_min_strength", 25))'),
        (r'\b14\b(?!.*config)', 'ADX period (should use config.get("adx_period", 14))'),
    ],
    'ATR Values': [
        (r'\b2\.0\b(?!.*config)', 'ATR multiplier (should use config.get("atr_multiplier", 2.0))'),
        (r'\b1\.5\b(?!.*config)', 'ATR multiplier variant'),
    ],
    'MA Periods': [
        (r'\b20\b(?!.*config)', 'Fast MA period (should use config.get("fast_ma_period", 20))'),
        (r'\b50\b(?!.*config)', 'Slow MA period (should use config.get("slow_ma_period", 50))'),
        (r'\b100\b(?!.*config)', 'Trend MA period (should use config.get("trend_ma_period", 100))'),
    ],
    'TP/SL Ratios': [
        (r'\[1\.5,\s*2\.5,\s*4\.0\]', 'TP levels (should use config.get("tp_levels"))'),
        (r'\b1\.2\b(?!.*config)', 'Reward ratio (should use config.get("reward_ratio"))'),
    ],
    'Volume Thresholds': [
        (r'\b1\.0\b(?!.*volume.*config)', 'Volume MA threshold'),
        (r'\b1\.5\b(?!.*volume.*config)', 'High volume threshold'),
        (r'\b2\.0\b(?!.*volume.*config)', 'Very high volume threshold'),
    ],
    'Timeouts': [
        (r'\b100\b(?!.*ms.*config)', 'Analysis timeout (should use config.get("max_analysis_time_ms"))'),
        (r'\b250\b(?!.*ms.*config)', 'Analysis timeout variant'),
    ],
}

# Files to audit
files_to_check = [
    'src/mt5_trading_bot.py',
    'src/trend_detection_engine.py',
    'src/volume_analyzer.py',
    'src/adaptive_risk_manager.py',
    'src/dynamic_tp_manager.py',
    'src/dynamic_sl_manager.py',
]

issues_found = []

print("\nScanning files for hardcoded values...\n")

for filepath in files_to_check:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        print(f"\n{'='*100}")
        print(f"FILE: {filepath}")
        print(f"{'='*100}")
        
        file_issues = []
        
        for category, patterns in hardcoded_patterns.items():
            for pattern, description in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()
                    
                    # Skip if it's in a comment or already using config
                    if line_content.startswith('#') or 'config.get' in line_content or 'self.config' in line_content:
                        continue
                    
                    file_issues.append({
                        'category': category,
                        'line': line_num,
                        'content': line_content,
                        'description': description,
                        'value': match.group()
                    })
        
        if file_issues:
            for issue in file_issues:
                print(f"\n[!] {issue['category']}")
                print(f"   Line {issue['line']}: {issue['content'][:80]}")
                print(f"   Found: {issue['value']}")
                print(f"   Issue: {issue['description']}")
            
            issues_found.extend([(filepath, issue) for issue in file_issues])
        else:
            print("\n[OK] No hardcoded values found")
    
    except FileNotFoundError:
        print(f"\n[ERROR] File not found: {filepath}")
    except Exception as e:
        print(f"\n[ERROR] Error reading {filepath}: {e}")

print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

print(f"\nTotal issues found: {len(issues_found)}")

if issues_found:
    print("\nIssues by category:")
    by_category = {}
    for filepath, issue in issues_found:
        cat = issue['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append((filepath, issue))
    
    for category, items in by_category.items():
        print(f"\n{category}: {len(items)} issues")
        for filepath, issue in items[:3]:  # Show first 3
            print(f"  - {filepath}:{issue['line']}")

print(f"\n{'='*100}")
print("CONFIGURATION KEYS IN bot_config.json")
print(f"{'='*100}")

print("\nAll available config keys:")
for key in sorted(config.keys()):
    print(f"  - {key}: {config[key]}")

print(f"\n{'='*100}")
print("RECOMMENDATIONS")
print(f"{'='*100}")

print("\n1. Replace hardcoded values with config.get() calls")
print("2. Add missing config keys to bot_config.json")
print("3. Update dashboard to expose all configurable values")
print("4. Test that config changes are respected")

print("\nNext: Run 'python fix_hardcoded_values.py' to automatically fix issues")
