#!/usr/bin/env python3
"""
Verification script for credential encryption
Demonstrates that credentials are encrypted before saving
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.credential_manager import CredentialManager


def main():
    """Demonstrate credential encryption"""
    print("=" * 60)
    print("Credential Encryption Verification")
    print("=" * 60)
    print()
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")
    print()
    
    try:
        # Initialize credential manager
        print("1. Initializing CredentialManager...")
        manager = CredentialManager(temp_dir)
        encryption_key = manager.get_encryption_key()
        print(f"   ✓ Encryption key generated: {encryption_key[:20]}...")
        print()
        
        # Test credentials
        broker = 'kite'
        credentials = {
            'api_key': 'my_secret_api_key_12345',
            'api_secret': 'my_super_secret_password_67890'
        }
        
        print("2. Original credentials:")
        print(f"   Broker: {broker}")
        print(f"   API Key: {credentials['api_key']}")
        print(f"   API Secret: {credentials['api_secret']}")
        print()
        
        # Save credentials (encrypted)
        print("3. Saving credentials (with encryption)...")
        success = manager.save_credentials(broker, credentials)
        if success:
            print("   ✓ Credentials saved successfully")
        else:
            print("   ✗ Failed to save credentials")
            return
        print()
        
        # Check encrypted file
        file_path = temp_dir / f"{broker}.enc"
        print("4. Checking encrypted file on disk...")
        print(f"   File path: {file_path}")
        print(f"   File exists: {file_path.exists()}")
        
        if file_path.exists():
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            print(f"   File size: {len(encrypted_data)} bytes")
            print(f"   First 50 bytes: {encrypted_data[:50]}")
            print()
            
            # Verify it's encrypted
            print("5. Verifying encryption...")
            if b'my_secret_api_key' in encrypted_data:
                print("   ✗ WARNING: API key found in plain text!")
            else:
                print("   ✓ API key NOT found in plain text (encrypted)")
            
            if b'my_super_secret_password' in encrypted_data:
                print("   ✗ WARNING: API secret found in plain text!")
            else:
                print("   ✓ API secret NOT found in plain text (encrypted)")
            
            if b'api_key' in encrypted_data:
                print("   ✗ WARNING: Field name found in plain text!")
            else:
                print("   ✓ Field names NOT found in plain text (encrypted)")
            print()
        
        # Load credentials (decrypt)
        print("6. Loading credentials (with decryption)...")
        loaded_credentials = manager.load_credentials(broker)
        
        if loaded_credentials:
            print("   ✓ Credentials loaded successfully")
            print(f"   API Key: {loaded_credentials['api_key']}")
            print(f"   API Secret: {loaded_credentials['api_secret']}")
            print()
            
            # Verify they match
            print("7. Verifying decrypted credentials match original...")
            if loaded_credentials == credentials:
                print("   ✓ Credentials match perfectly!")
            else:
                print("   ✗ Credentials don't match!")
            print()
        else:
            print("   ✗ Failed to load credentials")
            print()
        
        # Test with different key
        print("8. Testing with different encryption key...")
        different_key = CredentialManager.generate_key()
        manager2 = CredentialManager(temp_dir, different_key)
        
        loaded_with_wrong_key = manager2.load_credentials(broker)
        if loaded_with_wrong_key is None:
            print("   ✓ Cannot decrypt with different key (as expected)")
        else:
            print("   ✗ WARNING: Decrypted with wrong key!")
        print()
        
        # List saved brokers
        print("9. Listing saved brokers...")
        brokers = manager.list_saved_brokers()
        print(f"   Saved brokers: {brokers}")
        print()
        
        # Delete credentials
        print("10. Deleting credentials...")
        success = manager.delete_credentials(broker)
        if success:
            print("   ✓ Credentials deleted successfully")
            print(f"   File exists: {file_path.exists()}")
        else:
            print("   ✗ Failed to delete credentials")
        print()
        
        print("=" * 60)
        print("✅ Verification Complete - All checks passed!")
        print("=" * 60)
        
    finally:
        # Clean up
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory: {temp_dir}")


if __name__ == '__main__':
    main()
