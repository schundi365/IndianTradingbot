"""
Quick Deployment Verification Script
Runs essential checks to verify deployment is working
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class DeploymentVerifier:
    """Quick deployment verification"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_total = 0
        self.root_dir = Path(__file__).parent
    
    def check(self, name, condition, message=""):
        """Run a check"""
        self.checks_total += 1
        status = "✓" if condition else "✗"
        print(f"{status} {name}")
        if message:
            print(f"  {message}")
        if condition:
            self.checks_passed += 1
        return condition
    
    def verify_files(self):
        """Verify essential files exist"""
        print("\n=== Verifying Files ===")
        
        essential_files = [
            "indian_dashboard.py",
            "run_dashboard.py",
            "config.py",
            "requirements.txt",
            ".env.example"
        ]
        
        all_exist = True
        for file_name in essential_files:
            file_path = self.root_dir / file_name
            exists = file_path.exists()
            self.check(f"File: {file_name}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def verify_directories(self):
        """Verify essential directories exist"""
        print("\n=== Verifying Directories ===")
        
        essential_dirs = [
            "api",
            "services",
            "static",
            "templates",
            "tests"
        ]
        
        all_exist = True
        for dir_name in essential_dirs:
            dir_path = self.root_dir / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            self.check(f"Directory: {dir_name}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def verify_dependencies(self):
        """Verify Python dependencies"""
        print("\n=== Verifying Dependencies ===")
        
        try:
            import flask
            self.check("Flask installed", True, f"Version: {flask.__version__}")
        except ImportError:
            self.check("Flask installed", False, "Run: pip install flask")
            return False
        
        try:
            import cryptography
            self.check("Cryptography installed", True)
        except ImportError:
            self.check("Cryptography installed", False, 
                      "Run: pip install cryptography")
            return False
        
        try:
            import requests
            self.check("Requests installed", True)
        except ImportError:
            self.check("Requests installed", False, 
                      "Run: pip install requests")
        
        return True
    
    def verify_configuration(self):
        """Verify configuration is valid"""
        print("\n=== Verifying Configuration ===")
        
        try:
            sys.path.insert(0, str(self.root_dir))
            import config
            
            self.check("Config module loads", True)
            
            # Check essential config values
            has_config = hasattr(config, 'DASHBOARD_CONFIG')
            self.check("DASHBOARD_CONFIG exists", has_config)
            
            if has_config:
                cfg = config.DASHBOARD_CONFIG
                self.check("Port configured", 'port' in cfg, 
                          f"Port: {cfg.get('port', 'N/A')}")
                self.check("Host configured", 'host' in cfg,
                          f"Host: {cfg.get('host', 'N/A')}")
            
            return has_config
            
        except Exception as e:
            self.check("Config module loads", False, str(e))
            return False
    
    def verify_broker_adapters(self):
        """Verify broker adapters are available"""
        print("\n=== Verifying Broker Adapters ===")
        
        # Check if broker adapter files exist
        adapter_dir = self.root_dir.parent / "src" / "adapters"
        
        adapters = [
            "broker_adapter.py",
            "paper_trading_adapter.py",
            "kite_adapter.py"
        ]
        
        all_exist = True
        for adapter_file in adapters:
            adapter_path = adapter_dir / adapter_file
            exists = adapter_path.exists()
            self.check(f"Adapter: {adapter_file}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def verify_services(self):
        """Verify services are importable"""
        print("\n=== Verifying Services ===")
        
        try:
            sys.path.insert(0, str(self.root_dir))
            
            from services import broker_manager
            self.check("BrokerManager service", True)
            
            from services import instrument_service
            self.check("InstrumentService", True)
            
            from services import bot_controller
            self.check("BotController service", True)
            
            from services import credential_manager
            self.check("CredentialManager service", True)
            
            return True
            
        except Exception as e:
            self.check("Services import", False, str(e))
            return False
    
    def verify_api_endpoints(self):
        """Verify API endpoint modules exist"""
        print("\n=== Verifying API Endpoints ===")
        
        api_dir = self.root_dir / "api"
        
        endpoints = [
            "broker.py",
            "instruments.py",
            "config.py",
            "bot.py",
            "session.py"
        ]
        
        all_exist = True
        for endpoint_file in endpoints:
            endpoint_path = api_dir / endpoint_file
            exists = endpoint_path.exists()
            self.check(f"API: {endpoint_file}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def verify_frontend(self):
        """Verify frontend files exist"""
        print("\n=== Verifying Frontend ===")
        
        # Check templates
        template_path = self.root_dir / "templates" / "dashboard.html"
        self.check("Main template", template_path.exists())
        
        # Check essential CSS
        css_files = [
            "static/css/dashboard.css",
            "static/css/ui-enhancements.css",
            "static/css/loading-states.css"
        ]
        
        for css_file in css_files:
            css_path = self.root_dir / css_file
            self.check(f"CSS: {css_file}", css_path.exists())
        
        # Check essential JS
        js_files = [
            "static/js/app.js",
            "static/js/api-client.js",
            "static/js/state.js",
            "static/js/utils.js"
        ]
        
        for js_file in js_files:
            js_path = self.root_dir / js_file
            self.check(f"JS: {js_file}", js_path.exists())
        
        return True
    
    def verify_data_directories(self):
        """Verify data directories are writable"""
        print("\n=== Verifying Data Directories ===")
        
        data_dirs = [
            "data",
            "configs",
            "logs"
        ]
        
        for dir_name in data_dirs:
            dir_path = self.root_dir / dir_name
            
            # Create if doesn't exist
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.check(f"Created: {dir_name}", True)
                except Exception as e:
                    self.check(f"Create: {dir_name}", False, str(e))
                    continue
            
            # Check writable
            writable = os.access(dir_path, os.W_OK)
            self.check(f"Writable: {dir_name}", writable)
        
        return True
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("=" * 60)
        print("DEPLOYMENT VERIFICATION")
        print("=" * 60)
        
        # Run all checks
        self.verify_files()
        self.verify_directories()
        self.verify_dependencies()
        self.verify_configuration()
        self.verify_broker_adapters()
        self.verify_services()
        self.verify_api_endpoints()
        self.verify_frontend()
        self.verify_data_directories()
        
        # Print summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        success_rate = (self.checks_passed / self.checks_total * 100) if self.checks_total > 0 else 0
        
        print(f"Checks Passed: {self.checks_passed}/{self.checks_total}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.checks_passed == self.checks_total:
            print("\n✓ Deployment verification PASSED")
            print("  You can start the dashboard with: python run_dashboard.py")
            return True
        else:
            print("\n✗ Deployment verification FAILED")
            print(f"  {self.checks_total - self.checks_passed} checks failed")
            print("  Please fix the issues above before starting the dashboard")
            return False


def main():
    """Main entry point"""
    verifier = DeploymentVerifier()
    success = verifier.run_all_checks()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
