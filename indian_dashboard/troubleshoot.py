#!/usr/bin/env python3
"""
Indian Market Web Dashboard - Troubleshooting Script
Run this script to diagnose common issues
"""

import sys
import os
from pathlib import Path
import importlib.util

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(check, status, message=""):
    """Print check status"""
    symbol = "✓" if status else "✗"
    status_text = "PASS" if status else "FAIL"
    print(f"  [{symbol}] {check}: {status_text}")
    if message:
        print(f"      {message}")

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    required = (3, 8)
    
    print(f"  Current: Python {version.major}.{version.minor}.{version.micro}")
    print(f"  Required: Python {required[0]}.{required[1]}+")
    
    is_valid = version >= required
    print_status("Python Version", is_valid)
    return is_valid

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Dependency Check")
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('flask_limiter', 'Flask-Limiter'),
        ('cryptography', 'cryptography'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('pytz', 'pytz'),
    ]
    
    all_installed = True
    for module_name, package_name in required_packages:
        spec = importlib.util.find_spec(module_name)
        is_installed = spec is not None
        print_status(package_name, is_installed, 
                    "" if is_installed else f"Install with: pip install {package_name}")
        all_installed = all_installed and is_installed
    
    return all_installed

def check_directories():
    """Check if required directories exist"""
    print_header("Directory Structure Check")
    
    required_dirs = [
        'data/cache',
        'data/credentials',
        'configs',
        'logs',
        'static',
        'templates',
        'api',
        'services',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print_status(dir_path, exists,
                    "" if exists else "Will be created automatically")
        all_exist = all_exist and exists
    
    return all_exist

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Environment Configuration Check")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        print_status(".env file", False, 
                    f"Copy {env_example} to .env and configure")
        return False
    
    print_status(".env file", True)
    
    # Check for required variables
    required_vars = [
        'FLASK_SECRET_KEY',
        'ENCRYPTION_KEY',
    ]
    
    with open(env_file) as f:
        content = f.read()
    
    all_set = True
    for var in required_vars:
        # Check if variable exists and is not the default placeholder
        has_var = var in content
        is_set = has_var and 'change-this' not in content.lower().split(var)[1].split('\n')[0]
        
        print_status(var, is_set,
                    "" if is_set else "Set this variable in .env file")
        all_set = all_set and is_set
    
    return all_set

def check_port_availability():
    """Check if default port is available"""
    print_header("Port Availability Check")
    
    import socket
    
    host = '127.0.0.1'
    port = 8080
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        sock.close()
        print_status(f"Port {port}", True, "Available")
        return True
    except OSError:
        print_status(f"Port {port}", False, 
                    f"Port in use. Use --port flag to specify different port")
        return False

def check_file_permissions():
    """Check if we have write permissions"""
    print_header("File Permissions Check")
    
    test_dirs = ['data', 'configs', 'logs']
    all_writable = True
    
    for dir_path in test_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        
        is_writable = os.access(path, os.W_OK)
        print_status(f"{dir_path} writable", is_writable,
                    "" if is_writable else "Check directory permissions")
        all_writable = all_writable and is_writable
    
    return all_writable

def check_config_loading():
    """Check if config.py loads correctly"""
    print_header("Configuration Loading Check")
    
    try:
        from config import DASHBOARD_CONFIG, BROKER_CONFIGS, PRESET_CONFIGS
        print_status("config.py", True, "Configuration loaded successfully")
        
        # Check critical config values
        critical_keys = ['host', 'port', 'secret_key', 'cache_dir', 'config_dir', 'log_dir']
        all_present = all(key in DASHBOARD_CONFIG for key in critical_keys)
        print_status("Critical config keys", all_present)
        
        return True
    except Exception as e:
        print_status("config.py", False, f"Error: {str(e)}")
        return False

def check_imports():
    """Check if main application imports work"""
    print_header("Application Import Check")
    
    modules_to_check = [
        ('services.broker_manager', 'BrokerManager'),
        ('services.instrument_service', 'InstrumentService'),
        ('services.bot_controller', 'BotController'),
        ('services.credential_manager', 'CredentialManager'),
        ('api.broker', 'init_broker_api'),
        ('api.instruments', 'init_instruments_api'),
        ('api.config', 'init_config_api'),
        ('api.bot', 'init_bot_api'),
    ]
    
    all_imported = True
    for module_name, class_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            has_class = hasattr(module, class_name)
            print_status(f"{module_name}.{class_name}", has_class)
            all_imported = all_imported and has_class
        except Exception as e:
            print_status(f"{module_name}", False, f"Error: {str(e)}")
            all_imported = False
    
    return all_imported

def print_summary(results):
    """Print summary of all checks"""
    print_header("Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    
    if failed == 0:
        print("\n  ✓ All checks passed! You're ready to run the dashboard.")
        print("\n  Start with: python indian_dashboard.py")
    else:
        print("\n  ✗ Some checks failed. Please fix the issues above.")
        print("\n  Common fixes:")
        print("    - Install dependencies: pip install -r requirements.txt")
        print("    - Create .env file: cp .env.example .env")
        print("    - Set secret keys in .env file")
        print("    - Check file permissions")
    
    return failed == 0

def main():
    """Run all troubleshooting checks"""
    print("\n" + "=" * 60)
    print("  Indian Market Web Dashboard - Troubleshooting")
    print("=" * 60)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Directories': check_directories(),
        'Environment File': check_env_file(),
        'Port Availability': check_port_availability(),
        'File Permissions': check_file_permissions(),
        'Configuration': check_config_loading(),
        'Application Imports': check_imports(),
    }
    
    success = print_summary(results)
    
    print("\n" + "=" * 60 + "\n")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
