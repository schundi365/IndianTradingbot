"""
Deployment Testing Suite
Tests fresh installation, broker integration, and all features
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DeploymentTester:
    """Test deployment scenarios"""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"  {message}")
        return passed
    
    def test_fresh_installation(self):
        """Test fresh installation requirements"""
        print("\n=== Testing Fresh Installation ===")
        
        # Check required files exist
        required_files = [
            "indian_dashboard.py",
            "run_dashboard.py",
            "config.py",
            "requirements.txt",
            ".env.example",
            "templates/dashboard.html",
            "static/css/dashboard.css",
            "static/js/app.js"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = Path(__file__).parent.parent / file_path
            exists = full_path.exists()
            if not exists:
                all_exist = False
            self.log_test(f"File exists: {file_path}", exists)
        
        # Check required directories
        required_dirs = [
            "api",
            "services",
            "static",
            "templates",
            "tests",
            "data",
            "configs"
        ]
        
        for dir_path in required_dirs:
            full_path = Path(__file__).parent.parent / dir_path
            exists = full_path.exists() and full_path.is_dir()
            if not exists:
                all_exist = False
            self.log_test(f"Directory exists: {dir_path}", exists)
        
        # Check Python dependencies
        try:
            import flask
            import cryptography
            self.log_test("Flask installed", True)
            self.log_test("Cryptography installed", True)
        except ImportError as e:
            self.log_test("Dependencies installed", False, str(e))
            all_exist = False
        
        return all_exist
    
    def test_server_startup(self):
        """Test server can start"""
        print("\n=== Testing Server Startup ===")
        
        try:
            # Check if server is running
            response = requests.get(f"{self.base_url}/", timeout=5)
            running = response.status_code == 200
            self.log_test("Server is running", running)
            return running
        except requests.exceptions.RequestException as e:
            self.log_test("Server is running", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints are accessible"""
        print("\n=== Testing API Endpoints ===")
        
        endpoints = [
            # Broker endpoints
            ("GET", "/api/broker/list"),
            ("GET", "/api/broker/status"),
            
            # Instruments endpoints
            ("GET", "/api/instruments"),
            
            # Config endpoints
            ("GET", "/api/config"),
            ("GET", "/api/config/list"),
            ("GET", "/api/config/presets"),
            
            # Bot endpoints
            ("GET", "/api/bot/status"),
            ("GET", "/api/bot/account"),
            ("GET", "/api/bot/positions"),
            ("GET", "/api/bot/trades"),
            
            # Session endpoints
            ("GET", "/api/session/status")
        ]
        
        all_passed = True
        for method, endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.request(method, url, timeout=5)
                passed = response.status_code in [200, 401]  # 401 is ok for auth endpoints
                self.log_test(f"{method} {endpoint}", passed, f"Status: {response.status_code}")
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log_test(f"{method} {endpoint}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_broker_paper_trading(self):
        """Test paper trading broker (no credentials needed)"""
        print("\n=== Testing Paper Trading Broker ===")
        
        try:
            # Connect to paper trading
            response = requests.post(
                f"{self.base_url}/api/broker/connect",
                json={"broker": "paper", "credentials": {}},
                timeout=10
            )
            
            connected = response.status_code == 200
            self.log_test("Connect to paper trading", connected, 
                         f"Status: {response.status_code}")
            
            if connected:
                # Check status
                response = requests.get(f"{self.base_url}/api/broker/status", timeout=5)
                status_data = response.json()
                is_connected = status_data.get("connected", False)
                self.log_test("Paper trading status", is_connected)
                
                # Get instruments
                response = requests.get(f"{self.base_url}/api/instruments", timeout=10)
                has_instruments = response.status_code == 200
                self.log_test("Fetch instruments", has_instruments)
                
                if has_instruments:
                    instruments = response.json().get("instruments", [])
                    self.log_test("Instruments available", len(instruments) > 0,
                                 f"Count: {len(instruments)}")
                
                return True
            
            return False
            
        except Exception as e:
            self.log_test("Paper trading broker", False, str(e))
            return False
    
    def test_configuration_features(self):
        """Test configuration management features"""
        print("\n=== Testing Configuration Features ===")
        
        try:
            # Get presets
            response = requests.get(f"{self.base_url}/api/config/presets", timeout=5)
            has_presets = response.status_code == 200
            self.log_test("Load presets", has_presets)
            
            if has_presets:
                presets = response.json().get("presets", [])
                expected_presets = ["nifty_futures", "banknifty_futures", 
                                   "equity_intraday", "options_trading"]
                
                for preset_name in expected_presets:
                    found = any(p.get("name") == preset_name for p in presets)
                    self.log_test(f"Preset exists: {preset_name}", found)
            
            # Test configuration validation
            test_config = {
                "name": "test_config",
                "broker": "paper",
                "instruments": [],
                "strategy": "trend_following",
                "timeframe": "5min",
                "risk_per_trade": 2.0,
                "max_positions": 3
            }
            
            response = requests.post(
                f"{self.base_url}/api/config/validate",
                json=test_config,
                timeout=5
            )
            
            validation_works = response.status_code == 200
            self.log_test("Configuration validation", validation_works)
            
            # Test save configuration
            response = requests.post(
                f"{self.base_url}/api/config",
                json=test_config,
                timeout=5
            )
            
            save_works = response.status_code == 200
            self.log_test("Save configuration", save_works)
            
            # Test list configurations
            response = requests.get(f"{self.base_url}/api/config/list", timeout=5)
            list_works = response.status_code == 200
            self.log_test("List configurations", list_works)
            
            return has_presets and validation_works
            
        except Exception as e:
            self.log_test("Configuration features", False, str(e))
            return False
    
    def test_bot_control(self):
        """Test bot control features"""
        print("\n=== Testing Bot Control ===")
        
        try:
            # Get bot status
            response = requests.get(f"{self.base_url}/api/bot/status", timeout=5)
            status_works = response.status_code == 200
            self.log_test("Get bot status", status_works)
            
            # Get account info
            response = requests.get(f"{self.base_url}/api/bot/account", timeout=5)
            account_works = response.status_code in [200, 400]  # 400 if not connected
            self.log_test("Get account info", account_works)
            
            # Get positions
            response = requests.get(f"{self.base_url}/api/bot/positions", timeout=5)
            positions_works = response.status_code in [200, 400]
            self.log_test("Get positions", positions_works)
            
            # Get trades
            response = requests.get(f"{self.base_url}/api/bot/trades", timeout=5)
            trades_works = response.status_code in [200, 400]
            self.log_test("Get trades", trades_works)
            
            return status_works
            
        except Exception as e:
            self.log_test("Bot control", False, str(e))
            return False
    
    def test_frontend_assets(self):
        """Test frontend assets are accessible"""
        print("\n=== Testing Frontend Assets ===")
        
        assets = [
            "/static/css/dashboard.css",
            "/static/css/ui-enhancements.css",
            "/static/css/loading-states.css",
            "/static/css/error-handler.css",
            "/static/js/app.js",
            "/static/js/api-client.js",
            "/static/js/state.js",
            "/static/js/utils.js",
            "/static/js/ui-enhancements.js",
            "/static/js/loading-states.js",
            "/static/js/error-handler.js"
        ]
        
        all_passed = True
        for asset in assets:
            try:
                response = requests.get(f"{self.base_url}{asset}", timeout=5)
                passed = response.status_code == 200
                self.log_test(f"Asset: {asset}", passed)
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log_test(f"Asset: {asset}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_security_features(self):
        """Test security features"""
        print("\n=== Testing Security Features ===")
        
        try:
            # Test session management
            response = requests.get(f"{self.base_url}/api/session/status", timeout=5)
            session_works = response.status_code == 200
            self.log_test("Session management", session_works)
            
            # Test rate limiting (make multiple requests)
            rate_limit_triggered = False
            for i in range(15):
                response = requests.get(f"{self.base_url}/api/broker/list", timeout=5)
                if response.status_code == 429:
                    rate_limit_triggered = True
                    break
            
            self.log_test("Rate limiting active", rate_limit_triggered)
            
            # Test input validation (send invalid data)
            response = requests.post(
                f"{self.base_url}/api/config/validate",
                json={"invalid": "data"},
                timeout=5
            )
            
            validation_rejects = response.status_code in [400, 422]
            self.log_test("Input validation", validation_rejects)
            
            return session_works
            
        except Exception as e:
            self.log_test("Security features", False, str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n=== Testing Error Handling ===")
        
        try:
            # Test 404 handling
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=5)
            handles_404 = response.status_code == 404
            self.log_test("404 error handling", handles_404)
            
            # Test invalid broker
            response = requests.post(
                f"{self.base_url}/api/broker/connect",
                json={"broker": "invalid_broker", "credentials": {}},
                timeout=5
            )
            handles_invalid = response.status_code in [400, 404]
            self.log_test("Invalid broker handling", handles_invalid)
            
            # Test invalid config
            response = requests.post(
                f"{self.base_url}/api/config",
                json={"invalid": "config"},
                timeout=5
            )
            handles_invalid_config = response.status_code in [400, 422]
            self.log_test("Invalid config handling", handles_invalid_config)
            
            return handles_404 and handles_invalid
            
        except Exception as e:
            self.log_test("Error handling", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all deployment tests"""
        print("=" * 60)
        print("DEPLOYMENT TEST SUITE")
        print("=" * 60)
        
        # Run all test categories
        tests = [
            ("Fresh Installation", self.test_fresh_installation),
            ("Server Startup", self.test_server_startup),
            ("API Endpoints", self.test_api_endpoints),
            ("Paper Trading Broker", self.test_broker_paper_trading),
            ("Configuration Features", self.test_configuration_features),
            ("Bot Control", self.test_bot_control),
            ("Frontend Assets", self.test_frontend_assets),
            ("Security Features", self.test_security_features),
            ("Error Handling", self.test_error_handling)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"\n✗ FAIL: {test_name} - {str(e)}")
                results[test_name] = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} test categories passed")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Save detailed results
        report_path = Path(__file__).parent / "deployment_test_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                "summary": {
                    "passed": passed,
                    "total": total,
                    "success_rate": (passed/total)*100
                },
                "categories": results,
                "detailed_results": self.test_results,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")
        
        return passed == total


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test dashboard deployment")
    parser.add_argument("--url", default="http://localhost:8080",
                       help="Dashboard URL (default: http://localhost:8080)")
    parser.add_argument("--wait", action="store_true",
                       help="Wait for server to start")
    
    args = parser.parse_args()
    
    # Wait for server if requested
    if args.wait:
        print("Waiting for server to start...")
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = requests.get(args.url, timeout=2)
                if response.status_code == 200:
                    print("Server is ready!")
                    break
            except:
                pass
            time.sleep(2)
            print(f"Attempt {i+1}/{max_attempts}...")
        else:
            print("Server did not start in time")
            return False
    
    # Run tests
    tester = DeploymentTester(args.url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
