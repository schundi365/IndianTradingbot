"""
Unit tests for credential encryption API endpoints
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from indian_dashboard import app as flask_app
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from indian_dashboard.indian_dashboard import app as flask_app

from services.credential_manager import CredentialManager


class TestCredentialAPIEndpoints:
    """Test credential encryption API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for credentials
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Configure app for testing
        flask_app.config['TESTING'] = True
        flask_app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Create credential manager
        credential_manager = CredentialManager(self.temp_dir)
        
        # Update app config
        flask_app.config['CREDENTIAL_MANAGER'] = credential_manager
        
        # Reinitialize broker API with credential manager
        from api.broker import init_broker_api
        broker_manager = flask_app.config['BROKER_MANAGER']
        broker_bp = init_broker_api(broker_manager, credential_manager)
        
        # Create test client
        self.client = flask_app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_list_saved_credentials_empty(self):
        """Test listing saved credentials when none exist"""
        response = self.client.get('/api/broker/credentials/saved')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['brokers'] == []
    
    def test_list_saved_credentials(self):
        """Test listing brokers with saved credentials"""
        # Save some credentials directly
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        credential_manager.save_credentials('broker1', {'key': 'value1'})
        credential_manager.save_credentials('broker2', {'key': 'value2'})
        
        # List saved credentials
        response = self.client.get('/api/broker/credentials/saved')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['brokers']) == 2
        assert 'broker1' in data['brokers']
        assert 'broker2' in data['brokers']
    
    def test_delete_saved_credentials(self):
        """Test deleting saved credentials"""
        # Save credentials
        broker = 'test_broker'
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        credential_manager.save_credentials(broker, {'key': 'value'})
        
        # Verify it exists
        assert credential_manager.load_credentials(broker) is not None
        
        # Delete via API
        response = self.client.delete(f'/api/broker/credentials/delete/{broker}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Deleted' in data['message']
        
        # Verify deleted
        saved_creds = credential_manager.load_credentials(broker)
        assert saved_creds is None
    
    def test_delete_nonexistent_credentials(self):
        """Test deleting credentials that don't exist"""
        response = self.client.delete('/api/broker/credentials/delete/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No saved credentials' in data['error']
    
    def test_credentials_encrypted_on_disk(self):
        """Test that credentials are actually encrypted on disk"""
        # Save credentials directly
        broker = 'test_broker'
        credentials = {'api_key': 'secret123', 'api_secret': 'topsecret456'}
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        credential_manager.save_credentials(broker, credentials)
        
        # Read raw file
        file_path = self.temp_dir / f"{broker}.enc"
        assert file_path.exists()
        
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Verify it's encrypted (not plain text)
        assert b'secret123' not in encrypted_data
        assert b'topsecret456' not in encrypted_data
        assert b'api_key' not in encrypted_data
        
        # Verify we can decrypt it
        decrypted = credential_manager.decrypt_credentials(encrypted_data)
        assert decrypted == credentials
    
    def test_encryption_key_persistence(self):
        """Test that same encryption key can decrypt credentials"""
        # Get the encryption key
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        encryption_key = credential_manager.get_encryption_key()
        
        # Save credentials
        broker = 'test_broker'
        credentials = {'api_key': 'test123', 'api_secret': 'secret456'}
        credential_manager.save_credentials(broker, credentials)
        
        # Create new credential manager with same key
        new_manager = CredentialManager(self.temp_dir, encryption_key)
        
        # Should be able to load credentials
        loaded = new_manager.load_credentials(broker)
        assert loaded == credentials
    
    def test_different_key_cannot_decrypt(self):
        """Test that different encryption key cannot decrypt credentials"""
        # Save credentials with first manager
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        broker = 'test_broker'
        credentials = {'api_key': 'test123'}
        credential_manager.save_credentials(broker, credentials)
        
        # Create new manager with different key
        different_key = CredentialManager.generate_key()
        new_manager = CredentialManager(self.temp_dir, different_key)
        
        # Should fail to load (returns None on error)
        loaded = new_manager.load_credentials(broker)
        assert loaded is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
