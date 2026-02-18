# Credential Encryption Guide

## Overview

The Indian Market Web Dashboard uses Fernet encryption (from the `cryptography` library) to securely store broker credentials. This ensures that sensitive information like API keys and secrets are never stored in plain text.

## How It Works

### Encryption Process

1. **User enters credentials** in the web interface
2. **Credentials are sent to the backend** via HTTPS (in production)
3. **Backend encrypts credentials** using Fernet symmetric encryption
4. **Encrypted data is saved** to disk in the `data/credentials/` directory
5. **Original credentials are never stored** in plain text

### Decryption Process

1. **User requests to load saved credentials**
2. **Backend reads encrypted file** from disk
3. **Backend decrypts credentials** using the encryption key
4. **Decrypted credentials are used** to connect to broker
5. **Credentials are never sent** to the frontend

## Encryption Key Management

### Development Environment

For development, the dashboard will automatically generate an encryption key if one is not provided. However, this key will be different each time the application starts, making previously saved credentials unreadable.

**To persist credentials across restarts:**

1. Generate a key:
```python
from services.credential_manager import CredentialManager
key = CredentialManager.generate_key()
print(key)
```

2. Set the environment variable:
```bash
# Windows
set ENCRYPTION_KEY=your-generated-key-here

# Linux/Mac
export ENCRYPTION_KEY=your-generated-key-here
```

3. Or add to `.env` file:
```
ENCRYPTION_KEY=your-generated-key-here
```

### Production Environment

**CRITICAL: In production, you MUST:**

1. **Generate a secure encryption key** before first use
2. **Store the key securely** (environment variable, secrets manager, etc.)
3. **Never commit the key** to version control
4. **Back up the key** - if lost, saved credentials cannot be recovered
5. **Rotate the key periodically** for enhanced security

### Generating a Production Key

```python
from cryptography.fernet import Fernet

# Generate a new key
key = Fernet.generate_key()
print(key.decode())
```

Or use the provided utility:

```python
from services.credential_manager import CredentialManager
key = CredentialManager.generate_key()
print(key)
```

### Storing the Key Securely

**Recommended approaches:**

1. **Environment Variable** (simplest):
   ```bash
   export ENCRYPTION_KEY="your-key-here"
   ```

2. **AWS Secrets Manager** (for AWS deployments):
   ```python
   import boto3
   client = boto3.client('secretsmanager')
   response = client.get_secret_value(SecretId='dashboard/encryption-key')
   key = response['SecretString']
   ```

3. **Azure Key Vault** (for Azure deployments):
   ```python
   from azure.keyvault.secrets import SecretClient
   client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
   key = client.get_secret("encryption-key").value
   ```

4. **Docker Secrets** (for Docker deployments):
   ```bash
   docker secret create encryption_key key.txt
   ```

## API Endpoints

### Save Credentials During Connection

```javascript
POST /api/broker/connect
{
  "broker": "kite",
  "credentials": {
    "api_key": "your-api-key",
    "api_secret": "your-api-secret"
  },
  "save_credentials": true  // Set to true to save encrypted
}
```

### List Saved Credentials

```javascript
GET /api/broker/credentials/saved

Response:
{
  "success": true,
  "brokers": ["kite", "alice_blue"]
}
```

### Load Saved Credentials

```javascript
POST /api/broker/credentials/load/kite

Response:
{
  "success": true,
  "message": "Connected to kite using saved credentials",
  "user_info": {...}
}
```

### Delete Saved Credentials

```javascript
DELETE /api/broker/credentials/delete/kite

Response:
{
  "success": true,
  "message": "Deleted saved credentials for kite"
}
```

## Security Best Practices

### 1. Use HTTPS in Production

Always use HTTPS to prevent credentials from being intercepted during transmission:

```python
# In production config
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### 2. Set Proper File Permissions

Ensure credential files are only readable by the application:

```bash
# Linux/Mac
chmod 600 data/credentials/*.enc
chmod 700 data/credentials/
```

### 3. Regular Key Rotation

Rotate encryption keys periodically:

1. Generate new key
2. Decrypt all credentials with old key
3. Re-encrypt with new key
4. Update environment variable
5. Securely delete old key

### 4. Backup Strategy

- **Back up the encryption key** separately from credentials
- Store backups in a secure location (password manager, vault)
- Test recovery process regularly

### 5. Access Control

- Limit access to the `data/credentials/` directory
- Use file system permissions
- Consider encrypting the entire directory with disk encryption

## Troubleshooting

### "Decryption error" when loading credentials

**Cause:** Encryption key has changed or is incorrect

**Solution:**
1. Check that `ENCRYPTION_KEY` environment variable is set correctly
2. Verify the key hasn't been modified
3. If key is lost, credentials cannot be recovered - delete and re-enter

### Credentials not persisting across restarts

**Cause:** No encryption key set, so a new one is generated each time

**Solution:**
1. Generate a key: `CredentialManager.generate_key()`
2. Set `ENCRYPTION_KEY` environment variable
3. Restart the application

### "Credential manager not available" error

**Cause:** Credential manager not initialized properly

**Solution:**
1. Check that `ENCRYPTION_KEY` is set (optional but recommended)
2. Verify `data/credentials/` directory exists and is writable
3. Check application logs for initialization errors

## Implementation Details

### Encryption Algorithm

- **Algorithm:** Fernet (symmetric encryption)
- **Key Size:** 256-bit
- **Based on:** AES in CBC mode with PKCS7 padding
- **Authentication:** HMAC using SHA256

### File Format

Encrypted credential files (`.enc`) contain:
- Fernet token (base64-encoded)
- Includes timestamp for key rotation
- Binary format, not human-readable

### Code Example

```python
from services.credential_manager import CredentialManager

# Initialize
manager = CredentialManager(
    credentials_dir='data/credentials',
    encryption_key='your-key-here'  # Optional
)

# Save credentials
credentials = {
    'api_key': 'your-api-key',
    'api_secret': 'your-api-secret'
}
manager.save_credentials('kite', credentials)

# Load credentials
loaded = manager.load_credentials('kite')
print(loaded)  # {'api_key': 'your-api-key', 'api_secret': 'your-api-secret'}

# Delete credentials
manager.delete_credentials('kite')
```

## Compliance Considerations

### Data Protection

- Credentials are encrypted at rest
- Encryption key must be protected
- Consider compliance requirements (GDPR, PCI-DSS, etc.)

### Audit Trail

- All credential operations are logged
- Check `logs/dashboard.log` for audit trail
- Consider implementing additional audit logging for compliance

### Data Retention

- Credentials are stored indefinitely until explicitly deleted
- Implement retention policies as needed
- Provide user option to delete their credentials

## Migration Guide

### From Unencrypted to Encrypted Storage

If you have existing unencrypted credentials:

```python
import json
from pathlib import Path
from services.credential_manager import CredentialManager

# Initialize credential manager
manager = CredentialManager('data/credentials')

# Read old unencrypted file
with open('old_credentials.json') as f:
    old_creds = json.load(f)

# Save with encryption
for broker, credentials in old_creds.items():
    manager.save_credentials(broker, credentials)

# Delete old file
Path('old_credentials.json').unlink()
```

## Support

For issues or questions:
1. Check application logs: `logs/dashboard.log`
2. Review this guide
3. Check the test files for examples
4. Consult the main README

## References

- [Cryptography Library Documentation](https://cryptography.io/)
- [Fernet Specification](https://github.com/fernet/spec/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
