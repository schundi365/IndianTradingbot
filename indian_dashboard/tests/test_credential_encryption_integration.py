"""
Integration tests for credential encryption in broker API
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
    # If running from project root
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from indian_dashboard.indian_dashboard import app as flask_app

from services.credential_manager import CredentialManager


class TestCredentialEncryptionIntegration:
    """Test credential encryption integration with broker API"""
    
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
    
    def test_connect_with_save_credentials(self):
        """Test connecting to broker and saving encrypted credentials"""
        # Test data
        broker = 'paper'
        credentials = {
            'test_key': 'test_value'
        }
        
        # Connect with save_credentials flag
        response = self.client.post('/api/broker/connect', 
            json={
                'broker': broker,
                'credentials': credentials,
                'save_credentials': True
            }
        )
        
        # Should succeed (paper trading doesn't require real credentials)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['credentials_saved'] is True
        
        # Verify credentials were saved
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        saved_creds = credential_manager.load_credentials(broker)
        assert saved_creds == credentials
    
    def test_connect_without_save_credentials(self):
        """Test connecting without saving credentials"""
        broker = 'paper'
        credentials = {
            'test_key': 'test_value'
        }
        
        # Connect without save_credentials flag
        response = self.client.post('/api/broker/connect',
            json={
                'broker': broker,
                'credentials': credentials,
                'save_credentials': False
            }
        )
        
        # Should succeed
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify credentials were NOT saved
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        saved_creds = credential_manager.load_credentials(broker)
        assert saved_creds is None
    
    def test_list_saved_credentials(self):
        """Test listing brokers with saved credentials"""
        # Save some credentials
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
    
    def test_load_saved_credentials(self):
        """Test loading saved credentials and connecting"""
        # Save credentials
        broker = 'paper'
        credentials = {'test_key': 'test_value'}
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        credential_manager.save_credentials(broker, credentials)
        
        # Load and connect
        response = self.client.post(f'/api/broker/credentials/load/{broker}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Connected to' in data['message']
    
    def test_load_nonexistent_credentials(self):
        """Test loading credentials that don't exist"""
        response = self.client.post('/api/broker/credentials/load/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No saved credentials' in data['error']
    
    def test_delete_saved_credentials(self):
        """Test deleting saved credentials"""
        # Save credentials
        broker = 'test_broker'
        credential_manager = flask_app.config['CREDENTIAL_MANAGER']
        credential_manager.save_credentials(broker, {'key': 'value'})
        
        # Delete
        response = self.client.delete(f'/api/broker/credentials/delete/{broker}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify deleted
        saved_creds = credential_manager.load_credentials(broker)
        assert saved_creds is None
    
    def test_delete_nonexistent_credentials(self):
        """Test deleting credentials that don't exist"""
        response = self.client.delete('/api/broker/credentials/delete/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_credentials_encrypted_on_disk(self):
        """Test that credentials are actually encrypted on disk"""
        # Save credentials
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
