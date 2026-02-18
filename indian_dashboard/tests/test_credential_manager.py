"""
Unit tests for CredentialManager service
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.credential_manager import CredentialManager


class TestCredentialManager:
    """Test CredentialManager service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for tests
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CredentialManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_encrypt_decrypt_credentials(self):
        """Test encrypting and decrypting credentials"""
        credentials = {
            'api_key': 'test_key_123',
            'api_secret': 'test_secret_456'
        }
        
        # Encrypt
        encrypted = self.manager.encrypt_credentials(credentials)
        assert isinstance(encrypted, bytes)
        assert len(encrypted) > 0
        
        # Decrypt
        decrypted = self.manager.decrypt_credentials(encrypted)
        assert decrypted == credentials
    
    def test_save_and_load_credentials(self):
        """Test saving and loading credentials"""
        broker = 'test_broker'
        credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        
        # Save
        success = self.manager.save_credentials(broker, credentials)
        assert success is True
        
        # Verify file exists
        file_path = self.temp_dir / f"{broker}.enc"
        assert file_path.exists()
        
        # Load
        loaded = self.manager.load_credentials(broker)
        assert loaded == credentials
    
    def test_load_nonexistent_credentials(self):
        """Test loading credentials that don't exist"""
        loaded = self.manager.load_credentials('nonexistent')
        assert loaded is None
    
    def test_delete_credentials(self):
        """Test deleting credentials"""
        broker = 'test_broker'
        credentials = {'key': 'value'}
        
        # Save
        self.manager.save_credentials(broker, credentials)
        
        # Delete
        success = self.manager.delete_credentials(broker)
        assert success is True
        
        # Verify file doesn't exist
        file_path = self.temp_dir / f"{broker}.enc"
        assert not file_path.exists()
        
        # Try to load
        loaded = self.manager.load_credentials(broker)
        assert loaded is None
    
    def test_delete_nonexistent_credentials(self):
        """Test deleting credentials that don't exist"""
        success = self.manager.delete_credentials('nonexistent')
        assert success is False
    
    def test_list_saved_brokers(self):
        """Test listing saved brokers"""
        # Initially empty
        brokers = self.manager.list_saved_brokers()
        assert brokers == []
        
        # Save some credentials
        self.manager.save_credentials('broker1', {'key': 'value1'})
        self.manager.save_credentials('broker2', {'key': 'value2'})
        
        # List
        brokers = self.manager.list_saved_brokers()
        assert len(brokers) == 2
        assert 'broker1' in brokers
        assert 'broker2' in brokers
    
    def test_get_encryption_key(self):
        """Test getting encryption key"""
        key = self.manager.get_encryption_key()
        assert isinstance(key, str)
        assert len(key) > 0
    
    def test_generate_key(self):
        """Test generating new encryption key"""
        key = CredentialManager.generate_key()
        assert isinstance(key, str)
        assert len(key) > 0
        
        # Each generated key should be unique
        key2 = CredentialManager.generate_key()
        assert key != key2
    
    def test_encryption_with_custom_key(self):
        """Test using custom encryption key"""
        # Generate a key
        custom_key = CredentialManager.generate_key()
        
        # Create manager with custom key
        manager = CredentialManager(self.temp_dir, custom_key)
        
        credentials = {'test': 'data'}
        
        # Save with first manager
        manager.save_credentials('test', credentials)
        
        # Load with new manager using same key
        manager2 = CredentialManager(self.temp_dir, custom_key)
        loaded = manager2.load_credentials('test')
        
        assert loaded == credentials
