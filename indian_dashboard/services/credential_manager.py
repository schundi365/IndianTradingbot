"""
Credential Manager Service
Handles secure storage and retrieval of broker credentials
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages secure credential storage with encryption"""
    
    def __init__(self, credentials_dir: Path, encryption_key: Optional[str] = None):
        """
        Initialize credential manager
        
        Args:
            credentials_dir: Directory to store encrypted credentials
            encryption_key: Base64-encoded encryption key (generates new if None)
        """
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            # Generate new key if not provided
            self.encryption_key = Fernet.generate_key()
            logger.warning("Generated new encryption key - store this securely!")
            logger.warning(f"Encryption key: {self.encryption_key.decode()}")
        
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_credentials(self, credentials: Dict) -> bytes:
        """
        Encrypt credentials dictionary
        
        Args:
            credentials: Dictionary of credentials to encrypt
            
        Returns:
            Encrypted bytes
        """
        try:
            # Convert to JSON string
            json_str = json.dumps(credentials)
            
            # Encrypt
            encrypted = self.cipher.encrypt(json_str.encode())
            
            return encrypted
            
        except Exception as e:
            logger.error(f"Encryption error: {e}", exc_info=True)
            raise
    
    def decrypt_credentials(self, encrypted_data: bytes) -> Dict:
        """
        Decrypt credentials
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted credentials dictionary
        """
        try:
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted_data)
            
            # Parse JSON
            credentials = json.loads(decrypted.decode())
            
            return credentials
            
        except Exception as e:
            logger.error(f"Decryption error: {e}", exc_info=True)
            raise
    
    def save_credentials(self, broker: str, credentials: Dict) -> bool:
        """
        Save encrypted credentials to file
        
        Args:
            broker: Broker ID
            credentials: Credentials dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Encrypt credentials
            encrypted = self.encrypt_credentials(credentials)
            
            # Save to file
            file_path = self.credentials_dir / f"{broker}.enc"
            with open(file_path, 'wb') as f:
                f.write(encrypted)
            
            logger.info(f"Saved encrypted credentials for {broker}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}", exc_info=True)
            return False
    
    def load_credentials(self, broker: str) -> Optional[Dict]:
        """
        Load and decrypt credentials from file
        
        Args:
            broker: Broker ID
            
        Returns:
            Credentials dictionary or None if not found
        """
        try:
            file_path = self.credentials_dir / f"{broker}.enc"
            
            if not file_path.exists():
                logger.info(f"No saved credentials found for {broker}")
                return None
            
            # Read encrypted data
            with open(file_path, 'rb') as f:
                encrypted = f.read()
            
            # Decrypt
            credentials = self.decrypt_credentials(encrypted)
            
            logger.info(f"Loaded credentials for {broker}")
            return credentials
            
        except Exception as e:
            logger.error(f"Error loading credentials: {e}", exc_info=True)
            return None
    
    def delete_credentials(self, broker: str) -> bool:
        """
        Delete saved credentials
        
        Args:
            broker: Broker ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.credentials_dir / f"{broker}.enc"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted credentials for {broker}")
                return True
            else:
                logger.info(f"No credentials to delete for {broker}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting credentials: {e}", exc_info=True)
            return False
    
    def list_saved_brokers(self) -> list:
        """
        List brokers with saved credentials
        
        Returns:
            List of broker IDs
        """
        try:
            brokers = []
            for file_path in self.credentials_dir.glob("*.enc"):
                broker = file_path.stem
                brokers.append(broker)
            
            return brokers
            
        except Exception as e:
            logger.error(f"Error listing saved brokers: {e}", exc_info=True)
            return []
    
    def get_encryption_key(self) -> str:
        """
        Get the encryption key (for backup/storage)
        
        Returns:
            Base64-encoded encryption key
        """
        return self.encryption_key.decode()
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64-encoded encryption key
        """
        key = Fernet.generate_key()
        return key.decode()
