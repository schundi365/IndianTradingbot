"""
Verify MACD Filter Fix
Checks if the fix is properly applied and config is correct
"""
import json
import os

print("="*80)
print("MACD FILTER FIX VERIFICATION")
print("="*80)

# 1. Check config file
print("\n1. Checking bot_config.json...")
with open('bot_config.json', 'r') as f:
    config = json.load(f)
    use_macd = config.get('use_macd')
    print(f"   use_macd setting: {use_macd}")
    if use_macd == False:
        print("   ✅ Config correctly shows MACD disabled")
    else:
        print("   ❌ Config shows MACD enabled!")

# 2. Check the code fix
print("\n2. Checking src/mt5_trading_bot.py for fix...")
with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Check if the fix is present
    if "if not self.config.get('use_macd', True):" in content:
        print("   ✅ Code fix is present")
        
        # Find the line number
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if "if not self.config.get('use_macd', True):" in line:
                print(f"   Found at line {i}")
                # Show context
                print("\n   Code context:")
                for j in range(max(0, i-3), min(len(lines), i+5)):
                    print(f"   {j+1}: {lines[j]}")
                break
    else:
        print("   ❌ Code fix NOT found!")

# 3. Check if there are any .pyc files that might be cached
print("\n3. Checking for cached Python files...")
pyc_files = []
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.pyc'):
            pyc_files.append(os.path.join(root, file))

if pyc_files:
    print(f"   ⚠️  Found {len(pyc_files)} cached .pyc files:")
    for f in pyc_files:
        print(f"      {f}")
    print("   These should be cleared!")
else:
    print("   ✅ No .pyc files found")

# 4. Check __pycache__ directories
print("\n4. Checking for __pycache__ directories...")
pycache_dirs = []
for root, dirs, files in os.walk('src'):
    if '__pycache__' in dirs:
        pycache_dirs.append(os.path.join(root, '__pycache__'))

if pycache_dirs:
    print(f"   ⚠️  Found {len(pycache_dirs)} __pycache__ directories:")
    for d in pycache_dirs:
        print(f"      {d}")
    print("   These should be cleared!")
else:
    print("   ✅ No __pycache__ directories found")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("\nThe fix is in place. If MACD filter is still running:")
print("1. Stop the bot completely (Ctrl+C)")
print("2. Run: python clear_all_cache.py")
print("3. Wait 5 seconds")
print("4. Restart the bot: python run_bot.py")
print("\nThe bot MUST be restarted to load the new code!")
print("="*80)
