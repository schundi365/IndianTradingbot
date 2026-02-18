"""
Broker-Specific Deployment Tests
Tests integration with different broker adapters
"""

import os
import sys
import json
import requests
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class BrokerDeploymentTester:
    """Test broker-specific deployment scenarios"""
    
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
    
    def test_broker_list(self):
        """Test broker list endpoint"""
        print("\n=== Testing Broker List ===")
        
        try:
            response = requests.get(f"{self.base_url}/api/broker/list", timeout=5)
            
            if response.status_code != 200:
                return self.log_test("Get broker list", False, 
                                    f"Status: {response.status_code}")
            
            data = response.json()
            brokers = data.get("brokers", [])
            
            self.log_test("Get broker list", True, f"Found {len(brokers)} brokers")
            
            # Check for expected brokers
            expected_brokers = ["kite", "alice_blue", "angel_one", "upstox", "paper"]
            found_brokers = [b.get("id") for b in brokers]
            
            for broker_id in expected_brokers:
                found = broker_id in found_brokers
                self.log_test(f"Broker available: {broker_id}", found)
            
            return len(brokers) > 0
            
        except Exception as e:
            return self.log_test("Get broker list", False, str(e))
    
    def test_paper_trading_broker(self):
        """Test paper trading broker (no credentials needed)"""
        print("\n=== Testing Paper Trading Broker ===")
        
        try:
            # Get credentials form (should be empty for paper trading)
            response = requests.get(
                f"{self.base_url}/api/broker/credentials-form/paper",
                timeout=5
            )
            
            form_works = response.status_code == 200
            self.log_test("Get paper trading form", form_works)
            
            if form_works:
                fields = response.json().get("fields", [])
                self.log_test("Paper trading requires no credentials", 
                             len(fields) == 0)
            
            # Connect to paper trading
            response = requests.post(
                f"{self.base_url}/api/broker/connect",
                json={"broker": "paper", "credentials": {}},
                timeout=10
            )
            
            connected = response.status_code == 200
            self.log_test("Connect to paper trading", connected)
            
            if connected:
                # Verify connection status
                response = requests.get(f"{self.base_url}/api/broker/status", timeout=5)
                status_data = response.json()
                
                is_connected = status_data.get("connected", False)
                broker_type = status_data.get("broker", "")
                
                self.log_test("Paper trading connected", is_connected)
                self.log_test("Correct broker type", broker_type == "paper")
                
                # Test getting instruments
                response = requests.get(
                    f"{self.base_url}/api/instruments",
                    timeout=10
                )
                
                has_instruments = response.status_code == 200
                self.log_test("Fetch instruments from paper trading", has_instruments)
                
                if has_instruments:
                    instruments = response.json().get("instruments", [])
                    self.log_test("Paper trading has instruments", 
                                 len(instruments) > 0,
                                 f"Count: {len(instruments)}")
                
                # Disconnect
                response = requests.post(
                    f"{self.base_url}/api/broker/disconnect",
                    timeout=5
                )
                
                disconnected = response.status_code == 200
                self.log_test("Disconnect from paper trading", disconnected)
                
                return connected and is_connected
            
            return False
            
        except Exception as e:
            return self.log_test("Paper trading broker", False, str(e))
    
    def test_kite_broker_form(self):
        """Test Kite Connect broker form"""
        print("\n=== Testing Kite Connect Broker Form ===")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/broker/credentials-form/kite",
                timeout=5
            )
            
            if response.status_code != 200:
                return self.log_test("Get Kite form", False,
                                    f"Status: {response.status_code}")
            
            data = response.json()
            fields = data.get("fields", [])
            
            self.log_test("Get Kite form", True, f"Fields: {len(fields)}")
            
            # Check for required fields
            field_names = [f.get("name") for f in fields]
            
            required_fields = ["api_key", "api_secret"]
            for field_name in required_fields:
                found = field_name in field_names
                self.log_test(f"Kite field exists: {field_name}", found)
            
            # Check for OAuth option
            has_oauth = any(f.get("type") == "button" and "oauth" in f.get("action", "")
                           for f in fields)
            self.log_test("Kite has OAuth option", has_oauth)
            
            return len(fields) > 0
            
        except Exception as e:
            return self.log_test("Kite broker form", False, str(e))
    
    def test_alice_blue_broker_form(self):
        """Test Alice Blue broker form"""
        print("\n=== Testing Alice Blue Broker Form ===")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/broker/credentials-form/alice_blue",
                timeout=5
            )
            
            if response.status_code != 200:
                return self.log_test("Get Alice Blue form", False,
                                    f"Status: {response.status_code}")
            
            data = response.json()
            fields = data.get("fields", [])
            
            self.log_test("Get Alice Blue form", True, f"Fields: {len(fields)}")
            
            # Check for required fields
            field_names = [f.get("name") for f in fields]
            
            required_fields = ["user_id", "api_key"]
            for field_name in required_fields:
                found = field_name in field_names
                self.log_test(f"Alice Blue field exists: {field_name}", found)
            
            return len(fields) > 0
            
        except Exception as e:
            return self.log_test("Alice Blue broker form", False, str(e))
    
    def test_angel_one_broker_form(self):
        """Test Angel One broker form"""
        print("\n=== Testing Angel One Broker Form ===")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/broker/credentials-form/angel_one",
                timeout=5
            )
            
            if response.status_code != 200:
                return self.log_test("Get Angel One form", False,
                                    f"Status: {response.status_code}")
            
            data = response.json()
            fields = data.get("fields", [])
            
            self.log_test("Get Angel One form", True, f"Fields: {len(fields)}")
            
            # Check for required fields
            field_names = [f.get("name") for f in fields]
            
            required_fields = ["client_id", "password", "totp"]
            for field_name in required_fields:
                found = field_name in field_names
                self.log_test(f"Angel One field exists: {field_name}", found)
            
            return len(fields) > 0
            
        except Exception as e:
            return self.log_test("Angel One broker form", False, str(e))
    
    def test_upstox_broker_form(self):
        """Test Upstox broker form"""
        print("\n=== Testing Upstox Broker Form ===")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/broker/credentials-form/upstox",
                timeout=5
            )
            
            if response.status_code != 200:
                return self.log_test("Get Upstox form", False,
                                    f"Status: {response.status_code}")
            
            data = response.json()
            fields = data.get("fields", [])
            
            self.log_test("Get Upstox form", True, f"Fields: {len(fields)}")
            
            # Check for required fields
            field_names = [f.get("name") for f in fields]
            
            required_fields = ["api_key", "api_secret", "redirect_uri"]
            for field_name in required_fields:
                found = field_name in field_names
                self.log_test(f"Upstox field exists: {field_name}", found)
            
            return len(fields) > 0
            
        except Exception as e:
            return self.log_test("Upstox broker form", False, str(e))
    
    def test_invalid_broker(self):
        """Test handling of invalid broker"""
        print("\n=== Testing Invalid Broker Handling ===")
        
        try:
            # Try to get form for invalid broker
            response = requests.get(
                f"{self.base_url}/api/broker/credentials-form/invalid_broker",
                timeout=5
            )
            
            handles_invalid = response.status_code in [400, 404]
            self.log_test("Invalid broker form request", handles_invalid,
                         f"Status: {response.status_code}")
            
            # Try to connect to invalid broker
            response = requests.post(
                f"{self.base_url}/api/broker/connect",
                json={"broker": "invalid_broker", "credentials": {}},
                timeout=5
            )
            
            rejects_invalid = response.status_code in [400, 404]
            self.log_test("Invalid broker connection", rejects_invalid,
                         f"Status: {response.status_code}")
            
            return handles_invalid and rejects_invalid
            
        except Exception as e:
            return self.log_test("Invalid broker handling", False, str(e))
    
    def run_all_tests(self):
        """Run all broker deployment tests"""
        print("=" * 60)
        print("BROKER DEPLOYMENT TEST SUITE")
        print("=" * 60)
        
        tests = [
            ("Broker List", self.test_broker_list),
            ("Paper Trading Broker", self.test_paper_trading_broker),
            ("Kite Broker Form", self.test_kite_broker_form),
            ("Alice Blue Broker Form", self.test_alice_blue_broker_form),
            ("Angel One Broker Form", self.test_angel_one_broker_form),
            ("Upstox Broker Form", self.test_upstox_broker_form),
            ("Invalid Broker Handling", self.test_invalid_broker)
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
        report_path = Path(__file__).parent / "broker_deployment_test_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                "summary": {
                    "passed": passed,
                    "total": total,
                    "success_rate": (passed/total)*100
                },
                "categories": results,
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")
        
        return passed == total


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test broker deployment")
    parser.add_argument("--url", default="http://localhost:8080",
                       help="Dashboard URL")
    
    args = parser.parse_args()
    
    tester = BrokerDeploymentTester(args.url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
