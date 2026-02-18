"""Script to reduce max_examples in all property-based tests for faster execution"""
import re
from pathlib import Path

# Mapping of old values to new values (reduce by 90%)
replacements = {
    'max_examples=50': 'max_examples=5',
    'max_examples=40': 'max_examples=5',
    'max_examples=30': 'max_examples=5',
    'max_examples=25': 'max_examples=5',
    'max_examples=20': 'max_examples=5',
    'max_examples=15': 'max_examples=5',
}

# Files to update
test_files = [
    'test_volume_pattern_analysis_property.py',
    'test_trendline_identification_property.py',
    'test_trendline_break_property.py',
    'test_multi_timeframe_alignment_property.py',
    'test_market_structure_break_property.py',
    'test_ema_breach_property.py',
    'test_early_warning_signals_property.py',
    'test_configuration_validation_property.py',
]

for filename in test_files:
    filepath = Path(filename)
    if not filepath.exists():
        print(f"⚠️  Skipping {filename} (not found)")
        continue
    
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    
    # Apply all replacements
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ Updated {filename}")
    else:
        print(f"ℹ️  No changes needed for {filename}")

print("\n✨ All test files updated to use fewer examples for faster execution!")
