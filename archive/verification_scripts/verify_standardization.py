"""
Verify Configuration Standardization
"""

from src.config_manager import ConfigManager
import json

print("=" * 80)
print("CONFIGURATION STANDARDIZATION VERIFICATION")
print("=" * 80)
print()

# Create a test config manager
cm = ConfigManager('test_verify_standardization.json')
config = cm.get_config()

print("Standardized Values:")
print("-" * 80)
print(f"fast_ma_period:  {config['fast_ma_period']} (expected: 10)")
print(f"slow_ma_period:  {config['slow_ma_period']} (expected: 21)")
print(f"dead_hours:      {config['dead_hours']}")
print(f"                 (expected: [0, 1, 2, 17, 20, 21, 22])")
print(f"golden_hours:    {config['golden_hours']}")
print(f"                 (expected: [8, 11, 13, 14, 15, 19, 23])")
print()

# Verify values
errors = []

if config['fast_ma_period'] != 10:
    errors.append(f"fast_ma_period is {config['fast_ma_period']}, expected 10")

if config['slow_ma_period'] != 21:
    errors.append(f"slow_ma_period is {config['slow_ma_period']}, expected 21")

expected_dead = [0, 1, 2, 17, 20, 21, 22]
if config['dead_hours'] != expected_dead:
    errors.append(f"dead_hours is {config['dead_hours']}, expected {expected_dead}")

expected_golden = [8, 11, 13, 14, 15, 19, 23]
if config['golden_hours'] != expected_golden:
    errors.append(f"golden_hours is {config['golden_hours']}, expected {expected_golden}")

if errors:
    print("❌ VERIFICATION FAILED:")
    print("-" * 80)
    for error in errors:
        print(f"  • {error}")
else:
    print("✅ VERIFICATION PASSED!")
    print("-" * 80)
    print("All standardized values are correct.")

print()
print("=" * 80)
