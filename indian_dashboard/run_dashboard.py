#!/usr/bin/env python3
"""
Indian Market Web Dashboard - Startup Script
Entry point with command-line arguments and startup checks
"""

import argparse
import sys
import os
import logging
from pathlib import Path
import subprocess
import secrets
from typing import Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


class DashboardStarter:
    """Dashboard startup manager with pre-flight checks"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.parent_dir = self.base_dir.parent
        self.errors = []
        self.warnings = []
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        required_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < required_version:
            self.errors.append(
                f"Python {required_version[0]}.{required_version[1]}+ required. "
                f"Current version: {current_version[0]}.{current_version[1]}"
            )
            return False
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        required_packages = [
            'flask',
            'flask_cors',
            'cryptography',
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            self.errors.append(
                f"Missing required packages: {', '.join(missing)}\n"
                f"Install with: pip install -r requirements.txt"
            )
            return False
        return True
    
    def check_directories(self) -> bool:
        """Check and create required directories"""
        required_dirs = [
            self.parent_dir / 'data' / 'cache',
            self.parent_dir / 'data' / 'credentials',
            self.parent_dir / 'configs',
            self.parent_dir / 'logs',
        ]
        
        for dir_path in required_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.errors.append(f"Failed to create directory {dir_path}: {e}")
                return False
        
        return True
    
    def check_env_file(self) -> bool:
        """Check if .env file exists and has required variables"""
        env_file = self.base_dir / '.env'
        env_example = self.base_dir / '.env.example'
        
        if not env_file.exists():
            if env_example.exists():
                self.warnings.append(
                    f".env file not found. Example available at {env_example}\n"
                    "Consider creating .env from .env.example and setting your keys."
                )
            else:
                self.warnings.append(
                    ".env file not found. Using default configuration.\n"
                    "For production, create .env file with proper secret keys."
                )
        
        return True
    
    def check_secret_keys(self) -> bool:
        """Check if secret keys are properly configured"""
        flask_secret = os.getenv('FLASK_SECRET_KEY')
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if not flask_secret or flask_secret == 'dev-secret-key-change-in-production':
            self.warnings.append(
                "FLASK_SECRET_KEY not set or using default value.\n"
                "Generate a secure key with:\n"
                "  python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        if not encryption_key:
            self.warnings.append(
                "ENCRYPTION_KEY not set. Credential encryption will use default key.\n"
                "Generate a secure key with:\n"
                "  python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        
        return True
    
    def check_broker_adapters(self) -> bool:
        """Check if broker adapter files exist"""
        adapter_files = [
            self.parent_dir / 'src' / 'kite_adapter.py',
            self.parent_dir / 'src' / 'paper_trading_adapter.py',
        ]
        
        missing = []
        for adapter_file in adapter_files:
            if not adapter_file.exists():
                missing.append(adapter_file.name)
        
        if missing:
            self.warnings.append(
                f"Some broker adapters not found: {', '.join(missing)}\n"
                "Some broker connections may not work."
            )
        
        return True
    
    def run_checks(self) -> bool:
        """Run all startup checks"""
        print("=" * 80)
        print("Indian Market Web Dashboard - Startup Checks")
        print("=" * 80)
        print()
        
        checks = [
            ("Python version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Directories", self.check_directories),
            ("Environment file", self.check_env_file),
            ("Secret keys", self.check_secret_keys),
            ("Broker adapters", self.check_broker_adapters),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"Checking {check_name}...", end=" ")
            try:
                result = check_func()
                if result:
                    print("✓ OK")
                else:
                    print("✗ FAILED")
                    all_passed = False
            except Exception as e:
                print(f"✗ ERROR: {e}")
                self.errors.append(f"{check_name} check failed: {e}")
                all_passed = False
        
        print()
        
        # Display warnings
        if self.warnings:
            print("⚠ WARNINGS:")
            print("-" * 80)
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # Display errors
        if self.errors:
            print("✗ ERRORS:")
            print("-" * 80)
            for error in self.errors:
                print(f"  {error}")
            print()
            print("Please fix the errors above before starting the dashboard.")
            return False
        
        if self.warnings:
            print("Startup checks completed with warnings. Dashboard can start.")
        else:
            print("✓ All startup checks passed!")
        
        print()
        return all_passed
    
    def generate_keys(self):
        """Generate and display secure keys"""
        print("=" * 80)
        print("Generating Secure Keys")
        print("=" * 80)
        print()
        
        # Generate Flask secret key
        flask_secret = secrets.token_hex(32)
        print("Flask Secret Key:")
        print(f"  FLASK_SECRET_KEY={flask_secret}")
        print()
        
        # Generate encryption key
        try:
            from cryptography.fernet import Fernet
            encryption_key = Fernet.generate_key().decode()
            print("Encryption Key:")
            print(f"  ENCRYPTION_KEY={encryption_key}")
            print()
        except ImportError:
            print("Encryption Key: (install cryptography package first)")
            print()
        
        print("Add these to your .env file:")
        print("-" * 80)
        print(f"FLASK_SECRET_KEY={flask_secret}")
        if 'encryption_key' in locals():
            print(f"ENCRYPTION_KEY={encryption_key}")
        print()
    
    def start_dashboard(self, args):
        """Start the dashboard with given arguments"""
        # Import here to avoid import errors during checks
        from indian_dashboard import app, logger
        
        print("=" * 80)
        print("Starting Indian Market Web Dashboard")
        print("=" * 80)
        print()
        print(f"  Host: {args.host}")
        print(f"  Port: {args.port}")
        print(f"  Debug: {args.debug}")
        print(f"  URL: http://{args.host}:{args.port}")
        print()
        print("  Press Ctrl+C to stop")
        print("=" * 80)
        print()
        
        try:
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug,
                use_reloader=args.reload,
                threaded=True
            )
        except KeyboardInterrupt:
            print()
            print("=" * 80)
            print("Dashboard stopped by user")
            print("=" * 80)
        except Exception as e:
            print()
            print("=" * 80)
            print(f"Error starting dashboard: {e}")
            print("=" * 80)
            sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Indian Market Web Dashboard - Multi-broker trading dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with default settings
  python run_dashboard.py
  
  # Start on custom host and port
  python run_dashboard.py --host 0.0.0.0 --port 5000
  
  # Start in debug mode
  python run_dashboard.py --debug
  
  # Generate secure keys
  python run_dashboard.py --generate-keys
  
  # Skip startup checks (not recommended)
  python run_dashboard.py --skip-checks
        """
    )
    
    # Server options
    parser.add_argument(
        '--host',
        default=os.getenv('DASHBOARD_HOST', '127.0.0.1'),
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('DASHBOARD_PORT', '8080')),
        help='Port to bind to (default: 8080)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=os.getenv('DASHBOARD_DEBUG', 'False').lower() == 'true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--reload',
        action='store_true',
        default=False,
        help='Enable auto-reload on code changes (debug mode only)'
    )
    
    # Utility options
    parser.add_argument(
        '--generate-keys',
        action='store_true',
        help='Generate secure keys for .env file'
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip startup checks (not recommended)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Run startup checks only, do not start dashboard'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=os.getenv('LOG_LEVEL', 'INFO'),
        help='Set logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Set log level
    os.environ['LOG_LEVEL'] = args.log_level
    
    # Create starter instance
    starter = DashboardStarter()
    
    # Handle generate-keys command
    if args.generate_keys:
        starter.generate_keys()
        return
    
    # Run startup checks
    if not args.skip_checks:
        checks_passed = starter.run_checks()
        
        if not checks_passed:
            sys.exit(1)
        
        if args.check_only:
            print("Startup checks completed. Exiting.")
            return
    
    # Start dashboard
    starter.start_dashboard(args)


if __name__ == '__main__':
    main()
