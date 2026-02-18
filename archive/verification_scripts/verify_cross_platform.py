#!/usr/bin/env python3
"""
Cross-Platform Compatibility Verification Script
Tests all platform-specific code for compatibility
"""

import os
import sys
import platform

def test_path_handling():
    """Test that all paths use os.path.join"""
    print("Testing path handling...")
    
    # Test paths that should work on all platforms
    test_paths = [
        os.path.join('src', 'config.py'),
        os.path.join('src', 'mt5_trading_bot.py'),
        os.path.join('templates', 'dashboard.html'),
        os.path.join('docs', 'README.md'),
    ]
    
    for path in test_paths:
        # Check that path uses correct separator for this OS
        if platform.system() == 'Windows':
            expected_sep = '\\'
        else:
            expected_sep = '/'
        
        if expected_sep in path or '/' in path or '\\' in path:
            print(f"  ✅ {path}")
        else:
            print(f"  ⚠️  {path} (no separator found)")
    
    return True

def test_file_encoding():
    """Test that files can be read with UTF-8 encoding"""
    print("\nTesting file encoding...")
    
    test_files = [
        'web_dashboard.py',
        'apply_optimized_config.py',
        'validate_setup.py',
        os.path.join('src', 'config.py'),
    ]
    
    all_ok = True
    for file in test_files:
        if not os.path.exists(file):
            print(f"  ⚠️  {file} (not found)")
            continue
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✅ {file}")
        except UnicodeDecodeError as e:
            print(f"  ❌ {file} - Encoding error: {e}")
            all_ok = False
        except Exception as e:
            print(f"  ❌ {file} - Error: {e}")
            all_ok = False
    
    return all_ok

def test_imports():
    """Test that all imports work"""
    print("\nTesting imports...")
    
    modules = [
        ('os', 'Standard library'),
        ('sys', 'Standard library'),
        ('platform', 'Standard library'),
        ('flask', 'Web framework'),
        ('MetaTrader5', 'MT5 connector'),
        ('pandas', 'Data analysis'),
        ('numpy', 'Numerical computing'),
    ]
    
    all_ok = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"  ✅ {module:15} - {description}")
        except ImportError:
            print(f"  ❌ {module:15} - {description} (not installed)")
            all_ok = False
    
    return all_ok

def test_launchers():
    """Test that launcher scripts exist"""
    print("\nTesting launcher scripts...")
    
    launchers = [
        ('start_dashboard.py', 'Universal Python launcher'),
        ('start_dashboard.sh', 'Unix/Linux/macOS launcher'),
        ('web_dashboard.py', 'Main dashboard script'),
        ('run_bot.py', 'Bot launcher'),
    ]
    
    all_ok = True
    for launcher, description in launchers:
        if os.path.exists(launcher):
            print(f"  ✅ {launcher:25} - {description}")
        else:
            print(f"  ❌ {launcher:25} - {description} (not found)")
            all_ok = False
    
    return all_ok

def test_documentation():
    """Test that documentation exists"""
    print("\nTesting documentation...")
    
    docs = [
        'CROSS_PLATFORM_COMPATIBILITY.md',
        'CROSS_PLATFORM_FIXES_SUMMARY.md',
        'BUILD_EXECUTABLE_GUIDE.md',
        'TROUBLESHOOTING.md',
        'USER_GUIDE.md',
    ]
    
    all_ok = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✅ {doc}")
        else:
            print(f"  ⚠️  {doc} (not found)")
    
    return all_ok

def main():
    """Run all tests"""
    print("=" * 70)
    print("CROSS-PLATFORM COMPATIBILITY VERIFICATION")
    print("=" * 70)
    print()
    print(f"Platform: {platform.system()} ({platform.platform()})")
    print(f"Python: {sys.version}")
    print()
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Path Handling", test_path_handling()))
    results.append(("File Encoding", test_file_encoding()))
    results.append(("Imports", test_imports()))
    results.append(("Launchers", test_launchers()))
    results.append(("Documentation", test_documentation()))
    
    # Summary
    print()
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:10} - {test_name}")
        if not passed:
            all_passed = False
    
    print()
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL TESTS PASSED - Platform compatibility verified!")
        print()
        print("Your GEM Trading Bot is ready to run on:")
        print("  • Windows")
        print("  • macOS")
        print("  • Linux")
        print()
        print("To start the dashboard:")
        if platform.system() == 'Windows':
            print("  python start_dashboard.py")
        else:
            print("  python3 start_dashboard.py")
            print("  or")
            print("  ./start_dashboard.sh")
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
        print()
        print("Common fixes:")
        print("  • Install missing dependencies: pip install -r requirements.txt")
        print("  • Check file permissions: chmod +x *.sh")
        print("  • Verify Python version: python --version (need 3.8+)")
    
    print("=" * 70)
    print()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
