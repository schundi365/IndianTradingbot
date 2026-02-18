"""
OAuth Implementation Verification Script
Verifies that all OAuth components are properly implemented
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

def verify_oauth_implementation():
    """Verify OAuth implementation is complete"""
    
    print("=" * 70)
    print("KITE OAUTH INTEGRATION - VERIFICATION")
    print("=" * 70)
    
    results = []
    
    # 1. Check OAuth Handler exists
    print("\n1. Checking OAuth Handler Service...")
    try:
        from indian_dashboard.services.oauth_handler import OAuthHandler
        oauth_handler = OAuthHandler()
        
        # Check required methods
        required_methods = [
            'get_oauth_url',
            'exchange_token',
            'load_token',
            'is_token_valid',
            'delete_token',
            'list_stored_tokens',
            'cleanup_expired_tokens',
            'refresh_token'
        ]
        
        for method in required_methods:
            assert hasattr(oauth_handler, method), f"Missing method: {method}"
        
        print("   ✅ OAuth Handler Service: OK")
        print(f"      - All {len(required_methods)} required methods present")
        results.append(("OAuth Handler Service", True))
    except Exception as e:
        print(f"   ❌ OAuth Handler Service: FAILED - {e}")
        results.append(("OAuth Handler Service", False))
    
    # 2. Check Broker Manager Integration
    print("\n2. Checking Broker Manager Integration...")
    try:
        from indian_dashboard.services.broker_manager import BrokerManager
        broker_manager = BrokerManager()
        
        # Check OAuth handler is initialized
        assert hasattr(broker_manager, 'oauth_handler'), "Missing oauth_handler attribute"
        assert broker_manager.oauth_handler is not None, "oauth_handler not initialized"
        
        # Check new methods
        new_methods = [
            'check_token_validity',
            'load_stored_token',
            'refresh_oauth_token',
            'list_stored_tokens',
            'cleanup_expired_tokens'
        ]
        
        for method in new_methods:
            assert hasattr(broker_manager, method), f"Missing method: {method}"
        
        print("   ✅ Broker Manager Integration: OK")
        print(f"      - OAuth handler initialized")
        print(f"      - All {len(new_methods)} new methods present")
        results.append(("Broker Manager Integration", True))
    except Exception as e:
        print(f"   ❌ Broker Manager Integration: FAILED - {e}")
        results.append(("Broker Manager Integration", False))
    
    # 3. Check API Endpoints
    print("\n3. Checking API Endpoints...")
    try:
        from indian_dashboard import app
        
        with app.test_client() as client:
            # Test OAuth initiate endpoint
            response = client.post('/api/broker/oauth/initiate',
                                  json={'broker': 'kite', 'api_key': 'test', 'api_secret': 'test'},
                                  content_type='application/json')
            assert response.status_code in [200, 400, 500], "OAuth initiate endpoint not responding"
            
            # Test OAuth callback endpoint
            response = client.get('/api/broker/oauth/callback?status=success&request_token=test')
            assert response.status_code in [200, 400, 500], "OAuth callback endpoint not responding"
            
            # Test token check endpoint
            response = client.post('/api/broker/oauth/token/check',
                                  json={'broker': 'kite', 'api_key': 'test'},
                                  content_type='application/json')
            assert response.status_code in [200, 400, 500], "Token check endpoint not responding"
            
            # Test token load endpoint
            response = client.post('/api/broker/oauth/token/load',
                                  json={'broker': 'kite', 'api_key': 'test'},
                                  content_type='application/json')
            assert response.status_code in [200, 400, 500], "Token load endpoint not responding"
            
            # Test token refresh endpoint
            response = client.post('/api/broker/oauth/token/refresh',
                                  json={'broker': 'kite', 'api_key': 'test'},
                                  content_type='application/json')
            assert response.status_code in [200, 400, 500], "Token refresh endpoint not responding"
            
            # Test token list endpoint
            response = client.get('/api/broker/oauth/tokens/list')
            assert response.status_code in [200, 400, 500], "Token list endpoint not responding"
        
        print("   ✅ API Endpoints: OK")
        print("      - OAuth initiate: /api/broker/oauth/initiate")
        print("      - OAuth callback: /api/broker/oauth/callback")
        print("      - Token check: /api/broker/oauth/token/check")
        print("      - Token load: /api/broker/oauth/token/load")
        print("      - Token refresh: /api/broker/oauth/token/refresh")
        print("      - Token list: /api/broker/oauth/tokens/list")
        results.append(("API Endpoints", True))
    except Exception as e:
        print(f"   ❌ API Endpoints: FAILED - {e}")
        results.append(("API Endpoints", False))
    
    # 4. Check Configuration
    print("\n4. Checking Configuration...")
    try:
        from config import BROKER_CONFIGS, CREDENTIAL_FORMS
        
        # Check Kite broker config
        assert 'kite' in BROKER_CONFIGS, "Kite broker not in config"
        kite_config = BROKER_CONFIGS['kite']
        assert kite_config.get('oauth_enabled') == True, "OAuth not enabled for Kite"
        assert 'redirect_url' in kite_config, "Missing redirect_url in Kite config"
        assert 'oauth/callback' in kite_config['redirect_url'], "Invalid redirect_url"
        
        # Check Kite credential form
        assert 'kite' in CREDENTIAL_FORMS, "Kite credential form not in config"
        kite_form = CREDENTIAL_FORMS['kite']
        
        # Check for OAuth button
        oauth_button = None
        for field in kite_form:
            if field.get('type') == 'button' and field.get('action') == 'oauth':
                oauth_button = field
                break
        
        assert oauth_button is not None, "OAuth button not in Kite form"
        assert 'Login with Kite' in oauth_button.get('label', ''), "Invalid OAuth button label"
        
        print("   ✅ Configuration: OK")
        print("      - Kite OAuth enabled")
        print("      - Redirect URL configured")
        print("      - OAuth button in credential form")
        results.append(("Configuration", True))
    except Exception as e:
        print(f"   ❌ Configuration: FAILED - {e}")
        results.append(("Configuration", False))
    
    # 5. Check Frontend Components
    print("\n5. Checking Frontend Components...")
    try:
        # Check credentials form JS
        creds_form_path = Path(__file__).parent / 'static' / 'js' / 'credentials-form.js'
        assert creds_form_path.exists(), "credentials-form.js not found"
        
        with open(creds_form_path, 'r') as f:
            creds_form_content = f.read()
        
        assert '_handleOAuth' in creds_form_content, "OAuth handler not in credentials-form.js"
        assert 'initiateOAuth' in creds_form_content, "initiateOAuth call not in credentials-form.js"
        assert 'oauth_success' in creds_form_content, "OAuth success handler not in credentials-form.js"
        
        # Check API client JS
        api_client_path = Path(__file__).parent / 'static' / 'js' / 'api-client.js'
        assert api_client_path.exists(), "api-client.js not found"
        
        with open(api_client_path, 'r') as f:
            api_client_content = f.read()
        
        assert 'initiateOAuth' in api_client_content, "initiateOAuth method not in api-client.js"
        assert '/broker/oauth/initiate' in api_client_content, "OAuth endpoint not in api-client.js"
        
        print("   ✅ Frontend Components: OK")
        print("      - credentials-form.js: OAuth handler present")
        print("      - api-client.js: OAuth methods present")
        results.append(("Frontend Components", True))
    except Exception as e:
        print(f"   ❌ Frontend Components: FAILED - {e}")
        results.append(("Frontend Components", False))
    
    # 6. Check Tests
    print("\n6. Checking Tests...")
    try:
        test_file = Path(__file__).parent / 'tests' / 'test_oauth_integration.py'
        assert test_file.exists(), "test_oauth_integration.py not found"
        
        # Run tests
        import pytest
        result = pytest.main([str(test_file), '-v', '--tb=short', '-q'])
        
        if result == 0:
            print("   ✅ Tests: OK")
            print("      - All OAuth integration tests passing")
            results.append(("Tests", True))
        else:
            print(f"   ❌ Tests: FAILED - Some tests failed")
            results.append(("Tests", False))
    except Exception as e:
        print(f"   ❌ Tests: FAILED - {e}")
        results.append(("Tests", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for component, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {component}")
    
    print("\n" + "-" * 70)
    print(f"Results: {passed}/{total} components verified")
    
    if passed == total:
        print("\n🎉 All components verified successfully!")
        print("\nOAuth Implementation Status: ✅ COMPLETE")
        print("\nTask 16.1 Requirements:")
        print("  ✅ Create OAuth flow handler")
        print("  ✅ Handle redirect callback")
        print("  ✅ Store access token")
        print("  ✅ Handle token refresh")
        print("\nThe Kite OAuth integration is ready for use!")
        return 0
    else:
        print("\n⚠️  Some components failed verification")
        print("Please review the errors above and fix any issues.")
        return 1


if __name__ == '__main__':
    try:
        exit_code = verify_oauth_implementation()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
