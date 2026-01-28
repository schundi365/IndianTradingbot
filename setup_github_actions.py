#!/usr/bin/env python3
"""
GitHub Actions Setup Helper
Verifies everything is ready for automated builds
"""

import os
import sys
import subprocess

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"  ✅ {filepath:40} - {description}")
        return True
    else:
        print(f"  ❌ {filepath:40} - {description} (MISSING)")
        return False

def check_executable(filepath):
    """Check if a file is executable (Unix)"""
    if os.name != 'nt':  # Not Windows
        if os.access(filepath, os.X_OK):
            print(f"  ✅ {filepath} is executable")
            return True
        else:
            print(f"  ⚠️  {filepath} is not executable")
            print(f"     Run: chmod +x {filepath}")
            return False
    return True

def check_git_repo():
    """Check if this is a git repository"""
    try:
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("  ✅ Git repository initialized")
            return True
        else:
            print("  ❌ Not a git repository")
            print("     Run: git init")
            return False
    except FileNotFoundError:
        print("  ❌ Git not installed")
        return False
    except Exception as e:
        print(f"  ⚠️  Could not check git status: {e}")
        return False

def check_git_remote():
    """Check if git remote is configured"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            print("  ✅ Git remote configured")
            print(f"     {result.stdout.strip().split()[0]}: {result.stdout.strip().split()[1]}")
            return True
        else:
            print("  ⚠️  No git remote configured")
            print("     Run: git remote add origin <your-repo-url>")
            return False
    except Exception as e:
        print(f"  ⚠️  Could not check git remote: {e}")
        return False

def main():
    """Main setup verification"""
    print("=" * 70)
    print("GITHUB ACTIONS SETUP VERIFICATION")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # Check workflow files
    print("📁 Checking GitHub Actions workflow files...")
    workflows = [
        ('.github/workflows/build-macos.yml', 'macOS build workflow'),
        ('.github/workflows/build-all-platforms.yml', 'Multi-platform build workflow'),
    ]
    
    for filepath, description in workflows:
        if not check_file(filepath, description):
            all_ok = False
    print()
    
    # Check build scripts
    print("🔧 Checking build scripts...")
    scripts = [
        ('build_mac.sh', 'macOS build script'),
        ('build_windows.bat', 'Windows build script'),
    ]
    
    for filepath, description in scripts:
        if not check_file(filepath, description):
            all_ok = False
    
    # Check if scripts are executable
    if os.path.exists('build_mac.sh'):
        check_executable('build_mac.sh')
    print()
    
    # Check dependencies
    print("📦 Checking dependency files...")
    deps = [
        ('requirements.txt', 'Python dependencies'),
        ('requirements_web.txt', 'Web dashboard dependencies'),
    ]
    
    for filepath, description in deps:
        check_file(filepath, description)
    print()
    
    # Check documentation
    print("📖 Checking documentation...")
    docs = [
        ('GITHUB_ACTIONS_BUILD_GUIDE.md', 'GitHub Actions guide'),
        ('BUILD_EXECUTABLE_GUIDE.md', 'Build guide'),
        ('USER_GUIDE.md', 'User guide'),
    ]
    
    for filepath, description in docs:
        check_file(filepath, description)
    print()
    
    # Check git setup
    print("🔗 Checking Git configuration...")
    git_ok = check_git_repo()
    if git_ok:
        check_git_remote()
    print()
    
    # Summary
    print("=" * 70)
    print("SETUP SUMMARY")
    print("=" * 70)
    print()
    
    if all_ok:
        print("✅ All required files are present!")
        print()
        print("🚀 Next Steps:")
        print()
        print("1. Push to GitHub:")
        print("   git add .")
        print("   git commit -m 'Add GitHub Actions workflows'")
        print("   git push origin main")
        print()
        print("2. Go to GitHub Actions:")
        print("   https://github.com/yourusername/yourrepo/actions")
        print()
        print("3. Run workflow manually:")
        print("   - Click 'Build macOS Executable'")
        print("   - Click 'Run workflow'")
        print("   - Enter version: 2.0.0")
        print("   - Click 'Run workflow'")
        print()
        print("4. Download executable:")
        print("   - Wait 5-10 minutes")
        print("   - Download from Artifacts section")
        print()
        print("OR create a release:")
        print("   git tag v2.0.0")
        print("   git push origin v2.0.0")
        print()
    else:
        print("⚠️  Some files are missing!")
        print()
        print("Missing files need to be created before using GitHub Actions.")
        print("Check the errors above and create the missing files.")
        print()
    
    print("=" * 70)
    print()
    print("📚 For detailed instructions, see:")
    print("   GITHUB_ACTIONS_BUILD_GUIDE.md")
    print()
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
