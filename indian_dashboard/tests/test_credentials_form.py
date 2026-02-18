"""
Tests for dynamic credentials form functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CREDENTIAL_FORMS


class TestCredentialsForm:
    """Test credential form configurations"""
    
    def test_all_brokers_have_forms(self):
        """Test that all brokers have credential form definitions"""
        expected_brokers = ['kite', 'alice_blue', 'angel_one', 'upstox', 'paper']
        
        for broker in expected_brokers:
            assert broker in CREDENTIAL_FORMS, f"Missing form for {broker}"
    
    def test_kite_form_structure(self):
        """Test Kite form has required fields"""
        kite_form = CREDENTIAL_FORMS['kite']
        
        # Should have at least 2 input fields + 1 button
        assert len(kite_form) >= 3
        
        # Check for required fields
        field_names = [f['name'] for f in kite_form]
        assert 'api_key' in field_names
        assert 'api_secret' in field_names
        
        # Check field properties
        api_key_field = next(f for f in kite_form if f['name'] == 'api_key')
        assert api_key_field['required'] is True
        assert api_key_field['type'] == 'text'
        assert 'help' in api_key_field
        assert 'minlength' in api_key_field
        
        api_secret_field = next(f for f in kite_form if f['name'] == 'api_secret')
        assert api_secret_field['required'] is True
        assert api_secret_field['type'] == 'password'
        assert 'help' in api_secret_field
    
    def test_alice_blue_form_structure(self):
        """Test Alice Blue form has required fields"""
        alice_form = CREDENTIAL_FORMS['alice_blue']
        
        field_names = [f['name'] for f in alice_form]
        assert 'user_id' in field_names
        assert 'api_key' in field_names
        
        # All fields should be required
        for field in alice_form:
            if field['type'] != 'button':
                assert field['required'] is True
    
    def test_angel_one_form_structure(self):
        """Test Angel One form has required fields including TOTP"""
        angel_form = CREDENTIAL_FORMS['angel_one']
        
        field_names = [f['name'] for f in angel_form]
        assert 'client_id' in field_names
        assert 'password' in field_names
        assert 'totp' in field_names
        
        # Check TOTP field has pattern validation
        totp_field = next(f for f in angel_form if f['name'] == 'totp')
        assert 'pattern' in totp_field
        assert totp_field['pattern'] == '\\d{6}'
        assert totp_field['maxlength'] == 6
    
    def test_upstox_form_structure(self):
        """Test Upstox form has required fields"""
        upstox_form = CREDENTIAL_FORMS['upstox']
        
        field_names = [f['name'] for f in upstox_form]
        assert 'api_key' in field_names
        assert 'api_secret' in field_names
        assert 'redirect_uri' in field_names
    
    def test_paper_trading_no_credentials(self):
        """Test paper trading requires no credentials"""
        paper_form = CREDENTIAL_FORMS['paper']
        assert len(paper_form) == 0
    
    def test_all_required_fields_have_labels(self):
        """Test all required fields have labels"""
        for broker, fields in CREDENTIAL_FORMS.items():
            for field in fields:
                if field.get('required'):
                    assert 'label' in field, f"Missing label for {field['name']} in {broker}"
                    assert field['label'], f"Empty label for {field['name']} in {broker}"
    
    def test_password_fields_are_masked(self):
        """Test password fields have correct type"""
        for broker, fields in CREDENTIAL_FORMS.items():
            for field in fields:
                if 'password' in field['name'].lower() or 'secret' in field['name'].lower():
                    if field['type'] != 'button':
                        assert field['type'] == 'password', f"Field {field['name']} should be password type"
    
    def test_help_text_exists_for_complex_fields(self):
        """Test complex fields have help text"""
        # Fields that should have help text
        complex_fields = ['totp', 'redirect_uri', 'api_key', 'api_secret']
        
        for broker, fields in CREDENTIAL_FORMS.items():
            for field in fields:
                if field['name'] in complex_fields:
                    assert 'help' in field, f"Missing help text for {field['name']} in {broker}"
                    assert field['help'], f"Empty help text for {field['name']} in {broker}"
    
    def test_validation_rules_present(self):
        """Test validation rules are present where needed"""
        for broker, fields in CREDENTIAL_FORMS.items():
            for field in fields:
                if field['type'] == 'text' or field['type'] == 'password':
                    # API keys should have minimum length
                    if 'api_key' in field['name'] or 'api_secret' in field['name']:
                        assert 'minlength' in field, f"Missing minlength for {field['name']}"
                    
                    # TOTP should have pattern
                    if field['name'] == 'totp':
                        assert 'pattern' in field, "TOTP should have pattern validation"
                        assert 'maxlength' in field, "TOTP should have maxlength"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
